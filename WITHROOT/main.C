#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"
#include "BranchReader.C"
#include "BranchReader.h"
#include "ColumnPrinter.C"
#include "ColumnPrinter.h"

int main()
{
    // Open the NanoAOD file and grab the "Events" TTree.
    TTree *Events = getEventsTree("../nanoaodsim_coffea_1.root");

    // BranchReader only manages which branches are active on the tree
    // (disables everything, then re-enables the ones we pass in).
    BranchReader reader(Events);
    reader.enableBranches({"nTau", "Tau_pt", "Tau_eta", "MET_pt"});

    // ColumnPrinter only knows how to read/print branch values it is
    // told about — it has no hardcoded branch names, array sizes, event
    // counts or output paths; all of that is passed in below.
    ColumnPrinter printer(Events);

    // Example 1: print a single branch ("MET_pt") for the first 10
    // events into its own output file.
    printer.printSingleBranch("MET_pt", 10, "met_pt_column.txt");

    // Example 2: print a "counted array" group of branches — the tau
    // count, the two per-tau arrays, and MET_pt as an extra scalar —
    // for the first 10 events. 32 is the NanoAOD array capacity for
    // Tau_pt/Tau_eta in this file, passed explicitly rather than
    // hardcoded inside ColumnPrinter.
    printer.printCountedArrayBranches("nTau", "Tau_pt", "Tau_eta", "MET_pt",
                                      32, 10, "tau_kinematics_columns.txt");

    return 0;
}
