#include "event.C"
#include "event.h"

int main()
{
    TTree *Events = getEventsTree("../nanoaodsim_coffea_1.root");

    printEventTree(Events);

    return 0;
}
