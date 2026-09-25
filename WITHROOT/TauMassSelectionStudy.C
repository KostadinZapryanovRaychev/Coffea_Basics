// 2D studies: every selection variable (y) vs the visible di-tau mass
// (x) = (p1+p2).M(). Pair = the two highest-pT taus of the event.
// No cut is applied, so the whole distribution is visible and the
// threshold of each cut (pT > 20, |eta| < 2.3, |dphi| > 2.5, |pz| < 300,
// opposite sign) can be judged against it.
// Also answers: what happens with more than 2 taus in the event?
// Runs over every file listed in file_config_data.json (real data).

#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "TLorentzVector.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TFile.h"
#include "TMath.h"

namespace
{
    // x axis of every 2D histogram: 100 bins, 0-300 GeV.
    const Int_t MASS_BINS = 100;
    const Double_t MASS_MAX = 300.0;

    Double_t wrappedDeltaPhi(Double_t phi1, Double_t phi2)
    {
        return TVector2::Phi_mpi_pi(phi1 - phi2);
    }

    TH2F makeHistogram(const char *name, const char *yTitle, Int_t yBins, Double_t yMin, Double_t yMax)
    {
        TString title = TString::Format("%s vs m_{vis}(#tau#tau);m_{vis}(#tau#tau) [GeV];%s", yTitle, yTitle);
        return TH2F(name, title, MASS_BINS, 0, MASS_MAX, yBins, yMin, yMax);
    }

    // with more than 2 taus: is there an opposite-sign pair among the taus
    // other than the two leading ones?
    bool hasOppositeSignPair(const TTreeReaderArray<Short_t> &charge)
    {
        for (size_t i = 0; i < charge.GetSize(); ++i)
        {
            for (size_t j = i + 1; j < charge.GetSize(); ++j)
            {
                if (charge[i] * charge[j] == -1)
                {
                    return true;
                }
            }
        }
        return false;
    }
} // namespace

void TauMassSelectionStudy()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauMassSelectionStudy: " << rootFiles.size() << " file(s) to process." << std::endl;

    TH2F h_pz = makeHistogram("h2_pairPz_vs_mass", "pz(#tau#tau) [GeV]", 120, -600, 600);
    TH2F h_dphi = makeHistogram("h2_absDeltaPhi_vs_mass", "|#Delta#phi(#tau#tau)|", 64, 0, 3.2);
    TH2F h_ptLead = makeHistogram("h2_ptLeading_vs_mass", "pT leading #tau [GeV]", 100, 0, 200);
    TH2F h_ptSub = makeHistogram("h2_ptSubleading_vs_mass", "pT subleading #tau [GeV]", 100, 0, 200);
    TH2F h_etaLead = makeHistogram("h2_absEtaLeading_vs_mass", "|#eta| leading #tau", 52, 0, 2.6);
    TH2F h_etaSub = makeHistogram("h2_absEtaSubleading_vs_mass", "|#eta| subleading #tau", 52, 0, 2.6);
    TH2F h_charge = makeHistogram("h2_chargeProduct_vs_mass", "charge product (-1 = opposite sign)", 3, -1.5, 1.5);

    // multiplicity: how many taus per event, and does the leading-pair mass depend on it
    TH1F h_nTau("h_nTau", "number of taus per event;nTau;Events", 10, -0.5, 9.5);
    TH2F h_nTauMass = makeHistogram("h2_nTau_vs_mass", "nTau in the event", 10, -0.5, 9.5);

    Long64_t nEvents = 0;
    Long64_t nWithPair = 0;
    Long64_t nExactlyTwo = 0;
    Long64_t nMoreThanTwo = 0;
    Long64_t nMoreLeadingNotOS = 0;
    Long64_t nMoreLeadingNotOSButOtherOS = 0;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            std::cerr << "TauMassSelectionStudy: skipping " << file.path << std::endl;
            continue;
        }

        TTreeReader reader(Events);
        TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
        TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
        TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
        TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
        TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");

        while (reader.Next())
        {
            ++nEvents;

            const size_t nTau = tauPt.GetSize();
            h_nTau.Fill(nTau);
            if (nTau < 2)
            {
                continue;
            }

            // leading pair = two highest-pT taus
            std::vector<size_t> order(nTau);
            for (size_t i = 0; i < nTau; ++i)
            {
                order[i] = i;
            }
            std::sort(order.begin(), order.end(),
                      [&](size_t a, size_t b)
                      { return tauPt[a] > tauPt[b]; });
            const size_t iLead = order[0];
            const size_t iSub = order[1];

            TLorentzVector p1, p2;
            p1.SetPtEtaPhiM(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            p2.SetPtEtaPhiM(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            const Double_t mVis = (p1 + p2).M();

            const Int_t chargeProduct = tauCharge[iLead] * tauCharge[iSub];
            const Double_t pairPz = p1.Pz() + p2.Pz();
            const Double_t absDeltaPhi = std::abs(wrappedDeltaPhi(tauPhi[iLead], tauPhi[iSub]));

            h_pz.Fill(mVis, pairPz);
            h_dphi.Fill(mVis, absDeltaPhi);
            h_ptLead.Fill(mVis, tauPt[iLead]);
            h_ptSub.Fill(mVis, tauPt[iSub]);
            h_etaLead.Fill(mVis, std::abs(tauEta[iLead]));
            h_etaSub.Fill(mVis, std::abs(tauEta[iSub]));
            h_charge.Fill(mVis, chargeProduct);
            h_nTauMass.Fill(mVis, nTau);

            ++nWithPair;
            if (nTau == 2)
            {
                ++nExactlyTwo;
                continue;
            }

            ++nMoreThanTwo;
            if (chargeProduct != -1)
            {
                ++nMoreLeadingNotOS;
                if (hasOppositeSignPair(tauCharge))
                {
                    ++nMoreLeadingNotOSButOtherOS;
                }
            }
        }
    }

    std::cout << "TauMassSelectionStudy: " << nEvents << " events read, " << nWithPair
              << " with at least 2 taus." << std::endl;
    std::cout << "  exactly 2 taus:  " << nExactlyTwo << std::endl;
    std::cout << "  more than 2 taus: " << nMoreThanTwo << std::endl;
    std::cout << "    of those, leading pair NOT opposite sign: " << nMoreLeadingNotOS << std::endl;
    std::cout << "    of those, another opposite-sign pair exists (lost by the leading-pair rule): "
              << nMoreLeadingNotOSButOtherOS << std::endl;

    const std::string outFile = "outputs/tau_mass_selection_study.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_pz.Write();
    h_dphi.Write();
    h_ptLead.Write();
    h_ptSub.Write();
    h_etaLead.Write();
    h_etaSub.Write();
    h_charge.Write();
    h_nTau.Write();
    h_nTauMass.Write();
    out.Close();

    std::cout << "TauMassSelectionStudy: wrote " << outFile << std::endl;
}
