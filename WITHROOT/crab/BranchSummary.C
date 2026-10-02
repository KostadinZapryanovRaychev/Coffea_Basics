// Very basic per-file summary, run as one CRAB job per input file:
//   - number of branches in the Events tree
//   - name of every branch
//   - number of events (tree entries)
// Writes both a human-readable .txt and a one-row .root (for easy hadd
// across jobs later) to the current directory, which CRAB then stages out.

#include <fstream>
#include <iostream>

#include "TFile.h"
#include "TTree.h"
#include "TObjArray.h"
#include "TH1I.h"

void BranchSummary(const char *inputFile, const char *outputPrefix = "branch_summary")
{
    TFile f(inputFile);
    if (f.IsZombie())
    {
        std::cerr << "BranchSummary: cannot open " << inputFile << std::endl;
        return;
    }

    TTree *events = (TTree *)f.Get("Events");
    if (!events)
    {
        std::cerr << "BranchSummary: no Events tree in " << inputFile << std::endl;
        return;
    }

    TObjArray *branches = events->GetListOfBranches();
    const Int_t nBranches = branches->GetEntries();
    const Long64_t nEvents = events->GetEntries();

    const std::string txtName = std::string(outputPrefix) + ".txt";
    std::ofstream txt(txtName);
    txt << "file: " << inputFile << "\n";
    txt << "events: " << nEvents << "\n";
    txt << "branches: " << nBranches << "\n";
    for (Int_t i = 0; i < nBranches; ++i)
    {
        txt << branches->At(i)->GetName() << "\n";
    }
    txt.close();

    const std::string rootName = std::string(outputPrefix) + ".root";
    TFile out(rootName.c_str(), "RECREATE");
    TH1I h_summary("h_summary", "nEvents;;nBranches", 2, 0, 2);
    h_summary.SetBinContent(1, nEvents);
    h_summary.SetBinContent(2, nBranches);
    h_summary.Write();
    out.Close();

    std::cout << "BranchSummary: " << inputFile << " -> " << nEvents << " events, "
              << nBranches << " branches. Wrote " << txtName << " and " << rootName << std::endl;
}
