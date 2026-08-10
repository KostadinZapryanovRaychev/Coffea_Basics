#include "helpers.h"
#include <fstream>
#include <cstdio>
#include <iostream>
#include <sys/stat.h>
#include <cerrno>
#include <cstring>

void reader(std::string filePath)
{
    std::ifstream file(filePath);

    if (file.is_open())
    {
        printf("File opened successfully: %s\n", filePath.c_str());
        file.close();
    }
    else
    {
        printf("Failed to open file: %s\n", filePath.c_str());
    }
}

Long64_t getEntries(TTree *tree)
{
    if (!tree)
    {
        printf("Cannot get entries: null pointer\n");
        return -1;
    }

    return tree->GetEntries();
}

// ==============================================

// HLT_HT350 -Total scalar sum of jet transverse energy 350GeV.

void printBoolBranch(TTree *tree, const std::string &branchName, Long64_t maxEvents = 10)
{
    if (!tree)
    {
        std::cerr << "Error: Null TTree pointer provided." << std::endl;
        return;
    }

    TBranch *branch = tree->GetBranch(branchName.c_str());
    if (!branch)
    {
        std::cerr << "Error: Branch '" << branchName << "' not found!" << std::endl;
        return;
    }

    Bool_t branchValue = false;

    tree->SetBranchStatus("*", 0);
    tree->SetBranchStatus(branchName.c_str(), 1);
    tree->SetBranchAddress(branchName.c_str(), &branchValue);

    Long64_t nEntries = tree->GetEntries();
    Long64_t limit = std::min(maxEvents, nEntries);

    std::cout << "\n=== Inspecting Branch: " << branchName << " ===" << std::endl;
    for (Long64_t i = 0; i < limit; ++i)
    {
        tree->GetEntry(i);
        std::cout << "Event " << i << " | " << branchName << " = "
                  << (branchValue ? "true (1)" : "false (0)") << std::endl;
    }

    tree->SetBranchStatus("*", 1);
}

void printBoolHLT_HT350OnlyTrue(TTree *tree, Long64_t maxEvents)
{
    if (!tree)
    {
        std::cerr << "Error: Null TTree pointer provided." << std::endl;
        return;
    }
    TBranch *branch = tree->GetBranch("HLT_HT350");
    if (!branch)
    {
        std::cerr << "Error: Branch 'HLT_HT350' not found!" << std::endl;
        return;
    }

    Bool_t branchValue = false;

    tree->SetBranchStatus("*", 0);
    tree->SetBranchStatus("HLT_HT350", 1);
    tree->SetBranchAddress("HLT_HT350", &branchValue);
    std::ofstream outFile("HLT_HT350_passed_events.txt");
    if (!outFile.is_open())
    {
        std::cerr << "Error: Could not create output file!" << std::endl;
        tree->SetBranchStatus("*", 1);
        return;
    }

    Long64_t nEntries = tree->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;
    Long64_t passCount = 0;

    outFile << "=== Events Passing HLT_HT350 ===" << std::endl;
    for (Long64_t i = 0; i < limit; ++i)
    {
        tree->GetEntry(i);
        if (branchValue)
        {
            outFile << "Event " << i << " | HLT_HT350 = true (1)" << std::endl;
            passCount++;
        }
    }
    outFile << "\nSummary: " << passCount << " / " << limit << " events passed." << std::endl;
    outFile.close();
    std::cout << "Done! Found " << passCount << " passing events. Saved results to 'HLT_HT350_passed_events.txt'." << std::endl;
    tree->SetBranchStatus("*", 1);
}

// Additional functions can be added here as needed. !!!!!!!!!!!!!!!! TODO: Implement more helper functions for other branches or analyses.

void createOutputsFolder()
{
    if (mkdir("outputs", 0777) == 0)
    {
        std::cout << "Created outputs directory." << std::endl;
    }
    else if (errno == EEXIST)
    {
        std::cout << "Outputs directory already exists." << std::endl;
    }
    else
    {
        std::cerr << "Failed to create outputs directory: "
                  << std::strerror(errno)
                  << std::endl;
    }
}

