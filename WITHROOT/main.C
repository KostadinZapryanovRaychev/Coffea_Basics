#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"

int main()
{
    TTree *Events = getEventsTree("../nanoaodsim_coffea_1.root");

    // printEventTree(Events);
    Long64_t nEntries = getEntries(Events);
    printBoolHLT_HT350OnlyTrue(Events, nEntries);

    return 0;
}
