#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"
#include "HistogramWriter.C"
#include "HistogramWriter.h"
#include "TauPogMass.C"
#include "TauPogMass.h"

int main()
{
    // Debug mode: enable by starting the session with, e.g.
    //   DEBUG=1 root -l -q main.C
    // When off, the printer calls below are skipped entirely.
    const bool debug = (gSystem->Getenv("DEBUG") != nullptr) &&
                       (TString(gSystem->Getenv("DEBUG")) == "1");

    // Load path from here
    Config config = loadConfig("config.json");

    // Open the NanoAOD file and grab the "Events" TTree.
    TTree *Events = getEventsTree(config.inputFile);
    printEventTree(Events);

    // Dump every branch name on the Events tree to a txt file for exploration.
    listBranchNames(Events, "outputs/branch_names.txt");

    // Use all events in the file.
    const Long64_t maxEvents = Events->GetEntries();

    // ======================================================================
    // Only TauPogMass runs: the Tau POG Run-3 baseline tau selection
    // (pT > 20, |eta| < 2.5, |dz| < 0.2 -- nothing else), then the mass
    // of the two leading taus in every event with >= 2 of them.
    //
    // The other modules (TauHadHadRecoMass, TauHadHadDataMass,
    // TauChannelAnalysis, TauLHEKinematics, TauGenParticleKinematics)
    // still exist as separate files and can be added back with one call
    // each -- see git history.
    // ======================================================================
    TauPogMass::run(Events, debug, maxEvents, config.inputFile);

    return 0;
}
