// Real data, file_config_data.json, with the golden-JSON lumi mask applied:
//   - mass histograms cover 0-2000 GeV instead of 0-250 GeV, since the
//     Z' hypothesis has a wide, unknown mass range (checked up to 6000 GeV,
//     nothing above 2000 GeV, so the range was trimmed back down)
//   - MET is added to the visible pair to make a "total" mass, on top of
//     the plain visible mass
// TauMassByProng.C itself is left untouched, for testing/reference.
//
// Per-tau selection, same idea as ditauAna.cc's DeepTau requirement plus our own
// kinematic cuts:
//   - DeepTau vs jet, e, mu (VLoose/VVVLoose/VLoose): rejects jets faked as taus,
//     AND rejects real muons/electrons reconstructed as a "Tau" candidate.
//   - pT > 20 GeV, |eta| < 2.3
//   - opposite sign
//   - |delta_phi(tau, antitau)| > 2.5: back-to-back requirement
//
// delta_r is not cut on here, only shown: one h_deltaR_* histogram per channel.
//
// Next to TLorentzVector's .M(), the same pair's visible mass is also computed
// with the two other formulas used elsewhere in this session, so all three can
// be compared per channel:
//   h_mass_*           : (p1+p2).M(), via TLorentzVector
//   h_massFormula_*     : sqrt((E1+E2)^2-(px1+px2)^2-(py1+py2)^2-(pz1+pz2)^2)
//   h_massPtEtaPhi_*    : sqrt(2*pt1*pt2*(cosh(deltaEta)-cos(deltaPhi))),
//                         taus treated as massless
//
// MET (PuppiMET_pt/phi) is added as a massless, pz=0 four-vector to the
// visible pair to build a "total" mass, one h_massWithMET_* histogram per
// channel:
//   h_massWithMET_*     : (p1+p2+pMET).M()
//
// Prong grouping (NanoAOD Tau_decayMode):
//   1-prong: 0 (1prong0pi0), 1 (1prong1pi0), 2 (1prong2pi0)
//   2-prong: 5, 6 (rare / partial reconstructions)
//   3-prong: 10 (3prong0pi0), 11 (3prong1pi0)
// A pair is put in a channel only if BOTH legs are in that same prong group;
// mixed-prong pairs (e.g. 1-prong with 3-prong) go into h_mass_mixedProng.
//
// Runs over file_config_data.json (real data), filtered to certified
// good lumisections via golden_2024.json.

#include "../Config.C"
#include "../Config.h"
#include "../CutFlow.h"
#include "../event.C"
#include "../event.h"
#include "../LumiMask.C"
#include "../LumiMask.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "TTreeReaderValue.h"
#include "TLorentzVector.h"
#include "TH1F.h"
#include "TFile.h"
#include "TMath.h"

namespace
{
    constexpr Double_t TAU_PT_MIN = 20.0;
    constexpr Double_t TAU_ETA_MAX = 2.3;
    constexpr Double_t DELTA_PHI_MIN = 2.5; // back-to-back requirement

    constexpr Double_t MASS_MAX = 2000.0;
    constexpr Int_t MASS_BINS = 200;

    const char *GOLDEN_JSON = "golden_2024.json";

    // DeepTau 2018v2p5 working points: 1 = VVVLoose, 2 = VVLoose, 3 = VLoose, ...
    constexpr UChar_t VSJET_MIN = 3; // VLoose
    constexpr UChar_t VSE_MIN = 1;   // VVVLoose
    constexpr UChar_t VSMU_MIN = 1;  // VLoose

    // Wraps a phi difference into (-pi, pi], same convention as
    // NAOD_TAU/helpers/lhe/angles.py's compute_delta_phi.
    Double_t wrappedDeltaPhi(Double_t phi1, Double_t phi2)
    {
        return TVector2::Phi_mpi_pi(phi1 - phi2);
    }

    struct FourVector
    {
        Double_t px, py, pz, e;
    };

    // M = sqrt((E1+E2)^2 - (px1+px2)^2 - (py1+py2)^2 - (pz1+pz2)^2)
    Double_t formulaMass(const FourVector &a, const FourVector &b)
    {
        const Double_t e = a.e + b.e;
        const Double_t px = a.px + b.px;
        const Double_t py = a.py + b.py;
        const Double_t pz = a.pz + b.pz;
        return std::sqrt(std::max(0.0, e * e - px * px - py * py - pz * pz));
    }

