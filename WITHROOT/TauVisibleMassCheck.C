// Checks in real data: (1) the Tau_mass branch of each tau and anti-tau is
// ~1 GeV (the visible decay products only), not ~45 GeV (half the Z mass);
// (2) the visible di-tau mass m_vis = sqrt((p_tau1+p_tau2)^2), built from
// full 4-vectors, peaks below 91 GeV because the neutrinos are missing.
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
    constexpr Double_t TAU_ETA_MAX = 2.3; // analysis note ?
    constexpr Double_t PAIR_PZ_MAX = 300.0;

    // the result from the function is compared with DELTA_PHI_MIN for the back-to-back cut.
    Double_t wrappedDeltaPhi(Double_t phi1, Double_t phi2)
    {
        return TVector2::Phi_mpi_pi(phi1 - phi2);
    }
}

void TauVisibleMassCheck()
{
    // load the list of files to process, from the JSON config file.
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauVisibleMassCheck: " << rootFiles.size() << " file(s) to process."
              << std::endl;

    // emtpy histograms to fill, and then write to output file.
    TH1F h_tau_mass("h_tau_mass", "Tau_mass of tau (charge -1);Tau_mass [GeV];Events",
                    10, 0, 10);
    TH1F h_antitau_mass("h_antitau_mass", "Tau_mass of anti-tau (charge +1);Tau_mass [GeV];Events",
                        10, 0, 10);
    TH1F h_vis_mass("h_vis_mass", "m_{vis}(#tau#tau);m_{vis} [GeV];Events", 250, 0, 250);

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
            // reader.Next() moves to the next event
            ++nEventsSeen;

            // gets the events with more than one tau
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

            // skips event if either tau fails the pT or eta cuts
            if (!(tauPt[iLead] > TAU_PT_MIN && tauPt[iSub] > TAU_PT_MIN &&
                  std::abs(tauEta[iLead]) < TAU_ETA_MAX && std::abs(tauEta[iSub]) < TAU_ETA_MAX))
            {
                continue;
            }

            // it skips the events that are not back-to-back
            // const Double_t deltaPhi = wrappedDeltaPhi(tauPhi[iLead], tauPhi[iSub]);
            // if (std::abs(deltaPhi) <= DELTA_PHI_MIN)
            // {
            //     continue;
            // }

            // it computes the pair's longitudinal momentum, and skips if too large.
            // const Double_t pairPz = tauPt[iLead] * std::sinh(tauEta[iLead]) +
            //                         tauPt[iSub] * std::sinh(tauEta[iSub]);
            // if (std::abs(pairPz) >= PAIR_PZ_MAX)
            // {
            //     continue;
            // }

            // Tau_mass alone: visible mass of ONE tau's decay system
            // the pair is opposite sign, so exactly one is the tau (-1) and one the anti-tau (+1).
            const size_t iTau = (tauCharge[iLead] == -1) ? iLead : iSub;
            const size_t iAntiTau = (tauCharge[iLead] == -1) ? iSub : iLead;

            // most probably here is the problem
            h_tau_mass.Fill(tauMass[iTau]);
            h_antitau_mass.Fill(tauMass[iAntiTau]);

            // the invariant mass of four vector by TLorentzVector
            // https://root.cern.ch/doc/v632/classTLorentzVector.html
            // It converts to Cartesian components: px = pT·cos φ, py = pT·sin φ, pz = pT·sinh η. SetXYZM then sets the energy as E = √(px² + py² + pz² + m²) (line 341).
            // M() (line 502) calls Mag()
            TLorentzVector p1, p2;
            p1.SetPtEtaPhiM(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            p2.SetPtEtaPhiM(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            // p1.M() // returns the invariant mass of the system, which is the visible mass of the tau pair.
            h_vis_mass.Fill((p1 + p2).M());

            ++nPairsUsed;
        }
    }

    std::cout << "TauVisibleMassCheck: " << nPairsUsed << " good pairs out of "
              << nEventsSeen << " events read." << std::endl;

    const std::string outFile = "outputs/tau_visible_mass_check.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_tau_mass.Write();
    h_antitau_mass.Write();
    h_vis_mass.Write();
    out.Close();

    std::cout << "TauVisibleMassCheck: wrote " << outFile << std::endl;
}
