#include "TauPogMass.h"
#include <algorithm>
#include <cmath>
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

    // One kept event: its entry number + the taus that passed the POG
    // selection in it.
    struct SelectedEvent
    {
        Long64_t id;
        std::vector<Tau> taus;
    };
}

void TauPogMass::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                     const std::string &inputFilePath)
{
    (void)debug;
    (void)inputFilePath;

    // ---- enable branches ----
    TTreeReader reader(Events);
    TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
    TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
    TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
    TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
    TTreeReaderArray<Float_t> tauDz(reader, "Tau_dz");
    TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");

    // keptEvents: all events with >= 2 taus and at least one of each charge
    std::vector<Long64_t> keptEvents;
    Long64_t nEventsSeen = 0;

    while (reader.Next())
    {
        if (maxEvents > 0 && nEventsSeen >= maxEvents)
        {
            break;
        }
        ++nEventsSeen;

        const size_t nRawTaus = tauPt.GetSize();
        if (nRawTaus < 2)
        {
            continue;
        }

        bool hasMinus = false;
        bool hasPlus = false;
        for (size_t j = 0; j < nRawTaus; ++j)
        {
            if (tauCharge[j] < 0)
            {
                hasMinus = true;
            }
            else if (tauCharge[j] > 0)
            {
                hasPlus = true;
            }
        }

        if (hasMinus && hasPlus)
        {
            keptEvents.push_back(reader.GetCurrentEntry());
        }
    }

    // tauPogRecommended: all events with >= 2 taus that pass the POG
    // baseline selection (pT > 20, |eta| < 2.5, |dz| < 0.2) and at least one of each charge
    std::vector<SelectedEvent> tauPogRecommended;

    for (Long64_t id : keptEvents)
    {
        reader.SetEntry(id);

        std::vector<Tau> selected;
        bool hasMinus = false;
        bool hasPlus = false;
        for (size_t j = 0; j < tauPt.GetSize(); ++j)
        {
            if (!passesTauPogSelection(tauPt[j], tauEta[j], tauDz[j]))
            {
                continue;
            }
            Tau t{tauPt[j], tauEta[j], tauPhi[j], tauMass[j], tauCharge[j]};
            selected.push_back(t);
            if (t.charge < 0)
            {
                hasMinus = true;
            }
            else if (t.charge > 0)
            {
                hasPlus = true;
            }
        }

        if (selected.size() >= 2 && hasMinus && hasPlus)
        {
            tauPogRecommended.push_back({id, selected});
        }
    }

    // reconstruct the invariant mass of the two leading taus in each event
    std::vector<double> masses;

    for (const SelectedEvent &ev : tauPogRecommended)
    {
        const Tau *leadingMinus = nullptr;
        const Tau *leadingPlus = nullptr;
        for (const Tau &t : ev.taus)
        {
            if (t.charge < 0 && (leadingMinus == nullptr || t.pt > leadingMinus->pt))
            {
                leadingMinus = &t;
            }
            else if (t.charge > 0 && (leadingPlus == nullptr || t.pt > leadingPlus->pt))
            {
                leadingPlus = &t;
            }
        }

        if (leadingMinus != nullptr && leadingPlus != nullptr)
        {
            masses.push_back(invariantMass(*leadingMinus, *leadingPlus));
        }
    }

    HistogramWriter::write(masses, "m_vis_tautau", 300, 0, 3000,
                           "outputs/tau_pog_mass.root", "RECREATE");
}
