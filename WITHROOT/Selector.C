#include "Selector.h"

#include <algorithm>
#include <iostream>

#include "TFile.h"
#include "TH1F.h"
#include "TTreeFormula.h"

// ============================================================
// Constructor: just stores the TTree pointer we'll read from.
// ============================================================
Selector::Selector(TTree *tree)
    : tree_(tree)
{
    if (!tree_)
    {
        std::cerr << "Error: Selector received a null TTree pointer."
                  << std::endl;
    }
}

// ============================================================
// Fill and save a histogram of varExpr, restricted to entries/objects
// passing cutExpression (empty string means no cut). Mirrors what
// Events->Draw(varExpr, cutExpression) does interactively: both
// expressions are evaluated with TTreeFormula, which transparently
// handles scalar branches (one value per event) and per-object array
// branches (one value per object per event) through the same
// GetNdata()/EvalInstance() loop — no hardcoded array size needed.
// ============================================================
void Selector::plot(const std::string &varExpr,
                     const std::string &cutExpression,
                     const std::string &histName,
                     Int_t nBins,
                     Double_t xMin,
                     Double_t xMax,
                     Long64_t maxEvents,
                     const std::string &outputPath) const
{
    if (!tree_)
    {
        std::cerr << "Error: Cannot plot selection. TTree pointer is null."
                   << std::endl;
        return;
    }

    TTreeFormula varFormula("varFormula", varExpr.c_str(), tree_);
    TTreeFormula *cutFormula = nullptr;
    if (!cutExpression.empty())
    {
        cutFormula = new TTreeFormula("cutFormula", cutExpression.c_str(), tree_);
    }

    TH1F hist(histName.c_str(), varExpr.c_str(), nBins, xMin, xMax);

    // maxEvents <= 0 means "use every entry in the tree".
    Long64_t nEntries = tree_->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;

    for (Long64_t i = 0; i < limit; ++i)
    {
        tree_->GetEntry(i);

        Int_t varNData = varFormula.GetNdata();
        Int_t cutNData = cutFormula ? cutFormula->GetNdata() : 1;

        // Matches TTree::Draw's broadcasting: a scalar (Ndata==1) side
        // (e.g. "nTau") is re-evaluated at every index of the array
        // side (e.g. "Tau_pt>=20"), so a scalar var plotted under a
        // per-object cut still gets filled once per object passing the
        // cut, not just once per event.
        Int_t nData = std::max(varNData, cutNData);
        for (Int_t j = 0; j < nData; ++j)
        {
            if (cutFormula)
            {
                Int_t cutIdx = (cutNData > 1) ? j : 0;
                if (cutFormula->EvalInstance(cutIdx) == 0)
                {
                    continue;
                }
            }
            Int_t varIdx = (varNData > 1) ? j : 0;
            hist.Fill(varFormula.EvalInstance(varIdx));
        }
    }

    TFile outFile(outputPath.c_str(), "UPDATE");
    if (outFile.IsZombie())
    {
        std::cerr << "Error: Could not open " << outputPath
                   << " for writing!" << std::endl;
        delete cutFormula;
        return;
    }
    hist.Write();
    outFile.Close();

    delete cutFormula;

    std::cout << "Saved histogram '" << histName << "' (" << hist.GetEntries()
              << " entries passing selection) from " << limit
              << " events to " << outputPath << std::endl;
}

// ============================================================
// Fill one histogram per cut (same binning), all into outputPath, so
// the caller can overlay them afterwards to compare how progressively
// tighter/different selections reshape the distribution of varExpr —
// the actual "test a hypothesis" step.
// ============================================================
void Selector::plotOverlay(const std::string &varExpr,
                            const std::vector<Cut> &cuts,
                            const std::string &histNamePrefix,
                            Int_t nBins,
                            Double_t xMin,
                            Double_t xMax,
                            Long64_t maxEvents,
                            const std::string &outputPath) const
{
    // Truncate/create the file once, then let each plot() call below
    // append (UPDATE) into it.
    TFile outFile(outputPath.c_str(), "RECREATE");
    outFile.Close();

    for (const Cut &cut : cuts)
    {
        std::string histName = histNamePrefix + "_" + cut.name;
        plot(varExpr, cut.expression, histName, nBins, xMin, xMax, maxEvents, outputPath);
    }
}
