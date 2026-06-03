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

## Batch Processing Multiple Mass Points

To process all 9 mass points (250 GeV to 6000 GeV) with organized outputs:

```bash
# Activate environment first
source .venv_local/bin/activate

# Option 1: Use pre-configured batch file
cp NAOD_TAU/file_config_batch_all_mass_points.json NAOD_TAU/file_config.json

# Option 2: Generate configuration automatically
python NAOD_TAU/generate_batch_config.py

# Run batch analysis (processes each mass point sequentially)
python NAOD_TAU/batch_runner.py

# Compare results across all mass points
python NAOD_TAU/batch_compare_results.py --all
```

Results will be organized in:

```
outputs/M-250/   → histograms for M-250 GeV
outputs/M-500/   → histograms for M-500 GeV
outputs/M-750/   → histograms for M-750 GeV
... (and so on for all mass points)
```

See [BATCH_PROCESSING.md](BATCH_PROCESSING.md) for detailed batch workflow documentation.

## Output

Histograms saved to `NAOD_TAU/outputs/{file_name}/`:

Methodology: [PhysRevD.111.112004](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004)
