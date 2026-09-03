#include "TauGenParticleKinematics.h"

#include <cmath>
#include <iostream>
#include <regex>

#include "TLorentzVector.h"
#include "TMath.h"

#include "BranchReader.h"
#include "Selector.h"
#include "HistogramWriter.h"

namespace
{
// Same idea as TauLHEKinematics.C's extractMassPoint() -- duplicated
// rather than shared, on purpose: each analysis module stays
// self-contained (see TauChannelAnalysis.h for the reasoning), so a
// module can be copied, modified, or deleted without touching its
// siblings. Named differently (extractGenMassPoint, not
// extractMassPoint) because main.C #includes every module's .C file
// into one translation unit, where two same-named functions --even
// each in their own anonymous namespace-- collide.
Double_t extractGenMassPoint(const std::string &inputFilePath)
{
    static const std::regex massPattern("M-(\\d+)");
    std::smatch match;
    if (std::regex_search(inputFilePath, match, massPattern))
    {
        return std::stod(match[1].str());
    }
    std::cout << "TauGenParticleKinematics: could not find an 'M-<number>' mass point in '"
              << inputFilePath << "', defaulting to 500 GeV for histogram ranges." << std::endl;
    return 500.0;
}
} // namespace

// ============================================================
// GenPart-level tau/anti-tau kinematics: enable branches -> select
// events with exactly one tau and one anti-tau -> build per-event
// Lorentz vectors -> histogram single-particle and pair-difference
// variables, mirroring NAOD_TAU/helpers/gen_particles/{reader,histograms}.py.
// ============================================================
void TauGenParticleKinematics::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                                    const std::string &inputFilePath)
{
    // ======================================================================
    // 1. BRANCH ENABLING
    // ======================================================================
    BranchReader reader(Events);
    reader.enableBranches({"nGenPart", "GenPart_pt", "GenPart_eta", "GenPart_phi",
                           "GenPart_mass", "GenPart_pdgId", "GenPart_statusFlags"});

    if (debug)
    {
        std::cout << "TauGenParticleKinematics: DEBUG mode has no dedicated column dumps "
                  << "yet (see ColumnPrinter for the pattern used by TauChannelAnalysis)."
                  << std::endl;
    }

    // ======================================================================
    // 2. SELECTION: exactly one tau (pdgId==15) and one anti-tau
    // (pdgId==-15) in GenPart -- but restricted to each particle's LAST
    // recorded copy first.
    //
    // This deviates from a literal port of select_gen_tau_pairs() in
    // reader.py, which requires ak.sum(pdgId==15)==1 with no status-flag
    // restriction. Checked against this file directly: GenPart records a
    // tau at multiple stages of the parton-shower history (radiation,
    // re-emission, ...), not just once like LHEPart -- of the first 2000
    // events, 1476 have 2 copies of pdgId==15, 495 have 3, 29 have 4, and
    // NONE have exactly 1. So the literal "==1" filter selects zero
    // events; it appears to be untested on the python side too, since
    // both make_lhe_ditau_histograms(...) and make_gen_ditau_histograms(...)
    // are commented out at their call sites in mc_tau_analysis.py.
    //
    // The standard fix (standard CMS GenPart analysis convention) is to
    // first restrict to each particle's LAST copy via GenPart_statusFlags
    // bit 13 ("isLastCopy", mask 0x2000 = 8192) -- the copy immediately
    // before it decays, i.e. its true final kinematics -- and only then
    // require exactly one tau and one anti-tau among those last copies.
    // See https://cms-nanoaod-integration.web.cern.ch/autoDoc/ for the
    // statusFlags bit definitions.
    // ======================================================================
    Selector selector(Events);

    const std::string isLastCopy = "(GenPart_statusFlags & 8192) == 8192";
    const std::string exactlyOnePair =
        "Sum$(GenPart_pdgId == 15 && " + isLastCopy + ") == 1 && "
        "Sum$(GenPart_pdgId == -15 && " + isLastCopy + ") == 1";
    const std::string tauCut = "GenPart_pdgId == 15 && " + isLastCopy + " && " + exactlyOnePair;
    const std::string antiTauCut = "GenPart_pdgId == -15 && " + isLastCopy + " && " + exactlyOnePair;

    std::vector<Double_t> tauPt = selector.select("GenPart_pt", tauCut, maxEvents);
    std::vector<Double_t> tauEta = selector.select("GenPart_eta", tauCut, maxEvents);
    std::vector<Double_t> tauPhi = selector.select("GenPart_phi", tauCut, maxEvents);
    std::vector<Double_t> tauMass = selector.select("GenPart_mass", tauCut, maxEvents);

    std::vector<Double_t> antiTauPt = selector.select("GenPart_pt", antiTauCut, maxEvents);
    std::vector<Double_t> antiTauEta = selector.select("GenPart_eta", antiTauCut, maxEvents);
    std::vector<Double_t> antiTauPhi = selector.select("GenPart_phi", antiTauCut, maxEvents);
    std::vector<Double_t> antiTauMass = selector.select("GenPart_mass", antiTauCut, maxEvents);

    std::cout << "TauGenParticleKinematics: " << tauPt.size()
              << " events passed the exactly-one-tau-and-one-antitau GenPart selection "
              << "(out of " << maxEvents << ")." << std::endl;

    if (tauPt.size() != antiTauPt.size())
    {
        std::cerr << "TauGenParticleKinematics: tau(-)/tau(+) count mismatch ("
                  << tauPt.size() << " vs " << antiTauPt.size() << ") -- this shouldn't "
                  << "happen given the exactly-one-of-each cut; pairing-dependent "
                  << "histograms are skipped as a precaution." << std::endl;
    }

    // ======================================================================
    // 3. DERIVED KINEMATICS: pz = pt*sinh(eta), and the pair four-vector
    // sum -> invariant mass, delta-phi, delta-eta, delta-R.
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

    std::vector<Double_t> pairMass, deltaPhi, deltaEta, deltaR;
    const size_t nPairs = std::min(tauPt.size(), antiTauPt.size());
    pairMass.reserve(nPairs);
    deltaPhi.reserve(nPairs);
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

        Double_t dEta = tauEta[i] - antiTauEta[i];
        deltaEta.push_back(dEta);

        // TLorentzVector::DeltaR wraps dPhi into [-pi, pi] internally,
        // matching vector.behavior's delta_r() used in the python pipeline.
        deltaR.push_back(tauLv.DeltaR(antiTauLv));
    }

    // ======================================================================
    // 4. PLOTTING: same variables and ranges as
    // NAOD_TAU/helpers/gen_particles/histograms.py's _get_histogram_ranges()
    // and per-histogram bin_edge_min/max calls:
    //   invariant mass:  0     .. 2.0*M   (250 bins)
    //   pt:              0     .. 0.6*M   (120 bins)
    //   pz:             -1.5*M .. 1.5*M   (120 bins)
    //   eta:            -3     .. 3       (120 bins)
    //   phi:            -3.2   .. 3.2     (120 bins)
    //   delta-phi:      -6.4   .. 6.4     (120 bins, unwrapped difference,
    //                                      unlike TauLHEKinematics/-pi..pi)
    //   delta-eta:      -7.5   .. 7.5     (120 bins)
    //   delta-R:         0     .. 6.0     (120 bins; TauLHEKinematics uses
    //                                      2..6 instead)
    // Note: unlike the LHE module, this GenPart pipeline has no
    // cos(delta-phi) histogram.
    // All saved into one combined ROOT file, matching
    // save_lhe_histograms_root()'s single "gen_tau_pair_histograms.root".
    // ======================================================================
    const Double_t M = extractGenMassPoint(inputFilePath);
    const std::string outFile = "outputs/gen_tau_pair_histograms.root";

    HistogramWriter::write(tauPt, "gen_tau_pt", 120, 0, 0.6 * M, outFile, "RECREATE");
    HistogramWriter::write(antiTauPt, "gen_antitau_pt", 120, 0, 0.6 * M, outFile, "UPDATE");
    HistogramWriter::write(tauPz, "gen_tau_pz", 120, -1.5 * M, 1.5 * M, outFile, "UPDATE");
    HistogramWriter::write(antiTauPz, "gen_antitau_pz", 120, -1.5 * M, 1.5 * M, outFile, "UPDATE");
    HistogramWriter::write(tauEta, "gen_tau_eta", 120, -3, 3, outFile, "UPDATE");
    HistogramWriter::write(antiTauEta, "gen_antitau_eta", 120, -3, 3, outFile, "UPDATE");
    HistogramWriter::write(tauPhi, "gen_tau_phi", 120, -3.2, 3.2, outFile, "UPDATE");
    HistogramWriter::write(antiTauPhi, "gen_antitau_phi", 120, -3.2, 3.2, outFile, "UPDATE");

    if (!pairMass.empty())
    {
        HistogramWriter::write(pairMass, "gen_mass", 250, 0, 2.0 * M, outFile, "UPDATE");
        HistogramWriter::write(deltaPhi, "gen_delta_phi", 120, -6.4, 6.4, outFile, "UPDATE");
        HistogramWriter::write(deltaEta, "gen_delta_eta", 120, -7.5, 7.5, outFile, "UPDATE");
        HistogramWriter::write(deltaR, "gen_delta_r", 120, 0, 6, outFile, "UPDATE");
    }
}
