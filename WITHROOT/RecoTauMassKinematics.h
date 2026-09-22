#ifndef RECOTAUMASSKINEMATICS_H
#define RECOTAUMASSKINEMATICS_H

#include <string>
#include <vector>
#include "Rtypes.h"
#include "Config.h"

// Reconstructed-Tau (detector-level) counterpart of
// NAOD_TAU/reco_tau_kinematics.py + NAOD_TAU/reco_tau_mass.py, combined
// into one module: same pair selection, same mother-boson (Z/Z') mass
// reconstructed three ways, same kinematic distributions, run over a
// SET of input files (not just config.json's single inputFile) and all
// written into one output ROOT file.
//
// The three mass histograms answer the same cross-check question the
// python side does:
//   m_reco             -- TLorentzVector sum of the two visible taus (.M())
//   m_reco_formula      -- same mass, computed by hand from the
//                          E = sqrt(px^2+py^2+pz^2+m^2) formula, as a
//                          cross-check that .M() and the explicit formula
//                          agree (they should, to float precision)
//   m_reco_formula_neutrino -- the visible-mass formula PLUS the missing
//                          transverse momentum of the escaping tau
//                          neutrinos, via Eq. (1) of the CMS paper
//                          arXiv:2412.04357 / PRD 111, 112004:
//                            pT_miss = -(pT1_vis + pT2_vis), pz_miss = 0
//                            m_rec = sqrt[(E1+E2+|pT_miss|)^2 - (pz1+pz2)^2]
//                          This is the mother boson (Z/Z') mass estimate;
//                          it should sit closer to the true resonance mass
//                          than the plain visible mass, because it
//                          partially accounts for the neutrinos that
//                          m_reco and m_reco_formula both ignore.
class RecoTauMassKinematics
{
public:
    // rootFiles: files to process (e.g. loadRootFileList("file_config_reco.json")).
    //   Every file's surviving pairs are pooled into one set of histograms,
    //   mirroring collect_kinematics_from_files() in the python pipeline.
    // debug: mirrors main()'s DEBUG=1 env var switch.
    // maxEventsPerFile: how many entries to process per file (<=0 means all).
    static void run(const std::vector<RootFileEntry> &rootFiles, Bool_t debug,
                     Long64_t maxEventsPerFile);
};

#endif
