#include "RecoTauMassKinematics.h"

#include <algorithm>
#include <cmath>
#include <iostream>

#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "TLorentzVector.h"
#include "TMath.h"

#include "event.h"
#include "HistogramWriter.h"

namespace
{
    // Selection thresholds, matching NAOD_TAU/reco_tau_kinematics.py
    // exactly (DELTA_PHI_MIN, TAU_PT_MIN, TAU_ETA_MAX, PAIR_PZ_MAX).
    constexpr Double_t DELTA_PHI_MIN = 2.5;
    constexpr Double_t TAU_PT_MIN = 20.0;
    constexpr Double_t TAU_ETA_MAX = 2.3;
    constexpr Double_t PAIR_PZ_MAX = 300.0;

    struct Tau
    {
        Double_t pt;
        Double_t eta;
        Double_t phi;
        Double_t mass;
        Short_t charge;

        Double_t px() const { return pt * std::cos(phi); }
        Double_t py() const { return pt * std::sin(phi); }
        Double_t pz() const { return pt * std::sinh(eta); }
        Double_t energy() const
        {
            return std::sqrt(px() * px() + py() * py() + pz() * pz() + mass * mass);
        }
    };

    // Wraps a phi difference into (-pi, pi], the same convention coffea's
    // tau.delta_phi(antitau) (used by NAOD_TAU/helpers/lhe/angles.py) and
    // TLorentzVector::DeltaR use internally.
    Double_t wrappedDeltaPhi(Double_t phi1, Double_t phi2)
    {
        return TVector2::Phi_mpi_pi(phi1 - phi2);
    }

    // One event's worth of accumulated per-pair kinematics, appended to
    // across every file in rootFiles -- mirrors
    // collect_kinematics_from_files() pooling all files' pairs together.
    struct Accumulated
    {
        std::vector<Double_t> mass;
        std::vector<Double_t> massFormula;
        std::vector<Double_t> massFormulaNeutrino;
        std::vector<Double_t> pz;
        std::vector<Double_t> deltaR;
        std::vector<Double_t> cosDeltaPhi;
        std::vector<Double_t> eta;
    };

    // Runs the full selection + kinematics pipeline for one file, in the
    // same order as the python pipeline:
    //   1. leading tau pair (two highest-pT Tau objects in the event)
    //   2. opposite sign
    //   3. back-to-back (|delta_phi| > DELTA_PHI_MIN)
    //   4. kinematic (pt > TAU_PT_MIN, |eta| < TAU_ETA_MAX, both legs)
    //   5. pair |pz| < PAIR_PZ_MAX
    // matching select_leading_tau_pair -> select_opposite_sign_pairs ->
    // select_back_to_back_pairs -> select_kinematic_pairs ->
    // select_pz_pairs in NAOD_TAU/reco_tau_kinematics.py.
    void processFile(const RootFileEntry &file, Long64_t maxEvents, Accumulated &out)
    {
        std::cout << "reading: " << file.path << std::endl;

        TTree *events = getEventsTree(file.path);
        if (!events)
        {
            std::cerr << "RecoTauMassKinematics: skipping " << file.path
                      << " (could not open Events tree)." << std::endl;
            return;
        }

        TTreeReader reader(events);
        TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
        TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
        TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
        TTreeReaderArray<Float_t> tauMass(reader, "Tau_mass");
        TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");

        Long64_t nEntries = events->GetEntries();
        Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;

        Long64_t nSeen = 0;
        Long64_t nGoodPairs = 0;
        while (reader.Next() && nSeen < limit)
        {
            ++nSeen;

            // 0. gather this event's taus, sorted by descending pT (the
            // leading pair is just the first two after sorting).
            std::vector<Tau> taus;
            for (size_t j = 0; j < tauPt.GetSize(); ++j)
            {
                taus.push_back({tauPt[j], tauEta[j], tauPhi[j], tauMass[j], tauCharge[j]});
            }
            if (taus.size() < 2)
            {
                continue;
            }
            std::sort(taus.begin(), taus.end(),
                      [](const Tau &a, const Tau &b) { return a.pt > b.pt; });

            const Tau &tau = taus[0];
            const Tau &antitau = taus[1];

            // 2. opposite sign
            if (tau.charge * antitau.charge != -1)
            {
                continue;
            }

            // 3. back-to-back
            const Double_t deltaPhi = wrappedDeltaPhi(tau.phi, antitau.phi);
            if (std::abs(deltaPhi) <= DELTA_PHI_MIN)
            {
                continue;
            }

            // 4. kinematic cuts, both legs
            if (!(tau.pt > TAU_PT_MIN && antitau.pt > TAU_PT_MIN &&
                  std::abs(tau.eta) < TAU_ETA_MAX && std::abs(antitau.eta) < TAU_ETA_MAX))
            {
                continue;
            }

            // 5. pair pz cut
            const Double_t pairPz = tau.pz() + antitau.pz();
            if (std::abs(pairPz) >= PAIR_PZ_MAX)
            {
                continue;
            }

            // ---- mother boson (Z/Z') mass, three ways ----

            // m_reco: TLorentzVector sum of the two visible taus, same as
            // (tau + antitau).mass in the python pipeline.
            TLorentzVector tauLv, antiTauLv;
            tauLv.SetPtEtaPhiM(tau.pt, tau.eta, tau.phi, tau.mass);
            antiTauLv.SetPtEtaPhiM(antitau.pt, antitau.eta, antitau.phi, antitau.mass);
            const Double_t mReco = (tauLv + antiTauLv).M();

            // m_reco_formula: same physics, computed by hand from
            // E = sqrt(px^2+py^2+pz^2+m^2) -- a cross-check that this
            // agrees with TLorentzVector's .M() to float precision.
            const Double_t px = tau.px() + antitau.px();
            const Double_t py = tau.py() + antitau.py();
            const Double_t pz = tau.pz() + antitau.pz();
            const Double_t energy = tau.energy() + antitau.energy();
            const Double_t mFormula = std::sqrt(
                std::max(0.0, energy * energy - px * px - py * py - pz * pz));

            // m_reco_formula_neutrino: Eq. (1) of arXiv:2412.04357 --
            // adds the missing transverse momentum of the escaping tau
            // neutrinos, assuming pT_miss = -(pT1_vis + pT2_vis) and
            // pz_miss = 0. The transverse part of
            // (p1vis + p2vis + p_miss) cancels to exactly zero by
            // construction, so only the pz term survives under the
            // square root -- an exact simplification, not an
            // approximation.
            const Double_t missPt = std::sqrt(px * px + py * py);
            const Double_t energyTerm = energy + missPt;
            const Double_t mFormulaNeutrino = std::sqrt(
                std::max(0.0, energyTerm * energyTerm - pz * pz));

            out.mass.push_back(mReco);
            out.massFormula.push_back(mFormula);
            out.massFormulaNeutrino.push_back(mFormulaNeutrino);
            out.pz.push_back(pairPz);
            out.deltaR.push_back(tauLv.DeltaR(antiTauLv));
            out.cosDeltaPhi.push_back(std::cos(deltaPhi));
            out.eta.push_back(tau.eta);
            out.eta.push_back(antitau.eta);

            ++nGoodPairs;
        }

        std::cout << file.name << ": " << nGoodPairs << " good pairs (out of "
                  << nSeen << " events read)." << std::endl;
    }
} // namespace

