## Quick Setup

Project available on

/eos/user/k/kraychev/Coffea_Basics

```bash
cd ..
bash NAOD_TAU/setup_option_b_venv.sh
source .venv_local/bin/activate
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

## Batch Processing Multiple Mass Points

To process more mass points (250 GeV to 6000 GeV) at once with organized outputs:

```bash
source .venv_local/bin/activate
cp NAOD_TAU/file_config_batch_all_mass_points.json NAOD_TAU/file_config.json
python NAOD_TAU/generate_batch_config.py

# Run batch analysis (processes each mass point sequentially)
python NAOD_TAU/batch_runner.py

# in progress
( python NAOD_TAU/batch_compare_results.py --all )
```

Results will be organized in:

```
outputs/M-250/   → histograms for M-250 GeV
outputs/M-500/   → histograms for M-500 GeV
outputs/M-750/   → histograms for M-750 GeV
... (and so on for all mass points)
```

Methodology: [PhysRevD.111.112004](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004)

The Plan 17.07.26

1. To understand the structure of NANOAOD data and how they are related to real physics
2. To start using Root and Python and to compare the results from both
3. To Figure out what we have and what we can do with this
4. To save all the results in root files ( C files )
