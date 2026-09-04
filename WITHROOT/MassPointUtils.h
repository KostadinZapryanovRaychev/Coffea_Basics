#ifndef MASSPOINTUTILS_H
#define MASSPOINTUTILS_H

#include <string>
#include "Rtypes.h"

// Shared helper so every analysis module can scale its histogram ranges
// to the actual Z' mass point of the sample being analyzed, instead of
// hardcoding a range that only makes sense for one specific mass
// (config.json points at a different file per production, e.g.
// ".../ZprimeTo2Tau-2Jets_M-250_.../nanoaodsim_coffea_1.root" one run,
// ".../ZprimeTo2Tau-2Jets_M-500_.../nanoaodsim_coffea_1.root" the next --
// see file_config_batch_all_mass_points.json in NAOD_TAU for the full
// list of mass points this can be).
//
// Used by TauChannelAnalysis, TauLHEKinematics, and TauGenParticleKinematics
// alike, so all three modules' histogram ranges move together when you
// point config.json at a different mass point -- rather than each module
// carrying its own copy of this logic (which is how it started, and
// promptly collided: main.C #includes every module's .C file into one
// translation unit, so two same-named helper functions in two different
// files' anonymous namespaces still clash).
namespace MassPointUtils
{
// Extracts the integer mass value from a "...M-<number>_..." substring
// of a file path, mirroring extract_mass_point() in NAOD_TAU/helpers/io.py.
// Returns 500 (matching the python pipeline's fallback) if no such
// substring is found, and prints a note explaining why.
Double_t extractMassPoint(const std::string &inputFilePath);
} // namespace MassPointUtils

#endif
