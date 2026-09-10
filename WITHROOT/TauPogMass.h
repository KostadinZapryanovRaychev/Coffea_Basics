#ifndef TAUPOGMASS_H
#define TAUPOGMASS_H

#include <string>
#include "TTree.h"
#include "Rtypes.h"

// Reconstructs the di-tau mass using ONLY the baseline kinematic tau
// selection recommended by the CMS Tau POG for Run 3
// (https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendationForRun3):
//
//     "We recommend to use reconstructed taus with
//      pT > 20 GeV, |eta| < 2.5, |dz| < 0.2."
//
// Nothing else. No DeepTau isolation working point, no HLT trigger, no
// opposite-sign requirement, no decay-mode restriction. (The Tau POG
// page notes the NanoAOD Tau collection *already* has
// decayModeFindingNewDMs and a loose weak-ID OR applied by construction,
// so every Tau entry in the file has passed that -- we do not re-apply
// it.)
//
// For every event with at least two taus passing that selection, it
// takes the two highest-pT ones and fills the PLAIN invariant mass of
// the two visible tau 4-vectors, (t1 + t2).M(), into a histogram. No
// neutrino / missing-momentum correction -- just the visible particles.
class TauPogMass
{
public:
    static void run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                     const std::string &inputFilePath);
};

#endif