    // M = sqrt(2*pt1*pt2*(cosh(deltaEta) - cos(deltaPhi))), taus treated as
    // massless. cosh(x) >= 1 and cos(x) <= 1, so the argument is never negative.
    Double_t ptEtaPhiMass(Double_t pt1, Double_t pt2, Double_t deltaEta, Double_t deltaPhi)
    {
        return std::sqrt(2 * pt1 * pt2 * (std::cosh(deltaEta) - std::cos(deltaPhi)));
    }

    enum class Prong
    {
        One,
        Two,
        Three,
        Other
    };

    Prong prongOf(UChar_t decayMode)
    {
        switch (decayMode)
        {
        case 0:
        case 1:
        case 2:
            return Prong::One;
        case 5:
        case 6:
            return Prong::Two;
        case 10:
        case 11:
            return Prong::Three;
        default:
            return Prong::Other;
        }
    }
} // namespace

void TauMassByProngWideMET()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauMassByProngWideMET: " << rootFiles.size() << " file(s) to process." << std::endl;

    const LumiMask lumiMask(GOLDEN_JSON);
    if (!lumiMask.isLoaded())
    {
        std::cerr << "TauMassByProngWideMET: golden JSON missing, stopping" << std::endl;
        return;
    }

    TH1F h_mass_oneProng("h_mass_oneProng", "m_{vis}(#tau#tau), both legs 1-prong;m_{vis} [GeV];Events",
                         MASS_BINS, 0, MASS_MAX);
    TH1F h_mass_twoProng("h_mass_twoProng", "m_{vis}(#tau#tau), both legs 2-prong;m_{vis} [GeV];Events",
                         MASS_BINS, 0, MASS_MAX);
    TH1F h_mass_threeProng("h_mass_threeProng", "m_{vis}(#tau#tau), both legs 3-prong;m_{vis} [GeV];Events",
                           MASS_BINS, 0, MASS_MAX);
    TH1F h_mass_mixedProng("h_mass_mixedProng", "m_{vis}(#tau#tau), legs in different prong groups;m_{vis} [GeV];Events",
                           MASS_BINS, 0, MASS_MAX);

    TH1F h_deltaR_oneProng("h_deltaR_oneProng", "#Delta R(#tau#tau), both legs 1-prong;#Delta R;Events", 64, 0, 6);
    TH1F h_deltaR_twoProng("h_deltaR_twoProng", "#Delta R(#tau#tau), both legs 2-prong;#Delta R;Events", 64, 0, 6);
    TH1F h_deltaR_threeProng("h_deltaR_threeProng", "#Delta R(#tau#tau), both legs 3-prong;#Delta R;Events", 64, 0, 6);
    TH1F h_deltaR_mixedProng("h_deltaR_mixedProng", "#Delta R(#tau#tau), legs in different prong groups;#Delta R;Events", 64, 0, 6);

    // same masses as h_mass_*, but from the explicit E/px/py/pz formula
    TH1F h_massFormula_oneProng("h_massFormula_oneProng", "m_{vis} formula, both legs 1-prong;m_{vis} [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massFormula_twoProng("h_massFormula_twoProng", "m_{vis} formula, both legs 2-prong;m_{vis} [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massFormula_threeProng("h_massFormula_threeProng", "m_{vis} formula, both legs 3-prong;m_{vis} [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massFormula_mixedProng("h_massFormula_mixedProng", "m_{vis} formula, legs in different prong groups;m_{vis} [GeV];Events", MASS_BINS, 0, MASS_MAX);

    // same masses again, from the massless pt/eta/phi formula
    TH1F h_massPtEtaPhi_oneProng("h_massPtEtaPhi_oneProng", "m_{vis} pt/eta/phi formula, both legs 1-prong;m_{vis} [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massPtEtaPhi_twoProng("h_massPtEtaPhi_twoProng", "m_{vis} pt/eta/phi formula, both legs 2-prong;m_{vis} [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massPtEtaPhi_threeProng("h_massPtEtaPhi_threeProng", "m_{vis} pt/eta/phi formula, both legs 3-prong;m_{vis} [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massPtEtaPhi_mixedProng("h_massPtEtaPhi_mixedProng", "m_{vis} pt/eta/phi formula, legs in different prong groups;m_{vis} [GeV];Events", MASS_BINS, 0, MASS_MAX);

    // visible pair + MET, added as a massless pz=0 four-vector
    TH1F h_massWithMET_oneProng("h_massWithMET_oneProng", "m(#tau#tau+MET), both legs 1-prong;m [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massWithMET_twoProng("h_massWithMET_twoProng", "m(#tau#tau+MET), both legs 2-prong;m [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massWithMET_threeProng("h_massWithMET_threeProng", "m(#tau#tau+MET), both legs 3-prong;m [GeV];Events", MASS_BINS, 0, MASS_MAX);
    TH1F h_massWithMET_mixedProng("h_massWithMET_mixedProng", "m(#tau#tau+MET), legs in different prong groups;m [GeV];Events", MASS_BINS, 0, MASS_MAX);

    CutFlow cutFlow;
    Long64_t nGoodLumi = 0;
    Long64_t nOneProng = 0, nTwoProng = 0, nThreeProng = 0, nMixedProng = 0;
    Double_t maxDiffFormula = 0.0;
    Double_t maxDiffPtEtaPhi = 0.0;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            std::cerr << "TauMassByProngWideMET: skipping " << file.path << std::endl;
            continue;
        }

        TTreeReader reader(Events);
        TTreeReaderValue<UInt_t> run(reader, "run");
        TTreeReaderValue<UInt_t> lumiBlock(reader, "luminosityBlock");
        TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
        TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
        TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
        TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
        TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");
        TTreeReaderArray<UChar_t> tauDecayMode(reader, "Tau_decayMode");
        TTreeReaderArray<UChar_t> tauVsJet(reader, "Tau_idDeepTau2018v2p5VSjet");
        TTreeReaderArray<UChar_t> tauVsE(reader, "Tau_idDeepTau2018v2p5VSe");
        TTreeReaderArray<UChar_t> tauVsMu(reader, "Tau_idDeepTau2018v2p5VSmu");
        TTreeReaderValue<Float_t> metPt(reader, "PuppiMET_pt");
        TTreeReaderValue<Float_t> metPhi(reader, "PuppiMET_phi");

        while (reader.Next())
        {
            ++cutFlow.eventsRead;
            if (!lumiMask.isGood(*run, *lumiBlock))
            {
                continue;
            }
            ++nGoodLumi;

            const size_t nTau = tauPt.GetSize();
            if (nTau < 2)
            {
                continue;
            }

            // per-tau selection: DeepTau ID (rejects jet/e/mu fakes) + pT + eta,
            // BEFORE picking the leading pair -- a tau failing the ID (e.g. a
            // real muon) is not eligible to be "leading" at all.
            //
            // Only the top 2 by pT are ever used, so this tracks them in a
            // single pass instead of collecting every good tau into a vector
            // and sorting it -- no heap allocation per event.
            size_t iLead = SIZE_MAX, iSub = SIZE_MAX;
            Double_t leadPt = -1.0, subPt = -1.0;
            size_t nGood = 0;
            for (size_t i = 0; i < nTau; ++i)
            {
                const bool passesId = tauVsJet[i] >= VSJET_MIN && tauVsE[i] >= VSE_MIN && tauVsMu[i] >= VSMU_MIN;
                const bool passesKinematics = tauPt[i] > TAU_PT_MIN && std::abs(tauEta[i]) < TAU_ETA_MAX;
                if (!passesId || !passesKinematics)
                {
                    continue;
                }
                ++nGood;
                if (tauPt[i] > leadPt)
                {
                    iSub = iLead;
                    subPt = leadPt;
                    iLead = i;
                    leadPt = tauPt[i];
                }
                else if (tauPt[i] > subPt)
                {
                    iSub = i;
                    subPt = tauPt[i];
                }
            }
            if (nGood < 2)
            {
                continue;
            }
            ++cutFlow.atLeastTwoTaus;

            // opposite sign
            if (tauCharge[iLead] * tauCharge[iSub] != -1)
            {
                continue;
            }
            ++cutFlow.oppositeSign;
            ++cutFlow.passKinematics; // pT/eta already required above, for symmetry with the other macros

            // back-to-back requirement
            const Double_t deltaPhi = wrappedDeltaPhi(tauPhi[iLead], tauPhi[iSub]);
            if (std::abs(deltaPhi) <= DELTA_PHI_MIN)
            {
                continue;
            }

            TLorentzVector p1, p2;
            p1.SetPtEtaPhiM(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            p2.SetPtEtaPhiM(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            const Double_t mVis = (p1 + p2).M();
            const Double_t deltaR = p1.DeltaR(p2);

            // the same mass, from the other two formulas -- reuse p1/p2's
            // already-computed px/py/pz/E instead of recomputing
            // cos/sin/sinh a second time
            const FourVector v1{p1.Px(), p1.Py(), p1.Pz(), p1.E()};
            const FourVector v2{p2.Px(), p2.Py(), p2.Pz(), p2.E()};
            const Double_t mVisFormula = formulaMass(v1, v2);
            const Double_t mVisPtEtaPhi = ptEtaPhiMass(tauPt[iLead], tauPt[iSub],
                                                       tauEta[iLead] - tauEta[iSub], deltaPhi);
            maxDiffFormula = std::max(maxDiffFormula, std::abs(mVis - mVisFormula));
            maxDiffPtEtaPhi = std::max(maxDiffPtEtaPhi, std::abs(mVis - mVisPtEtaPhi));

            // MET added as a massless, pz=0 four-vector
            TLorentzVector pMET;
            pMET.SetPxPyPzE(*metPt * std::cos(*metPhi), *metPt * std::sin(*metPhi), 0.0, *metPt);
            const Double_t mWithMET = (p1 + p2 + pMET).M();

            const Prong prong1 = prongOf(tauDecayMode[iLead]);
            const Prong prong2 = prongOf(tauDecayMode[iSub]);

            if (prong1 == Prong::Other || prong2 == Prong::Other)
            {
                // one leg is an uncommon/failed decay mode: not counted in any channel
            }
            else if (prong1 == prong2)
            {
                switch (prong1)
                {
                case Prong::One:
                    h_mass_oneProng.Fill(mVis);
                    h_massFormula_oneProng.Fill(mVisFormula);
                    h_massPtEtaPhi_oneProng.Fill(mVisPtEtaPhi);
                    h_massWithMET_oneProng.Fill(mWithMET);
                    h_deltaR_oneProng.Fill(deltaR);
                    ++nOneProng;
                    break;
                case Prong::Two:
                    h_mass_twoProng.Fill(mVis);
                    h_massFormula_twoProng.Fill(mVisFormula);
                    h_massPtEtaPhi_twoProng.Fill(mVisPtEtaPhi);
                    h_massWithMET_twoProng.Fill(mWithMET);
                    h_deltaR_twoProng.Fill(deltaR);
                    ++nTwoProng;
                    break;
                case Prong::Three:
                    h_mass_threeProng.Fill(mVis);
                    h_massFormula_threeProng.Fill(mVisFormula);
                    h_massPtEtaPhi_threeProng.Fill(mVisPtEtaPhi);
                    h_massWithMET_threeProng.Fill(mWithMET);
                    h_deltaR_threeProng.Fill(deltaR);
                    ++nThreeProng;
                    break;
                default:
                    break;
                }
            }
            else
            {
                h_mass_mixedProng.Fill(mVis);
                h_massFormula_mixedProng.Fill(mVisFormula);
                h_massPtEtaPhi_mixedProng.Fill(mVisPtEtaPhi);
                h_massWithMET_mixedProng.Fill(mWithMET);
                h_deltaR_mixedProng.Fill(deltaR);
                ++nMixedProng;
            }

            ++cutFlow.used;
        }
    }

    std::cout << "TauMassByProngWideMET: " << cutFlow.used << " good pairs out of "
              << cutFlow.eventsRead << " events read (" << nGoodLumi << " in good lumi)." << std::endl;
    std::cout << "  1-prong/1-prong:   " << nOneProng << std::endl;
    std::cout << "  2-prong/2-prong:   " << nTwoProng << std::endl;
    std::cout << "  3-prong/3-prong:   " << nThreeProng << std::endl;
    std::cout << "  mixed prong:       " << nMixedProng << std::endl;
    std::cout << "TauMassByProngWideMET: max |M - M_formula|   = " << maxDiffFormula << " GeV" << std::endl;
    std::cout << "TauMassByProngWideMET: max |M - M_ptEtaPhi|   = " << maxDiffPtEtaPhi << " GeV" << std::endl;

    const std::string outFile = "outputs/tau_mass_by_prong_wide_met.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_mass_oneProng.Write();
    h_mass_twoProng.Write();
    h_mass_threeProng.Write();
    h_mass_mixedProng.Write();
    h_massFormula_oneProng.Write();
    h_massFormula_twoProng.Write();
    h_massFormula_threeProng.Write();
    h_massFormula_mixedProng.Write();
    h_massPtEtaPhi_oneProng.Write();
    h_massPtEtaPhi_twoProng.Write();
    h_massPtEtaPhi_threeProng.Write();
    h_massPtEtaPhi_mixedProng.Write();
    h_massWithMET_oneProng.Write();
    h_massWithMET_twoProng.Write();
    h_massWithMET_threeProng.Write();
    h_massWithMET_mixedProng.Write();
    h_deltaR_oneProng.Write();
    h_deltaR_twoProng.Write();
    h_deltaR_threeProng.Write();
    h_deltaR_mixedProng.Write();
    out.Close();

    std::cout << "TauMassByProngWideMET: wrote " << outFile << std::endl;
}
