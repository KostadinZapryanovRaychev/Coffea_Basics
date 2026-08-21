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
#include "HistogramOverlay.C"
#include "HistogramOverlay.h"

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
    const Int_t tauArraySize = 32; // NanoAOD array capacity for Tau_* branches in this file. TODO to be checked further why it is needed

    // ======================================================================
    // 1. BRANCH ENABLING
    // BranchReader only manages which branches are active on the tree(disables everything, then re - enables the ones we pass in).
    // For optimization purposes in order to run faster
    // ======================================================================
    BranchReader reader(Events);
    reader.enableBranches({"nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_dz", "Tau_idDeepTau2017v2p1VSjet",
                           "Tau_idDeepTau2018v2p5VSjet", "Tau_idDeepTau2018v2p5VSmu", "Tau_idDeepTau2018v2p5VSe",
                           "nElectron", "Electron_pt", "Electron_eta", "Electron_cutBased",
                           "nMuon", "Muon_pt", "Muon_eta", "Muon_tightId", "Muon_pfRelIso04_all",
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

        // VSmu/VSe raw WP values for the first 50 events, so the WP
        // encoding assumed by tauDecayedHadronically below (VSjet: 1..8,
        // VSmu: 1..4, VSe: 1..8) can be checked against this NanoAOD
        // production before trusting the cut on real data.
        printer.printCountedUCharArrayBranch("nTau", "Tau_idDeepTau2018v2p5VSjet",
                                             tauArraySize, 50,
                                             "Tau_idDeepTau2018v2p5VSjet_column_50.txt");
        printer.printCountedUCharArrayBranch("nTau", "Tau_idDeepTau2018v2p5VSmu",
                                             tauArraySize, 50,
                                             "Tau_idDeepTau2018v2p5VSmu_column_50.txt");
        printer.printCountedUCharArrayBranch("nTau", "Tau_idDeepTau2018v2p5VSe",
                                             tauArraySize, 50,
                                             "Tau_idDeepTau2018v2p5VSe_column_50.txt");
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

    // Three independent selections, one per tau decay channel, each its own
    // vector processed by identical code below, so they're easy to check
    // side by side. Cuts follow the CMS Z'->tautau search
    // (arXiv:2412.04357 / PRD 111, 112004), Sec. 6.1-6.3.
    //
    // WP encodings for the DeepTau branches below (verify against
    // Tau_idDeepTau2018v2p5VS{jet,mu,e}_column_50.txt from a DEBUG=1 run
    // before trusting this on real data):
    //   VSjet: 1=VVVLoose .. 6=Tight .. 8=VVTight
    //   VSmu:  1=VLoose, 2=Loose, 3=Medium, 4=Tight
    //   VSe:   1=VVVLoose .. 5=Medium .. 8=VVTight

    // 1) tau decayed hadronically (tau_h), Sec. 6.3 tau_h tau_h SR:
    // pT > 70 GeV (trigger turn-on), |eta| < 2.1, DeepTau tight-vs-jet,
    // tight-vs-muon, medium-vs-electron.
    std::vector<Cut> hadronicTauCuts = {
        {"noCut", ""},
        {"tauDecayedHadronically", "Tau_pt > 70 && abs(Tau_eta) < 2.1 && abs(Tau_dz) < 0.2 "
                                   "&& Tau_idDeepTau2018v2p5VSjet >= 6 "
                                   "&& Tau_idDeepTau2018v2p5VSmu >= 4 "
                                   "&& Tau_idDeepTau2018v2p5VSe >= 5"},
    };

    // 2) tau decayed muonically (tau -> mu nu nu), Sec. 6.1 tau_mu leg:
    // pT > 35 GeV, |eta| < 2.1, tight muon ID, relative isolation < 0.15.
    std::vector<Cut> muonicTauCuts = {
        {"noCut", ""},
        {"tauDecayedMuonically", "Muon_pt > 35 && abs(Muon_eta) < 2.1 "
                                 "&& Muon_tightId == 1 && Muon_pfRelIso04_all < 0.15"},
    };

    // 3) tau decayed electronically (tau -> e nu nu), Sec. 6.2 tau_e leg:
    // pT > 35 GeV, |eta| < 2.1 excluding the barrel-endcap transition
    // 1.44 < |eta| < 1.57, tight cut-based electron ID (approximating the
    // paper's HEEP ID, which may not be available in this NanoAOD production).
    std::vector<Cut> electronicTauCuts = {
        {"noCut", ""},
        {"tauDecayedElectronically", "Electron_pt > 35 && abs(Electron_eta) < 2.1 "
                                     "&& !(abs(Electron_eta) > 1.44 && abs(Electron_eta) < 1.57) "
                                     "&& Electron_cutBased >= 4"},
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
    for (size_t i = 0; i < hadronicTauCuts.size(); ++i)
    {
        const Cut &cut = hadronicTauCuts[i];
        std::string varExpr = cut.expression.empty() ? "nTau" : "Sum$(" + cut.expression + ")";
        std::vector<Double_t> values = selector.select(varExpr, "", maxEvents);
        HistogramWriter::write(values, "h_nTau_" + cut.name, 10, 0, 10,
                               "h_nTau_selection.root", i == 0 ? "RECREATE" : "UPDATE");

        std::vector<Double_t> tauPt = selector.select("Tau_pt", cut.expression, maxEvents);
        HistogramWriter::write(tauPt, "h_Tau_pt_" + cut.name, 50, 0, 200,
                               "h_nTau_selection.root", "UPDATE");

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

    // ---- 2) tau decayed muonically: same code as above, on Muon_* ----
    for (size_t i = 0; i < muonicTauCuts.size(); ++i)
    {
        const Cut &cut = muonicTauCuts[i];
        std::string varExpr = cut.expression.empty() ? "nMuon" : "Sum$(" + cut.expression + ")";
        std::vector<Double_t> values = selector.select(varExpr, "", maxEvents);
        HistogramWriter::write(values, "h_nMuon_" + cut.name, 10, 0, 10,
                               "h_nTau_selection.root", "UPDATE");

        std::vector<Double_t> muonPt = selector.select("Muon_pt", cut.expression, maxEvents);
        HistogramWriter::write(muonPt, "h_Muon_pt_" + cut.name, 50, 0, 200,
                               "h_nTau_selection.root", "UPDATE");

        if (!cut.expression.empty())
        {
            std::vector<Long64_t> eventIndices = selector.selectEventIndices(cut.expression, maxEvents);
            std::cout << "Cut '" << cut.name << "': " << eventIndices.size()
                      << " / " << maxEvents << " events have >=1 muon passing." << std::endl;

            std::ofstream idFile("event_ids_" + cut.name + ".txt");
            for (Long64_t evId : eventIndices)
            {
                idFile << evId << "\n";
            }
        }
    }

    // ---- 3) tau decayed electronically: same code again, on Electron_* ----
    for (size_t i = 0; i < electronicTauCuts.size(); ++i)
    {
        const Cut &cut = electronicTauCuts[i];
        std::string varExpr = cut.expression.empty() ? "nElectron" : "Sum$(" + cut.expression + ")";
        std::vector<Double_t> values = selector.select(varExpr, "", maxEvents);
        HistogramWriter::write(values, "h_nElectron_" + cut.name, 10, 0, 10,
                               "h_nTau_selection.root", "UPDATE");

        std::vector<Double_t> electronPt = selector.select("Electron_pt", cut.expression, maxEvents);
        HistogramWriter::write(electronPt, "h_Electron_pt_" + cut.name, 50, 0, 200,
                               "h_nTau_selection.root", "UPDATE");

        if (!cut.expression.empty())
        {
            std::vector<Long64_t> eventIndices = selector.selectEventIndices(cut.expression, maxEvents);
            std::cout << "Cut '" << cut.name << "': " << eventIndices.size()
                      << " / " << maxEvents << " events have >=1 electron passing." << std::endl;

            std::ofstream idFile("event_ids_" + cut.name + ".txt");
            for (Long64_t evId : eventIndices)
            {
                idFile << evId << "\n";
            }
        }
    }

    // ======================================================================
    // 4. OVERLAY: put the pt distributions from each channel's cut on top
    // of "noCut" of the same channel, and separately compare the three
    // channels' selected-tau pt spectra against each other, so differences
    // are visible in one picture instead of three separate histograms.
    // Canvases are written back into h_nTau_selection.root (same file as
    // the histograms), not saved out as PNGs -- open it in a TBrowser or
    // f->Get("c_pt_overlay_hadronic") etc. to view them.
    // ======================================================================
    HistogramOverlay::overlay("h_nTau_selection.root",
                              {"h_Tau_pt_noCut", "h_Tau_pt_tauDecayedHadronically"},
                              {"No cut", "tau decayed hadronically"},
                              "Tau p_{T}: no cut vs hadronic selection",
                              "c_pt_overlay_hadronic");

    HistogramOverlay::overlay("h_nTau_selection.root",
                              {"h_Muon_pt_noCut", "h_Muon_pt_tauDecayedMuonically"},
                              {"No cut", "tau decayed muonically"},
                              "Muon p_{T}: no cut vs muonic selection",
                              "c_pt_overlay_muonic");

    HistogramOverlay::overlay("h_nTau_selection.root",
                              {"h_Electron_pt_noCut", "h_Electron_pt_tauDecayedElectronically"},
                              {"No cut", "tau decayed electronically"},
                              "Electron p_{T}: no cut vs electronic selection",
                              "c_pt_overlay_electronic");

    // Cross-channel comparison: the selected-tau pt spectra side by side.
    HistogramOverlay::overlay("h_nTau_selection.root",
                              {"h_Tau_pt_tauDecayedHadronically", "h_Muon_pt_tauDecayedMuonically",
                               "h_Electron_pt_tauDecayedElectronically"},
                              {"Hadronic (tau_h)", "Muonic (tau->mu)", "Electronic (tau->e)"},
                              "Selected tau pT by decay channel",
                              "c_pt_overlay_by_channel");

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
