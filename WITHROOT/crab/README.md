# CRAB: very basic per-file summary (branch count, branch names, event count)

Pattern borrowed from a working reference:
`CMSSW_16_0_2_patch1/src/DQM/RPCMonitorModule/test/crab/RPCMon_LR/` (shift
analysis). That job is a full CMSSW `EDAnalyzer` (loads geometry/global tag,
runs reconstruction) via `config.JobType.psetName` running a real `cmsRun`
config. We don't need that here: NanoAOD is a flat ROOT tree, so the actual
work is just `BranchSummary.C`, a plain ROOT macro, run via
`config.JobType.scriptExe` instead of a real CMSSW analyzer.

## Files

- `BranchSummary.C` — the actual work: opens the file, counts/lists
  `Events` tree branches, counts events, writes `branch_summary.txt` and
  `branch_summary.root`. Verified locally against `nanoaodsim_coffea_1.root`
  (1782 branches, 60806 events).
- `PSet.py` — minimal, required by CRAB even in `scriptExe` mode: CRAB
  rewrites `process.source.fileNames` on the worker node with that job's
  assigned input file before `crab_script.sh` runs.
- `crab_script.sh` — runs on the worker node. Reads the input file path back
  out of `PSet.py` (NOT passed as `$1`: scriptExe is called as
  `crab_script.sh <jobId> <scriptArgs>`, so the input file has to come from
  PSet.py, not the arguments), then runs `BranchSummary.C` on it.
- `ListOfFiles.txt` — 102 unique Run2024D Tau NanoAOD files (both the
  `/120000/` and `/90000/` blocks), full `root://cms-xrd-global.cern.ch/`
  URLs, from `WITHROOT/das_files.sh`.
- `crabConfig.py` — uses `config.Data.userInputFiles =
  open('ListOfFiles.txt').readlines()` (explicit file list, same pattern as
  the reference `RPCMon_LR/sub_crab.py`, not a single DAS dataset string).
  `config.Site.storageSite = 'T3_CH_CERNBOX'` and
  `config.Data.outLFNDirBase = '/store/user/kraychev/Coffea_Basics/outputs/'`
  match
  https://cernbox.cern.ch/files/spaces/eos/user/k/kraychev/Coffea_Basics/outputs
  -- adjust the username/path if that's not the right one.

## Not yet verified

The `PSet.py`-rewrite step (`crab_script.sh` reading the assigned input file
back from `PSet.py`) can only be tested inside a real CMSSW environment
(`cmsenv`), which isn't available locally -- `FWCore.ParameterSet.Config`
only exists there. Everything else (`BranchSummary.C` itself) is verified
locally; this one step needs its first real test on lxplus.

## How to run a first test, step by step

The `PSet.py`-rewrite mechanism (how the worker node learns which file it's
assigned) hasn't been tested on a real submission yet, so this first run
uses only 1 file, not the full 102.

**1. Set up the CMSSW environment.** CRAB jobs run inside CMSSW, so you need
the area from `CMSSW_16_0_2_patch1.tar` set up first:
```bash
tar -xf CMSSW_16_0_2_patch1.tar
cd CMSSW_16_0_2_patch1/src
cmsenv
```

**2. Set up the CRAB client**, if `crab` isn't already a recognized command:
```bash
source /cvmfs/cms.cern.ch/common/crab-setup.sh
```

**3. Get a grid proxy** (needed to submit jobs and read `root://` files):
```bash
voms-proxy-init --rfc --voms cms --valid 168:00
```

**4. Go to the crab folder and back up the full file list:**
```bash
cd /path/to/WITHROOT/crab
cp ListOfFiles.txt ListOfFiles.txt.full
```

**5. Trim it down to 1 file for the first test:**
```bash
head -1 ListOfFiles.txt.full > ListOfFiles.txt
```

**6. Submit:**
```bash
crab submit -c crabConfig.py
```
This prints a line like `Success: Your task has been submitted` with a task
name under `crab_BranchSummary/`. Note that exact folder name for the next
step.

**7. Check status every few minutes, until it says `COMPLETED`:**
```bash
crab status -d crab_BranchSummary/<task-name-from-step-6>
```
A `FAILED` job here is exactly what this first small test is for catching
cheaply — if it fails, check `crab status --long` and the job log it
points to, since the most likely failure point is the `PSet.py`-rewrite
step in `crab_script.sh`.

**8. Once `COMPLETED`, check the output landed on CERNBox:**
```bash
crab status -d crab_BranchSummary/<task-name-from-step-6> --long
```
or check directly at
https://cernbox.cern.ch/files/spaces/eos/user/k/kraychev/Coffea_Basics/outputs
for `branch_summary.txt`/`branch_summary.root`. Open the `.txt` file and
confirm it lists real branch names (`run`, `luminosityBlock`, `Tau_pt`, ...)
and a sensible event count, not an error message.

**9. Once step 8 looks right, restore the full file list and resubmit:**
```bash
cp ListOfFiles.txt.full ListOfFiles.txt
crab submit -c crabConfig.py
```
This submits 102 separate jobs (one per file, `FileBased` splitting,
`unitsPerJob = 1`), each writing its own `branch_summary.txt`/`.root` to the
same CERNBox output folder.

## Output

Each job's `branch_summary.txt`/`.root` land in
`/store/user/kraychev/Coffea_Basics/outputs/` on `T3_CH_CERNBOX`, visible at
the CERNBox link above once jobs finish and stage out
(`config.General.transferOutputs = True`).
