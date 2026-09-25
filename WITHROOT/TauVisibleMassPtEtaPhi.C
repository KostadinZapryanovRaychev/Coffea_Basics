// Visible di-tau mass from the pT / eta / phi formula (taus treated as massless):
//   M = sqrt( 2 * pt1 * pt2 * ( cosh(delta_eta) - cos(delta_phi) ) )
// Same files and same selection as TauVisibleMassFormula.C.
// Runs over file_config_data.json (real data).

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
#include "TH1F.h"
#include "TFile.h"

namespace
{
    constexpr Double_t TAU_PT_MIN = 20.0;
    constexpr Double_t TAU_ETA_MAX = 2.3;

    // M^2 = 2 * pt1 * pt2 * ( cosh(delta_eta) - cos(delta_phi) )
    // cosh(x) >= 1 and cos(x) <= 1, so M^2 is never negative.
    Double_t invariantMassSquared(Double_t pt1, Double_t pt2, Double_t deltaEta, Double_t deltaPhi)
    {
        return 2 * pt1 * pt2 * (std::cosh(deltaEta) - std::cos(deltaPhi));
    }
}

void TauVisibleMassPtEtaPhi()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauVisibleMassPtEtaPhi: " << rootFiles.size() << " file(s) to process."
              << std::endl;

    TH1F h_mVis_ptEtaPhi("h_mVis_ptEtaPhi",
                         "m_{vis}(#tau#tau) = #sqrt{2 p_{T1} p_{T2} (cosh#Delta#eta - cos#Delta#phi)};m_{vis} [GeV];Events",
                         250, 0, 250);

    Long64_t nEventsSeen = 0;
    Long64_t nPairsUsed = 0;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            std::cerr << "TauVisibleMassPtEtaPhi: skipping " << file.path << std::endl;
            continue;
        }

        TTreeReader reader(Events);
        TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
        TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
        TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
        TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");

        while (reader.Next())
        {
            ++nEventsSeen;

            const size_t nTau = tauPt.GetSize();
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

            // opposite sign
            if (tauCharge[iLead] * tauCharge[iSub] != -1)
            {
                continue;
            }

            // pT and eta cuts, both taus
            if (!(tauPt[iLead] > TAU_PT_MIN && tauPt[iSub] > TAU_PT_MIN &&
                  std::abs(tauEta[iLead]) < TAU_ETA_MAX && std::abs(tauEta[iSub]) < TAU_ETA_MAX))
            {
                continue;
            }

            // the two differences that go into the formula.
            const Double_t deltaEta = tauEta[iLead] - tauEta[iSub];
            const Double_t deltaPhi = tauPhi[iLead] - tauPhi[iSub];

            const Double_t massSquared = invariantMassSquared(tauPt[iLead], tauPt[iSub], deltaEta, deltaPhi);
            h_mVis_ptEtaPhi.Fill(std::sqrt(massSquared));

            ++nPairsUsed;
        }
    }

    std::cout << "TauVisibleMassPtEtaPhi: " << nPairsUsed << " good pairs out of "
              << nEventsSeen << " events read." << std::endl;

    const std::string outFile = "outputs/tau_visible_mass_ptEtaPhi.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_mVis_ptEtaPhi.Write();
    out.Close();

    std::cout << "TauVisibleMassPtEtaPhi: wrote " << outFile << std::endl;
}
