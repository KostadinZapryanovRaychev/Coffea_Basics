#include "HistogramWriter.h"

#include <iostream>

#include "TFile.h"
#include "TH1F.h"

// ============================================================
// Fill a TH1F from values and write it into outputPath. No TTree, no
// branches, no cuts — just numbers in, histogram-on-disk out.
// ============================================================
void HistogramWriter::write(const std::vector<Double_t> &values,
                             const std::string &histName,
                             Int_t nBins,
                             Double_t xMin,
                             Double_t xMax,
                             const std::string &outputPath,
                             const std::string &mode)
{
    TH1F hist(histName.c_str(), histName.c_str(), nBins, xMin, xMax);
    for (Double_t value : values)
    {
        hist.Fill(value);
    }

    TFile outFile(outputPath.c_str(), mode.c_str());
    if (outFile.IsZombie())
    {
        std::cerr << "Error: Could not open " << outputPath
                   << " for writing!" << std::endl;
        return;
    }
    hist.Write();
    outFile.Close();

    std::cout << "Saved histogram '" << histName << "' (" << hist.GetEntries()
               << " entries) to " << outputPath << std::endl;
}
