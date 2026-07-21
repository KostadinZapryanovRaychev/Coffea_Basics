#ifndef BRANCHREADER_H
#define BRANCHREADER_H

#include <string>
#include <vector>
#include "TTree.h"

class BranchReader
{
public:
    // Constructor
    BranchReader(TTree *tree);

    // Disable all branches in the TTree
    void disableAllBranches();

    // Enable one branch
    bool enableBranch(const std::string &branchName);

    // Enable multiple branches
    void enableBranches(const std::vector<std::string> &branchNames);

    // Get number of entries/events
    Long64_t getEntries() const;

    // Get the underlying TTree
    TTree *getTree() const;

private:
    // Pointer to the ROOT TTree
    TTree *tree_;
};

#endif
