// MC counterpart of DATA/TauHypothesisTest.C: same selection, regions and
// QCD-estimate logic, run on signal MC (file_config_reco.json) instead of
// real data, so the reco-level result can be checked against GenVisTau
// truth in the same events.
//
// MC has no real lumisections (run == 1 always), so there is no golden-JSON
// filter and no HLT trigger requirement here -- those only apply to data.
//
// On top of the same OS_iso / SS_iso / OS_anti / SS_anti regions as the data
// version, each OS_iso reco pair is also gen-matched (dR < 0.3) to the two
// GenVisTau objects; when both legs match, the GenVisTau pair mass is filled
// too, so h_mVis_OS_iso (reco) and h_mVis_OS_iso_genVis (truth) can be
// compared directly for the same events.

#include "../Config.C"
#include "../Config.h"
#include "../event.C"
#include "../event.h"

#include <cmath>
#include <iostream>
#include <memory>

#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "TTreeReaderValue.h"
#include "TLorentzVector.h"
#include "TVector2.h"
#include "TH1D.h"
#include "TFile.h"

namespace
{
    constexpr Double_t TAU_PT_MIN = 40.0;
    constexpr Double_t TAU_ETA_MAX = 2.1;
    constexpr Double_t TAU_DZ_MAX = 0.2;
    constexpr Double_t PAIR_DR_MIN = 0.5;
    constexpr Double_t GEN_MATCH_DR_MAX = 0.3;

    // DeepTau 2018v2p5: vsJet/vsE 1..8 = VVVLoose..VVTight, vsMu 1..4 = VLoose..Tight
    constexpr UChar_t VSJET_BASE = 1;
    constexpr UChar_t VSJET_ISO = 5;
    constexpr UChar_t VSE_LOOSE = 2;
    constexpr UChar_t VSMU_LOOSE = 1;

    constexpr Double_t MUON_VETO_PT = 10.0;
    constexpr Double_t ELECTRON_VETO_PT = 10.0;

    enum Region
    {
        OS_ISO,
        SS_ISO,
        OS_ANTI,
        SS_ANTI,
        N_REGIONS
    };
    const char *REGION_NAMES[N_REGIONS] = {"OS_iso", "SS_iso", "OS_anti", "SS_anti"};

    struct Histos
    {
        std::unique_ptr<TH1D> mVis[N_REGIONS];
        std::unique_ptr<TH1D> mCol[N_REGIONS];
        std::unique_ptr<TH1D> mTtot[N_REGIONS];
        std::unique_ptr<TH1D> mVisOsIsoGenVis;
    };

    struct Tau
    {
        TLorentzVector p4;
        Short_t charge;
        UChar_t vsJet;
    };

    bool isStandardDecayMode(UChar_t dm)
    {
        return dm == 0 || dm == 1 || dm == 10 || dm == 11;
    }

    Double_t transverseMass(const TLorentzVector &a, const TLorentzVector &b)
    {
        return std::sqrt(std::max(0.0, 2 * a.Pt() * b.Pt() * (1 - std::cos(a.DeltaPhi(b)))));
    }

    Double_t totalTransverseMass(const TLorentzVector &t1, const TLorentzVector &t2, const TLorentzVector &met)
    {
        const Double_t a = transverseMass(t1, met);
        const Double_t b = transverseMass(t2, met);
        const Double_t c = transverseMass(t1, t2);
        return std::sqrt(a * a + b * b + c * c);
    }

    Double_t collinearMass(const TLorentzVector &t1, const TLorentzVector &t2, const TLorentzVector &met)
    {
        const Double_t det = t1.Px() * t2.Py() - t2.Px() * t1.Py();
        if (std::abs(det) < 0.1 * t1.Pt() * t2.Pt())
        {
            return -1;
        }
        const Double_t a1 = (met.Px() * t2.Py() - met.Py() * t2.Px()) / det;
        const Double_t a2 = (t1.Px() * met.Py() - t1.Py() * met.Px()) / det;
        if (a1 < 0 || a2 < 0)
        {
            return -1;
        }
        const Double_t x1 = 1.0 / (1.0 + a1);
        const Double_t x2 = 1.0 / (1.0 + a2);
        return (t1 + t2).M() / std::sqrt(x1 * x2);
    }

    Histos makeHistos()
    {
        Histos h;
        for (int r = 0; r < N_REGIONS; ++r)
        {
            const TString n = REGION_NAMES[r];
            h.mVis[r] = std::make_unique<TH1D>("h_mVis_" + n, "m_{vis} " + n + ";m_{vis} [GeV];Events", 100, 0, 500);
            h.mCol[r] = std::make_unique<TH1D>("h_mCol_" + n, "m_{col} " + n + ";m_{col} [GeV];Events", 100, 0, 500);
            h.mTtot[r] = std::make_unique<TH1D>("h_mTtot_" + n, "m_{T}^{tot} " + n + ";m_{T}^{tot} [GeV];Events", 100, 0, 2000);
        }
        h.mVisOsIsoGenVis = std::make_unique<TH1D>("h_mVis_OS_iso_genVis", "GenVisTau m_{vis}, same OS_iso events;m_{vis} [GeV];Events", 100, 0, 500);
        return h;
    }

