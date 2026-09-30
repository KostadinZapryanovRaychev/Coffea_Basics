#ifndef LUMIMASK_H
#define LUMIMASK_H

#include <map>
#include <string>
#include <utility>
#include <vector>

class LumiMask
{
public:
    explicit LumiMask(const std::string &jsonPath);
    bool isLoaded() const;
    bool isGood(unsigned int run, unsigned int lumi) const;

private:
    std::map<unsigned int, std::vector<std::pair<unsigned int, unsigned int>>> ranges_;
    bool loaded_ = false;
};

#endif
