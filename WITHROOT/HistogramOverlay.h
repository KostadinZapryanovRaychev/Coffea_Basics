#ifndef HISTOGRAMOVERLAY_H
#define HISTOGRAMOVERLAY_H

#include <string>
#include <vector>
#include "Rtypes.h"

// Reads several already-saved histograms back out of one ROOT file
// (e.g. the different h_Tau_pt_*/h_Muon_pt_*/h_Electron_pt_* produced
// by HistogramWriter for each cut) and draws them on a single canvas,
// each in a different color with a legend, so the differences between
// them are visible at a glance. The canvas itself is saved back as a
// TCanvas object inside a ROOT file (so it can be reopened with
// TBrowser and re-drawn, panned/zoomed, colors inspected, etc.),
// instead of a flattened PNG.
//
// This is the "put one histogram over the other" step: HistogramWriter
// only knows how to turn numbers into a histogram on disk; this class
// only knows how to take histograms already on disk and overlay them.
class HistogramOverlay
{
public:
    // inputPath: the .root file containing all the histograms (e.g.
    //   "h_nTau_selection.root").
    // histNames: names of the histograms to overlay, in draw order
    //   (e.g. {"h_Tau_pt_noCut", "h_Tau_pt_tauDecayedHadronically"}).
    // legendLabels: one label per entry in histNames, shown in the
    //   legend (e.g. {"No cut", "tau_h selection"}).
    // canvasTitle: title shown on the canvas/plot.
    // canvasName: object name the canvas is saved under (e.g.
    //   "c_pt_overlay_hadronic") -- this is what you'll see/click on in
    //   a TBrowser or f->Get("c_pt_overlay_hadronic").
    // outputPath: the .root file to save the canvas into. Defaults to
    //   the same file the histograms came from, so everything -- raw
    //   histograms and overlay canvases alike -- lives in one place.
    // mode: TFile open mode for outputPath ("UPDATE" appends without
    //   touching what's already there; "RECREATE" would wipe it).
    static void overlay(const std::string &inputPath,
                         const std::vector<std::string> &histNames,
                         const std::vector<std::string> &legendLabels,
                         const std::string &canvasTitle,
                         const std::string &canvasName,
                         const std::string &outputPath = "",
                         const std::string &mode = "UPDATE");
};

#endif
