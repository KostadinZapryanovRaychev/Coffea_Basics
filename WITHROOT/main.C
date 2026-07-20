#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"

int main()
{
    TTree *Events = getEventsTree("../nanoaodsim_coffea_1.root");

    // printEventTree(Events);
    Long64_t nEntries = getEntries(Events);
    printBoolBranch(Events, "HLT_HT350", nEntries);

    return 0;
}
