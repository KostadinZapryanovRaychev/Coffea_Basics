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

void printBoolHLT_HT350OnlyTrue(TTree *tree, Long64_t maxEvents)
{
    if (!tree)
    {
        std::cerr << "Error: Null TTree pointer provided." << std::endl;
        return;
    }
    TBranch *branch = tree->GetBranch("HLT_HT350");
    if (!branch)
    {
        std::cerr << "Error: Branch 'HLT_HT350' not found!" << std::endl;
        return;
    }

    Bool_t branchValue = false;

    tree->SetBranchStatus("*", 0);
    tree->SetBranchStatus("HLT_HT350", 1);
    tree->SetBranchAddress("HLT_HT350", &branchValue);
    std::ofstream outFile("HLT_HT350_passed_events.txt");
    if (!outFile.is_open())
    {
        std::cerr << "Error: Could not create output file!" << std::endl;
        tree->SetBranchStatus("*", 1);
        return;
    }

    Long64_t nEntries = tree->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;
    Long64_t passCount = 0;

    outFile << "=== Events Passing HLT_HT350 ===" << std::endl;
    for (Long64_t i = 0; i < limit; ++i)
    {
        tree->GetEntry(i);
        if (branchValue)
        {
            outFile << "Event " << i << " | HLT_HT350 = true (1)" << std::endl;
            passCount++;
        }
    }
    outFile << "\nSummary: " << passCount << " / " << limit << " events passed." << std::endl;
    outFile.close();
    std::cout << "Done! Found " << passCount << " passing events. Saved results to 'HLT_HT350_passed_events.txt'." << std::endl;
    tree->SetBranchStatus("*", 1);
}