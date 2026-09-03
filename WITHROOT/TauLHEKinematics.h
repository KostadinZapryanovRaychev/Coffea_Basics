#ifndef TAULHEKINEMATICS_H
#define TAULHEKINEMATICS_H

#include <string>
#include "TTree.h"
#include "Rtypes.h"

// Ports the LHE-level (generator, pre-detector) tau-pair analysis from
// NAOD_TAU/helpers/lhe_ditau_candidates.py + plotting.py (the coffea
// pipeline) to this ROOT/TTreeFormula-based codebase: select the LHE
// tau (pdgId==15) and anti-tau (pdgId==-15), build their kinematics,
// and histogram the single-particle and pair-difference variables that
// pipeline plots (pt, pz, eta, phi, pair mass, delta-phi, cos(delta-phi),
// delta-eta, delta-R). Same shape as TauChannelAnalysis: one .C/.h pair,
// one run() entry point, branch enabling through plotting -- see
// TauChannelAnalysis.h for why each analysis domain gets its own module.
//
// LHE ("Les Houches Event") particles are the generator-level, pre-parton
// shower final state of the hard scattering -- i.e. what the matrix
// element calculation produced, before hadronization/detector simulation.
// This is truth-level, not reconstructed: unlike TauChannelAnalysis (which
// reasons about reconstructed Tau_*/Muon_*/Electron_* and cannot know the
// true decay), LHEPart_pdgId==15/-15 tells you with certainty this is a
// tau/anti-tau as generated, since it's exactly what's recorded before
// any detector effects.
class TauLHEKinematics
{
public:
    // Events: the NanoAOD "Events" TTree (already opened by main()).
    // debug: mirrors main()'s DEBUG=1 env var switch.
    // maxEvents: how many entries to process.
    // inputFilePath: the source file path (e.g. config.inputFile) -- used
    //   only to extract the Z' mass point (a "M-250" style substring) so
    //   histogram ranges can scale with it, matching extract_mass_point()
    //   in NAOD_TAU/helpers/io.py. Pass "" if unknown; a default of
    //   500 GeV is used then (same fallback as the python pipeline).
    static void run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                     const std::string &inputFilePath);
};

#endif
