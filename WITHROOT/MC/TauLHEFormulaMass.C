// LHE-level di-tau mass on signal MC, computed with the explicit formula
//   M = sqrt( (E1+E2)^2 - |p1+p2|^2 )
// (not TLorentzVector's .M()), same style as DATA/TauVisibleMassFormula.C.
//
// LHEPart holds the matrix-element particles before parton showering/decay:
// the tau+ tau- pair here should sit right at the generated Z' mass, since
// nothing has decayed or been smeared yet (see WITHROOT/SignalVsBackground
// Stage1_LHE.C, which found a mean of ~247 GeV on the M-250 sample).
//
// Selection: same as always -- pT > 20 GeV, |eta| < 2.3, opposite sign,
// |delta_phi| > 2.5 (back-to-back).
//
// Runs over file_config_reco.json (Monte Carlo, ZprimeTo2Tau samples).

#include "../Config.C"
#include "../Config.h"
#include "../CutFlow.h"
#include "../event.C"
#include "../event.h"

#include <cmath>
#include <iostream>
#include <vector>

#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "TVector2.h"
#include "TH1F.h"
#include "TFile.h"

namespace
{
    constexpr Double_t TAU_PT_MIN = 20.0;
    constexpr Double_t TAU_ETA_MAX = 2.3;
    constexpr Double_t DELTA_PHI_MIN = 2.5; // back-to-back requirement

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

    Double_t wrappedDeltaPhi(Double_t phi1, Double_t phi2)
    {
        return TVector2::Phi_mpi_pi(phi1 - phi2);
    }
}

void TauLHEFormulaMass()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_reco.json");
    std::cout << "TauLHEFormulaMass: " << rootFiles.size() << " file(s) to process." << std::endl;

    TH1F h_lhe_mass("h_lhe_mass", "LHE m(#tau^{+}#tau^{-}) from the formula;m [GeV];Events", 100, 0, 300);

    CutFlow cutFlow;
    Long64_t nNegativeMassSquared = 0;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            std::cerr << "TauLHEFormulaMass: skipping " << file.path << std::endl;
            continue;
        }

        TTreeReader reader(Events);
        TTreeReaderArray<Int_t> pdgId(reader, "LHEPart_pdgId");
        TTreeReaderArray<Int_t> status(reader, "LHEPart_status");
        TTreeReaderArray<Float_t> pt(reader, "LHEPart_pt");
        TTreeReaderArray<Float_t> eta(reader, "LHEPart_eta");
        TTreeReaderArray<Float_t> phi(reader, "LHEPart_phi");
        TTreeReaderArray<Float_t> mass(reader, "LHEPart_mass");

        while (reader.Next())
        {
            ++cutFlow.eventsRead;

            Int_t iTauMinus = -1, iTauPlus = -1;
            for (size_t i = 0; i < pdgId.GetSize(); ++i)
            {
                if (status[i] != 1)
                {
                    continue;
                }
                if (pdgId[i] == 15)
                {
                    iTauMinus = i;
                }
                else if (pdgId[i] == -15)
                {
                    iTauPlus = i;
                }
            }
            if (iTauMinus < 0 || iTauPlus < 0)
            {
                continue;
            }
            ++cutFlow.atLeastTwoTaus;

            if (!(pt[iTauMinus] > TAU_PT_MIN && pt[iTauPlus] > TAU_PT_MIN &&
                  std::abs(eta[iTauMinus]) < TAU_ETA_MAX && std::abs(eta[iTauPlus]) < TAU_ETA_MAX))
            {
                continue;
            }
            ++cutFlow.passKinematics;

            // LHE taus from a Z'->tautau decay are always opposite sign
            // (pdgId 15 vs -15, checked above), so this is a sanity check,
            // not a real cut.
            ++cutFlow.oppositeSign;

            const Double_t deltaPhi = wrappedDeltaPhi(phi[iTauMinus], phi[iTauPlus]);
            if (std::abs(deltaPhi) <= DELTA_PHI_MIN)
            {
                continue;
            }

            const FourVector tau1 = makeFourVector(pt[iTauMinus], eta[iTauMinus], phi[iTauMinus], mass[iTauMinus]);
            const FourVector tau2 = makeFourVector(pt[iTauPlus], eta[iTauPlus], phi[iTauPlus], mass[iTauPlus]);
            const Double_t massSquared = invariantMassSquared(tau1, tau2);
            if (massSquared < 0)
            {
                ++nNegativeMassSquared;
                continue;
            }

            h_lhe_mass.Fill(std::sqrt(massSquared));
            ++cutFlow.used;
        }
    }

    std::cout << "TauLHEFormulaMass: " << cutFlow.used << " good pairs out of "
              << cutFlow.eventsRead << " events read." << std::endl;
    std::cout << "TauLHEFormulaMass: " << nNegativeMassSquared << " pairs skipped because M^2 < 0." << std::endl;
    std::cout << "TauLHEFormulaMass: mean mass = " << h_lhe_mass.GetMean() << " GeV, RMS = " << h_lhe_mass.GetRMS() << " GeV" << std::endl;

    const std::string outFile = "outputs/tau_lhe_formula_mass.root";
    TFile out(outFile.c_str(), "RECREATE");
    h_lhe_mass.Write();
    out.Close();
    std::cout << "TauLHEFormulaMass: wrote " << outFile << std::endl;
}
