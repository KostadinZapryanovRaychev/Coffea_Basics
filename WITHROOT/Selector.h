#ifndef SELECTOR_H
#define SELECTOR_H

#include <string>
#include <vector>
#include "TTree.h"

// A named boolean selection, e.g.
//   { "tightTau", "Tau_idDeepTau2018v2p5VSjet>=3 && Tau_pt>=20" }
// The expression is anything TTreeFormula/TTree::Draw accepts.
struct Cut
{
    std::string name;
    std::string expression;
};

// Builds histograms of a branch/expression under a boolean selection,
// e.g. what Events->Draw("nTau", "Tau_pt>=20") does interactively.
//
// Uses TTreeFormula (the same engine TTree::Draw uses) for both the
// plotted expression and the cut, so it needs no hardcoded branch
// names, array sizes, or per-branch type handling: scalar branches
// (nTau) and per-object array branches (Tau_pt) both work through the
// same code path, and a cut like "Tau_pt>=20" is applied per-object,
// not per-event, exactly like Draw does.
//
// Kept separate from BranchPlotter (which plots an unfiltered branch)
// so each class has a single responsibility; Selector is specifically
// about testing a hypothesis by comparing distributions with/without
// a cut applied.
class Selector
{
public:
    Selector(TTree *tree);

    // Fill a TH1F of varExpr for entries passing cutExpression, save it
    // into outputPath under histName. Pass "" for cutExpression to plot
    // with no selection (baseline).
    void plot(const std::string &varExpr,
              const std::string &cutExpression,
              const std::string &histName,
              Int_t nBins,
              Double_t xMin,
              Double_t xMax,
              Long64_t maxEvents,
              const std::string &outputPath) const;

    // Fill one histogram of varExpr per cut in cuts (same binning for
    // all), into the same outputPath, so the resulting histograms can
    // be overlaid to compare how each selection reshapes the
    // distribution. Each histogram is named "<histNamePrefix>_<cut.name>".
    void plotOverlay(const std::string &varExpr,
                      const std::vector<Cut> &cuts,
                      const std::string &histNamePrefix,
                      Int_t nBins,
                      Double_t xMin,
                      Double_t xMax,
                      Long64_t maxEvents,
                      const std::string &outputPath) const;

private:
    TTree *tree_;
};

#endif
