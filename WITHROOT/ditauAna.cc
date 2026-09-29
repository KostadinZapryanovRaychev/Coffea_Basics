#include <algorithm>
#include <functional>
#include <iostream>
#include <string>
#include <cmath>
#include <fstream>

#include "Config.C"
#include "Config.h"

const int MAXTAU = 200;

// Turns a file path into a short, unique label for its output directory,
// e.g. ".../120000/e8393d52-174a-...root" -> "e8393d52".
TString labelFromPath(const std::string &path)
{
  std::string base = path;
  size_t slash = base.find_last_of('/');
  if (slash != std::string::npos)
  {
    base = base.substr(slash + 1);
  }
  size_t dash = base.find('-');
  if (dash != std::string::npos)
  {
    base = base.substr(0, dash);
  }
  else
  {
    size_t dot = base.find_last_of('.');
    if (dot != std::string::npos)
    {
      base = base.substr(0, dot);
    }
  }
  return TString(base.c_str());
}

void ditauAna()
{

  std::string mode;
  std::cout << "enter your preference (cut or pre-cut): ";
  std::cin >> mode;

  // every file listed in file_config_data.json, same config the other
  // WITHROOT macros in this session use.
  std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
  std::cout << rootFiles.size() << " file(s) to process." << std::endl;
  int nFiles = rootFiles.size();

  double ptCut = 30.0;
  double etaCut = 2.1;
  double metCut = 35.0;
  double cosCutLow = -0.8;
  double cosCutHigh = 1.0;

  bool applyCuts = false;
  if (mode == "cut")
  {
    applyCuts = true;

    std::cout << "enter pt cut (default = 30): ";
    std::cin >> ptCut;

    std::cout << "enter eta cut (default = 2.1): ";
    std::cin >> etaCut;

    std::cout << "enter MET pt cut (default = 35): ";
    std::cin >> metCut;

    std::cout << "enter the lower bound of cos cut (default = -0.8): ";
    std::cin >> cosCutLow;

    std::cout << "enter the higher bound of cos cut (default = 1): ";
    std::cin >> cosCutHigh;
  }
  else if (mode == "pre-cut")
  {
    applyCuts = false;
  }
  else
  {
    std::cerr << "invalid option. use only 'cut' or 'pre-cut' \n";
    return;
  }

  Int_t maxEntries;
  std::cout << "enter desired amount of entries (use -1 for entire population) \n";
  std::cin >> maxEntries;

  std::string outputFile = "my_histograms_";
  outputFile += (applyCuts ? "cut_" : "precut_");
  outputFile += "experimental_";
  outputFile += "Run2024D";
  outputFile += ".root";

  TFile *fout = new TFile(outputFile.c_str(), "RECREATE");
  cout << "output file name is: " << outputFile << endl;

  std::vector<TString> usedLabels; // guards against two files giving the same label

  for (int fileIdx = 0; fileIdx < nFiles; fileIdx++)
  {
    TString label = labelFromPath(rootFiles[fileIdx].path);
    while (std::find(usedLabels.begin(), usedLabels.end(), label) != usedLabels.end())
    {
      label += "_dup"; // two files gave the same label: keep both, make the second one distinct
    }
    usedLabels.push_back(label);
    std::cout << "[" << (fileIdx + 1) << "/" << nFiles << "] reading: "
              << rootFiles[fileIdx].path << std::endl;

    TChain *t1 = new TChain("Events");
    t1->Add(rootFiles[fileIdx].path.c_str());

    Float_t MET_pt;
    Float_t MET_phi;

    ////////////TAU BRANCHES///////////////
    Int_t nTau; // Int_t in this NanoAOD (was UInt_t)
    Float_t Tau_pt[MAXTAU];
    Float_t Tau_eta[MAXTAU];
    Float_t Tau_phi[MAXTAU];
    Float_t Tau_mass[MAXTAU];
    Short_t Tau_charge[MAXTAU]; // Short_t in this NanoAOD (was Int_t)
    UChar_t Tau_decayMode[MAXTAU];

    UChar_t Tau_idDeepTau2018v2p5VSjet[MAXTAU];
    UChar_t Tau_idDeepTau2018v2p5VSe[MAXTAU];
    UChar_t Tau_idDeepTau2018v2p5VSmu[MAXTAU];

    /////////////BRANCH ADDRESSES///////////////
    t1->SetBranchAddress("PuppiMET_pt", &MET_pt);   // transverse momentum of missing energy (PuppiMET: this file has no MET_pt)
    t1->SetBranchAddress("PuppiMET_phi", &MET_phi); // azimuthal angle of MET (PuppiMET)

    t1->SetBranchAddress("nTau", &nTau);
    t1->SetBranchAddress("Tau_pt", &Tau_pt);
    t1->SetBranchAddress("Tau_eta", &Tau_eta);
    t1->SetBranchAddress("Tau_phi", &Tau_phi);
    t1->SetBranchAddress("Tau_mass", &Tau_mass);
    t1->SetBranchAddress("Tau_charge", &Tau_charge);
    t1->SetBranchAddress("Tau_decayMode", &Tau_decayMode);
    t1->SetBranchAddress("Tau_idDeepTau2018v2p5VSjet", &Tau_idDeepTau2018v2p5VSjet);
    t1->SetBranchAddress("Tau_idDeepTau2018v2p5VSe", &Tau_idDeepTau2018v2p5VSe);
    t1->SetBranchAddress("Tau_idDeepTau2018v2p5VSmu", &Tau_idDeepTau2018v2p5VSmu);

    //////////////HISTOGRAM ANALYSIS////////////////
    /////////MET/////////////////////////
    TH1F *hMET_pt = new TH1F("hMET_pt", "MET p_{t}", 200, 0., 100.);
    TH1F *hMET_phi = new TH1F("hMET_phi", "MET #varphi", 20, -5., 5.);
    //////////////TAU HISTOGRAMS//////////////////
    TH1F *hnTau = new TH1F("nTau", "number of tau leptons", 10000, 0., 10000.);
    TH1F *hTau_eta = new TH1F("hTau_eta", "pseudorapidity of tau leptons", 50, -2.5, 2.5);
    TH1F *hTau_phi = new TH1F("hTau_phi", "azimuthal angle (BEAM AXIS)", 70, -3.5, 3.5);
    TH1F *hTau_pt = new TH1F("hTau_pt", "transverse momentum of tau events", 200, 0., 100.);
    /////////////ANALYSIS////////////////////////
    TH1F *hDitau_mass = new TH1F("hDitau_mass", "mass of di-tau events", 300, 0., 150.);
    hDitau_mass->SetYTitle("events / 0.5 [GeV/c^{2}]");
    hDitau_mass->SetXTitle("mass(#tau#tau) [GeV/c^{2}]");

    TH1F *hDitau_cosDeltaPhi = new TH1F("hDitau_cosDeltaPhi", "cos(#Delta#varphi) of di-tau events", 20, -1., 1.);
    hDitau_cosDeltaPhi->SetYTitle("events / 0.1");
    hDitau_cosDeltaPhi->SetXTitle("cos(#Delta#varphi) of di-#tau events");

    std::vector<TH1 *> histos = {
        hMET_pt, hMET_phi, hnTau,
        hTau_eta, hTau_phi, hTau_pt, hDitau_mass,
        hDitau_cosDeltaPhi};
    for (auto *h : histos)
      h->SetDirectory(0);

    Int_t nentries = t1->GetEntries();
    cout << "Number of events in the file: " << nentries << endl;

    Int_t entriesToRun = nentries;
    if (maxEntries > 0 && maxEntries < nentries)
    {
      entriesToRun = maxEntries;
    }

    cout << "entries to process: " << entriesToRun << endl;

    for (Int_t i = 0; i < entriesToRun; i++)
    {
      t1->GetEntry(i);

      hnTau->Fill(nTau);

      if (applyCuts && MET_pt > metCut)
        continue;

      std::vector<int> goodTauIdx;
      for (UInt_t tau = 0; tau < nTau; tau++)
      {
        hTau_eta->Fill(Tau_eta[tau]);
        hTau_pt->Fill(Tau_pt[tau]);
        hTau_phi->Fill(Tau_phi[tau]);

        /////
        // here the ID is the working point index (1 = VVVLoose, 2 = VVLoose, 3 = VLoose ...),
        // not a bitmask: ">= n" is the same cut as the old "bit n-1 is set".
        bool passesVSjet = Tau_idDeepTau2018v2p5VSjet[tau] >= 3; // was & (1 << 2)
        bool passesVSe = Tau_idDeepTau2018v2p5VSe[tau] >= 1;     // was & (1 << 0)
        bool passesVSmu = Tau_idDeepTau2018v2p5VSmu[tau] >= 1;   // was & (1 << 0)

        if (!(passesVSjet && passesVSe && passesVSmu))
          continue;
        if (applyCuts)
        {
          if (Tau_pt[tau] < ptCut)
            continue;
          if (std::abs(Tau_eta[tau]) > etaCut)
            continue;
        }
        goodTauIdx.push_back(tau);
      }

      if (goodTauIdx.size() < 2)
        continue;

      std::sort(goodTauIdx.begin(), goodTauIdx.end(),
                [&](int a, int b)
                {
                  return Tau_pt[a] > Tau_pt[b];
                });
      int tau1 = goodTauIdx[0];
      int tau2 = goodTauIdx[1];

      if (Tau_charge[tau1] * Tau_charge[tau2] != -1)
        continue;

      TLorentzVector tau1Vis, tau2Vis;
      tau1Vis.SetPtEtaPhiM(Tau_pt[tau1], Tau_eta[tau1], Tau_phi[tau1], Tau_mass[tau1]);
      tau2Vis.SetPtEtaPhiM(Tau_pt[tau2], Tau_eta[tau2], Tau_phi[tau2], Tau_mass[tau2]);

      double cosDeltaPhi = std::cos(tau1Vis.Phi() - tau2Vis.Phi());
      hDitau_cosDeltaPhi->Fill(cosDeltaPhi);

      if (applyCuts && (cosDeltaPhi < cosCutLow || cosDeltaPhi > cosCutHigh))
        continue;

      double ditauMass = (tau1Vis + tau2Vis).M();
      hDitau_mass->Fill(ditauMass);

      hMET_pt->Fill(MET_pt);
      hMET_phi->Fill(MET_phi);
    }

    fout->mkdir(label + "/METHist");
    fout->mkdir(label + "/tauHist");

    fout->cd(label + "/METHist");
    hMET_pt->Write();
    hMET_phi->Write();

    fout->cd(label + "/tauHist");
    hnTau->Write();
    hTau_eta->Write();
    hTau_phi->Write();
    hTau_pt->Write();
    hDitau_mass->Write();
    hDitau_cosDeltaPhi->Write();

    fout->cd("");
    delete t1;
  }

  fout->Close();
}

