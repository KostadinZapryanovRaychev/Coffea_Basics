#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"
#include "BranchReader.C"
#include "BranchReader.h"
#include "ColumnPrinter.C"
#include "ColumnPrinter.h"
#include "Selector.C"
#include "Selector.h"
#include "HistogramWriter.C"
#include "HistogramWriter.h"
#include "HistogramOverlay.C"
#include "HistogramOverlay.h"
#include "MassPointUtils.C"
#include "MassPointUtils.h"
#include "TauPogMass.C"
#include "TauPogMass.h"
#include "TauChannelAnalysis.C"
#include "TauChannelAnalysis.h"

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

    // Tau POG baseline di-tau mass (before / after the POG selection).
    TauPogMass::run(Events, debug, maxEvents, config.inputFile);

    // Full tau-decay-channel analysis + di-tau invariant mass (section 5).
    TauChannelAnalysis::run(Events, debug, maxEvents, config.inputFile);

    return 0;
}
