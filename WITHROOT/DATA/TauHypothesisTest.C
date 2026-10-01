// Reco-level di-tau visible mass on real Run2024D Tau data: the two
// reconstructed Tau objects' decay products, missing the neutrino energy
// each tau lost. Same selection, branches and explicit mass formula as
// MC/TauHypothesisTestMC.C, so the two are directly comparable -- the only
// extra pieces here are the ones real data actually needs: the golden-JSON
// lumi mask and the HLT trigger requirement (MC has neither: run == 1
// always, and this signal MC file has no HLT branches).
//
// tau_h tau_h channel only: both legs are the Tau collection (hadronic
// decays by construction), events with an extra muon/electron are vetoed.
//
// Runs over file_config_data.json (real data), filtered to certified good
// lumisections via golden_2024.json.

#include "../Config.C"
#include "../Config.h"
#include "../event.C"
#include "../event.h"
#include "../LumiMask.C"
#include "../LumiMask.h"

#include <cmath>
#include <iostream>
#include <memory>

#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "TTreeReaderValue.h"
#include "TLorentzVector.h"
#include "TH1F.h"
#include "TFile.h"

namespace
{
    constexpr Double_t TAU_PT_MIN = 40.0;
    constexpr Double_t TAU_ETA_MAX = 2.1;
    constexpr Double_t TAU_DZ_MAX = 0.2;
    constexpr Double_t PAIR_DR_MIN = 0.5;

    // DeepTau 2018v2p5: vsJet/vsE 1..8 = VVVLoose..VVTight, vsMu 1..4 = VLoose..Tight
    // VSJET_ISO = Medium: the isolated signal-region working point.
    constexpr UChar_t VSJET_ISO = 5;
    constexpr UChar_t VSE_LOOSE = 2;
    constexpr UChar_t VSMU_LOOSE = 1;

    constexpr Double_t MUON_VETO_PT = 10.0;
    constexpr Double_t ELECTRON_VETO_PT = 10.0;

    const char *TRIGGER = "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1";
    const char *GOLDEN_JSON = "golden_2024.json";

    bool isStandardDecayMode(UChar_t dm)
    {
        return dm == 0 || dm == 1 || dm == 10 || dm == 11;
    }

    struct FourVector
    {
        Double_t px, py, pz, e;
    };

    // (pt, eta, phi, mass) -> (px, py, pz, E)
    FourVector makeFourVector(Double_t pt, Double_t eta, Double_t phi, Double_t mass)
    {
        FourVector v;
        v.px = pt * std::cos(phi);
        v.py = pt * std::sin(phi);
        v.pz = pt * std::sinh(eta);
        v.e = std::sqrt(v.px * v.px + v.py * v.py + v.pz * v.pz + mass * mass);
        return v;
    }

    // M^2 = (E1+E2)^2 - (px1+px2)^2 - (py1+py2)^2 - (pz1+pz2)^2
    Double_t invariantMassSquared(const FourVector &a, const FourVector &b)
    {
        const Double_t e = a.e + b.e;
        const Double_t px = a.px + b.px;
        const Double_t py = a.py + b.py;
        const Double_t pz = a.pz + b.pz;
        return e * e - px * px - py * py - pz * pz;
    }
} // namespace