// ============================================================================
// HOW TO RUN (on lxplus)
// ============================================================================
//
// 1. Log in and go to the folder that contains this file:
//      ssh kraychev@lxplus.cern.ch
//      cd /eos/user/k/kraychev/Coffea_Basics/WITHROOT
//
// 2. Set up ROOT (if the command "root" is not found), for example with an LCG view
//    or with "cmsenv" inside a CMSSW release you already have.
//
// 3. Get the grid proxy (valid about 12 hours). It is needed to read the
//    root://cms-xrd-global.cern.ch/... files:
//      voms-proxy-init --rfc --voms cms
//
// 4. Run the macro. It asks its questions when it starts, so type the answers
//    in this order:
//      root -l -b -q ditauAna.cc
//
//      question 1: "enter your preference (cut or pre-cut):"
//                  type   pre-cut   (no extra cuts, only the DeepTau ID requirements)
//                  or     cut       (then it also asks, one by one: pt cut, eta cut,
//                                    MET cut, lower and upper bound of the cos cut)
//      last question: "enter desired amount of entries (use -1 for entire population)"
//                  type   10000     for a quick first test
//                  type   -1        for all entries of the file
//
//    The same with the answers typed in for you (pre-cut, first 10000 entries).
//    This also writes the long output to a log file, so it stays readable:
//      printf "pre-cut\n10000\n" | root -l -b -q ditauAna.cc > ditau.log 2>&1
//      grep -i "error\|unknown branch\|entries to process\|output file" ditau.log
//
// 5. Check the log:
//    - Any line with "unknown branch" means a branch name is missing in the file.
//      The results of that run are not valid.
//    - "entries to process: N" shows how many events were read.
//
// 6. Find the result. The file is written in the folder where you started ROOT,
//    when the macro finishes:
//      my_histograms_precut_experimental_Run2024D.root    (pre-cut)
//      my_histograms_cut_experimental_Run2024D.root       (cut)
//    Look inside:
//      root -l my_histograms_precut_experimental_Run2024D.root
//      .ls
//      Run2024D_e8393d52->ls()
//      Run2024D_e8393d52/tauHist/hDitau_mass->Draw()      (the di-tau mass)
//
// FILES: the macro reads every file listed as "enabled": true in
//        file_config_data.json (same config the other WITHROOT macros in this
//        session use). Each file gets its own folder in the output, named
//        after its file name (e.g. Run2024D_e8393d52/tauHist/hDitau_mass).
//        Add or remove files there, not in this .cc file.
// ============================================================================
