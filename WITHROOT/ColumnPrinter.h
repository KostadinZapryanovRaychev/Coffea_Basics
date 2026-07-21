#ifndef COLUMNPRINTER_H
#define COLUMNPRINTER_H

#include <string>
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

    // Print a single scalar Float_t branch (e.g. "MET_pt") to outputPath.
    void printSingleBranch(const std::string &branchName,
                            Long64_t maxEvents,
                            const std::string &outputPath) const;

    // Print a per-event count branch (e.g. "nTau") together with its two
    // associated fixed-size array branches (e.g. "Tau_pt", "Tau_eta") and
    // one extra scalar branch (e.g. "MET_pt") to outputPath.
    // maxArraySize must match (or exceed) the array size reserved by the
    // ntuple for the array branches (NanoAOD typically caps at 32).
    void printCountedArrayBranches(const std::string &countBranch,
                                    const std::string &arrayBranch1,
                                    const std::string &arrayBranch2,
                                    const std::string &extraScalarBranch,
                                    Int_t maxArraySize,
                                    Long64_t maxEvents,
                                    const std::string &outputPath) const;

private:
    TTree *tree_;
};

#endif
