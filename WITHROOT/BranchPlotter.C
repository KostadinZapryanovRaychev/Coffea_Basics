#include "BranchPlotter.h"

#include <algorithm>
#include <iostream>
#include <vector>

#include "TFile.h"
#include "TH1F.h"

// ============================================================
// Constructor: just stores the TTree pointer we'll read from.
// ============================================================
BranchPlotter::BranchPlotter(TTree *tree)
    : tree_(tree)
{
    if (!tree_)
    {
        std::cerr << "Error: BranchPlotter received a null TTree pointer."
                  << std::endl;
    }
}

// ============================================================
// Fill and save a histogram of a single scalar Float_t branch.
// branchName / histName / binning / maxEvents / outputPath are all
// supplied by the caller, so this method makes no assumption about
// which branch it plots.
// ============================================================

void BranchPlotter::plotSingleBranch(const std::string &branchName,
                                      const std::string &histName,
                                      Int_t nBins,
                                      Double_t xMin,
                                      Double_t xMax,
                                      Long64_t maxEvents,
                                      const std::string &outputPath) const
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot plot branch. TTree pointer is null."
                   << std::endl;
        return;
    }

    Float_t value = 0.0;
    tree_->SetBranchAddress(branchName.c_str(), &value);

    TH1F hist(histName.c_str(), branchName.c_str(), nBins, xMin, xMax);

    // maxEvents <= 0 means "fill from every entry in the tree".
    Long64_t nEntries = tree_->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;

    for (Long64_t i = 0; i < limit; ++i)
    {
        tree_->GetEntry(i);
        hist.Fill(value);
    }

    TFile outFile(outputPath.c_str(), "RECREATE");
    if (outFile.IsZombie())
    {
        std::cerr << "Error: Could not open " << outputPath
                   << " for writing!" << std::endl;
        return;
    }
    hist.Write();
    outFile.Close();

    // Branch address bound above points at a local that is about to go
    // out of scope. Without this, the TTree keeps that dangling pointer
    // registered and the next GetEntry() call anywhere (by this class
    // or another) writes into freed memory.
    tree_->ResetBranchAddresses();

    std::cout << "Saved histogram '" << histName << "' from " << limit
              << " events to " << outputPath << std::endl;
}

// ============================================================
// Fill and save a histogram of a single scalar Int_t branch (e.g.
// nTau on its own). Kept separate from plotSingleBranch because that
// one binds a Float_t address and would misread an Int_t branch.
// ============================================================

void BranchPlotter::plotIntBranch(const std::string &branchName,
                                   const std::string &histName,
                                   Int_t nBins,
                                   Double_t xMin,
                                   Double_t xMax,
                                   Long64_t maxEvents,
                                   const std::string &outputPath) const
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot plot branch. TTree pointer is null."
                   << std::endl;
        return;
    }

    Int_t value = 0;
    tree_->SetBranchAddress(branchName.c_str(), &value);

    TH1F hist(histName.c_str(), branchName.c_str(), nBins, xMin, xMax);

    // maxEvents <= 0 means "fill from every entry in the tree".
    Long64_t nEntries = tree_->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;

    for (Long64_t i = 0; i < limit; ++i)
    {
        tree_->GetEntry(i);
        hist.Fill(value);
    }

    TFile outFile(outputPath.c_str(), "RECREATE");
    if (outFile.IsZombie())
    {
        std::cerr << "Error: Could not open " << outputPath
                   << " for writing!" << std::endl;
        return;
    }
    hist.Write();
    outFile.Close();

    // See plotSingleBranch: without this, the address bound above to a
    // local stays registered on the TTree after it goes out of scope,
    // and the next GetEntry() anywhere writes into freed memory.
    tree_->ResetBranchAddresses();

    std::cout << "Saved histogram '" << histName << "' from " << limit
              << " events to " << outputPath << std::endl;
}

// ============================================================
// Fill and save a histogram of a "counted array" branch: one Int_t
// branch giving the number of objects in the event (e.g. nTau), and one
// Float_t array branch holding one value per object (e.g. Tau_pt).
// Every object across every event is filled into the same histogram.
// All branch names, the array capacity, binning, event count and the
// output path are supplied by the caller — nothing here is tied to a
// specific ntuple layout.
// ============================================================

void BranchPlotter::plotCountedArrayBranch(const std::string &countBranch,
                                            const std::string &arrayBranch,
                                            const std::string &histName,
                                            Int_t maxArraySize,
                                            Int_t nBins,
                                            Double_t xMin,
                                            Double_t xMax,
                                            Long64_t maxEvents,
                                            const std::string &outputPath) const
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot plot branches. TTree pointer is null."
                   << std::endl;
        return;
    }

    Int_t count = 0;
    tree_->SetBranchAddress(countBranch.c_str(), &count);

    // Sized at runtime from the caller-supplied maxArraySize.
    std::vector<Float_t> buffer(maxArraySize);
    tree_->SetBranchAddress(arrayBranch.c_str(), buffer.data());

    TH1F hist(histName.c_str(), arrayBranch.c_str(), nBins, xMin, xMax);

    // maxEvents <= 0 means "fill from every entry in the tree".
    Long64_t nEntries = tree_->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;

    for (Long64_t i = 0; i < limit; ++i)
    {
        tree_->GetEntry(i);

        // Guard against a count larger than the buffer we allocated.
        Int_t objectsToFill = std::min(count, maxArraySize);
        for (Int_t t = 0; t < objectsToFill; ++t)
        {
            hist.Fill(buffer[t]);
        }
    }

    TFile outFile(outputPath.c_str(), "RECREATE");
    if (outFile.IsZombie())
    {
        std::cerr << "Error: Could not open " << outputPath
                   << " for writing!" << std::endl;
        return;
    }
    hist.Write();
    outFile.Close();

    // See plotSingleBranch: without this, the addresses bound above to
    // locals (count + array buffer) stay registered on the TTree after
    // they go out of scope, and the next GetEntry() anywhere writes
    // into freed memory.
    tree_->ResetBranchAddresses();

    std::cout << "Saved histogram '" << histName << "' from " << limit
              << " events to " << outputPath << std::endl;
}
