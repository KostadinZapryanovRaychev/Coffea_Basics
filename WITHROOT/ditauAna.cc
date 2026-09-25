#include <algorithm>
#include <functional>
#include <iostream>
#include <string>
#include <cmath>
#include <fstream>

const int MAXGEN = 5000;
const int MAXTAU = 200;
void ditauAna()
{

  std::string mode;
  std::cout << "enter your preference (cut or pre-cut): ";
  std::cin >> mode;

  std::string answer;
  bool isExperimental = false;

  std::cout << "is your data experimental? [yes]/[no] only: ";
  std::cin >> answer;

  const char *mcFileNames[] = {"root://eospublic.cern.ch//eos/opendata/cms/mc/RunIISummer20UL16NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_v17-v1/40000/F9F34B8E-DAA6-7A4E-B4A5-43F2D741CFE3.root"};
  const char *mcFileLabels[] = {"drellYan"};

  const char *expFileNames[] = {"root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/e8393d52-174a-4cde-bb15-0f98571d0b33.root",
                                "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/d0e3a051-2fc4-49f1-b6e7-25fd936e0101.root"};
  const char *expFileLabels[] = {"Run2024D_e8393d52", "Run2024D_d0e3a051"};

  const char **fileNames = nullptr;
  const char **fileLabels = nullptr;
  int nFiles = 0;

  if (answer == "yes")
  {
    isExperimental = true;
    fileNames = expFileNames;
    fileLabels = expFileLabels;
    nFiles = 2;
  }
  else if (answer == "no")
  {
    isExperimental = false;
    fileNames = mcFileNames;
    fileLabels = mcFileLabels;
    nFiles = 1;
  }
  else
  {
    std::cout << "invalid input";
    return;
  }

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
  outputFile += (isExperimental ? "experimental_" : "mc_");
  outputFile += "Run2024D";
  outputFile += ".root";

  TFile *fout = new TFile(outputFile.c_str(), "RECREATE");
  cout << "output file name is: " << outputFile << endl;

  for (int fileIdx = 0; fileIdx < nFiles; fileIdx++)
  {
    TString label = fileLabels[fileIdx];

    TChain *t1 = new TChain("Events");
    t1->Add(fileNames[fileIdx]);
    t1->Print();

    Float_t MET_pt;
    Float_t MET_phi;

    UInt_t nGenVisTau;
    Float_t GenVisTau_mass[MAXGEN];
    Float_t GenVisTau_pt[MAXGEN];
    Float_t GenVisTau_eta[MAXGEN];
    Float_t GenVisTau_phi[MAXGEN];
    Int_t GenVisTau_charge[MAXGEN];
    Int_t GenVisTau_status[MAXGEN];

    ////////////TAU BRANCHES///////////////
    Int_t nTau; // Int_t in this NanoAOD (was UInt_t)
    Float_t Tau_pt[MAXTAU];
    Float_t Tau_eta[MAXTAU];
    Float_t Tau_phi[MAXTAU];
    Float_t Tau_mass[MAXTAU];
    Short_t Tau_charge[MAXTAU]; // Short_t in this NanoAOD (was Int_t)
    UChar_t Tau_decayMode[MAXTAU];

    UChar_t Tau_idDeepTau2017v2p1VSjet[MAXTAU];
    UChar_t Tau_idDeepTau2017v2p1VSe[MAXTAU];
    UChar_t Tau_idDeepTau2017v2p1VSmu[MAXTAU];

    /////////////BRANCH ADDRESSES///////////////
    t1->SetBranchAddress("MET_pt", &MET_pt);   // transverse momentum of missing energy transfers
    t1->SetBranchAddress("MET_phi", &MET_phi); // azimuthal angle of MET

    if (!isExperimental)
    {
      t1->SetBranchAddress("nGenVisTau", &nGenVisTau);
      t1->SetBranchAddress("GenVisTau_pt", GenVisTau_pt);
      t1->SetBranchAddress("GenVisTau_eta", GenVisTau_eta);
      t1->SetBranchAddress("GenVisTau_phi", GenVisTau_phi);
      t1->SetBranchAddress("GenVisTau_mass", GenVisTau_mass);
      t1->SetBranchAddress("GenVisTau_charge", GenVisTau_charge);
      t1->SetBranchAddress("GenVisTau_status", GenVisTau_status);
    }

    t1->SetBranchAddress("nTau", &nTau);
    t1->SetBranchAddress("Tau_pt", &Tau_pt);
    t1->SetBranchAddress("Tau_eta", &Tau_eta);
    t1->SetBranchAddress("Tau_phi", &Tau_phi);
    t1->SetBranchAddress("Tau_mass", &Tau_mass);
    t1->SetBranchAddress("Tau_charge", &Tau_charge);
    t1->SetBranchAddress("Tau_decayMode", &Tau_decayMode);
    t1->SetBranchAddress("Tau_idDeepTau2017v2p1VSjet", &Tau_idDeepTau2017v2p1VSjet);
    t1->SetBranchAddress("Tau_idDeepTau2017v2p1VSe", &Tau_idDeepTau2017v2p1VSe);
    t1->SetBranchAddress("Tau_idDeepTau2017v2p1VSmu", &Tau_idDeepTau2017v2p1VSmu);

    //////////////HISTOGRAM ANALYSIS////////////////
    /////////MET/////////////////////////
    TH1F *hMET_pt = new TH1F("hMET_pt", "MET p_{t}", 200, 0., 100.);
    TH1F *hMET_phi = new TH1F("hMET_phi", "MET #varphi", 20, -5., 5.);
    ////////////////////////////////////////////////////////////////////////////////////////
    TH1F *hnGenVisTau = new TH1F("hnGenVisTau", "number of events in genVisTau collection", 200, 0., 100.);
    TH1F *hGenVisTau_pt = new TH1F("hGenVisTau_pt", "gen particles p_{t}", 400., 0., 200.);
    TH1F *hGenVisTau_phi = new TH1F("hGenVisTau_phi", "#varphi of gen particles", 130, -6.5, 6.5);
    TH1F *hGenVisTau_eta = new TH1F("hGenVisTau_eta", "#eta of gen particle events", 50, -2.5, 2.5);
    TH1F *hGenVisTau_ditauMass = new TH1F("hGenVisTau_ditauMass", "mass of di-tau event", 400, 0., 200.);
    TH1F *hGenVisTau_status = new TH1F("hGenVisTau_status", "status of events in genVisTau collection", 15, 0., 15.);
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
        hMET_pt, hMET_phi, hnGenVisTau,
        hGenVisTau_pt, hGenVisTau_phi, hGenVisTau_eta,
        hGenVisTau_ditauMass, hGenVisTau_status, hnTau,
        hTau_eta, hTau_phi, hTau_pt, hDitau_mass,
        hDitau_cosDeltaPhi

    };
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
        bool passesVSjet = Tau_idDeepTau2017v2p1VSjet[tau] >= 3; // was & (1 << 2)
        bool passesVSe = Tau_idDeepTau2017v2p1VSe[tau] >= 1;     // was & (1 << 0)
        bool passesVSmu = Tau_idDeepTau2017v2p1VSmu[tau] >= 1;   // was & (1 << 0)

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

      if (!isExperimental)
      {
        hnGenVisTau->Fill(nGenVisTau);

        std::vector<int> genVisTauIdx;
        for (Int_t gv = 0; gv < nGenVisTau; gv++)
        {
          hGenVisTau_status->Fill(GenVisTau_status[gv]);
          hGenVisTau_phi->Fill(GenVisTau_phi[gv]);
          hGenVisTau_eta->Fill(GenVisTau_eta[gv]);
          hGenVisTau_pt->Fill(GenVisTau_pt[gv]);
          genVisTauIdx.push_back(gv);
        }

        if (genVisTauIdx.size() >= 2)
        {
          std::sort(genVisTauIdx.begin(), genVisTauIdx.end(),
                    [&](int a, int b)
                    {
                      return GenVisTau_pt[a] > GenVisTau_pt[b];
                    });
          int gv1 = genVisTauIdx[0];
          int gv2 = genVisTauIdx[1];

          if (GenVisTau_charge[gv1] * GenVisTau_charge[gv2] == -1)
          {
            TLorentzVector g1, g2;
            g1.SetPtEtaPhiM(GenVisTau_pt[genVisTauIdx[0]], GenVisTau_eta[genVisTauIdx[0]], GenVisTau_phi[genVisTauIdx[0]], GenVisTau_mass[genVisTauIdx[0]]);
            g2.SetPtEtaPhiM(GenVisTau_pt[genVisTauIdx[1]], GenVisTau_eta[genVisTauIdx[1]], GenVisTau_phi[genVisTauIdx[1]], GenVisTau_mass[genVisTauIdx[1]]);
            ditauMass = (g1 + g2).M();
            hGenVisTau_ditauMass->Fill(ditauMass);
          }
        }
      }
    }

    fout->mkdir(label + "/METHist");
    fout->mkdir(label + "/tauHist");
    fout->mkdir(label + "/genVisHist");

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

    fout->cd(label + "/genVisHist");
    hnGenVisTau->Write();
    hGenVisTau_pt->Write();
    hGenVisTau_phi->Write();
    hGenVisTau_eta->Write();
    hGenVisTau_ditauMass->Write();
    fout->cd("");
    delete t1;
  }

  fout->Close();
}
