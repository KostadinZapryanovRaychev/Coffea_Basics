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
