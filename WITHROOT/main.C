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
    // Note: Tau_idDeepTau2017v2p1VSjet is left enabled but not printed
    // below — it is a UChar_t array, while ColumnPrinter's array path
    // currently only supports Float_t arrays (see ColumnPrinter.h).
    BranchReader reader(Events);
    reader.enableBranches({"nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_idDeepTau2017v2p1VSjet"});

    // ColumnPrinter only knows how to read/print branch values it is
    // told about — it has no hardcoded branch names, array sizes, event
    // counts or output paths; all of that is passed in below.
    ColumnPrinter printer(Events);

    // "nTau" is a per-event Int_t count, not a Float_t scalar — it must
    // NOT go through printSingleBranch (that caused a type mismatch and
    // a segfault previously). It is printed together with the per-tau
    // arrays below via printCountedArrayBranches instead.

    // Print the tau count together with all four per-tau Float_t arrays
    // (pt, eta, phi, mass) for the first 10 events. 32 is the NanoAOD
    // array capacity for Tau_* branches in this file, passed explicitly
    // rather than hardcoded inside ColumnPrinter.
    printer.printCountedArrayBranches("nTau",
                                      {"Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass"},
                                      32, 10, "tau_kinematics_columns.txt");

    return 0;
}
