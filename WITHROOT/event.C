#include "event.h"
#include <TFile.h>
#include <TTree.h>
#include <cstdio>

TTree *getEventsTree(std::string fileName)
{
    TFile *file = TFile::Open(fileName.c_str());

    if (!file || file->IsZombie())
    {
        printf("Cannot open file: %s\n", fileName.c_str());
        return nullptr;
    }

    TTree *tree = (TTree *)file->Get("Events");

    if (!tree)
    {
        printf("Events tree not found!\n");
        return nullptr;
    }

    return tree;
}

void printEventTree(TTree *Events)
{
    if (!Events)
    {
        printf("Cannot print tree: null pointer\n");
        return;
    }

    printf("\n========== Events Tree Information ==========\n");

    printf("Number of events: %lld\n",
           Events->GetEntries());

    printf("Printing branches...\n\n");

    Events->Print();

    printf("=============================================\n");
}