#include "BranchReader.h"

#include <iostream>

// ============================================================
// Constructor
// ============================================================

BranchReader::BranchReader(TTree *tree)
    : tree_(tree)
{
    if (!tree_)
    {
        std::cerr << "Error: BranchReader received a null TTree pointer."
                  << std::endl;
        return;
    }

    // By default, disable all branches.
    disableAllBranches();
}

// ============================================================
// Disable all branches
// ============================================================

void BranchReader::disableAllBranches()
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot disable branches."
                  << " TTree pointer is null."
                  << std::endl;
        return;
    }

    tree_->SetBranchStatus("*", 0);

    std::cout << "All TTree branches disabled."
              << std::endl;
}

// ============================================================
// Enable one branch
// ============================================================

bool BranchReader::enableBranch(const std::string &branchName)
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot enable branch."
                  << " TTree pointer is null."
                  << std::endl;
        return false;
    }

    if (branchName.empty())
    {
        std::cerr << "Error: Branch name is empty."
                  << std::endl;
        return false;
    }

    // Check if branch exists
    TBranch *branch = tree_->GetBranch(branchName.c_str());

    if (!branch)
    {
        std::cerr << "Error: Branch '"
                  << branchName
                  << "' was not found in the TTree."
                  << std::endl;

        return false;
    }

    // Enable requested branch
    tree_->SetBranchStatus(branchName.c_str(), 1);

    std::cout << "Enabled branch: "
              << branchName
              << std::endl;

    return true;
}

// ============================================================
// Enable multiple branches
// ============================================================

void BranchReader::enableBranches(
    const std::vector<std::string> &branchNames)
{
    for (const std::string &branchName : branchNames)
    {
        enableBranch(branchName);
    }
}

// ============================================================
// Get number of entries
// ============================================================

Long64_t BranchReader::getEntries() const
{
    if (!tree_)
    {
        return 0;
    }

    return tree_->GetEntries();
}

// ============================================================
// Get underlying TTree
// ============================================================

TTree *BranchReader::getTree() const
{
    return tree_;
}