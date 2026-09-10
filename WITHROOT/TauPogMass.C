#include "TauPogMass.h"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <vector>
#include "TTreeReader.h"
#include "TTreeReaderArray.h"

#include "HistogramWriter.h"

namespace
{
    struct Tau
    {
        double pt;
        double eta;
        double phi;
        double mass;
        int charge; // -1 = tau, +1 = anti-tau
    };

    // (pt, eta, phi, mass) -> Cartesian 4-momentum (E, px, py, pz):
    //   px = pt * cos(phi)
    //   py = pt * sin(phi)
    //   pz = pt * sinh(eta)
    //   E  = sqrt(px^2 + py^2 + pz^2 + mass^2)
    void toFourMomentum(const Tau &t, double &px, double &py, double &pz, double &E)
    {
        px = t.pt * std::cos(t.phi);
        py = t.pt * std::sin(t.phi);
        pz = t.pt * std::sinh(t.eta);
        E = std::sqrt(px * px + py * py + pz * pz + t.mass * t.mass);
    }

    // plain invariant mass of the two visible tau 4-vectors:
    //   m = sqrt[ (E1+E2)^2 - |p1+p2|^2 ]
    // no correction for the escaping neutrinos.
    double invariantMass(const Tau &a, const Tau &b)
    {
        double px1, py1, pz1, E1;
        double px2, py2, pz2, E2;
        toFourMomentum(a, px1, py1, pz1, E1);
        toFourMomentum(b, px2, py2, pz2, E2);

        const double E = E1 + E2;
        const double px = px1 + px2;
        const double py = py1 + py2;
        const double pz = pz1 + pz2;

        const double mSquared = E * E - px * px - py * py - pz * pz;
        return std::sqrt(std::max(0.0, mSquared));
    }

    // CMS Tau POG Run-3 baseline tau selection.
    bool passesTauPogSelection(double pt, double eta, double dz)
    {
        return pt > 20.0 && std::abs(eta) < 2.5 && std::abs(dz) < 0.2;
    }
}

void TauPogMass::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                     const std::string &inputFilePath)
{
    (void)debug;
    (void)inputFilePath;

    // ==================================================================
    // STEP 1 -- enable the branches we need.
    // With TTreeReader, binding a TTreeReaderArray to a branch name is
    // what enables it: only these branches are read from disk.
    // ==================================================================
    TTreeReader reader(Events);
    TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
    TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
    TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
    TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
    TTreeReaderArray<Float_t> tauDz(reader, "Tau_dz");
    TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");

    // ==================================================================
    // STEP 2 -- keep only events that have at least 2 tau candidates.
    // Raw count, before any quality selection: a cheap pre-filter that
    // skips events which can never give a di-tau pair. The entry number
    // of every surviving event is stored in keptEvents (and written out
    // to a text file for inspection).
    // ==================================================================
    std::vector<Long64_t> keptEvents;
    Long64_t nEventsSeen = 0;

    while (reader.Next())
    {
        if (maxEvents > 0 && nEventsSeen >= maxEvents)
        {
            break;
        }
        ++nEventsSeen;

        if (tauPt.GetSize() >= 2)
        {
            keptEvents.push_back(reader.GetCurrentEntry());
        }
    }

    // ==================================================================
    // STEP 3 + STEP 4 -- only over the events STEP 2 kept:
    //   STEP 3: apply the Tau POG selection to each tau candidate.
    //   STEP 4: from the selected taus, take the best di-tau pair --
    //           the highest-pT tau of each charge, i.e. the leading
    //           opposite-sign pair -- and reconstruct its invariant mass.
    // Events without a valid opposite-sign selected pair are dropped.
    // ==================================================================
    std::vector<double> masses;

    for (Long64_t id : keptEvents)
    {
        reader.SetEntry(id);

        Tau leadingMinus{};
        Tau leadingPlus{};
        bool haveMinus = false;
        bool havePlus = false;

        for (size_t j = 0; j < tauPt.GetSize(); ++j)
        {

            if (!passesTauPogSelection(tauPt[j], tauEta[j], tauDz[j]))
            {
                continue;
            }

            Tau t{tauPt[j], tauEta[j], tauPhi[j], tauMass[j], tauCharge[j]};

            if (t.charge < 0 && (!haveMinus || t.pt > leadingMinus.pt))
            {
                leadingMinus = t;
                haveMinus = true;
            }
            else if (t.charge > 0 && (!havePlus || t.pt > leadingPlus.pt))
            {
                leadingPlus = t;
                havePlus = true;
            }
        }

        if (haveMinus && havePlus)
        {
            masses.push_back(invariantMass(leadingMinus, leadingPlus));
        }
    }

    std::cout << "STEP 4: " << masses.size()
              << " events with a valid opposite-sign selected di-tau pair." << std::endl;

    HistogramWriter::write(masses, "m_vis_tautau", 300, 0, 3000,
                           "outputs/tau_pog_mass.root", "RECREATE");
}
