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
#include "BranchPlotter.C"
#include "BranchPlotter.h"

int main()
{
    // Load settings (currently just the input file path) from config.json
    // instead of hardcoding it here.
    Config config = loadConfig("config.json");

    // Open the NanoAOD file and grab the "Events" TTree.
    TTree *Events = getEventsTree(config.inputFile);

    printEventTree(Events);

    // BranchReader only manages which branches are active on the tree(disables everything, then re - enables the ones we pass in).
    BranchReader reader(Events);
    reader.enableBranches({"nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_idDeepTau2017v2p1VSjet"});

    // ColumnPrinter only knows how to read/print branch values it is
    // told about — it has no hardcoded branch names, array sizes, event
    // counts or output paths; all of that is passed in below.
    ColumnPrinter printer(Events);

    const Long64_t maxEvents = Events->GetEntries(); // Use all events in the file.
    const Int_t tauArraySize = 32;                   // NanoAOD array capacity for Tau_* branches in this file.

    // "nTau" is a per-event Int_t scalar count (not Float_t), so it gets
    // its own dedicated print path (printIntBranch), separate from the
    // per-tau array branches below.
    printer.printIntBranch("nTau", maxEvents, "nTau_column.txt");

    // Each per-tau Float_t array branch is printed to its own file.
    // "nTau" is still passed in as the count branch so each branch

    // printer.printCountedArrayBranches("nTau", {"Tau_pt"}, tauArraySize, maxEvents, "Tau_pt_column.txt");
    // printer.printCountedArrayBranches("nTau", {"Tau_eta"}, tauArraySize, maxEvents, "Tau_eta_column.txt");
    // printer.printCountedArrayBranches("nTau", {"Tau_phi"}, tauArraySize, maxEvents, "Tau_phi_column.txt");
    // printer.printCountedArrayBranches("nTau", {"Tau_mass"}, tauArraySize, maxEvents, "Tau_mass_column.txt");

    // Tau_idDeepTau2017v2p1VSjet is stored as UChar_t, not Float_t, so

    // printer.printCountedUCharArrayBranch("nTau", "Tau_idDeepTau2017v2p1VSjet",
    //                                      tauArraySize, maxEvents,
    //                                      "Tau_idDeepTau2017v2p1VSjet_column.txt");

    // Same branch again, but for the first 50 events, into its own file.

    // printer.printCountedUCharArrayBranch("nTau", "Tau_idDeepTau2017v2p1VSjet",
    //                                      tauArraySize, 50,
    //                                      "Tau_idDeepTau2017v2p1VSjet_column_50.txt");

    // BranchPlotter only knows how to fill and save histograms from
    // branch values it is told about — no hardcoded branch names,
    // binning, event counts or output paths; all of that is passed in
    // below. No event selection/cuts are applied here.
    BranchPlotter plotter(Events);

    // "nTau" is a per-event Int_t scalar count, so it gets its own
    // dedicated plot path (plotIntBranch).
    plotter.plotIntBranch("nTau", "h_nTau", 10, 0, 10, maxEvents, "h_nTau.root");

    // Each per-tau Float_t array branch is filled into its own
    // histogram, one entry per tau object across all events. "nTau" is
    // still passed in as the count branch so it knows how many of the
    // 32 slots are valid per event.
    plotter.plotCountedArrayBranch("nTau", "Tau_pt", "h_Tau_pt", tauArraySize, 50, 0, 200, maxEvents, "h_Tau_pt.root");
    plotter.plotCountedArrayBranch("nTau", "Tau_eta", "h_Tau_eta", tauArraySize, 50, -3, 3, maxEvents, "h_Tau_eta.root");

    return 0;
}
