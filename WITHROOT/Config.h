#ifndef CONFIG_H
#define CONFIG_H

#include <string>
#include <vector>

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

// One entry of a multi-file config, e.g. one mass point's NanoAOD file.
// Mirrors NAOD_TAU's file_config.json / file_config_batch_all_mass_points.json
// "root_files" array, so the same JSON files can drive both pipelines.
struct RootFileEntry
{
    std::string name;
    std::string path;
    std::string tree;
    bool enabled;
};

// Load a list of ROOT files from a JSON config shaped like
// { "root_files": [ { "name", "path", "tree", "enabled" }, ... ] }.
// "tree" defaults to "Events" and "enabled" defaults to true when
// missing. Only entries with "enabled": true are returned. On any
// error (file missing, malformed JSON, missing "root_files" key)
// prints an error and returns an empty vector.
std::vector<RootFileEntry> loadRootFileList(const std::string &configPath);

#endif
