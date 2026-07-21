#include "ColumnPrinter.h"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <vector>

// ============================================================
// Constructor: just stores the TTree pointer we'll read from.
// ============================================================
ColumnPrinter::ColumnPrinter(TTree *tree)
    : tree_(tree)
{
    if (!tree_)
    {
        std::cerr << "Error: ColumnPrinter received a null TTree pointer."
                  << std::endl;
    }
}

// ============================================================
// Print a single scalar branch
// branchName / maxEvents / outputPath are all supplied by the caller,
// so this method makes no assumption about which branch it prints.
// ============================================================

void ColumnPrinter::printSingleBranch(const std::string &branchName,
                                       Long64_t maxEvents,
                                       const std::string &outputPath) const
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot print branch. TTree pointer is null."
                   << std::endl;
        return;
    }

    // Bind a local variable to the requested branch (given by name).
    Float_t value = 0.0;
    tree_->SetBranchAddress(branchName.c_str(), &value);

    std::ofstream outFile(outputPath);
    if (!outFile.is_open())
    {
        std::cerr << "Error: Could not open " << outputPath
                   << " for writing!" << std::endl;
        return;
    }

    // maxEvents <= 0 means "print every entry in the tree".
    Long64_t nEntries = tree_->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;

    outFile << "Event | " << branchName << std::endl;
    for (Long64_t i = 0; i < limit; ++i)
    {
        tree_->GetEntry(i);
        outFile << "Event " << i << " | " << branchName << "=" << value << std::endl;
    }

    outFile.close();
    std::cout << "Saved " << limit << " events to " << outputPath << std::endl;
}

// ============================================================
// Print a "counted array" pattern: one Int_t branch giving the number
// of objects in the event (e.g. nTau), two Float_t array branches
// holding one value per object (e.g. Tau_pt, Tau_eta), and one extra
// per-event scalar branch (e.g. MET_pt). All branch names, the array
// capacity, the event count and the output path are supplied by the
// caller — nothing here is tied to a specific ntuple layout.
// ============================================================

void ColumnPrinter::printCountedArrayBranches(const std::string &countBranch,
                                               const std::string &arrayBranch1,
                                               const std::string &arrayBranch2,
                                               const std::string &extraScalarBranch,
                                               Int_t maxArraySize,
                                               Long64_t maxEvents,
                                               const std::string &outputPath) const
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot print branches. TTree pointer is null."
                   << std::endl;
        return;
    }

    Int_t count = 0;
    Float_t extraScalar = 0.0;
    // Sized at runtime from the caller-supplied maxArraySize instead of
    // a hardcoded constant.
    std::vector<Float_t> array1(maxArraySize);
    std::vector<Float_t> array2(maxArraySize);

    tree_->SetBranchAddress(countBranch.c_str(), &count);
    tree_->SetBranchAddress(arrayBranch1.c_str(), array1.data());
    tree_->SetBranchAddress(arrayBranch2.c_str(), array2.data());
    tree_->SetBranchAddress(extraScalarBranch.c_str(), &extraScalar);

    std::ofstream outFile(outputPath);
    if (!outFile.is_open())
    {
        std::cerr << "Error: Could not open " << outputPath
                   << " for writing!" << std::endl;
        return;
    }

    // maxEvents <= 0 means "print every entry in the tree".
    Long64_t nEntries = tree_->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;

    outFile << "Event | " << countBranch << " | " << extraScalarBranch
            << " | " << arrayBranch1 << ", " << arrayBranch2 << std::endl;

    for (Long64_t i = 0; i < limit; ++i)
    {
        tree_->GetEntry(i);
        outFile << "Event " << i << " | " << countBranch << "=" << count
                << " | " << extraScalarBranch << "=" << extraScalar << " | ";

        // Guard against a count larger than the buffer we allocated.
        Int_t objectsToPrint = std::min(count, maxArraySize);
        for (Int_t t = 0; t < objectsToPrint; ++t)
        {
            outFile << "[#" << t << " " << arrayBranch1 << ": " << array1[t]
                    << ", " << arrayBranch2 << ": " << array2[t] << "] ";
        }
        outFile << std::endl;
    }

    outFile.close();
    std::cout << "Saved " << limit << " events to " << outputPath << std::endl;
}
