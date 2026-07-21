#include "event.C"
#include "event.h"
#include "helpers.C"
#include "helpers.h"
#include "BranchReader.C"
#include "BranchReader.h"

int main()
{
    TTree *Events = getEventsTree("../nanoaodsim_coffea_1.root");
    Long64_t nEntries = getEntries(Events);

    return 0;
}
