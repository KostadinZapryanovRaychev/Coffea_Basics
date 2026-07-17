#ifndef EVENT_H
#define EVENT_H

#include <string>

class TTree;

TTree *getEventsTree(std::string fileName);

void printEventTree(TTree *Events);

#endif