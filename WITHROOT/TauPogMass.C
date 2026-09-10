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
        double dz;
        int charge; // -1 = tau, +1 = anti-tau

        double px() const { return pt * std::cos(phi); }
        double py() const { return pt * std::sin(phi); }
        double pz() const { return pt * std::sinh(eta); }
        double e() const { return std::sqrt(px() * px() + py() * py() + pz() * pz() + mass * mass); }
    };

    // m = sqrt[ (E1+E2)^2 - |p1+p2|^2 ]  -- visible mass, neutrinos ignored
    double invariantMass(const Tau &a, const Tau &b)
    {
        const double e = a.e() + b.e();
        const double x = a.px() + b.px();
        const double y = a.py() + b.py();
        const double z = a.pz() + b.pz();
        return std::sqrt(std::max(0.0, e * e - x * x - y * y - z * z));
    }

    // CMS Tau POG Run-3 baseline selection
    bool passesTauPog(const Tau &t)
    {
        return t.pt > 20.0 && std::abs(t.eta) < 2.5 && std::abs(t.dz) < 0.2;
    }

    bool hasOppositeSignPair(const std::vector<Tau> &taus)
    {
        bool minus = false;
        bool plus = false;
        for (const Tau &t : taus)
        {
            minus = minus || t.charge < 0;
            plus = plus || t.charge > 0;
        }
        return minus && plus;
    }

    // invariant mass of the leading tau of each charge,
    // or -1 if the event does not have one of each
    double ditauMass(const std::vector<Tau> &taus)
    {
        const Tau *minus = nullptr;
        const Tau *plus = nullptr;
        for (const Tau &t : taus)
        {
            if (t.charge < 0 && (minus == nullptr || t.pt > minus->pt))
            {
                minus = &t;
            }
            if (t.charge > 0 && (plus == nullptr || t.pt > plus->pt))
            {
                plus = &t;
            }
        }
        return (minus && plus) ? invariantMass(*minus, *plus) : -1.0;
    }
}

void TauPogMass::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                     const std::string &inputFilePath)
{
    (void)debug;
    (void)inputFilePath;

    TTreeReader reader(Events);
    TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
    TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
    TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
    TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
    TTreeReaderArray<Float_t> tauDz(reader, "Tau_dz");
    TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");

    std::vector<double> massBeforePog;
    std::vector<double> massAfterPog;
    Long64_t nEventsSeen = 0;

    while (reader.Next())
    {
        if (maxEvents > 0 && nEventsSeen >= maxEvents)
        {
            break;
        }
        ++nEventsSeen;

        // all taus in this event
        std::vector<Tau> taus;
        for (size_t j = 0; j < tauPt.GetSize(); ++j)
        {
            taus.push_back({tauPt[j], tauEta[j], tauPhi[j], tauMass[j], tauDz[j], tauCharge[j]});
        }

        // need at least two taus, with an opposite-sign pair among them
        if (taus.size() < 2 || !hasOppositeSignPair(taus))
        {
            continue;
        }

        // 1) di-tau mass before the Tau POG selection
        massBeforePog.push_back(ditauMass(taus));

        // 2) di-tau mass after the Tau POG selection
        std::vector<Tau> selected;
        for (const Tau &t : taus)
        {
            if (passesTauPog(t))
            {
                selected.push_back(t);
            }
        }
        if (selected.size() >= 2 && hasOppositeSignPair(selected))
        {
            massAfterPog.push_back(ditauMass(selected));
        }
    }

    HistogramWriter::write(massBeforePog, "m_vis_tautau_before_pog", 100, 0, 500,
                           "outputs/tau_pog_mass.root", "RECREATE");
    HistogramWriter::write(massAfterPog, "m_vis_tautau_after_pog", 100, 0, 500,
                           "outputs/tau_pog_mass.root", "UPDATE");
}
