#include "TauLHEKinematics.h"

#include <cmath>
#include <iostream>

#include "TLorentzVector.h"
#include "TMath.h"

#include "BranchReader.h"
#include "Selector.h"
#include "HistogramWriter.h"
#include "MassPointUtils.h"

void TauLHEKinematics::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                           const std::string &inputFilePath)
{

    // Object property	Type	Description

    // LHEPart_eta	Float_t	Pseodorapidity of LHE particles
    // LHEPart_mass	Float_t	Mass of LHE particles
    // LHEPart_pdgId	Int_t	PDG ID of LHE particles
    // LHEPart_phi	Float_t	Phi of LHE particles
    // LHEPart_pt	Float_t	Pt of LHE particles
    // nLHEPart	Int_t

    // LHEPart_spin	Int_t	Spin of LHE particles can we use spin ?
    // LHEPart_incomingpz	Float_t	Pz of incoming LHE particles can we use this ?
    BranchReader reader(Events);
    reader.enableBranches({"nLHEPart", "LHEPart_pt", "LHEPart_eta", "LHEPart_phi",
                           "LHEPart_mass", "LHEPart_pdgId"});

    if (debug)
    {
        std::cout << "TauLHEKinematics: DEBUG mode has no dedicated column dumps yet "
                  << "(see ColumnPrinter for the pattern used by TauChannelAnalysis)."
                  << std::endl;
    }

    // ======================================================================
    // 2. SELECTION: LHE tau (pdgId == 15) and anti-tau (pdgId == -15).
    //
    // This assumes exactly one tau and one anti-tau per event at LHE level
    // (true for this Z'->tautau hard process), so selecting each kinematic
    // branch under the same pdgId cut yields one aligned value per event
    // per array, in the same event order across all four branches
    // ======================================================================
    Selector selector(Events);

    const std::string tauCut = "LHEPart_pdgId == 15";
    const std::string antiTauCut = "LHEPart_pdgId == -15";

    std::vector<Double_t> tauPt = selector.select("LHEPart_pt", tauCut, maxEvents);
    std::vector<Double_t> tauEta = selector.select("LHEPart_eta", tauCut, maxEvents);
    std::vector<Double_t> tauPhi = selector.select("LHEPart_phi", tauCut, maxEvents);
    std::vector<Double_t> tauMass = selector.select("LHEPart_mass", tauCut, maxEvents);

    std::vector<Double_t> antiTauPt = selector.select("LHEPart_pt", antiTauCut, maxEvents);
    std::vector<Double_t> antiTauEta = selector.select("LHEPart_eta", antiTauCut, maxEvents);
    std::vector<Double_t> antiTauPhi = selector.select("LHEPart_phi", antiTauCut, maxEvents);
    std::vector<Double_t> antiTauMass = selector.select("LHEPart_mass", antiTauCut, maxEvents);

    std::cout << "TauLHEKinematics: found " << tauPt.size() << " LHE tau(-) and "
              << antiTauPt.size() << " LHE tau(+) candidates over " << maxEvents
              << " events." << std::endl;

    if (tauPt.size() != antiTauPt.size())
    {
        std::cerr << "TauLHEKinematics: tau(-)/tau(+) count mismatch (" << tauPt.size()
                  << " vs " << antiTauPt.size() << ") -- pairing may be misaligned."
                  << std::endl;
    }

    // ======================================================================
    // 3. DERIVED KINEMATICS: pz (not a stored branch, pz = pt*sinh(eta))
    // and the pair four-vector sum -> invariant mass, for every event
    // that has both a tau(-) and a tau(+).
    // ======================================================================
    std::vector<Double_t> tauPz, antiTauPz;
    tauPz.reserve(tauPt.size());
    for (size_t i = 0; i < tauPt.size(); ++i)
    {
        tauPz.push_back(tauPt[i] * std::sinh(tauEta[i]));
    }
    antiTauPz.reserve(antiTauPt.size());
    for (size_t i = 0; i < antiTauPt.size(); ++i)
    {
        antiTauPz.push_back(antiTauPt[i] * std::sinh(antiTauEta[i]));
    }

    std::vector<Double_t> pairMass, deltaPhi, cosDeltaPhi, deltaEta, deltaR;
    const size_t nPairs = std::min(tauPt.size(), antiTauPt.size());
    pairMass.reserve(nPairs);
    deltaPhi.reserve(nPairs);
    cosDeltaPhi.reserve(nPairs);
    deltaEta.reserve(nPairs);
    deltaR.reserve(nPairs);
    for (size_t i = 0; i < nPairs; ++i)
    {
        TLorentzVector tauLv, antiTauLv;
        tauLv.SetPtEtaPhiM(tauPt[i], tauEta[i], tauPhi[i], tauMass[i]);
        antiTauLv.SetPtEtaPhiM(antiTauPt[i], antiTauEta[i], antiTauPhi[i], antiTauMass[i]);

        pairMass.push_back((tauLv + antiTauLv).M());

        Double_t dPhi = tauPhi[i] - antiTauPhi[i];
        deltaPhi.push_back(dPhi);
        cosDeltaPhi.push_back(std::cos(dPhi));

        Double_t dEta = tauEta[i] - antiTauEta[i];
        deltaEta.push_back(dEta);

        deltaR.push_back(std::sqrt(dEta * dEta + dPhi * dPhi));
    }

    // ======================================================================
    // 4. PLOTTING: same variables, same range-scaling-with-mass-point
    // convention as _get_histogram_ranges() in NAOD_TAU/helpers/plotting.py:
    //   invariant mass:  0        .. 2.0*M   (250 bins there; kept here)
    //   pt:              0        .. 0.6*M
    //   pz:             -1.5*M    .. 1.5*M
    //   delta-R:         2        .. 6.0     (fixed, mass-independent)
    //   delta-eta:      -7.5      .. 7.5     (fixed)
    //   delta-phi/eta:  -pi       .. pi       (fixed)
    //   cos(delta-phi): -1        .. 1        (fixed)
    // All saved into one combined ROOT file, matching
    // save_lhe_histograms_root()'s single "tau_pair_histograms.root".
    // ======================================================================
    const Double_t M = MassPointUtils::extractMassPoint(inputFilePath);
    const std::string outFile = "outputs/lhe_tau_pair_histograms.root";

    HistogramWriter::write(tauPt, "lhe_tau_pt", 120, 0, 0.6 * M, outFile, "RECREATE");
    HistogramWriter::write(antiTauPt, "lhe_antitau_pt", 120, 0, 0.6 * M, outFile, "UPDATE");
    HistogramWriter::write(tauPz, "lhe_tau_pz", 120, -1.5 * M, 1.5 * M, outFile, "UPDATE");
    HistogramWriter::write(antiTauPz, "lhe_antitau_pz", 120, -1.5 * M, 1.5 * M, outFile, "UPDATE");
    HistogramWriter::write(tauEta, "lhe_tau_eta", 120, -3, 3, outFile, "UPDATE");
    HistogramWriter::write(antiTauEta, "lhe_antitau_eta", 120, -3, 3, outFile, "UPDATE");
    HistogramWriter::write(tauPhi, "lhe_tau_phi", 120, -TMath::Pi(), TMath::Pi(), outFile, "UPDATE");
    HistogramWriter::write(antiTauPhi, "lhe_antitau_phi", 120, -TMath::Pi(), TMath::Pi(), outFile, "UPDATE");

    if (!pairMass.empty())
    {
        HistogramWriter::write(pairMass, "lhe_mass", 250, 0, 2.0 * M, outFile, "UPDATE");
        HistogramWriter::write(deltaPhi, "lhe_delta_phi", 60, -TMath::Pi(), TMath::Pi(), outFile, "UPDATE");
        HistogramWriter::write(cosDeltaPhi, "lhe_cos_delta_phi", 100, -1, 1, outFile, "UPDATE");
        HistogramWriter::write(deltaEta, "lhe_delta_eta_ditau_pair", 120, -7.5, 7.5, outFile, "UPDATE");
        HistogramWriter::write(deltaR, "lhe_delta_r_ditau_pair", 120, 2, 6, outFile, "UPDATE");
    }
}