    // closest GenVisTau to a reco tau, within GEN_MATCH_DR_MAX
    Int_t matchGenVisTau(const TLorentzVector &reco, const TTreeReaderArray<Float_t> &visEta,
                         const TTreeReaderArray<Float_t> &visPhi, Int_t exclude)
    {
        Int_t best = -1;
        Double_t bestDr = GEN_MATCH_DR_MAX;
        for (size_t i = 0; i < visEta.GetSize(); ++i)
        {
            if ((Int_t)i == exclude)
            {
                continue;
            }
            const Double_t dEta = reco.Eta() - visEta[i];
            Double_t dPhi = std::abs(reco.Phi() - visPhi[i]);
            if (dPhi > M_PI)
            {
                dPhi = 2 * M_PI - dPhi;
            }
            const Double_t dR = std::sqrt(dEta * dEta + dPhi * dPhi);
            if (dR < bestDr)
            {
                bestDr = dR;
                best = i;
            }
        }
        return best;
    }
} // namespace

void TauHypothesisTestMC()
{
    TH1::AddDirectory(kFALSE);
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_reco.json");
    std::cout << "TauHypothesisTestMC: " << rootFiles.size() << " file(s) to process." << std::endl;

    Histos h = makeHistos();
    Long64_t nRead = 0, nPairs = 0, nGenVisMatched = 0;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            continue;
        }

        TTreeReader reader(Events);
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
        TTreeReaderValue<Float_t> metPt(reader, "PuppiMET_pt");
        TTreeReaderValue<Float_t> metPhi(reader, "PuppiMET_phi");
        TTreeReaderArray<Float_t> visEta(reader, "GenVisTau_eta");
        TTreeReaderArray<Float_t> visPhi(reader, "GenVisTau_phi");
        TTreeReaderArray<Float_t> visPt(reader, "GenVisTau_pt");
        TTreeReaderArray<Float_t> visMass(reader, "GenVisTau_mass");

        while (reader.Next())
        {
            ++nRead;

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

            size_t iLead = SIZE_MAX, iSub = SIZE_MAX;
            Float_t leadPt = -1, subPt = -1;
            for (size_t i = 0; i < tauPt.GetSize(); ++i)
            {
                const bool pass = tauPt[i] > TAU_PT_MIN && std::abs(tauEta[i]) < TAU_ETA_MAX &&
                                  std::abs(tauDz[i]) < TAU_DZ_MAX && isStandardDecayMode(tauDecayMode[i]) &&
                                  tauVsJet[i] >= VSJET_BASE && tauVsE[i] >= VSE_LOOSE && tauVsMu[i] >= VSMU_LOOSE;
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

            Tau t1{TLorentzVector(), tauCharge[iLead], tauVsJet[iLead]};
            Tau t2{TLorentzVector(), tauCharge[iSub], tauVsJet[iSub]};
            t1.p4.SetPtEtaPhiM(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            t2.p4.SetPtEtaPhiM(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            if (t1.p4.DeltaR(t2.p4) < PAIR_DR_MIN)
            {
                continue;
            }
            ++nPairs;

            TLorentzVector met;
            met.SetPtEtaPhiM(*metPt, 0, *metPhi, 0);

            const bool os = t1.charge * t2.charge < 0;
            const bool iso = t1.vsJet >= VSJET_ISO && t2.vsJet >= VSJET_ISO;
            const Region region = os ? (iso ? OS_ISO : OS_ANTI) : (iso ? SS_ISO : SS_ANTI);

            const Double_t mVis = (t1.p4 + t2.p4).M();
            const Double_t mCol = collinearMass(t1.p4, t2.p4, met);
            h.mVis[region]->Fill(mVis);
            h.mTtot[region]->Fill(totalTransverseMass(t1.p4, t2.p4, met));
            if (mCol > 0)
            {
                h.mCol[region]->Fill(mCol);
            }

            if (region == OS_ISO)
            {
                const Int_t g1 = matchGenVisTau(t1.p4, visEta, visPhi, -1);
                const Int_t g2 = matchGenVisTau(t2.p4, visEta, visPhi, g1);
                if (g1 >= 0 && g2 >= 0)
                {
                    ++nGenVisMatched;
                    TLorentzVector v1, v2;
                    v1.SetPtEtaPhiM(visPt[g1], visEta[g1], visPhi[g1], visMass[g1]);
                    v2.SetPtEtaPhiM(visPt[g2], visEta[g2], visPhi[g2], visMass[g2]);
                    h.mVisOsIsoGenVis->Fill((v1 + v2).M());
                }
            }
        }
    }

    std::cout << "\nevents read: " << nRead << "  di-tau pairs: " << nPairs << std::endl;
    for (int r = 0; r < N_REGIONS; ++r)
    {
        std::cout << "  " << REGION_NAMES[r] << ": " << h.mVis[r]->Integral() << std::endl;
    }
    std::cout << "OS_iso pairs with both legs gen-matched: " << nGenVisMatched << std::endl;
    std::cout << "reco OS_iso mean mass    = " << h.mVis[OS_ISO]->GetMean() << " GeV" << std::endl;
    std::cout << "GenVisTau mean mass (same events) = " << h.mVisOsIsoGenVis->GetMean() << " GeV" << std::endl;

    const std::string outFile = "outputs/tau_hypothesis_test_mc.root";
    TFile out(outFile.c_str(), "RECREATE");
    for (int r = 0; r < N_REGIONS; ++r)
    {
        h.mVis[r]->Write();
        h.mCol[r]->Write();
        h.mTtot[r]->Write();
    }
    h.mVisOsIsoGenVis->Write();
    out.Close();
    std::cout << "\nTauHypothesisTestMC: wrote " << outFile << std::endl;
}
