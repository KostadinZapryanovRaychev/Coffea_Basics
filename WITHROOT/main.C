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
#include "Selector.C"
#include "Selector.h"

int main()
{
    // Load path from here
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

    BranchPlotter plotter(Events);

    // the numbers 10, 0 , 10 or 50 ,0 , 200 in arguments are actually the bining . for example 50 bins from 0 to 200 meaning 4 GeV per bin for Tau_pt. 50 bins from -3 to 3 meaning 0.12 per bin for Tau_eta. 10 bins from 0 to 10 meaning 1 per bin for nTau.
    plotter.plotIntBranch("nTau", "h_nTau", 10, 0, 10, maxEvents, "h_nTau.root");
    plotter.plotCountedArrayBranch("nTau", "Tau_pt", "h_Tau_pt", tauArraySize, 50, 0, 200, maxEvents, "h_Tau_pt.root");
    plotter.plotCountedArrayBranch("nTau", "Tau_eta", "h_Tau_eta", tauArraySize, 50, -3, 3, maxEvents, "h_Tau_eta.root");

    // Selector reproduces what the mentor did interactively at the ROOT
    // prompt (Events->Draw("nTau", "Tau_idDeepTau2018v2p5VSjet >= 3 && Tau_pt >= 20")),
    // but saved to file so the histograms can be compared/overlaid later.
    // Needs Tau_idDeepTau2018v2p5VSjet and Tau_pt re-enabled on the tree.
    reader.enableBranches({"Tau_idDeepTau2018v2p5VSjet"});

    Selector selector(Events);

    std::vector<Cut> tauCuts = {
        {"noCut", ""},
        {"tightVSjet", "Tau_idDeepTau2018v2p5VSjet >= 3"},
        {"tightVSjetAndPt20", "Tau_idDeepTau2018v2p5VSjet >= 3 && Tau_pt >= 20"},
    };
    // One nTau histogram per cut, all in h_nTau_selection.root, so the
    // effect of tightening the tau ID/pt selection on the nTau
    // distribution can be seen directly (this is the hypothesis test).
    selector.plotOverlay("nTau", tauCuts, "h_nTau", 10, 0, 10, maxEvents, "h_nTau_selection.root");

    // Second example from the mentor: GenPart_pt restricted to
    // generator-level taus (|pdgId|==15) that are the hard-process
    // final decay product (status==23).
    reader.enableBranches({"GenPart_pt", "GenPart_pdgId", "GenPart_status"});

    std::vector<Cut> genTauCuts = {
        {"allGenPart", ""},
        {"genTau", "abs(GenPart_pdgId)==15"},
        {"genTauHardProcess", "abs(GenPart_pdgId)==15 && GenPart_status==23"},
    };
    selector.plotOverlay("GenPart_pt", genTauCuts, "h_GenPart_pt", 50, 0, 200, maxEvents, "h_GenPart_pt_selection.root");

    return 0;
}
