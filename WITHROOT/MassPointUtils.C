#include "MassPointUtils.h"

#include <iostream>
#include <regex>

Double_t MassPointUtils::extractMassPoint(const std::string &inputFilePath)
{
    static const std::regex massPattern("M-(\\d+)");
    std::smatch match;
    if (std::regex_search(inputFilePath, match, massPattern))
    {
        return std::stod(match[1].str());
    }
    std::cout << "MassPointUtils: could not find an 'M-<number>' mass point in '"
              << inputFilePath << "', defaulting to 500 GeV for histogram ranges." << std::endl;
    return 500.0;
}
