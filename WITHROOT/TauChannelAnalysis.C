#include "TauChannelAnalysis.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <vector>

#include "TTreeReader.h"
#include "TTreeReaderArray.h"

#include "BranchReader.h"
#include "ColumnPrinter.h"
#include "Selector.h"
#include "HistogramWriter.h"
#include "HistogramOverlay.h"
#include "MassPointUtils.h"

// Helpers for the di-tau invariant mass (section 5). Same visible-mass
// formula as TauPogMass; named namespace so nothing clashes when several
// modules are compiled together in main.C.
namespace tauch
{
    struct Tau
    {
        double pt;
        double eta;
        double phi;
        double mass;
        int charge; // -1 = tau, +1 = anti-tau

        double px() const { return pt * std::cos(phi); }
        double py() const { return pt * std::sin(phi); }
        double pz() const { return pt * std::sinh(eta); }
        double e() const { return std::sqrt(px() * px() + py() * py() + pz() * pz() + mass * mass); }
    };

    // m = sqrt[ (E1+E2)^2 - |p1+p2|^2 ]  -- visible mass, neutrinos ignored
    double invariantMass(const Tau &a, const Tau &b)
    {
        const double e = a.e() + b.e();
        const double x = a.px() + b.px();
        const double y = a.py() + b.py();
        const double z = a.pz() + b.pz();
        return std::sqrt(std::max(0.0, e * e - x * x - y * y - z * z));
    }

    // invariant mass of the leading tau of each charge,
    // or -1 if the event does not have one of each
    double ditauMass(const std::vector<Tau> &taus)
    {
        const Tau *minus = nullptr;
        const Tau *plus = nullptr;
        for (const Tau &t : taus)
        {
            if (t.charge < 0 && (minus == nullptr || t.pt > minus->pt))
            {
                minus = &t;
            }
            if (t.charge > 0 && (plus == nullptr || t.pt > plus->pt))
            {
                plus = &t;
            }
        }
        return (minus && plus) ? invariantMass(*minus, *plus) : -1.0;
    }
}

