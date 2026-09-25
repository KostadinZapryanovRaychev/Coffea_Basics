// Writes a text table, one row per selected tau pair, with every value of the formula
//   M = sqrt( 2 * pt1 * pt2 * ( cosh(delta_eta) - cos(delta_phi) ) )
// for the first 10000 events. The last column is the four-vector mass
// (TLorentzVector) of the same pair, for comparison.
// Same files and same selection as TauVisibleMassPtEtaPhi.C.
// Reads file_config_data.json (real data).

#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <vector>
#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "TLorentzVector.h"

namespace
{
    constexpr Long64_t MAX_EVENTS = 10000;
    constexpr Double_t TAU_PT_MIN = 20.0;
    constexpr Double_t TAU_ETA_MAX = 2.3;

    void writeHeader(FILE *out)
    {
        fprintf(out, "# one row per selected pair (opposite sign, pT > 20, |eta| < 2.3), two highest-pT taus\n");
        fprintf(out, "# M2 = 2*pt1*pt2*(cosh(dEta) - cos(dPhi)), M = sqrt(M2), M_fourvector = (p1+p2).M() from TLorentzVector\n");
        fprintf(out, "%7s %4s %4s | %9s %9s %7s %7s %7s %7s | %8s %8s %9s %9s | %11s %9s %13s\n",
                "event", "nTau", "file",
                "pt1", "pt2", "eta1", "eta2", "phi1", "phi2",
                "dEta", "dPhi", "cosh(dEta)", "cos(dPhi)",
                "M2", "M", "M_fourvector");
    }
} // namespace

void TauPtEtaPhiDump()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauPtEtaPhiDump: " << rootFiles.size() << " file(s) listed." << std::endl;

    const std::string outFile = "outputs/tau_ptEtaPhi_table.txt";
    FILE *out = fopen(outFile.c_str(), "w");
    if (!out)
    {
        std::cerr << "TauPtEtaPhiDump: cannot open " << outFile << std::endl;
        return;
    }
    writeHeader(out);

    Long64_t nEventsSeen = 0;
    Long64_t nRows = 0;

    for (size_t fileIndex = 0; fileIndex < rootFiles.size() && nEventsSeen < MAX_EVENTS; ++fileIndex)
    {
        std::cout << "reading: " << rootFiles[fileIndex].path << std::endl;
        TTree *Events = getEventsTree(rootFiles[fileIndex].path);
        if (!Events)
        {
            std::cerr << "TauPtEtaPhiDump: skipping " << rootFiles[fileIndex].path << std::endl;
            continue;
        }

        TTreeReader reader(Events);
        TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
        TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
        TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
        TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
        TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");

        while (reader.Next() && nEventsSeen < MAX_EVENTS)
        {
            const Long64_t event = nEventsSeen;
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

            // every value of the formula
            const Double_t deltaEta = tauEta[iLead] - tauEta[iSub];
            const Double_t deltaPhi = tauPhi[iLead] - tauPhi[iSub];
            const Double_t coshDeltaEta = std::cosh(deltaEta);
            const Double_t cosDeltaPhi = std::cos(deltaPhi);
            const Double_t massSquared = 2 * tauPt[iLead] * tauPt[iSub] * (coshDeltaEta - cosDeltaPhi);
            const Double_t mass = std::sqrt(massSquared);

            // same pair with the four-vector mass, for comparison
            TLorentzVector p1, p2;
            p1.SetPtEtaPhiM(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            p2.SetPtEtaPhiM(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            const Double_t massFourVector = (p1 + p2).M();

            fprintf(out, "%7lld %4zu %4zu | %9.3f %9.3f %7.3f %7.3f %7.3f %7.3f | %8.3f %8.3f %9.4f %9.4f | %11.2f %9.3f %13.3f\n",
                    event, nTau, fileIndex,
                    tauPt[iLead], tauPt[iSub], tauEta[iLead], tauEta[iSub], tauPhi[iLead], tauPhi[iSub],
                    deltaEta, deltaPhi, coshDeltaEta, cosDeltaPhi,
                    massSquared, mass, massFourVector);
            ++nRows;
        }
    }

    fclose(out);
    std::cout << "TauPtEtaPhiDump: " << nEventsSeen << " events read, " << nRows
              << " selected pairs written." << std::endl;
    std::cout << "TauPtEtaPhiDump: wrote " << outFile << std::endl;
}
