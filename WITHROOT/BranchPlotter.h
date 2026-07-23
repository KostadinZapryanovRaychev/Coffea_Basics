#ifndef BRANCHPLOTTER_H
#define BRANCHPLOTTER_H

#include <string>
#include <vector>
#include "TTree.h"

// Builds ROOT histograms (TH1F) from branch values on a TTree and saves
// them into a .root file. Kept separate from BranchReader (branch
// enable/disable bookkeeping) and ColumnPrinter (text-file dumps) so
// each class has a single responsibility.
//
// Nothing about a specific ntuple layout (branch names, array sizes,
// binning, event counts, output paths) is hardcoded here — everything
// is passed in by the caller so the class stays reusable for any TTree.
// No event selection/cuts are applied here; pass in an already-narrowed
// TTree (e.g. via BranchReader) if needed.
class BranchPlotter
{
public:
    BranchPlotter(TTree *tree);

    // Fill a TH1F from a single per-event scalar Float_t branch (e.g.
    // "MET_pt") and save it into outputPath (a .root file), under
    // histName. Do NOT use this for count branches (Int_t, e.g. "nTau")
    // or per-object array branches (e.g. "Tau_pt") — use
    // plotCountedArrayBranch for those instead.
    void plotSingleBranch(const std::string &branchName,
                          const std::string &histName,
                          Int_t nBins,
                          Double_t xMin,
                          Double_t xMax,
                          Long64_t maxEvents,
                          const std::string &outputPath) const;

    // Fill a TH1F from a single per-event scalar Int_t branch (e.g.
    // "nTau") and save it into outputPath, under histName.
    void plotIntBranch(const std::string &branchName,
                       const std::string &histName,
                       Int_t nBins,
                       Double_t xMin,
                       Double_t xMax,
                       Long64_t maxEvents,
                       const std::string &outputPath) const;

    // Fill a TH1F from a per-object Float_t array branch (e.g. "Tau_pt"),
    // using countBranch (e.g. "nTau") to know how many of the
    // maxArraySize slots are valid per event. Every object across every
    // event is filled into the same histogram. Save it into outputPath,
    // under histName.
    void plotCountedArrayBranch(const std::string &countBranch,
                                const std::string &arrayBranch,
                                const std::string &histName,
                                Int_t maxArraySize,
                                Int_t nBins,
                                Double_t xMin,
                                Double_t xMax,
                                Long64_t maxEvents,
                                const std::string &outputPath) const;

private:
    TTree *tree_;
};

#endif
