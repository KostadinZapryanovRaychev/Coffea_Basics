# NAOD_TAU Setup Guide

This document explains the two setup options for the NAOD_TAU analysis framework.

## Quick Start

Choose **ONE** option below based on your environment:

### Option A: CERN LCG Environment (Original)

```bash
source NAOD_TAU/setup.sh
python NAOD_TAU/read_nanoaodsim_analysis.py
```

**Best for:** Users on CERN computing infrastructure with access to `/cvmfs/`

**⚠️ Issues?** If this doesn't work, try Option B.

---

### Option B: Local Virtual Environment

Choose **B1** (recommended) or **B2** based on your environment:

#### Option B1: Python venv (Lightweight)

```bash
bash NAOD_TAU/setup_option_b_venv.sh
source .venv_local/bin/activate
python NAOD_TAU/read_nanoaodsim_analysis.py
```

**Best for:**

- macOS and Linux users
- Users who have Python 3.8+ installed
- Minimal disk space requirements

---

#### Option B2: Conda/Mamba (Recommended for reproducibility)

```bash
bash NAOD_TAU/setup_option_b_conda.sh
conda activate naod-tau
python NAOD_TAU/read_nanoaodsim_analysis.py
```

**Best for:**

- Users with conda/mamba installed
- Better dependency management
- Package compatibility guarantees

---

## Detailed Instructions

### Option B1: Local venv Setup

#### Prerequisites

- Python 3.8 or higher
- `pip` (usually comes with Python)

#### Step 1: Run the setup script

```bash
cd /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea
bash NAOD_TAU/setup_option_b_venv.sh
```

This will:

1. ✓ Create a virtual environment at `.venv_local/`
2. ✓ Install all required packages (numpy, awkward, matplotlib, uproot, coffea)
3. ✓ Verify the installation

#### Step 2: Activate the environment

```bash
source .venv_local/bin/activate
```

You should see `(.venv_local)` in your terminal prompt.

#### Step 3: Run the analysis

```bash
python NAOD_TAU/read_nanoaodsim_analysis.py
```

#### To deactivate

```bash
deactivate
```

---

### Option B2: Conda/Mamba Setup

#### Prerequisites

- Miniconda or Mambaforge installed
  - [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html)
  - [Download Mambaforge](https://github.com/conda-forge/mambaforge)

#### Step 1: Run the setup script

```bash
cd /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea
bash NAOD_TAU/setup_option_b_conda.sh
```

This will:

1. ✓ Create a conda environment named `naod-tau`
2. ✓ Install all required packages
3. ✓ Verify the installation

#### Step 2: Activate the environment

```bash
conda activate naod-tau
```

You should see `(naod-tau)` in your terminal prompt.

#### Step 3: Run the analysis

```bash
python NAOD_TAU/read_nanoaodsim_analysis.py
```

#### To deactivate

```bash
conda deactivate
```

#### List your conda environments

```bash
conda env list
```

---

## Troubleshooting

### "Python: command not found"

**Solution:** Use `python3` instead of `python`

```bash
python3 NAOD_TAU/read_nanoaodsim_analysis.py
```

### "ModuleNotFoundError: No module named 'coffea'"

**Solution 1:** Make sure your environment is activated

```bash
# For venv:
source .venv_local/bin/activate

# For conda:
conda activate naod-tau
```

**Solution 2:** Reinstall packages

```bash
# For venv:
pip install -r NAOD_TAU/requirements.txt

# For conda:
conda install -y -n naod-tau numpy matplotlib pytest
conda activate naod-tau
pip install awkward uproot coffea
```

### "Permission denied" when running setup script

```bash
chmod +x NAOD_TAU/setup_option_b_venv.sh
chmod +x NAOD_TAU/setup_option_b_conda.sh
bash NAOD_TAU/setup_option_b_venv.sh
```

### ROOT library not found

This is normal on systems without ROOT installed locally. The `uproot` library handles this.
If you need full ROOT functionality, install it separately:

```bash
# For conda:
conda install -y -n naod-tau root
```

---

## Switching Between Options

You can easily switch between setups in the same terminal session:

```bash
# Deactivate current environment
deactivate          # for venv
# or
conda deactivate    # for conda

# Activate desired environment
source NAOD_TAU/setup.sh           # Option A
source .venv_local/bin/activate    # Option B1
conda activate naod-tau            # Option B2
```

---

## Files Included

| File                      | Purpose                                             |
| ------------------------- | --------------------------------------------------- |
| `setup.sh`                | **Option A:** CERN LCG environment setup (original) |
| `setup_option_b_venv.sh`  | **Option B1:** Create local Python venv             |
| `setup_option_b_conda.sh` | **Option B2:** Create conda environment             |
| `requirements.txt`        | Python package list for pip install                 |
| `SETUP_OPTIONS.md`        | This file                                           |

---

## Environment Details

### Installed Packages

**Core scientific libraries:**

- `numpy>=1.21` - Numerical computing
- `awkward>=2.0` - Jagged array processing
- `matplotlib>=3.5` - Plotting

**Physics/ROOT:**

- `uproot>=5.0` - ROOT file I/O without ROOT
- `coffea>=0.7.0` - High-energy physics analysis framework

**Utilities:**

- `pytest>=7.0` - Testing framework

### Python Version Compatibility

- **Option A:** Python 3.7+
- **Option B1 (venv):** Python 3.8+
- **Option B2 (conda):** Python 3.9 (configurable)

---

## For CERN Users with LCG Issues

If `/cvmfs/` is not available or setup.sh fails:

1. **First, try Option B1 (venv):**

   ```bash
   bash NAOD_TAU/setup_option_b_venv.sh
   ```

2. **If that fails, try Option B2 (conda):**

   ```bash
   bash NAOD_TAU/setup_option_b_conda.sh
   ```

3. **Still having issues?** Check:
   - Python version: `python3 --version` (needs 3.8+)
   - pip availability: `python3 -m pip --version`
   - Internet connection for package downloads

---

## Support

For issues or questions about the setup:

1. Check the **Troubleshooting** section above
2. Verify all prerequisites are installed
3. Run the setup script with verbose output:
   ```bash
   bash -x NAOD_TAU/setup_option_b_venv.sh  # Extra verbose
   ```

---

**Last Updated:** May 2026
