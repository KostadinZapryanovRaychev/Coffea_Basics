#include "LumiMask.h"

#include <fstream>
#include <iostream>

#include "third_party/nlohmann/json.hpp"

LumiMask::LumiMask(const std::string &jsonPath)
{
    std::ifstream in(jsonPath);
    if (!in)
    {
        std::cerr << "LumiMask: cannot open " << jsonPath << std::endl;
        return;
    }
    nlohmann::json runs;
    in >> runs;
    for (auto it = runs.begin(); it != runs.end(); ++it)
    {
        auto &runRanges = ranges_[std::stoul(it.key())];
        for (const auto &range : it.value())
        {
            runRanges.emplace_back(range[0].get<unsigned int>(), range[1].get<unsigned int>());
        }
    }
    loaded_ = true;
}

bool LumiMask::isLoaded() const
{
    return loaded_;
}

bool LumiMask::isGood(unsigned int run, unsigned int lumi) const
{
    const auto it = ranges_.find(run);
    if (it == ranges_.end())
    {
        return false;
    }
    for (const auto &range : it->second)
    {
        if (lumi >= range.first && lumi <= range.second)
        {
            return true;
        }
    }
    return false;
}
