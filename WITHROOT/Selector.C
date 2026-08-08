#include "Selector.h"

#include <algorithm>
#include <iostream>

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
// Evaluate varExpr for every event, restricted to entries/objects
// passing cutExpression (empty string means no cut), and return the
// surviving values. Mirrors what Events->Draw(varExpr, cutExpression)
// does interactively, minus the drawing: both expressions are
// evaluated with TTreeFormula, which transparently handles scalar
// branches (one value per event) and per-object array branches (one
// value per object per event) through the same GetNdata()/
// EvalInstance() loop — no hardcoded array size needed.
// ============================================================

// varExpr: a string like "nTau" or "Tau_pt" or "Tau_pt*Tau_eta" or "sqrt(Tau_pt*Tau_pt + Tau_eta*Tau_eta)". what to remain
// cutExpression: a string like "Tau_pt>20" or "nTau>0 && Tau_pt>20" or "abs(Tau_eta)<2.3". empty string means no cut, i.e. all events pass
// maxEvents: maximum number of events to process. <=0 means "use every entry in the tree".
std::vector<Double_t> Selector::select(const std::string &varExpr,
                                       const std::string &cutExpression,
                                       Long64_t maxEvents) const
{
    std::vector<Double_t> selected;

    if (!tree_)
    {
        std::cerr << "Error: Cannot select. TTree pointer is null."
                  << std::endl;
        return selected;
    }

    TTreeFormula varFormula("varFormula", varExpr.c_str(), tree_);
    TTreeFormula *cutFormula = nullptr;
    if (!cutExpression.empty())
    {
        cutFormula = new TTreeFormula("cutFormula", cutExpression.c_str(), tree_);
    }

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
        // side (e.g. "Tau_pt>=20"), so a scalar var selected under a
        // per-object cut still yields one value per object passing the
        // cut, not just one per event.
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
            selected.push_back(varFormula.EvalInstance(varIdx));
        }
    }

    delete cutFormula;

    return selected;
}
