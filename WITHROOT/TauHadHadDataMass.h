#ifndef TAUHADHADDATAMASS_H
#define TAUHADHADDATAMASS_H

#include <string>
#include "TTree.h"
#include "Rtypes.h"

// Reconstructs the tau_h tau_h m_rec(Z') mass from the RECONSTRUCTED Tau
// collection -- i.e. from what the detector actually measured.
//
// This is the module meant for REAL COLLISION DATA, e.g. the CMS dataset
//   /Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD
// Real data has no generator objects at all -- no GenVisTau, no GenPart,
// no LHEPart -- so TauHadHadRecoMass / TauLHEKinematics /
// TauGenParticleKinematics do not apply to it. Only reconstructed
// objects (Tau_*, Muon_*, Electron_*, HLT_*, ...) exist.
//
// Same m_rec formula as TauHadHadRecoMass (Eq. 1 of arXiv:2412.04357),
// but with three things a real-data analysis must do that a truth-level
// one skips:
//   1. HLT trigger: keep only events that fired the dedicated di-tau
//      trigger (otherwise the event sample is a random mix recorded for
//      unrelated reasons and normalization is meaningless).
//   2. Full Tau POG / analysis-note tau_h object selection (pT, |eta|,
//      |dz|, DeepTau working points, decay mode) -- reconstructed taus
//      are mostly misidentified jets without it.
//   3. deltaR(tau1, tau2) > 0.3 so the two tau candidates aren't the
//      same detector object counted twice.
//
// It also fills m_vis (the naive sum-of-visible-4-vectors mass) next to
// m_rec, so the effect of the missing-neutrino correction is visible.
class TauHadHadDataMass
{
public:
    static void run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                    const std::string &inputFilePath);
};

#endif
