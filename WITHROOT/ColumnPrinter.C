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

    // Branch addresses bound above point at locals that are about to go
    // out of scope. Without this, the TTree keeps those dangling
    // pointers registered and the next GetEntry() call anywhere (by
    // this class or another) writes into freed memory.
    tree_->ResetBranchAddresses();

    std::cout << "Saved " << limit << " events to " << outputPath << std::endl;
}

// ============================================================
// Print a single scalar Int_t branch (e.g. nTau on its own, with no
// associated arrays). Kept separate from printSingleBranch because
// that one binds a Float_t address and would misread an Int_t branch.
// ============================================================

void ColumnPrinter::printIntBranch(const std::string &branchName,
                                    Long64_t maxEvents,
                                    const std::string &outputPath) const
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot print branch. TTree pointer is null."
                   << std::endl;
        return;
    }

    Int_t value = 0;
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

    // See printSingleBranch: without this, the address bound above to
    // a local variable stays registered on the TTree after it goes out
    // of scope, and the next GetEntry() anywhere writes into freed
    // memory.
    tree_->ResetBranchAddresses();

    std::cout << "Saved " << limit << " events to " << outputPath << std::endl;
}

// ============================================================
// Print a "counted array" pattern: one Int_t branch giving the number
// of objects in the event (e.g. nTau), and any number of Float_t array
// branches holding one value per object (e.g. Tau_pt, Tau_eta, Tau_phi,
// Tau_mass). All branch names, the array capacity, the event count and
// the output path are supplied by the caller — nothing here is tied to
// a specific ntuple layout.
// ============================================================

void ColumnPrinter::printCountedArrayBranches(const std::string &countBranch,
                                               const std::vector<std::string> &arrayBranches,
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
    tree_->SetBranchAddress(countBranch.c_str(), &count);

    // One buffer per array branch, each sized at runtime from the
    // caller-supplied maxArraySize instead of a hardcoded constant.
    std::vector<std::vector<Float_t>> buffers(arrayBranches.size());
    for (size_t b = 0; b < arrayBranches.size(); ++b)
    {
        buffers[b].resize(maxArraySize);
        tree_->SetBranchAddress(arrayBranches[b].c_str(), buffers[b].data());
    }

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

    outFile << "Event | " << countBranch;
    for (const std::string &branchName : arrayBranches)
    {
        outFile << " | " << branchName;
    }
    outFile << std::endl;

    for (Long64_t i = 0; i < limit; ++i)
    {
        tree_->GetEntry(i);
        outFile << "Event " << i << " | " << countBranch << "=" << count << " | ";

        // Guard against a count larger than the buffer we allocated.
        Int_t objectsToPrint = std::min(count, maxArraySize);
        for (Int_t t = 0; t < objectsToPrint; ++t)
        {
            outFile << "[#" << t << " ";
            for (size_t b = 0; b < arrayBranches.size(); ++b)
            {
                outFile << arrayBranches[b] << ": " << buffers[b][t];
                if (b + 1 < arrayBranches.size())
                {
                    outFile << ", ";
                }
            }
            outFile << "] ";
        }
        outFile << std::endl;
    }

    outFile.close();

    // See printSingleBranch: without this, the addresses bound above to
    // locals (count + array buffers) stay registered on the TTree after
    // they go out of scope, and the next GetEntry() anywhere writes
    // into freed memory.
    tree_->ResetBranchAddresses();

    std::cout << "Saved " << limit << " events to " << outputPath << std::endl;
}

// ============================================================
// Print a single UChar_t array branch (e.g. Tau_idDeepTau2017v2p1VSjet)
// alongside its count branch (e.g. nTau). Separate from
// printCountedArrayBranches because NanoAOD ID/flag branches use
// UChar_t storage, not Float_t.
// ============================================================

void ColumnPrinter::printCountedUCharArrayBranch(const std::string &countBranch,
                                                  const std::string &arrayBranch,
                                                  Int_t maxArraySize,
                                                  Long64_t maxEvents,
                                                  const std::string &outputPath) const
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot print branch. TTree pointer is null."
                   << std::endl;
        return;
    }

    Int_t count = 0;
    // Sized at runtime from the caller-supplied maxArraySize.
    std::vector<UChar_t> buffer(maxArraySize);

    tree_->SetBranchAddress(countBranch.c_str(), &count);
    tree_->SetBranchAddress(arrayBranch.c_str(), buffer.data());

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

    outFile << "Event | " << countBranch << " | " << arrayBranch << std::endl;
    for (Long64_t i = 0; i < limit; ++i)
    {
        tree_->GetEntry(i);
        outFile << "Event " << i << " | " << countBranch << "=" << count << " | ";

        // Guard against a count larger than the buffer we allocated.
        Int_t objectsToPrint = std::min(count, maxArraySize);
        for (Int_t t = 0; t < objectsToPrint; ++t)
        {
            // Cast to int so it prints as a number, not a char.
            outFile << "[#" << t << " " << arrayBranch << ": "
                    << static_cast<int>(buffer[t]) << "] ";
        }
        outFile << std::endl;
    }

    outFile.close();

    // See printSingleBranch: without this, the addresses bound above to
    // locals (count + buffer) stay registered on the TTree after they
    // go out of scope, and the next GetEntry() anywhere writes into
    // freed memory.
    tree_->ResetBranchAddresses();

    std::cout << "Saved " << limit << " events to " << outputPath << std::endl;
}
