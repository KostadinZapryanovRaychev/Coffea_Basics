#include "Config.h"

#include <fstream>
#include <iostream>

#include "third_party/nlohmann/json.hpp"

Config loadConfig(const std::string &configPath)
{
    Config config;

    std::ifstream inFile(configPath);
    if (!inFile.is_open())
    {
        std::cerr << "Error: Could not open config file: " << configPath
                  << std::endl;
        return config;
    }

    nlohmann::json j;
    try
    {
        inFile >> j;
    }
    catch (const nlohmann::json::parse_error &e)
    {
        std::cerr << "Error: Malformed JSON in " << configPath << ": "
                  << e.what() << std::endl;
        return config;
    }

    if (!j.contains("inputFile"))
    {
        std::cerr << "Error: " << configPath
                  << " is missing required key \"inputFile\"." << std::endl;
        return config;
    }

    config.inputFile = j.at("inputFile").get<std::string>();

    return config;
}

std::vector<RootFileEntry> loadRootFileList(const std::string &configPath)
{
    std::vector<RootFileEntry> entries;

    std::ifstream inFile(configPath);
    if (!inFile.is_open())
    {
        std::cerr << "Error: Could not open config file: " << configPath
                  << std::endl;
        return entries;
    }

    nlohmann::json j;
    try
    {
        inFile >> j;
    }
    catch (const nlohmann::json::parse_error &e)
    {
        std::cerr << "Error: Malformed JSON in " << configPath << ": "
                  << e.what() << std::endl;
        return entries;
    }

    if (!j.contains("root_files"))
    {
        std::cerr << "Error: " << configPath
                  << " is missing required key \"root_files\"." << std::endl;
        return entries;
    }

    for (const auto &item : j.at("root_files"))
    {
        if (!item.value("enabled", true))
        {
            continue;
        }

        // Accepts either one "path" per entry, or a "paths" list (same
        // shape NAOD_TAU's file_config.json uses) -- one RootFileEntry
        // per path either way.
        std::vector<std::string> paths;
        if (item.contains("paths"))
        {
            for (const auto &p : item.at("paths"))
            {
                paths.push_back(p.get<std::string>());
            }
        }
        else
        {
            paths.push_back(item.at("path").get<std::string>());
        }

        for (const std::string &path : paths)
        {
            RootFileEntry entry;
            entry.name = item.value("name", "");
            entry.path = path;
            entry.tree = item.value("tree", "Events");
            entry.enabled = true;
            entries.push_back(entry);
        }
    }

    return entries;
}
