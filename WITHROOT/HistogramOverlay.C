#include "HistogramOverlay.h"

#include <iostream>

#include "TFile.h"
#include "TH1.h"
#include "TCanvas.h"
#include "TLegend.h"

// ============================================================
// Open inputPath, pull each named histogram out of it, give each one
// a distinct color, draw them all on one canvas ("HIST" then "HIST
// SAME" for the rest), add a legend, then write the canvas itself
// back into a ROOT file (outputPath, or inputPath if not given) as a
// TCanvas object instead of flattening it to a PNG.
// ============================================================
void HistogramOverlay::overlay(const std::string &inputPath,
                                const std::vector<std::string> &histNames,
                                const std::vector<std::string> &legendLabels,
                                const std::string &canvasTitle,
                                const std::string &canvasName,
                                const std::string &outputPath,
                                const std::string &mode)
{
    if (histNames.empty())
    {
        std::cerr << "Error: HistogramOverlay::overlay called with no histogram names." << std::endl;
        return;
    }
    if (histNames.size() != legendLabels.size())
    {
        std::cerr << "Error: histNames and legendLabels must be the same size." << std::endl;
        return;
    }

    TFile inFile(inputPath.c_str(), "READ");
    if (inFile.IsZombie())
    {
        std::cerr << "Error: Could not open " << inputPath << " for reading!" << std::endl;
        return;
    }

    // Fixed color cycle; repeats if there are more histograms than colors.
    static const Int_t colors[] = {kRed, kBlue, kGreen + 2, kMagenta, kOrange + 7, kCyan + 2, kBlack};
    static const Int_t nColors = sizeof(colors) / sizeof(colors[0]);

    Double_t globalMax = 0;
    std::vector<TH1 *> hists;
    for (const std::string &name : histNames)
    {
        TH1 *hist = dynamic_cast<TH1 *>(inFile.Get(name.c_str()));
        if (!hist)
        {
            std::cerr << "Error: Histogram '" << name << "' not found in " << inputPath << std::endl;
            continue;
        }
        hist->SetDirectory(nullptr); // detach from inFile so it survives inFile.Close()
        globalMax = std::max(globalMax, hist->GetMaximum());
        hists.push_back(hist);
    }
    inFile.Close();

    if (hists.empty())
    {
        std::cerr << "Error: None of the requested histograms were found; nothing to overlay." << std::endl;
        return;
    }

    TCanvas canvas(canvasName.c_str(), canvasTitle.c_str(), 800, 600);
    TLegend legend(0.65, 0.65, 0.88, 0.88);

    for (size_t i = 0; i < hists.size(); ++i)
    {
        TH1 *hist = hists[i];
        Int_t color = colors[i % nColors];
        hist->SetLineColor(color);
        hist->SetLineWidth(2);
        hist->SetMaximum(globalMax * 1.1);
        hist->SetTitle(canvasTitle.c_str());

        hist->Draw(i == 0 ? "HIST" : "HIST SAME");
        legend.AddEntry(hist, legendLabels[i].c_str(), "l");
    }

    legend.Draw();

    const std::string &resolvedOutputPath = outputPath.empty() ? inputPath : outputPath;
    TFile outFile(resolvedOutputPath.c_str(), mode.c_str());
    if (outFile.IsZombie())
    {
        std::cerr << "Error: Could not open " << resolvedOutputPath << " for writing!" << std::endl;
    }
    else
    {
        canvas.Write();
        outFile.Close();
        std::cout << "Saved overlay canvas '" << canvasName << "' (" << hists.size()
                  << " histogram(s)) to " << resolvedOutputPath << std::endl;
    }

    for (TH1 *hist : hists)
    {
        delete hist;
    }
}
