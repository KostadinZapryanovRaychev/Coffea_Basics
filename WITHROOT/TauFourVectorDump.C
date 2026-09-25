// Writes a text table with the values of every tau of the leading pair
// (Tau_pt, Tau_eta, Tau_phi, Tau_mass, Tau_charge, decay mode, DeepTau IDs)
// and its four-vector (px, py, pz, E), plus M^2 and M of the pair,
// for the first 10000 events. Used to look at the numbers behind the mass peak.
// Reads the files of file_config_data.json (real data).

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

namespace
{
    constexpr Long64_t MAX_EVENTS = 10000;
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
    Double_t invariantMassSquared(const FourVector &a, const FourVector &b)
    {
        const Double_t e = a.e + b.e;
        const Double_t px = a.px + b.px;
        const Double_t py = a.py + b.py;
        const Double_t pz = a.pz + b.pz;
        return e * e - px * px - py * py - pz * pz;
    }

    void writeHeader(FILE *out)
    {
        fprintf(out, "# one row per tau of the leading pair (the two highest-pT taus of the event)\n");
        fprintf(out, "# vsJet / vsE / vsMu = Tau_idDeepTau2018v2p5 working point (0 = fails all, 8 = tightest for jet and e, 4 for mu)\n");
        fprintf(out, "# pairM2 / pairM = M^2 and M of the two taus together; selected = opposite sign, pT > 20, |eta| < 2.3\n");
        fprintf(out, "%7s %5s %4s %4s | %9s %7s %7s %8s %3s %3s %5s %4s %4s | %10s %10s %10s %10s | %11s %9s %3s\n",
                "event", "role", "nTau", "file",
                "pt", "eta", "phi", "mass", "q", "dm", "vsJet", "vsE", "vsMu",
                "px", "py", "pz", "E",
                "pairM2", "pairM", "sel");
    }

    void writeTauRow(FILE *out, Long64_t event, const char *role, size_t nTau, size_t fileIndex,
                     Double_t pt, Double_t eta, Double_t phi, Double_t mass, Int_t charge,
                     Int_t decayMode, Int_t vsJet, Int_t vsE, Int_t vsMu,
                     const FourVector &v, Double_t pairMassSquared, Bool_t selected)
    {
        const Double_t pairMass = std::sqrt(std::max(0.0, pairMassSquared));
        fprintf(out, "%7lld %5s %4zu %4zu | %9.3f %7.3f %7.3f %8.4f %3d %3d %5d %4d %4d | %10.3f %10.3f %10.3f %10.3f | %11.2f %9.3f %3d\n",
                event, role, nTau, fileIndex,
                pt, eta, phi, mass, charge, decayMode, vsJet, vsE, vsMu,
                v.px, v.py, v.pz, v.e,
                pairMassSquared, pairMass, selected ? 1 : 0);
    }
} // namespace

void TauFourVectorDump()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauFourVectorDump: " << rootFiles.size() << " file(s) listed." << std::endl;

    const std::string outFile = "outputs/tau_fourvector_table.txt";
    FILE *out = fopen(outFile.c_str(), "w");
    if (!out)
    {
        std::cerr << "TauFourVectorDump: cannot open " << outFile << std::endl;
        return;
    }
    writeHeader(out);

    Long64_t nEventsSeen = 0;
    Long64_t nEventsWithPair = 0;

    for (size_t fileIndex = 0; fileIndex < rootFiles.size() && nEventsSeen < MAX_EVENTS; ++fileIndex)
    {
        std::cout << "reading: " << rootFiles[fileIndex].path << std::endl;
        TTree *Events = getEventsTree(rootFiles[fileIndex].path);
        if (!Events)
        {
            std::cerr << "TauFourVectorDump: skipping " << rootFiles[fileIndex].path << std::endl;
            continue;
        }

        TTreeReader reader(Events);
        TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
        TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
        TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
        TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
        TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");
        TTreeReaderArray<UChar_t> tauDecayMode(reader, "Tau_decayMode");
        TTreeReaderArray<UChar_t> tauVsJet(reader, "Tau_idDeepTau2018v2p5VSjet");
        TTreeReaderArray<UChar_t> tauVsE(reader, "Tau_idDeepTau2018v2p5VSe");
        TTreeReaderArray<UChar_t> tauVsMu(reader, "Tau_idDeepTau2018v2p5VSmu");

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

            const FourVector v1 = makeFourVector(tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead]);
            const FourVector v2 = makeFourVector(tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub]);
            const Double_t massSquared = invariantMassSquared(v1, v2);

            const Bool_t selected = tauCharge[iLead] * tauCharge[iSub] == -1 &&
                                    tauPt[iLead] > TAU_PT_MIN && tauPt[iSub] > TAU_PT_MIN &&
                                    std::abs(tauEta[iLead]) < TAU_ETA_MAX && std::abs(tauEta[iSub]) < TAU_ETA_MAX;

            writeTauRow(out, event, "LEAD", nTau, fileIndex,
                        tauPt[iLead], tauEta[iLead], tauPhi[iLead], tauMass[iLead], tauCharge[iLead],
                        tauDecayMode[iLead], tauVsJet[iLead], tauVsE[iLead], tauVsMu[iLead],
                        v1, massSquared, selected);
            writeTauRow(out, event, "SUB", nTau, fileIndex,
                        tauPt[iSub], tauEta[iSub], tauPhi[iSub], tauMass[iSub], tauCharge[iSub],
                        tauDecayMode[iSub], tauVsJet[iSub], tauVsE[iSub], tauVsMu[iSub],
                        v2, massSquared, selected);
            ++nEventsWithPair;
        }
    }

    fclose(out);
    std::cout << "TauFourVectorDump: " << nEventsSeen << " events read, " << nEventsWithPair
              << " with at least 2 taus." << std::endl;
    std::cout << "TauFourVectorDump: wrote " << outFile << std::endl;
}
