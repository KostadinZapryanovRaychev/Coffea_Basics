# CRAB config for BranchSummary.C: one job per input file, counts branches
# and events, writes a .txt + .root summary. Pattern borrowed from
# CMSSW_16_0_2_patch1/src/DQM/RPCMonitorModule/test/crab/RPCMon_LR/sub_crab.py,
# adapted to scriptExe (plain ROOT macro) instead of a full cmsRun EDAnalyzer,
# since NanoAOD doesn't need CMSSW event reconstruction to just read branches.

from CRABClient.UserUtilities import config

config = config()

config.section_("General")
config.General.requestName = 'BranchSummary'
config.General.workArea = 'crab_BranchSummary'
config.General.transferOutputs = True
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script.sh'
config.JobType.inputFiles = ['BranchSummary.C']
config.JobType.outputFiles = ['branch_summary.root', 'branch_summary.txt']
config.JobType.sendPythonFolder = True

config.section_("Data")
# Explicit file list (not a single DAS dataset string): Run2024D Tau data,
# both the /120000/ and /90000/ blocks, 102 unique files, from
# WITHROOT/das_files.sh. Same userInputFiles pattern as the reference
# RPCMon_LR/sub_crab.py.
config.Data.userInputFiles = open('ListOfFiles.txt').readlines()
config.Data.outputPrimaryDataset = 'Tau_Run2024D_branch_summary'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.publication = False
config.Data.outLFNDirBase = '/store/user/kraychev/Coffea_Basics/outputs/'
config.Data.outputDatasetTag = 'branch_summary'

config.section_("Site")
config.Site.storageSite = 'T3_CH_CERNBOX'