void TauHypothesisTest()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauHypothesisTest: " << rootFiles.size() << " file(s) to process." << std::endl;

    const LumiMask lumiMask(GOLDEN_JSON);
    if (!lumiMask.isLoaded())
    {
        std::cerr << "TauHypothesisTest: golden JSON missing, stopping" << std::endl;
        return;
    }

    TH1F h_reco_mass("h_reco_mass", "m = #sqrt{(E_{1}+E_{2})^{2}-|#vec{p}_{1}+#vec{p}_{2}|^{2}} (no MET added);m [GeV];Events", 100, 0, 500);

    Long64_t nRead = 0, nGoodLumi = 0, nTrigger = 0, nNoExtraLepton = 0, nTwoGoodTaus = 0, nOppositeSign = 0, nPairs = 0, nNegativeMassSquared = 0;
    bool warnedNoTrigger = false;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            continue;
        }

        TTreeReader reader(Events);
        TTreeReaderValue<UInt_t> run(reader, "run");
        TTreeReaderValue<UInt_t> lumiBlock(reader, "luminosityBlock");
        TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
        TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
        TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
        TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
        TTreeReaderArray<Float_t> tauDz(reader, "Tau_dz");
        TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");
        TTreeReaderArray<UChar_t> tauDecayMode(reader, "Tau_decayMode");
        TTreeReaderArray<UChar_t> tauVsJet(reader, "Tau_idDeepTau2018v2p5VSjet");
        TTreeReaderArray<UChar_t> tauVsE(reader, "Tau_idDeepTau2018v2p5VSe");
        TTreeReaderArray<UChar_t> tauVsMu(reader, "Tau_idDeepTau2018v2p5VSmu");
        TTreeReaderArray<Float_t> muPt(reader, "Muon_pt");
        TTreeReaderArray<Float_t> muEta(reader, "Muon_eta");
        TTreeReaderArray<Bool_t> muLooseId(reader, "Muon_looseId");
        TTreeReaderArray<Float_t> muIso(reader, "Muon_pfRelIso04_all");
        TTreeReaderArray<Float_t> elPt(reader, "Electron_pt");
        TTreeReaderArray<Float_t> elEta(reader, "Electron_eta");
        TTreeReaderArray<UChar_t> elCutBased(reader, "Electron_cutBased");

        std::unique_ptr<TTreeReaderValue<Bool_t>> trigger;
        if (Events->GetBranch(TRIGGER))
        {
            trigger = std::make_unique<TTreeReaderValue<Bool_t>>(reader, TRIGGER);
        }
        else if (!warnedNoTrigger)
        {
            std::cout << "WARNING: " << TRIGGER << " missing, running without trigger requirement" << std::endl;
            warnedNoTrigger = true;
        }

        while (reader.Next())
        {
            ++nRead;
            if (!lumiMask.isGood(*run, *lumiBlock))
            {
                continue;
            }
            ++nGoodLumi;
            if (trigger && !**trigger)
            {
                continue;
            }
            ++nTrigger;

            bool extraLepton = false;
            for (size_t i = 0; i < muPt.GetSize() && !extraLepton; ++i)
            {
                extraLepton = muPt[i] > MUON_VETO_PT && std::abs(muEta[i]) < 2.4 && muLooseId[i] && muIso[i] < 0.3;
            }
            for (size_t i = 0; i < elPt.GetSize() && !extraLepton; ++i)
            {
                extraLepton = elPt[i] > ELECTRON_VETO_PT && std::abs(elEta[i]) < 2.5 && elCutBased[i] >= 2;
            }
            if (extraLepton)
            {
                continue;
            }
            ++nNoExtraLepton;

            size_t iLead = SIZE_MAX, iSub = SIZE_MAX;
            Float_t leadPt = -1, subPt = -1;
            for (size_t i = 0; i < tauPt.GetSize(); ++i)
            {
                const bool pass = tauPt[i] > TAU_PT_MIN && std::abs(tauEta[i]) < TAU_ETA_MAX &&
                                  std::abs(tauDz[i]) < TAU_DZ_MAX && isStandardDecayMode(tauDecayMode[i]) &&
                                  tauVsJet[i] >= VSJET_ISO && tauVsE[i] >= VSE_LOOSE && tauVsMu[i] >= VSMU_LOOSE;
                if (!pass)
                {
                    continue;
                }
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
            if (iSub == SIZE_MAX)
            {
                continue;
            }
            ++nTwoGoodTaus;

            if (tauCharge[iLead] * tauCharge[iSub] != -1)
            {
                continue;
            }
            ++nOppositeSign;

            TLorentzVector t1, t2;
            t1.SetPtEtaPhiM(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            t2.SetPtEtaPhiM(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            if (t1.DeltaR(t2) < PAIR_DR_MIN)
            {
                continue;
            }
            ++nPairs;

            const FourVector v1 = makeFourVector(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            const FourVector v2 = makeFourVector(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            const Double_t massSquared = invariantMassSquared(v1, v2);
            if (massSquared < 0)
            {
                ++nNegativeMassSquared;
                continue;
            }

            h_reco_mass.Fill(std::sqrt(massSquared));
        }
    }

    std::cout << "TauHypothesisTest: cutflow:" << std::endl;
    std::cout << "  events read                          : " << nRead << std::endl;
    std::cout << "  after golden-JSON lumi mask           : " << nGoodLumi << std::endl;
    std::cout << "  after trigger                         : " << nTrigger << std::endl;
    std::cout << "  after muon/electron veto              : " << nNoExtraLepton << std::endl;
    std::cout << "  after pT/eta/dz/decayMode/DeepTau-ISO (2 taus) : " << nTwoGoodTaus << std::endl;
    std::cout << "  after opposite sign                   : " << nOppositeSign << std::endl;
    std::cout << "  after dR(tau1,tau2) > " << PAIR_DR_MIN << "             : " << nPairs << std::endl;
    std::cout << "  (" << nNegativeMassSquared << " of those skipped for M^2 < 0)" << std::endl;
    std::cout << "TauHypothesisTest: mean mass = " << h_reco_mass.GetMean() << " GeV, RMS = " << h_reco_mass.GetRMS() << " GeV" << std::endl;

    const std::string outFile = "outputs/tau_hypothesis_test.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_reco_mass.Write();
    out.Close();
    std::cout << "TauHypothesisTest: wrote " << outFile << std::endl;
}

// ============================================================================
// OVERLEAF CAPTION (for the h_reco_mass plot)
// ============================================================================
//
// {\raggedright\fontsize{6.6}{8.4}\selectfont\color{oliveInk!70}%
//  \setlength{\parskip}{0.2em}%
//  \srcline{Input: Run2024D Tau data,
//  \texttt{file\_config\_data.json}, filtered to golden\_2024.json good
//  lumisections.}
//  \srcline{$\tau_h\tau_h$ channel only: both legs are the \texttt{Tau}
//  collection (hadronic decays by construction), events with an extra
//  muon/electron are vetoed.}
//  \srcline{Cuts: HLT trigger, $p_T>40$~GeV, $|\eta|<2.1$, $|d_z|<0.2$~cm,
//  decay mode $\in\{0,1,10,11\}$ (1- or 3-prong), DeepTau vsJet Medium
//  (isolated), opposite sign, $\Delta R(\tau_1,\tau_2)>0.5$ -- same
//  selection as the MC analysis.}
//  \srcline{\textbf{Result:} the visible mass alone, no MET added -- real
//  data's analogue of MC/TauHypothesisTestMC.C.}}
