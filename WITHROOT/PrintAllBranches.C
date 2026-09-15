#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"

void PrintAllBranches()
{
    Config config = loadConfig("config.json");
    TTree *Events = getEventsTree(config.inputFile);
    Events->SetBranchStatus("*", 1);
    listBranchNames(Events, "outputs/branch_names.txt");
}