void RecoTauMassKinematics::run(const std::vector<RootFileEntry> &rootFiles, Bool_t debug,
                                Long64_t maxEventsPerFile)
{
    (void)debug;

    Accumulated all;
    for (const RootFileEntry &file : rootFiles)
    {
        processFile(file, maxEventsPerFile, all);
    }

    std::cout << "RecoTauMassKinematics: " << all.mass.size()
              << " good pairs pooled across all files." << std::endl;

    if (all.mass.empty())
    {
        std::cerr << "RecoTauMassKinematics: nothing to histogram, no output written."
                  << std::endl;
        return;
    }

    // Cross-check: m_reco and m_reco_formula are the same physics computed
    // two different ways, so they should agree to float precision.
    Double_t maxDiff = 0.0;
    for (size_t i = 0; i < all.mass.size(); ++i)
    {
        maxDiff = std::max(maxDiff, std::abs(all.mass[i] - all.massFormula[i]));
    }
    std::cout << "RecoTauMassKinematics: max |m_reco - m_reco_formula| = " << maxDiff
              << std::endl;

    // Same fixed ranges as NAOD_TAU/reco_tau_mass.py and
    // reco_tau_kinematics.py (no per-mass-point scaling there either).
    const std::string outFile = "outputs/reco_tau_mass_kinematics.root";

    HistogramWriter::write(all.mass, "reco_tau_mass", 100, 0, 500, outFile, "RECREATE");
    HistogramWriter::write(all.massFormula, "reco_tau_mass_formula", 100, 0, 500, outFile, "UPDATE");
    HistogramWriter::write(all.massFormulaNeutrino, "reco_tau_mass_formula_neutrino", 100, 0, 500,
                           outFile, "UPDATE");
    HistogramWriter::write(all.pz, "reco_tau_pz", 100, -500, 500, outFile, "UPDATE");
    HistogramWriter::write(all.deltaR, "reco_tau_delta_r", 64, 0, 6, outFile, "UPDATE");
    HistogramWriter::write(all.cosDeltaPhi, "reco_tau_cos_delta_phi", 100, -1, 1, outFile, "UPDATE");
    HistogramWriter::write(all.eta, "reco_tau_eta", 60, -TAU_ETA_MAX, TAU_ETA_MAX, outFile, "UPDATE");

    std::cout << "RecoTauMassKinematics: wrote " << outFile << std::endl;
}
