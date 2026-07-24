#ifndef CONFIG_H
#define CONFIG_H

#include <string>

// Plain-data settings loaded from a JSON config file (see config.json).
// Extend with more fields as WITHROOT needs more caller-supplied settings.
struct Config
{
    std::string inputFile;
};

// Load settings from configPath (a JSON file). On any error (file
// missing, malformed JSON, missing keys) prints an error and returns a
// Config with empty fields.
Config loadConfig(const std::string &configPath);

#endif
