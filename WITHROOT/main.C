#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"
#include "BranchReader.C"
#include "BranchReader.h"
#include "ColumnPrinter.C"
#include "ColumnPrinter.h"
#include "BranchPlotter.C"
#include "BranchPlotter.h"
#include "Selector.C"
#include "Selector.h"
#include "HistogramWriter.C"
#include "HistogramWriter.h"
#include "HistogramOverlay.C"
#include "HistogramOverlay.h"
#include "TauChannelAnalysis.C"
#include "TauChannelAnalysis.h"
#include "TauLHEKinematics.C"
#include "TauLHEKinematics.h"
#include "TauGenParticleKinematics.C"
#include "TauGenParticleKinematics.h"

int main()
{
    // Debug mode: enable by starting the session with, e.g.
    //   DEBUG=1 root -l -q main.C
    // When off, the printer calls below are skipped entirely.
    const bool debug = (gSystem->Getenv("DEBUG") != nullptr) &&
                       (TString(gSystem->Getenv("DEBUG")) == "1");

    // Load path from here
    Config config = loadConfig("config.json");

    // Open the NanoAOD file and grab the "Events" TTree.
    TTree *Events = getEventsTree(config.inputFile);
    printEventTree(Events);

    // Dump every branch name on the Events tree to a txt file for exploration.
    listBranchNames(Events, "outputs/branch_names.txt");

    // Use all events in the file.
    const Long64_t maxEvents = Events->GetEntries();

    // ======================================================================
    // Run each analysis module in turn. Every module is a self-contained
    // .C/.h pair (branch enabling through plotting, start to finish -- see
    // TauChannelAnalysis.h for the reasoning) so main() stays a short list
    // of "run this analysis, run that analysis" instead of growing without
    // bound as more parts of the event (LHE, GenParticles, ...) get their
    // own dedicated logic.
    //
    // ======================================================================
    TauChannelAnalysis::run(Events, debug, maxEvents);
    TauLHEKinematics::run(Events, debug, maxEvents, config.inputFile);
    TauGenParticleKinematics::run(Events, debug, maxEvents, config.inputFile);

    // TODO to be double checked the entries are not correct
    // TODO tau pog (physics object group) selection
    // TODO to read this https://twiki.cern.ch/twiki/bin/viewauth/CMS/Tau?extralog=-%20caching%20topic
    // TODO skip all the events where one tau pass this selection ( one tau to do it) leave the events
    // TODO to answer how much tau leptons can handle this selection

    // pog reccomendation
    // analysis note !!! shared
    // all tau collection is from reco part
    // twiki page ( working points what other use)
    // what is reconstructed tau lepton as an object
    // space to be created many dimensions
    // https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendationForRun3#Kinematic_tau_selection
    // https://cms-alcm.web.cern.ch/notes/CMS-AN-2020-134/AN2020_134_v17.pdf - page - 27
    // tau lepton channel to read
    // too tau leptons to tau pog selection and difference between their phi and so on

    return 0;
}
