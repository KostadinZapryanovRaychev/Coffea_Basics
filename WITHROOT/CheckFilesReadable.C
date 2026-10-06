// Quick readability check for a file list, using only BranchPlotter: for
// each file in the given config, open it and try to read Tau_pt (nTau
// counted) for the first few hundred events. Prints OK/FAIL per file, so
// switching datasets (MC/data, a different config) can be sanity-checked
// before running a full analysis over it.
//
// Usage: root -l -b -q 'CheckFilesReadable.C("file_config_mc.json")'
// Defaults to file_config_mc.json (MC) if no argument is given.

#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"

#include <iostream>

#include "HistogramWriter.C"
#include "HistogramWriter.h"
#include "BranchPlotter.C"
#include "BranchPlotter.h"

namespace
{
    constexpr Int_t MAX_TAU = 20;
    constexpr Long64_t CHECK_EVENTS = 500;
}

void CheckFilesReadable(const std::string &configFile = "file_config_mc.json")
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList(configFile);
    std::cout << "CheckFilesReadable: " << rootFiles.size() << " file(s) from " << configFile << std::endl;

    Long64_t nOk = 0, nFail = 0;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "checking: " << file.path << " ... ";

        TTree *events = getEventsTree(file.path);
        if (!events)
        {
            std::cout << "FAIL (could not open file or find Events tree)" << std::endl;
            ++nFail;
            continue;
        }

        if (!events->GetBranch("nTau") || !events->GetBranch("Tau_pt"))
        {
            std::cout << "FAIL (missing nTau/Tau_pt branch)" << std::endl;
            ++nFail;
            continue;
        }

        const std::string outPath = "outputs/check_readable_" + file.name + ".root";
        BranchPlotter plotter(events);
        plotter.plotCountedArrayBranch("nTau", "Tau_pt", "h_check_tau_pt",
                                        MAX_TAU, 50, 0, 200, CHECK_EVENTS, outPath);

        std::cout << "OK (" << events->GetEntries() << " events)" << std::endl;
        ++nOk;
    }

    std::cout << "CheckFilesReadable: " << nOk << " OK, " << nFail << " FAILED, out of " << rootFiles.size() << " file(s)." << std::endl;
}
