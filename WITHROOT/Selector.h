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

// Filters a TTree: evaluates varExpr under a boolean cutExpression and
// returns the surviving values, e.g. what
// Events->Draw("nTau", "Tau_pt>=20") does interactively, minus the
// drawing.
//
// Uses TTreeFormula (the same engine TTree::Draw uses) for both the
// selected expression and the cut, so it needs no hardcoded branch
// names, array sizes, or per-branch type handling: scalar branches
// (nTau) and per-object array branches (Tau_pt) both work through the
// same code path, and a cut like "Tau_pt>=20" is applied per-object,
// not per-event, exactly like Draw does.
//
// Selector only filters — it has no idea what a TH1F or TFile is.
// Hand its output to HistogramWriter to plot it; this keeps "which
// events/objects pass" and "how to draw them" as separate concerns.
class Selector
{
public:
    Selector(TTree *tree);

    // Returns the values of varExpr for every event/object passing
    // cutExpression. Pass "" for cutExpression to select everything
    // (no cut).
    std::vector<Double_t> select(const std::string &varExpr,
                                  const std::string &cutExpression,
                                  Long64_t maxEvents) const;

    // Event-level version: returns the tree entry index (== event id,
    // since Events is read in order) of every event that has at least
    // one object satisfying cutExpression. Unlike select(), this
    // counts events, not objects, so an event with 2 taus passing the
    // cut still contributes a single index.
    std::vector<Long64_t> selectEventIndices(const std::string &cutExpression,
                                              Long64_t maxEvents) const;

private:
    TTree *tree_;
};

#endif
