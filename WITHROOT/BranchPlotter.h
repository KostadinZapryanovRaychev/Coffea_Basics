#ifndef BRANCHPLOTTER_H
#define BRANCHPLOTTER_H

#include <string>
#include <vector>
#include "TTree.h"

// Reads branch values off a TTree and saves them as a histogram via
// HistogramWriter. Kept separate from BranchReader (branch
// enable/disable bookkeeping), ColumnPrinter (text-file dumps), and
// HistogramWriter (turning values into a TH1F on disk) so each class
// has a single responsibility: this one's job is only "get raw branch
// values off the tree".
//
// Nothing about a specific ntuple layout (branch names, array sizes,
// binning, event counts, output paths) is hardcoded here — everything
// is passed in by the caller so the class stays reusable for any TTree.
// No event selection/cuts are applied here; use Selector for that,
// and feed its output to HistogramWriter directly instead.
class BranchPlotter
{
public:
    BranchPlotter(TTree *tree);

    // Read a single per-event scalar Float_t branch (e.g. "MET_pt")
    // and save it into outputPath (a .root file), under histName. Do
    // NOT use this for count branches (Int_t, e.g. "nTau") or
    // per-object array branches (e.g. "Tau_pt") — use
    // plotCountedArrayBranch for those instead.
    void plotSingleBranch(const std::string &branchName,
                          const std::string &histName,
                          Int_t nBins,
                          Double_t xMin,
                          Double_t xMax,
                          Long64_t maxEvents,
                          const std::string &outputPath) const;

    // Read a single per-event scalar Int_t branch (e.g. "nTau") and
    // save it into outputPath, under histName.
    void plotIntBranch(const std::string &branchName,
                       const std::string &histName,
                       Int_t nBins,
                       Double_t xMin,
                       Double_t xMax,
                       Long64_t maxEvents,
                       const std::string &outputPath) const;

    // Read a per-object Float_t array branch (e.g. "Tau_pt"), using
    // countBranch (e.g. "nTau") to know how many of the maxArraySize
    // slots are valid per event. Every object across every event is
    // saved into the same histogram, under histName, into outputPath.
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
