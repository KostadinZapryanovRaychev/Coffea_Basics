#include "TauPogMass.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
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
        int vsJet;  // DeepTau2018v2p5 working-point index vs jets
        int vsMu;   // ... vs muons
        int vsE;    // ... vs electrons
        int decayMode;

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

    // ---- the tau selections we want to compare ----
    bool kinematic(const Tau &t, double ptMin, double etaMax)
    {
        return t.pt > ptMin && std::abs(t.eta) < etaMax && std::abs(t.dz) < 0.2;
    }

    bool selNone(const Tau &) { return true; }
    bool selPt20(const Tau &t) { return kinematic(t, 20.0, 2.5); }
    bool selPt35(const Tau &t) { return kinematic(t, 35.0, 2.5); }
    bool selPt50(const Tau &t) { return kinematic(t, 50.0, 2.5); }
    bool selPt70(const Tau &t) { return kinematic(t, 70.0, 2.5); }

    // full CMS tau_h tau_h selection: pT>70, |eta|<2.1, |dz|<0.2,
    // DeepTau Tight-vs-jet / Tight-vs-mu / Medium-vs-e, decay mode 1- or 3-prong
    bool selFullHadHad(const Tau &t)
    {
        if (!kinematic(t, 70.0, 2.1))
        {
            return false;
        }
        if (t.vsJet < 6 || t.vsMu < 4 || t.vsE < 5)
        {
            return false;
        }
        return t.decayMode == 0 || t.decayMode == 1 || t.decayMode == 2 ||
               t.decayMode == 10 || t.decayMode == 11;
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
    TTreeReaderArray<UChar_t> tauVSjet(reader, "Tau_idDeepTau2018v2p5VSjet");
    TTreeReaderArray<UChar_t> tauVSmu(reader, "Tau_idDeepTau2018v2p5VSmu");
    TTreeReaderArray<UChar_t> tauVSe(reader, "Tau_idDeepTau2018v2p5VSe");
    TTreeReaderArray<UChar_t> tauDecayMode(reader, "Tau_decayMode");

    // one di-tau mass distribution per selection, all in the same file
    struct Selection
    {
        const char *histName;
        bool (*pass)(const Tau &);
        std::vector<double> masses;
    };
    std::vector<Selection> selections = {
        {"m_vis_tautau_before_pog", selNone},
        {"m_vis_tautau_after_pog", selPt20},
        {"m_vis_tautau_pt35", selPt35},
        {"m_vis_tautau_pt50", selPt50},
        {"m_vis_tautau_pt70", selPt70},
        {"m_vis_tautau_full_hadhad", selFullHadHad},
    };

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
            taus.push_back({tauPt[j], tauEta[j], tauPhi[j], tauMass[j], tauDz[j], tauCharge[j],
                            tauVSjet[j], tauVSmu[j], tauVSe[j], tauDecayMode[j]});
        }

        // for each selection: keep the taus that pass it, then take the
        // leading opposite-sign pair and store its mass
        for (Selection &s : selections)
        {
            std::vector<Tau> selected;
            for (const Tau &t : taus)
            {
                if (s.pass(t))
                {
                    selected.push_back(t);
                }
            }
            const double m = ditauMass(selected);
            if (m >= 0.0)
            {
                s.masses.push_back(m);
            }
        }
    }

    bool first = true;
    for (const Selection &s : selections)
    {
        std::cout << s.histName << ": " << s.masses.size() << " events" << std::endl;
        HistogramWriter::write(s.masses, s.histName, 100, 0, 500,
                               "outputs/tau_pog_mass.root", first ? "RECREATE" : "UPDATE");
        first = false;
    }
}
