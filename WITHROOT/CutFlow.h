#ifndef CUTFLOW_H
#define CUTFLOW_H

#include <iostream>
#include <string>
#include "Rtypes.h"

// How many events are left after each selection step.
struct CutFlow
{
    Long64_t eventsRead = 0;
    Long64_t atLeastTwoTaus = 0;
    Long64_t oppositeSign = 0;
    Long64_t passKinematics = 0;
    Long64_t used = 0;
};

inline void printCutFlow(const std::string &label, const CutFlow &c)
{
    std::cout << label << " events read: " << c.eventsRead
              << " | >= 2 taus: " << c.atLeastTwoTaus
              << " | opposite sign: " << c.oppositeSign
              << " | pT and eta: " << c.passKinematics
              << " | used: " << c.used << std::endl;
}

#endif
