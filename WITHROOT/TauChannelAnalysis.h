#ifndef TAUCHANNELANALYSIS_H
#define TAUCHANNELANALYSIS_H

#include <string>
#include "TTree.h"
#include "Rtypes.h"

// Runs the full tau-decay-channel analysis: enables the Tau_*/Muon_*/
// Electron_* branches it needs, optionally prints DEBUG=1 column dumps,
// builds the hadronic/muonic/electronic decay-channel selections, fills
// their histograms, and overlays the resulting pT spectra into
// h_nTau_selection.root.
//
// This used to live inline in main(). It's pulled out into its own
// self-contained unit -- branch enabling through plotting, start to
// finish -- so it can be one module among several sibling analyses
// (e.g. a future LheAnalysis or GenParticleAnalysis covering a
// different part of the NanoAOD event), each with the same shape:
// one .C/.h pair, one run() entry point, called from main() in
// sequence. Keeps main() a short list of "run this analysis, run that
// analysis" instead of one file that grows without bound.
class TauChannelAnalysis
{
public:
    // Events: the NanoAOD "Events" TTree (already opened by main()).
    // debug: mirrors main()'s DEBUG=1 env var switch -- when true, also
    //   writes the *_column.txt / *_column_50.txt debug dumps.
    // maxEvents: how many entries to process (<=0 not meaningful here;
    //   main() passes Events->GetEntries()).
    // inputFilePath: source file path, used only to extract the Z' mass
    //   point (via MassPointUtils) so the pt histogram ranges scale with
    //   it -- config.json points at a different mass-point sample each
    //   run (see NAOD_TAU/file_config_batch_all_mass_points.json for the
    //   range of mass points this can be), so a hardcoded range would be
    //   wrong for every sample except the one it was tuned for.
    static void run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                     const std::string &inputFilePath);
};

#endif
