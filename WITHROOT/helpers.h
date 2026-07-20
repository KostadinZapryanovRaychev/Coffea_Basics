#ifndef HELPERS_H
#define HELPERS_H

#include <string>
#include <fstream>

// File utilities
void reader(std::string filePath);

Long64_t getEntries(TTree *tree);
void printBoolBranch(TTree *tree, const std::string &branchName, Long64_t maxEvents);
Long64_t getEntries(TTree *tree);
void printBoolHLT_HT350OnlyTrue(TTree *tree, Long64_t maxEvents);

// Later add more functions here:
// void anotherFunction();
// double calculateSomething();

#endif