void inspectTauKinematics(TTree *tree, Long64_t maxEvents)
{
    if (!tree)
    {
        std::cerr << "Error: Null TTree pointer provided." << std::endl;
        return;
    }

    // 1. Declare variables to hold branch data
    UInt_t nTau = 0;
    Float_t Tau_pt[32];
    Float_t Tau_eta[32];
    Float_t MET_pt = 0.0;

    // 2. Selectively enable ONLY the required branches for fast reading

    // disable reading all branches to speed up the process
    tree->SetBranchStatus("*", 0);

    tree->SetBranchStatus("nTau", 1);
    tree->SetBranchStatus("Tau_pt", 1);
    tree->SetBranchStatus("Tau_eta", 1);
    tree->SetBranchStatus("MET_pt", 1);

    // 3. Bind local C++ variables to ROOT tree branches
    tree->SetBranchAddress("nTau", &nTau);
    tree->SetBranchAddress("Tau_pt", Tau_pt);
    tree->SetBranchAddress("Tau_eta", Tau_eta);
    tree->SetBranchAddress("MET_pt", &MET_pt);

    // 4. Ensure 'outputs/' directory exists and open file
    createOutputsFolder();
    std::string outputPath = "outputs/Tau_Kinematics_Inspection.txt";
    std::ofstream outFile(outputPath);

    if (!outFile.is_open())
    {
        std::cerr << "Error: Could not open " << outputPath << " for writing!" << std::endl;
        tree->SetBranchStatus("*", 1);
        return;
    }

    // 5. Determine event loop limits
    Long64_t nEntries = tree->GetEntries();
    Long64_t limit = (maxEvents > 0) ? std::min(maxEvents, nEntries) : nEntries;

    outFile << "=== Tau Kinematics & Missing Energy (MET) Inspection ===" << std::endl;
    outFile << "Event | nTau | MET [GeV] | Taus (pT [GeV], eta)" << std::endl;
    outFile << "------------------------------------------------------------------" << std::endl;

    // 6. Main Event Loop
    for (Long64_t i = 0; i < limit; ++i)
    {
        tree->GetEntry(i);

        // Skip events with no taus to keep log clean
        if (nTau == 0)
            continue;

        outFile << "Event " << i << " | nTau=" << nTau << " | MET=" << MET_pt << " GeV | ";

        // Loop over individual tau objects inside the event array
        for (UInt_t t = 0; t < nTau; ++t)
        {
            outFile << "[Tau #" << t << " pT: " << Tau_pt[t] << ", eta: " << Tau_eta[t] << "] ";
        }
        outFile << std::endl;
    }

    outFile.close();
    std::cout << "Successfully written Tau data to: " << outputPath << std::endl;

    // 7. Reset branch status back to default
    tree->SetBranchStatus("*", 1);
}

// Writes the name of every branch on the tree to a txt file, one per line,
// so they can be browsed/grepped without opening ROOT.
void listBranchNames(TTree *tree, const std::string &outputPath)
{
    if (!tree)
    {
        std::cerr << "Error: Null TTree pointer provided." << std::endl;
        return;
    }

    createOutputsFolder();
    std::ofstream outFile(outputPath);
    if (!outFile.is_open())
    {
        std::cerr << "Error: Could not open " << outputPath << " for writing!" << std::endl;
        return;
    }

    TObjArray *branches = tree->GetListOfBranches();
    for (int i = 0; i < branches->GetEntries(); ++i)
    {
        TBranch *branch = static_cast<TBranch *>(branches->At(i));
        outFile << branch->GetName() << "\n";
    }

    outFile.close();
    std::cout << "Successfully written " << branches->GetEntries()
               << " branch names to: " << outputPath << std::endl;
}