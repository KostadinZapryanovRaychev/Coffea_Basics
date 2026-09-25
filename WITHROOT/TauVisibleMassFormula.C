// Same analysis as TauVisibleMassCheck.C (same files, same selection, same
// histograms), but the visible di-tau mass is computed directly with
//   M = sqrt( (E1+E2)^2 - (px1+px2)^2 - (py1+py2)^2 - (pz1+pz2)^2 )
// instead of TLorentzVector. Runs over file_config_data.json (real data).

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

    struct FourVector
    {
        Double_t px;
        Double_t py;
        Double_t pz;
        Double_t e;
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
    // (no square root here: the caller checks the sign first)
    Double_t invariantMassSquared(const FourVector &a, const FourVector &b)
    {
        const Double_t e = a.e + b.e;
        const Double_t px = a.px + b.px;
        const Double_t py = a.py + b.py;
        const Double_t pz = a.pz + b.pz;
        return e * e - px * px - py * py - pz * pz;
    }
}

void TauVisibleMassFormula()
{
    // load the list of files to process, from the JSON config file.
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauVisibleMassFormula: " << rootFiles.size() << " file(s) to process."
              << std::endl;

    TH1F h_tau_mass("h_tau_mass", "Tau_mass of tau (charge -1);Tau_mass [GeV];Events",
                    100, 0, 100);
    TH1F h_antitau_mass("h_antitau_mass", "Tau_mass of anti-tau (charge +1);Tau_mass [GeV];Events",
                        100, 0, 100);
    TH1F h_vis_mass("h_vis_mass", "m_{vis}(#tau#tau) from the formula;m_{vis} [GeV];Events",
                    250, 0, 250);

    Long64_t nEventsSeen = 0;
    Long64_t nPairsUsed = 0;
    Long64_t nNegativeMassSquared = 0;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            std::cerr << "TauVisibleMassFormula: skipping " << file.path << std::endl;
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

            // needs at least two taus
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

            // Mass of the di-tau (visible mass of the two taus):
            //   M = sqrt( (E1+E2)^2 - (px1+px2)^2 - (py1+py2)^2 - (pz1+pz2)^2 )
            // per tau: px = pt*cos(phi), py = pt*sin(phi), pz = pt*sinh(eta),
            //          E = sqrt(px^2 + py^2 + pz^2 + mass^2)
            // here we compute M^2 (the part under the square root).
            const FourVector tau1 = makeFourVector(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            const FourVector tau2 = makeFourVector(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            const Double_t massSquared = invariantMassSquared(tau1, tau2);

            // M^2 must be positive to take the square root: skip the pair if it is negative.
            if (massSquared < 0)
            {
                ++nNegativeMassSquared;
                continue;
            }

            // the pair is opposite sign: one is the tau (-1), the other the anti-tau (+1).
            const size_t iTau = (tauCharge[iLead] == -1) ? iLead : iSub;
            const size_t iAntiTau = (tauCharge[iLead] == -1) ? iSub : iLead;
            h_tau_mass.Fill(tauMass[iTau]);
            h_antitau_mass.Fill(tauMass[iAntiTau]);
            // M = sqrt(M^2)
            h_vis_mass.Fill(std::sqrt(massSquared));

            ++nPairsUsed;
        }
    }

    std::cout << "TauVisibleMassFormula: " << nPairsUsed << " good pairs out of "
              << nEventsSeen << " events read." << std::endl;
    std::cout << "TauVisibleMassFormula: " << nNegativeMassSquared
              << " pairs skipped because M^2 < 0." << std::endl;

    const std::string outFile = "outputs/tau_visible_mass_formula.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_tau_mass.Write();
    h_antitau_mass.Write();
    h_vis_mass.Write();
    out.Close();

    std::cout << "TauVisibleMassFormula: wrote " << outFile << std::endl;
}
