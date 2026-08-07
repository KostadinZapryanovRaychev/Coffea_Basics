#ifndef HISTOGRAMWRITER_H
#define HISTOGRAMWRITER_H

#include <string>
#include <vector>
#include "Rtypes.h"

// Fills a TH1F from already-computed values and saves it into a .root
// file. Knows nothing about TTrees, branches, or selections — it only
// turns numbers into a histogram on disk.
//
// Kept separate from Selector (which decides which values survive a
// cut) and BranchPlotter (which reads raw branch values off a TTree)
// so that "get the numbers" and "draw the numbers" stay independent:
// both of those classes hand their output here instead of building
// and writing histograms themselves.
class HistogramWriter
{
public:
    // Fill a TH1F named histName from values, then write it into
    // outputPath. mode is the TFile open mode: "RECREATE" to create/
    // truncate outputPath, "UPDATE" to append into an existing file
    // (e.g. when saving several cuts of the same variable side by
    // side for a later overlay).
    static void write(const std::vector<Double_t> &values,
                       const std::string &histName,
                       Int_t nBins,
                       Double_t xMin,
                       Double_t xMax,
                       const std::string &outputPath,
                       const std::string &mode = "RECREATE");
};

#endif
