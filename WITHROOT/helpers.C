#include "helpers.h"

#include <fstream>
#include <cstdio>

void reader(std::string filePath)
{
    std::ifstream file(filePath);

    if (file.is_open())
    {
        printf("File opened successfully: %s\n", filePath.c_str());
        file.close();
    }
    else
    {
        printf("Failed to open file: %s\n", filePath.c_str());
    }
}

Long64_t getEntries(TTree *tree)
{
    if (!tree)
    {
        printf("Cannot get entries: null pointer\n");
        return -1;
    }

    return tree->GetEntries();
}

// ==============================================

// HLT_HT350 -Total scalar sum of jet transverse energy 350GeV.

void printBoolBranch(TTree *tree, const std::string &branchName, Long64_t maxEvents = 10)
{
    if (!tree)
    {
        std::cerr << "Error: Null TTree pointer provided." << std::endl;
        return;
    }

    TBranch *branch = tree->GetBranch(branchName.c_str());
    if (!branch)
    {
        std::cerr << "Error: Branch '" << branchName << "' not found!" << std::endl;
        return;
    }

    Bool_t branchValue = false;

    tree->SetBranchStatus("*", 0);
    tree->SetBranchStatus(branchName.c_str(), 1);
    tree->SetBranchAddress(branchName.c_str(), &branchValue);

    Long64_t nEntries = tree->GetEntries();
    Long64_t limit = std::min(maxEvents, nEntries);

    std::cout << "\n=== Inspecting Branch: " << branchName << " ===" << std::endl;
    for (Long64_t i = 0; i < limit; ++i)
    {
        tree->GetEntry(i);
        std::cout << "Event " << i << " | " << branchName << " = "
                  << (branchValue ? "true (1)" : "false (0)") << std::endl;
    }

    tree->SetBranchStatus("*", 1);
}