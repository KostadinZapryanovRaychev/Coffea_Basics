#ifndef TAUGENPARTICLEKINEMATICS_H
#define TAUGENPARTICLEKINEMATICS_H

#include <string>
#include "TTree.h"
#include "Rtypes.h"

// Ports the GenPart-level tau-pair analysis from
// NAOD_TAU/helpers/gen_particles/{reader,histograms}.py (the coffea
// pipeline) to this ROOT/TTreeFormula-based codebase. Same shape as
// TauChannelAnalysis and TauLHEKinematics: one .C/.h pair, one run()
// entry point, branch enabling through plotting.
//
// GenPart is the post-parton-shower/hadronization generator record --
// "GEN particles / stable final-state particles" in the pipeline diagram
// in WITHROOT/README.md -- one stage downstream of LHEPart (which is the
// pre-shower matrix-element output). Like LHEPart, GenPart_pdgId is
// generator truth: pdgId==15/-15 tells you with certainty this is a
// tau/anti-tau, no reconstruction/ID purity caveats needed (unlike
// TauChannelAnalysis's reconstructed Tau_*/Muon_*/Electron_* objects).
//
// Differs from TauLHEKinematics in one important way: GenPart typically
// contains a tau at MULTIPLE stages of the parton-shower history (unlike
// LHEPart, which only has the single hard-process particle), so this
// module first restricts to each tau's LAST recorded copy
// (GenPart_statusFlags bit 13, "isLastCopy" -- its true final kinematics
// right before it decays), then requires exactly one such last-copy tau
// and one last-copy anti-tau per event. The python pipeline's
// select_gen_tau_pairs() requires exactly one pdgId==15 with no
// status-flag restriction at all, which -- checked directly against this
// project's sample -- selects zero events, since real events have 2-4
// copies of pdgId==15 (a physical property of GenPart's shower record,
// not a bug); see the SELECTION comment in TauGenParticleKinematics.C
// for the measured breakdown.
class TauGenParticleKinematics
{
public:
    // Events: the NanoAOD "Events" TTree (already opened by main()).
    // debug: mirrors main()'s DEBUG=1 env var switch.
    // maxEvents: how many entries to process.
    // inputFilePath: source file path, used only to extract the Z' mass
    //   point for histogram ranges (see TauLHEKinematics.h for details).
    static void run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                     const std::string &inputFilePath);
};

#endif
