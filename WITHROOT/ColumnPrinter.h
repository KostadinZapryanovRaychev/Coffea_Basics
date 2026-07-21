#ifndef COLUMNPRINTER_H
#define COLUMNPRINTER_H

#include <string>
#include <vector>
#include "TTree.h"

// Prints/exports branch ("column") values from a TTree to a text file.
// Kept separate from BranchReader (branch enable/disable bookkeeping) so
// each class has a single responsibility.
//
// Nothing about a specific ntuple layout (branch names, array sizes,
// event counts, output paths) is hardcoded here — everything is passed
// in by the caller so the class stays reusable for any TTree.
class ColumnPrinter
{
public:
    ColumnPrinter(TTree *tree);

    // Print a single per-event scalar Float_t branch (e.g. "MET_pt") to
    // outputPath. Do NOT use this for count branches (they are Int_t,
    // e.g. "nTau") or for per-object array branches (e.g. "Tau_pt") —
    // binding those to a single Float_t address reads garbage or
    // overruns memory. Use printCountedArrayBranches for those instead.
    void printSingleBranch(const std::string &branchName,
                           Long64_t maxEvents,
                           const std::string &outputPath) const;

    // Print a single per-event scalar Int_t branch (e.g. "nTau") to
    // outputPath — one value per event, no associated array.
    void printIntBranch(const std::string &branchName,
                         Long64_t maxEvents,
                         const std::string &outputPath) const;

    // Print a per-event Int_t count branch (e.g. "nTau") together with
    // any number of associated Float_t array branches (e.g. "Tau_pt",
    // "Tau_eta", "Tau_phi", "Tau_mass") to outputPath. Each array branch
    // holds one value per object in the event (up to maxArraySize
    // entries, the capacity reserved by the ntuple for those arrays —
    // NanoAOD typically caps at 32).
    void printCountedArrayBranches(const std::string &countBranch,
                                   const std::vector<std::string> &arrayBranches,
                                   Int_t maxArraySize,
                                   Long64_t maxEvents,
                                   const std::string &outputPath) const;

    // Print a single per-object UChar_t array branch (e.g.
    // "Tau_idDeepTau2017v2p1VSjet") to outputPath, using countBranch
    // (e.g. "nTau") to know how many of the maxArraySize slots are
    // valid per event. Separate from printCountedArrayBranches because
    // NanoAOD ID/flag branches are stored as UChar_t, not Float_t.
    void printCountedUCharArrayBranch(const std::string &countBranch,
                                       const std::string &arrayBranch,
                                       Int_t maxArraySize,
                                       Long64_t maxEvents,
                                       const std::string &outputPath) const;

private:
    TTree *tree_;
};

#endif
