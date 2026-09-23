// Checks the hypothesis: does Tau_mass[0]+Tau_mass[1] approach the Z mass
// (~91 GeV)? Compares it against the correct visible di-tau mass,
// m_vis = sqrt((p_tau1+p_tau2)^2), built from full 4-vectors.
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
#include "TFile.h"
#include "TMath.h"

namespace
{
    // Same thresholds as NAOD_TAU/reco_tau_kinematics.py.
    constexpr Double_t DELTA_PHI_MIN = 2.5;
    constexpr Double_t TAU_PT_MIN = 20.0;
    constexpr Double_t TAU_ETA_MAX = 2.3;
    constexpr Double_t PAIR_PZ_MAX = 300.0;

    Double_t wrappedDeltaPhi(Double_t phi1, Double_t phi2)
    {
        return TVector2::Phi_mpi_pi(phi1 - phi2);
    }
} // namespace

void TauVisibleMassCheck()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauVisibleMassCheck: " << rootFiles.size() << " file(s) to process."
              << std::endl;

    // Same histograms, pooled across every file.
    TH1F h_tau_mass_leading("h_tau_mass_leading", "Tau_mass(leading);Tau_mass [GeV];Events",
                            150, 0, 150);
    TH1F h_tau_mass_sum("h_tau_mass_sum", "Tau_mass[0]+Tau_mass[1];sum [GeV];Events",
                        150, 0, 150);
    TH1F h_vis_mass("h_vis_mass", "m_{vis}(#tau#tau);m_{vis} [GeV];Events", 150, 0, 150);

    Long64_t nEventsSeen = 0;
    Long64_t nPairsUsed = 0;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            std::cerr << "TauVisibleMassCheck: skipping " << file.path << std::endl;
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
                      [&](size_t a, size_t b) { return tauPt[a] > tauPt[b]; });
            const size_t iLead = order[0];
            const size_t iSub = order[1];

            // opposite sign
            if (tauCharge[iLead] * tauCharge[iSub] != -1)
            {
                continue;
            }

            // pT and eta cuts, both legs
            if (!(tauPt[iLead] > TAU_PT_MIN && tauPt[iSub] > TAU_PT_MIN &&
                  std::abs(tauEta[iLead]) < TAU_ETA_MAX && std::abs(tauEta[iSub]) < TAU_ETA_MAX))
            {
                continue;
            }

            // back-to-back
            const Double_t deltaPhi = wrappedDeltaPhi(tauPhi[iLead], tauPhi[iSub]);
            if (std::abs(deltaPhi) <= DELTA_PHI_MIN)
            {
                continue;
            }

            // pair pz cut
            const Double_t pairPz = tauPt[iLead] * std::sinh(tauEta[iLead]) +
                                    tauPt[iSub] * std::sinh(tauEta[iSub]);
            if (std::abs(pairPz) >= PAIR_PZ_MAX)
            {
                continue;
            }

            // Tau_mass alone: visible mass of ONE tau's decay system, not the Z.
            h_tau_mass_leading.Fill(tauMass[iLead]);

            // naive/wrong: scalar sum of two masses, not a 4-vector sum.
            h_tau_mass_sum.Fill(tauMass[iLead] + tauMass[iSub]);

            // correct first step: invariant mass of the two full 4-vectors.
            TLorentzVector p1, p2;
            p1.SetPtEtaPhiM(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            p2.SetPtEtaPhiM(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            h_vis_mass.Fill((p1 + p2).M());

            ++nPairsUsed;
        }
    }

    std::cout << "TauVisibleMassCheck: " << nPairsUsed << " good pairs out of "
              << nEventsSeen << " events read." << std::endl;

    const std::string outFile = "outputs/tau_visible_mass_check.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_tau_mass_leading.Write();
    h_tau_mass_sum.Write();
    h_vis_mass.Write();
    out.Close();

    std::cout << "TauVisibleMassCheck: wrote " << outFile << std::endl;
}
