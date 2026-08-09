#include <fstream>
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

    // Use all events in the file.
    const Long64_t maxEvents = Events->GetEntries();
    const Int_t tauArraySize = 32; // NanoAOD array capacity for Tau_* branches in this file. TODO to be checked further why it is needed

    // ======================================================================
    // 1. BRANCH ENABLING
    // BranchReader only manages which branches are active on the tree(disables everything, then re - enables the ones we pass in).
    // For optimization purposes in order to run faster
    // ======================================================================
    BranchReader reader(Events);
    reader.enableBranches({"nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_dz", "Tau_idDeepTau2017v2p1VSjet",
                           "Tau_idDeepTau2018v2p5VSjet",
                           "GenPart_pt", "GenPart_pdgId", "GenPart_status"});

    // create an instance of printer that is for debugging purposes
    // one if to be added for debugging
    ColumnPrinter printer(Events);

    // print info just for informative purposes
    if (debug)
    {
        printer.printIntBranch("nTau", maxEvents, "nTau_column.txt");

        printer.printCountedArrayBranches("nTau", {"Tau_pt"}, tauArraySize, maxEvents, "Tau_pt_column.txt");
        printer.printCountedArrayBranches("nTau", {"Tau_eta"}, tauArraySize, maxEvents, "Tau_eta_column.txt");
        printer.printCountedArrayBranches("nTau", {"Tau_phi"}, tauArraySize, maxEvents, "Tau_phi_column.txt");
        printer.printCountedArrayBranches("nTau", {"Tau_mass"}, tauArraySize, maxEvents, "Tau_mass_column.txt");

        // Tau_idDeepTau2017v2p1VSjet is stored as UChar_t, not Float_t, so
        printer.printCountedUCharArrayBranch("nTau", "Tau_idDeepTau2017v2p1VSjet",
                                             tauArraySize, maxEvents,
                                             "Tau_idDeepTau2017v2p1VSjet_column.txt");

        // Same branch again, but for the first 50 events, into its own file.
        printer.printCountedUCharArrayBranch("nTau", "Tau_idDeepTau2017v2p1VSjet",
                                             tauArraySize, 50,
                                             "Tau_idDeepTau2017v2p1VSjet_column_50.txt");
    }

    // ======================================================================
    // 2. SELECTIONS
    // Selector is a class that can filter events based on branch values, and return the values of a branch for the selected events.

    // TODO: to bechecked the following situations
    // A branch that doesn't exist
    // A valid branch but wrong type
    // A valid expression that is logically wrong
    // A valid expression that is syntactically complex
    // we are parsing the expression
    // ======================================================================
    Selector selector(Events);

    // here we put 3 types of selections in a shape of key value pairs in a vector and further they will be used to select the events.
    // The first one is no cut, the second one is tightVSjet and the third one is tightVSjetAndPt20
    // very important notion here could be added as much as needed cuts just making this object tauCuts bigger adding more conditions like previous {}
    // we can put expressions like that with more complicated logic {"example1", "sin(Tau_phi) > 0.5"}
    // README selection for reconstructed taus:
    // "Use reconstructed taus with pT > 20 GeV, |eta| < 2.5, |dz| < 0.2."
    std::vector<Cut> tauCuts = {
        {"noCut", ""},
        {"recoTauSelection", "Tau_pt > 20 && abs(Tau_eta) < 2.5 && abs(Tau_dz) < 0.2"},
        {"recoTauSelectionPt80to150", "Tau_pt > 80 && Tau_pt < 150 && abs(Tau_eta) < 2.5 && abs(Tau_dz) < 0.2"},
    };

    // ======================================================================
    // 3. PLOTTING into a single root file per  std::vector<Cut> created

    // One histogram per cut, all saved into the same file so they can
    // be overlaid afterwards: selector.select() does the filtering,
    // HistogramWriter::write() does the plotting — first cut
    // (re)creates the file, the rest append (UPDATE) into it.
    //
    // Each histogram is "how many taus per event pass this cut", one
    // entry per event (not per tau), so it's directly comparable to
    // "noCut" and its entry count always equals maxEvents:
    //   - noCut:   var = "nTau"                 -> raw tau multiplicity
    //   - a cut:   var = "Sum$(cutExpression)"   -> passing-tau count per event
    // Sum$ is a TTreeFormula/TTree::Draw builtin that sums a per-object
    // boolean expression over all objects in the event, collapsing it
    // to a single scalar per event, exactly the "how many taus pass"
    // question we want here. We pass "" as the cut to select() itself
    // so every event contributes one entry (including the "0 taus
    // passed" events), giving the full per-event distribution.
    for (size_t i = 0; i < tauCuts.size(); ++i)
    {
        const Cut &cut = tauCuts[i];
        std::string varExpr = cut.expression.empty() ? "nTau" : "Sum$(" + cut.expression + ")";
        std::vector<Double_t> values = selector.select(varExpr, "", maxEvents);
        HistogramWriter::write(values, "h_nTau_" + cut.name, 10, 0, 10,
                               "h_nTau_selection.root", i == 0 ? "RECREATE" : "UPDATE");

        // Kinematics of the individual taus that survive this cut (one
        // entry per passing tau, not per event), so we can actually
        // look at their pt/pz distributions instead of just counting
        // them. Same file, appended (UPDATE) so it never re-creates.
        // pz isn't a NanoAOD branch; it's derived from pt and eta via
        // pz = pt * sinh(eta), same as any 4-vector's longitudinal
        // momentum component.
        std::vector<Double_t> tauPt = selector.select("Tau_pt", cut.expression, maxEvents);
        HistogramWriter::write(tauPt, "h_Tau_pt_" + cut.name, 50, 0, 200,
                               "h_nTau_selection.root", "UPDATE");

        std::vector<Double_t> tauPz = selector.select("Tau_pt*sinh(Tau_eta)", cut.expression, maxEvents);
        HistogramWriter::write(tauPz, "h_Tau_pz_" + cut.name, 50, -500, 500,
                               "h_nTau_selection.root", "UPDATE");

        // Event-level view: how many *events* (not taus) have at least
        // one tau passing this cut, and which ones (their entry index
        // in Events, i.e. the event id since we read in order).
        if (!cut.expression.empty())
        {
            std::vector<Long64_t> eventIndices = selector.selectEventIndices(cut.expression, maxEvents);
            std::cout << "Cut '" << cut.name << "': " << eventIndices.size()
                      << " / " << maxEvents << " events have >=1 tau passing." << std::endl;

            std::ofstream idFile("event_ids_" + cut.name + ".txt");
            for (Long64_t evId : eventIndices)
            {
                idFile << evId << "\n";
            }
        }
    }

    // THIS WILL BE THE END SO FAR and MUCH STUFF WILL BE TESTED TILL THERE

    // TODO to be double checked the entries are not correct
    // TODO tau pog (physics object group) selection
    // TODO to read this https://twiki.cern.ch/twiki/bin/viewauth/CMS/Tau?extralog=-%20caching%20topic
    // TODO from reconstruted events to be applied this selection in new class
    // TODO skip all the events where one tau pass this selection ( one tau to do it) leave the events
    // TODO to answer how much tau leptons can handle this selection
    // TODO in one root file to be saved all the histograms

    // Alternativly we can do this selection To be tested
    // std::vector<Cut> tauCuts = {
    //     {"noCut", ""},
    //     {"tightVSjet", "Tau_idDeepTau2018v2p5VSjet >= 3"},
    //     {"tightVSjetAndPt20", "Tau_idDeepTau2018v2p5VSjet >= 3 && Tau_pt >= 20"},
    //     {"highPt", "Tau_pt >= 50"},
    //     {"centralTau", "abs(Tau_eta) < 2.3"},
    //     {"highPtCentral", "Tau_pt >= 50 && abs(Tau_eta) < 2.3"},
    // };

    // for (size_t i = 0; i < tauCuts.size(); ++i) {
    //     const Cut &cut = tauCuts[i];
    //     std::vector<Double_t> values = selector.select("Tau_pt", cut.expression, maxEvents);
    //     HistogramWriter::write(values, "h_Tau_pt_" + cut.name, 50, 0, 200,
    //                             "h_Tau_pt_selection.root", i == 0 ? "RECREATE" : "UPDATE");
    // }

    return 0;
}
