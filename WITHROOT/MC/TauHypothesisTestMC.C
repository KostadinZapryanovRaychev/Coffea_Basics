// Reco-level di-tau visible mass on signal MC: the two reconstructed Tau
// objects' decay products, missing the neutrino energy each tau lost.
// Same selection and branches as DATA/TauHypothesisTest.C's OS_iso region,
// so the two are directly comparable once run on real data.
//
// Compare to MC/TauLHEFormulaMass.C: that histogram peaks at the generated
// Z' mass (nothing lost yet); this one sits below it, by the amount the
// escaping neutrinos carried away.
//
// Runs over file_config_reco.json (Monte Carlo, ZprimeTo2Tau samples).

#include "../Config.C"
#include "../Config.h"
#include "../event.C"
#include "../event.h"

#include <cmath>
#include <iostream>

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
    constexpr UChar_t VSJET_ISO = 5;
    constexpr UChar_t VSE_LOOSE = 2;
    constexpr UChar_t VSMU_LOOSE = 1;

    constexpr Double_t MUON_VETO_PT = 10.0;
    constexpr Double_t ELECTRON_VETO_PT = 10.0;

    bool isStandardDecayMode(UChar_t dm)
    {
        return dm == 0 || dm == 1 || dm == 10 || dm == 11;
    }
} // namespace

void TauHypothesisTestMC()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_reco.json");
    std::cout << "TauHypothesisTestMC: " << rootFiles.size() << " file(s) to process." << std::endl;

    TH1F h_reco_mass("h_reco_mass", "m = #sqrt{(E_{1}+E_{2})^{2}-|#vec{p}_{1}+#vec{p}_{2}|^{2}};m [GeV];Events", 100, 0, 500);

    Long64_t nRead = 0, nPairs = 0;

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

            if (tauCharge[iLead] * tauCharge[iSub] != -1)
            {
                continue;
            }

            TLorentzVector t1, t2;
            t1.SetPtEtaPhiM(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            t2.SetPtEtaPhiM(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            if (t1.DeltaR(t2) < PAIR_DR_MIN)
            {
                continue;
            }
            ++nPairs;

            h_reco_mass.Fill((t1 + t2).M());
        }
    }

    std::cout << "TauHypothesisTestMC: " << nPairs << " good pairs out of " << nRead << " events read." << std::endl;
    std::cout << "TauHypothesisTestMC: mean mass = " << h_reco_mass.GetMean() << " GeV, RMS = " << h_reco_mass.GetRMS() << " GeV" << std::endl;

    const std::string outFile = "outputs/tau_hypothesis_test_mc.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_reco_mass.Write();
    out.Close();
    std::cout << "TauHypothesisTestMC: wrote " << outFile << std::endl;
}
