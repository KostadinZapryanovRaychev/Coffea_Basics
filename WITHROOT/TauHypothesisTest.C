// Hypothesis test on Run2024D Tau data (file_config_data.json), tau_h tau_h channel.
//
// H1: the opposite-sign isolated di-tau sample contains genuine Z -> tau tau.
// H0: the ~91 GeV bump in m_vis comes from Z -> ee / mumu leptons faking taus.
//
// Test A (neutrino recovery): genuine Z->tautau has m_vis BELOW 91 GeV and the
//   collinear mass (MET projected back onto the taus) moves UP to ~91 GeV.
// Test B (lepton fakes): the fraction of events in 85 < m_vis < 100 GeV must
//   drop when anti-e / anti-mu DeepTau is tightened, if the bump is fakes.
// Test C (high mass): QCD is estimated from data (ABCD: charge x isolation);
//   the OS-isolated m_T^tot spectrum minus QCD is scanned for a local excess.
//
// Only QCD is modelled; DY, ttbar and W+jets are not subtracted, so Test C
// excesses are NOT evidence of new physics without MC.

#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"
#include "LumiMask.C"
#include "LumiMask.h"

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

    // DeepTau 2018v2p5: vsJet/vsE 1..8 = VVVLoose..VVTight, vsMu 1..4 = VLoose..Tight
    constexpr UChar_t VSJET_BASE = 1;
    constexpr UChar_t VSJET_ISO = 5;
    constexpr UChar_t VSE_LOOSE = 2;
    constexpr UChar_t VSMU_LOOSE = 1;
    constexpr UChar_t VSE_TIGHT = 6;
    constexpr UChar_t VSMU_TIGHT = 4;

    constexpr Double_t MUON_VETO_PT = 10.0;
    constexpr Double_t ELECTRON_VETO_PT = 10.0;

    constexpr Double_t Z_WINDOW_LOW = 85.0;
    constexpr Double_t Z_WINDOW_HIGH = 100.0;
    constexpr Double_t HIGH_MASS_SCAN_MIN = 200.0;

    const char *TRIGGER = "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1";
    const char *GOLDEN_JSON = "golden_2024.json";

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
        std::unique_ptr<TH1D> mVisTightLep;
    };

    struct Tau
    {
        TLorentzVector p4;
        Short_t charge;
        UChar_t vsJet, vsE, vsMu;
    };

    bool isStandardDecayMode(UChar_t dm)
    {
        return dm == 0 || dm == 1 || dm == 10 || dm == 11;
    }

    Double_t transverseMass(const TLorentzVector &a, const TLorentzVector &b)
    {
        return std::sqrt(std::max(0.0, 2 * a.Pt() * b.Pt() * (1 - std::cos(a.DeltaPhi(b)))));
    }

    // CMS high-mass tautau variable: sqrt(mT(t1,MET)^2 + mT(t2,MET)^2 + mT(t1,t2)^2)
    Double_t totalTransverseMass(const TLorentzVector &t1, const TLorentzVector &t2, const TLorentzVector &met)
    {
        const Double_t a = transverseMass(t1, met);
        const Double_t b = transverseMass(t2, met);
        const Double_t c = transverseMass(t1, t2);
        return std::sqrt(a * a + b * b + c * c);
    }

    // Collinear approximation: MET = a1*vis1_T + a2*vis2_T, x_i = 1/(1+a_i).
    // Returns -1 when unsolvable (back-to-back taus) or unphysical (a_i < 0).
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
            h.mVis[r]->Sumw2();
            h.mCol[r]->Sumw2();
            h.mTtot[r]->Sumw2();
        }
        h.mVisTightLep = std::make_unique<TH1D>("h_mVis_OS_iso_tightLep", "m_{vis} OS_iso, tight anti-e/#mu;m_{vis} [GeV];Events", 100, 0, 500);
        h.mVisTightLep->Sumw2();
        return h;
    }

    Double_t integral(const TH1D &h, Double_t low, Double_t high)
    {
        return h.Integral(h.GetXaxis()->FindFixBin(low), h.GetXaxis()->FindFixBin(high - 1e-6));
    }

    Double_t peakPosition(const TH1D &h, Double_t low, Double_t high)
    {
        const Int_t first = h.GetXaxis()->FindFixBin(low);
        const Int_t last = h.GetXaxis()->FindFixBin(high - 1e-6);
        Int_t best = first;
        for (Int_t b = first; b <= last; ++b)
        {
            if (h.GetBinContent(b) > h.GetBinContent(best))
            {
                best = b;
            }
        }
        return h.GetBinCenter(best);
    }

    std::unique_ptr<TH1D> qcdEstimate(const TH1D &ssIso, Double_t transfer, const char *name)
    {
        auto qcd = std::unique_ptr<TH1D>((TH1D *)ssIso.Clone(name));
        qcd->Scale(transfer);
        return qcd;
    }

    std::unique_ptr<TH1D> subtract(const TH1D &data, const TH1D &bkg, const char *name)
    {
        auto out = std::unique_ptr<TH1D>((TH1D *)data.Clone(name));
        out->Add(&bkg, -1);
        return out;
    }

    void runTestA(const TH1D &mVisExcess, const TH1D &mColExcess)
    {
        const Double_t visPeak = peakPosition(mVisExcess, 30, 150);
        const Double_t colPeak = peakPosition(mColExcess, 30, 200);
        std::cout << "\n[Test A] neutrino recovery (QCD-subtracted OS_iso)" << std::endl;
        std::cout << "  m_vis peak: " << visPeak << " GeV   m_col peak: " << colPeak << " GeV" << std::endl;
        const bool visBelowZ = visPeak < 85;
        const bool colAtZ = colPeak > 75 && colPeak < 110;
        std::cout << "  => " << (visBelowZ && colAtZ ? "consistent with genuine Z->tautau (H1)"
                                                    : "NOT the Z->tautau pattern")
                  << std::endl;
    }

    void runTestB(const TH1D &loose, const TH1D &tight)
    {
        const Double_t nLoose = loose.Integral();
        const Double_t nTight = tight.Integral();
        if (nLoose <= 0 || nTight <= 0)
        {
            std::cout << "\n[Test B] not enough events" << std::endl;
            return;
        }
        const Double_t fLoose = integral(loose, Z_WINDOW_LOW, Z_WINDOW_HIGH) / nLoose;
        const Double_t fTight = integral(tight, Z_WINDOW_LOW, Z_WINDOW_HIGH) / nTight;
        const Double_t eLoose = std::sqrt(fLoose * (1 - fLoose) / nLoose);
        const Double_t eTight = std::sqrt(fTight * (1 - fTight) / nTight);
        const Double_t pull = (fLoose - fTight) / std::sqrt(eLoose * eLoose + eTight * eTight);
        std::cout << "\n[Test B] fraction of OS_iso events with " << Z_WINDOW_LOW << " < m_vis < " << Z_WINDOW_HIGH << std::endl;
        std::cout << "  loose anti-e/mu: " << fLoose << " +- " << eLoose << "  (N=" << nLoose << ")" << std::endl;
        std::cout << "  tight anti-e/mu: " << fTight << " +- " << eTight << "  (N=" << nTight << ")" << std::endl;
        std::cout << "  drop significance: " << pull << " sigma" << std::endl;
        std::cout << "  => " << (pull > 3 ? "91 GeV bump contains lepton fakes (H0 component present)"
                                          : "no significant lepton-fake contribution")
                  << std::endl;
    }

    void runTestC(const TH1D &osIso, const TH1D &qcd, Double_t transferErr, Double_t transfer)
    {
        Double_t bestZ = 0, bestMass = 0;
        for (Int_t b = osIso.GetXaxis()->FindFixBin(HIGH_MASS_SCAN_MIN); b <= osIso.GetNbinsX(); ++b)
        {
            const Double_t nObs = osIso.GetBinContent(b);
            const Double_t nBkg = qcd.GetBinContent(b);
            if (nBkg <= 0)
            {
                continue;
            }
            const Double_t relTf = transfer > 0 ? transferErr / transfer : 0;
            const Double_t bkgErr2 = qcd.GetBinError(b) * qcd.GetBinError(b) + nBkg * nBkg * relTf * relTf;
            const Double_t z = (nObs - nBkg) / std::sqrt(nBkg + bkgErr2);
            if (z > bestZ)
            {
                bestZ = z;
                bestMass = osIso.GetBinCenter(b);
            }
        }
        std::cout << "\n[Test C] high-mass scan, m_T^tot > " << HIGH_MASS_SCAN_MIN << " GeV (QCD-only background)" << std::endl;
        std::cout << "  largest local excess: " << bestZ << " sigma at m_T^tot ~ " << bestMass << " GeV" << std::endl;
        std::cout << "  (DY/ttbar/W+jets tails are not subtracted: an excess here needs MC before any claim)" << std::endl;
    }
} // namespace

