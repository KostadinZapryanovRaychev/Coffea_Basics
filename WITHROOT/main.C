#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"
#include "BranchReader.C"
#include "BranchReader.h"

#include <fstream>
#include <iostream>

int main()
{
    TTree *Events = getEventsTree("../nanoaodsim_coffea_1.root");

    BranchReader reader(Events);
    reader.enableBranches({"nTau", "Tau_pt", "Tau_eta", "MET_pt"});

    Int_t nTau = 0;
    Float_t Tau_pt[32];
    Float_t Tau_eta[32];
    Float_t MET_pt = 0.0;

    Events->SetBranchAddress("nTau", &nTau);
    Events->SetBranchAddress("Tau_pt", Tau_pt);
    Events->SetBranchAddress("Tau_eta", Tau_eta);
    Events->SetBranchAddress("MET_pt", &MET_pt);

    Long64_t nEntries = reader.getEntries();
    Long64_t maxEvents = std::min<Long64_t>(10, nEntries);

    std::ofstream outFile("class_based_columns.txt");
    outFile << "Event | nTau | MET [GeV] | Taus (pT [GeV], eta)" << std::endl;

    for (Long64_t i = 0; i < maxEvents; ++i)
    {
        Events->GetEntry(i);
        outFile << "Event " << i << " | nTau=" << nTau << " | MET=" << MET_pt << " GeV | ";
        for (UInt_t t = 0; t < nTau; ++t)
        {
            outFile << "[Tau #" << t << " pT: " << Tau_pt[t] << ", eta: " << Tau_eta[t] << "] ";
        }
        outFile << std::endl;
    }
    outFile.close();

    std::cout << "Saved " << maxEvents << " events to class_based_columns.txt" << std::endl;

    return 0;
}
