## Quick Setup

**Option A: CERN LCG** (if available)

```bash
source setup.sh
python mc_tau_analysis.py
```

**Option B1: Local Python venv** (recommended)

```bash
cd ..
bash NAOD_TAU/setup_option_b_venv.sh
source .venv_local/bin/activate
python NAOD_TAU/mc_tau_analysis.py
```

**Option B2: Conda** (if conda installed)

```bash
cd ..
bash NAOD_TAU/setup_option_b_conda.sh
conda activate naod-tau
python NAOD_TAU/mc_tau_analysis.py
```

## Run

```bash
python NAOD_TAU/mc_tau_analysis.py
```

## Configuration

Edit **`NAOD_TAU/file_config.json`** to specify ROOT files to process:

```json
{
  "root_files": [
    {
      "name": "nanoaodsim_coffea_1",
      "path": "nanoaodsim_coffea_1.root",
      "tree": "Events",
      "enabled": true
    }
  ]
}
```

**Fields:** `name` (output directory), `path` (file path, relative to project root), `tree` (ROOT tree name), `enabled` (process or skip)

## Output

Histograms saved to `NAOD_TAU/outputs/{file_name}/`:

Methodology: [PhysRevD.111.112004](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004)

The intput files for analysis https://codimd.web.cern.ch/s/LIHpoNf1g

1. bash NAOD_TAU/setup_option_b_venv.sh -- setup the requirements read all from setup_option_b_venv.sh
2. .venv_local/bin/activate ----- activating local venv
3. python NAOD_TAU/mc_tau_analysis.py --- run the analysis of files inside file_config.json

ls -la /eos/cms/store/user/mileva/bsm3g/GStest/ZprimeTo2Tau-2Jets_M-750_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_GS/250503_120139/0000
total 8
drwxr-xr-x. 2 mileva zh 4096 Jun 5 2025 .
drwxr-xr-x. 2 mileva zh 4096 May 3 2025 ..

over there paths and their content:

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-500_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_100139/0000/nanoaodsim_coffea_1.root

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-750_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_102612/0000/nanoaodsim_coffea_1.root

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-1000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_104735/0000/nanoaodsim_coffea_1.root

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-2000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_111643/0000/nanoaodsim_coffea_1.root

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-3000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_124833/0000 - nanoaodsim_coffea_1.root

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-4000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_160008/0000/nanoaodsim_coffea_1.root

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-5000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_130557/0000/nanoaodsim_coffea_1.root

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-6000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250725_100712/0000/nanoaodsim_coffea_1.root

/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-250_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_092714/0000/nanoaodsim_coffea_1.root