void TauHypothesisTest()
{
    TH1::AddDirectory(kFALSE);
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauHypothesisTest: " << rootFiles.size() << " file(s) to process." << std::endl;

    const LumiMask lumiMask(GOLDEN_JSON);
    if (!lumiMask.isLoaded())
    {
        std::cerr << "TauHypothesisTest: golden JSON missing, stopping" << std::endl;
        return;
    }

    Histos h = makeHistos();
    Long64_t nRead = 0, nGoodLumi = 0, nTrigger = 0, nPairs = 0;
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
        TTreeReaderValue<Float_t> metPt(reader, "PuppiMET_pt");
        TTreeReaderValue<Float_t> metPhi(reader, "PuppiMET_phi");

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

            Tau t1{TLorentzVector(), tauCharge[iLead], tauVsJet[iLead], tauVsE[iLead], tauVsMu[iLead]};
            Tau t2{TLorentzVector(), tauCharge[iSub], tauVsJet[iSub], tauVsE[iSub], tauVsMu[iSub]};
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

            const bool tightLep = t1.vsE >= VSE_TIGHT && t2.vsE >= VSE_TIGHT && t1.vsMu >= VSMU_TIGHT && t2.vsMu >= VSMU_TIGHT;
            if (region == OS_ISO && tightLep)
            {
                h.mVisTightLep->Fill(mVis);
            }
        }
    }

    std::cout << "\nevents read: " << nRead << "  good lumi: " << nGoodLumi << "  passing trigger: " << nTrigger << "  di-tau pairs: " << nPairs << std::endl;
    for (int r = 0; r < N_REGIONS; ++r)
    {
        std::cout << "  " << REGION_NAMES[r] << ": " << h.mVis[r]->Integral() << std::endl;
    }

    const Double_t osAnti = h.mVis[OS_ANTI]->Integral();
    const Double_t ssAnti = h.mVis[SS_ANTI]->Integral();
    const Double_t transfer = ssAnti > 0 ? osAnti / ssAnti : 0;
    const Double_t transferErr = (osAnti > 0 && ssAnti > 0) ? transfer * std::sqrt(1 / osAnti + 1 / ssAnti) : 0;
    std::cout << "QCD OS/SS transfer factor (anti-iso): " << transfer << " +- " << transferErr << std::endl;

    auto qcdVis = qcdEstimate(*h.mVis[SS_ISO], transfer, "h_mVis_QCD");
    auto qcdCol = qcdEstimate(*h.mCol[SS_ISO], transfer, "h_mCol_QCD");
    auto qcdTtot = qcdEstimate(*h.mTtot[SS_ISO], transfer, "h_mTtot_QCD");
    auto excessVis = subtract(*h.mVis[OS_ISO], *qcdVis, "h_mVis_excess");
    auto excessCol = subtract(*h.mCol[OS_ISO], *qcdCol, "h_mCol_excess");
    auto excessTtot = subtract(*h.mTtot[OS_ISO], *qcdTtot, "h_mTtot_excess");

    runTestA(*excessVis, *excessCol);
    runTestB(*h.mVis[OS_ISO], *h.mVisTightLep);
    runTestC(*h.mTtot[OS_ISO], *qcdTtot, transferErr, transfer);

    const std::string outFile = "outputs/tau_hypothesis_test.root";
    TFile out(outFile.c_str(), "RECREATE");
    for (int r = 0; r < N_REGIONS; ++r)
    {
        h.mVis[r]->Write();
        h.mCol[r]->Write();
        h.mTtot[r]->Write();
    }
    h.mVisTightLep->Write();
    qcdVis->Write();
    qcdCol->Write();
    qcdTtot->Write();
    excessVis->Write();
    excessCol->Write();
    excessTtot->Write();
    out.Close();
    std::cout << "\nTauHypothesisTest: wrote " << outFile << std::endl;
}
