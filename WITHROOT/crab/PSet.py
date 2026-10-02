# Minimal PSet, needed by CRAB even in scriptExe mode: CRAB rewrites
# process.source.fileNames on the worker node with the job's assigned input
# file(s) before running crab_script.sh. The script reads that back -- we
# never actually run cmsRun on this file ourselves.

import FWCore.ParameterSet.Config as cms

process = cms.Process("NOOP")

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring()
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(0)
)
