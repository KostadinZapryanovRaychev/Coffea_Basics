#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"
#include "BranchReader.C"
#include "BranchReader.h"
#include "Selector.C"
#include "Selector.h"
#include "HistogramWriter.C"
#include "HistogramWriter.h"
#include "MassPointUtils.C"
#include "MassPointUtils.h"
#include "TauHadHadRecoMass.C"
#include "TauHadHadRecoMass.h"
#include "TauHadHadDataMass.C"
#include "TauHadHadDataMass.h"

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
    // Two tau_h tau_h m_rec modules:
    //   TauHadHadRecoMass  -- TRUTH level, uses GenVisTau. Only works on
    //                         MC (real data has no generator objects).
    //   TauHadHadDataMass  -- RECONSTRUCTED level, uses the Tau collection
    //                         + HLT trigger + full tau selection. Works on
    //                         both MC and real data (e.g. the CMS dataset
    //                         /Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD).
    // On an MC file both run, so truth m_rec and reco m_rec can be
    // compared. On real data only TauHadHadDataMass produces a meaningful
    // result -- TauHadHadRecoMass just prints "branch not found" and an
    // empty histogram, harmless.
    // ======================================================================
    TauHadHadRecoMass::run(Events, debug, maxEvents, config.inputFile);
    TauHadHadDataMass::run(Events, debug, maxEvents, config.inputFile);

    return 0;
}
