#ifndef TAUHADHADRECOMASS_H
#define TAUHADHADRECOMASS_H

#include <string>
#include "TTree.h"
#include "Rtypes.h"

// Reconstructs the Z' candidate mass for the tau_h tau_h channel (both
// taus decayed hadronically) using GenVisTau -- the truth-level "visible
// decay products only" object -- following Eq. (1) of the CMS Z'->tautau
// search (arXiv:2412.04357 / PRD 111, 112004):
//
//   m_rec(Z') = sqrt[ (E1vis+E2vis+|pT_miss|)^2 - |p1vis+p2vis+p_miss|^2 ]
//
// where p_miss = (pT_miss, 0) is NOT the real missing transverse energy;
// it's assumed pT_miss = -(p1vis_T + p2vis_T) (the Z' is assumed to have
// zero net transverse momentum) with zero longitudinal component.
//
// This is deliberately NOT the same as TauLHEKinematics/
// TauGenParticleKinematics's (tau1+tau2).M(): those use the FULL tau
// (before it decays, neutrino included), which is a valid, complete
// 4-vector on its own. GenVisTau is the opposite: only the visible decay
// products, with the neutrino's momentum missing by construction, so
// naively summing two GenVisTau 4-vectors and calling .M() would give a
// systematically wrong ("visible-only") mass. This module reconstructs
// the correct m_rec instead.
//
// Only the tau_h tau_h case is implemented here (the simplest of the
// three channels: 2 missing neutrinos, one per leg, vs. 3 for a
// hadronic+leptonic pairing). GenVisTau only exists for hadronic tau
// decays in the first place, so requiring exactly two GenVisTau objects
// in an event is itself the tau_h tau_h selection.
class TauHadHadRecoMass
{
public:
    // Events: the NanoAOD "Events" TTree (already opened by main()).
    // debug: mirrors main()'s DEBUG=1 env var switch.
    // maxEvents: how many entries to process.
    // inputFilePath: source file path, used only to extract the Z' mass
    //   point for the histogram range (see MassPointUtils.h).
    static void run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                     const std::string &inputFilePath);
};

#endif