// ============================================================
// Full tau-decay-channel analysis: branch enabling -> (optional debug
// dumps) -> selections -> plotting -> overlay. See TauChannelAnalysis.h
// for why this is its own module.
// ============================================================
void TauChannelAnalysis::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                              const std::string &inputFilePath)
{
    // Scales the pt histogram ranges below to the actual Z' mass point of
    // the sample (see MassPointUtils.h) instead of a range hardcoded for
    // one specific mass. Same 0.6*M convention TauLHEKinematics and
    // TauGenParticleKinematics use for their pt ranges, so reco-level and
    // truth-level pt histograms stay visually comparable to each other.
    const Double_t M = MassPointUtils::extractMassPoint(inputFilePath);
    const Int_t ptBins = 120;
    const Double_t ptMax = 0.6 * M;

    const Int_t tauArraySize = 32; // NanoAOD array capacity for Tau_* branches in this file. TODO to be checked further why it is needed

    // ======================================================================
    // 1. BRANCH ENABLING
    // BranchReader only manages which branches are active on the tree(disables everything, then re - enables the ones we pass in).
    // For optimization purposes in order to run faster
    // ======================================================================
    BranchReader reader(Events);
    reader.enableBranches({"nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_dz", "Tau_decayMode",
                           "Tau_charge",
                           "Tau_idDeepTau2017v2p1VSjet",
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

    // 1) tau decayed hadronically (tau_h), Sec. 6.3 tau_h tau_h SR and
    // Table 56/57 of the analysis note (arXiv:2412.04357 and the CMS AN
    // behind it): pT > 70 GeV (trigger turn-on), |eta| < 2.1, DeepTau
    // tight-vs-jet, tight-vs-muon, medium-vs-electron, PLUS a decay-mode
    // (prong) filter that Table 56 lists explicitly ("Prongs: 1 or 3 hp")
    // and that the ID/kinematic cuts alone don't cover: HPS occasionally
    // emits a 2-prong candidate, which is almost always a reconstruction
    // failure (a genuine 3-prong decay that lost/merged a track) rather
    // than a real hadronic tau decay mode, since the physical hadronic
    // decays are only 1-prong (pi/K +- up to 2 pi0) or 3-prong (3 pi/K
    // +- optional pi0) -- see WITHROOT/README.md's list of hadronic decay
    // channels. NanoAOD Tau_decayMode encoding: 0 = 1-prong, 1 = 1-prong
    // + pi0, 2 = 1-prong + 2pi0, 10 = 3-prong, 11 = 3-prong + pi0.
    std::vector<Cut> hadronicTauCuts = {
        {"noCut", ""},
        {"tauDecayedHadronically", "Tau_pt > 70 && abs(Tau_eta) < 2.1 && abs(Tau_dz) < 0.2 "
                                   "&& Tau_idDeepTau2018v2p5VSjet >= 6 "
                                   "&& Tau_idDeepTau2018v2p5VSmu >= 4 "
                                   "&& Tau_idDeepTau2018v2p5VSe >= 5 "
                                   "&& (Tau_decayMode == 0 || Tau_decayMode == 1 || Tau_decayMode == 2 "
                                   "|| Tau_decayMode == 10 || Tau_decayMode == 11)"},
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
        HistogramWriter::write(tauPt, "h_Tau_pt_" + cut.name, ptBins, 0, ptMax,
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
        HistogramWriter::write(muonPt, "h_Muon_pt_" + cut.name, ptBins, 0, ptMax,
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
        HistogramWriter::write(electronPt, "h_Electron_pt_" + cut.name, ptBins, 0, ptMax,
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

    // ======================================================================
    // 5. DI-TAU INVARIANT MASS (tau_h tau_h channel)
    // Same visible-mass formula as TauPogMass: build each tau's 4-vector
    // from (pt, eta, phi, mass), take the leading tau of each charge, and
    // m = sqrt[(E1+E2)^2 - |p1+p2|^2]. One entry per event that has an
    // opposite-sign pair among the taus passing the SAME hadronic
    // selection as hadronicTauCuts["tauDecayedHadronically"] above
    // (pT > 70, |eta| < 2.1, |dz| < 0.2, DeepTau tight-jet/tight-mu/
    // medium-e, decay mode 0/1/2/10/11).
    // ======================================================================
    TTreeReader massReader(Events);
    TTreeReaderArray<Float_t> mTauPt(massReader, "Tau_pt");
    TTreeReaderArray<Float_t> mTauEta(massReader, "Tau_eta");
    TTreeReaderArray<Float_t> mTauPhi(massReader, "Tau_phi");
    TTreeReaderArray<Float_t> mTauMass(massReader, "Tau_mass");
    TTreeReaderArray<Float_t> mTauDz(massReader, "Tau_dz");
    TTreeReaderArray<Short_t> mTauCharge(massReader, "Tau_charge");
    TTreeReaderArray<UChar_t> mTauDecayMode(massReader, "Tau_decayMode");
    TTreeReaderArray<UChar_t> mTauVSjet(massReader, "Tau_idDeepTau2018v2p5VSjet");
    TTreeReaderArray<UChar_t> mTauVSmu(massReader, "Tau_idDeepTau2018v2p5VSmu");
    TTreeReaderArray<UChar_t> mTauVSe(massReader, "Tau_idDeepTau2018v2p5VSe");

    std::vector<Double_t> ditauMasses;

    while (massReader.Next())
    {
        std::vector<tauch::Tau> selected;
        for (size_t j = 0; j < mTauPt.GetSize(); ++j)
        {
            if (mTauPt[j] <= 70.0)
                continue;
            if (std::abs(mTauEta[j]) >= 2.1 || std::abs(mTauDz[j]) >= 0.2)
                continue;
            if (mTauVSjet[j] < 6 || mTauVSmu[j] < 4 || mTauVSe[j] < 5)
                continue;
            const int dm = mTauDecayMode[j];
            if (dm != 0 && dm != 1 && dm != 2 && dm != 10 && dm != 11)
                continue;
            selected.push_back({mTauPt[j], mTauEta[j], mTauPhi[j], mTauMass[j], mTauCharge[j]});
        }

        const double m = tauch::ditauMass(selected);
        if (m >= 0.0)
        {
            ditauMasses.push_back(m);
        }
    }

    std::cout << "Di-tau mass (tau_h tau_h): " << ditauMasses.size()
              << " events with an opposite-sign selected pair." << std::endl;

    HistogramWriter::write(ditauMasses, "h_ditau_mass_hadronic", 100, 0, 500,
                           "h_nTau_selection.root", "UPDATE");
}
