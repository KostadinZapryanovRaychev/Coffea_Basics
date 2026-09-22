#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"
#include "RecoTauMassKinematics.C"
#include "RecoTauMassKinematics.h"
#include "HistogramWriter.C"
#include "HistogramWriter.h"

// Runs the reconstructed-Tau mass + kinematics analysis over every file
// listed in file_config_reco.json, and writes one combined ROOT file:
// outputs/reco_tau_mass_kinematics.root (see RecoTauMassKinematics.h for
// what each histogram in it means).
//
// Usage: root -l -b -q RunRecoTauMassKinematics.C
void RunRecoTauMassKinematics()
{
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_reco.json");

    std::cout << "RunRecoTauMassKinematics: " << rootFiles.size()
              << " file(s) enabled in file_config_reco.json." << std::endl;

    const Long64_t maxEventsPerFile = -1; // use every entry in each file

    RecoTauMassKinematics::run(rootFiles, /*debug=*/false, maxEventsPerFile);
}
