# Mass-Point Aware Analysis Setup

## Overview

The analysis has been refactored to handle multiple mass points (M250, M500, M750, M1000, M2000, M3000, M4000, M5000, M6000) through a single `mc_tau_analysis.py` script with mass point selection.

## Configuration Files

### 1. `mass_points_config.json` (Master Configuration)

Contains metadata for all mass points:

- Mass point in GeV
- Number of events
- Memory footprint
- Cross section (where available)
- EOS path to NANOAODSIM files
- Enable/disable flag

**Currently**: Only M250 has a verified EOS path. Other mass points need `YYYYMMDD_HHMMSS` timestamps.

### 2. `file_config.json` (Auto-Generated)

Generated dynamically when analyzing a specific mass point. Contains:

- List of .root files for that mass point
- File paths (absolute EOS paths)
- Tree name ("Events")
- Metadata

---

## Usage

### Option A: Analyze a Specific Mass Point

```bash
# M250 (verified working)
python mc_tau_analysis.py --mass-point 250

# Alternative format
python mc_tau_analysis.py --mass-point M500

# Normalized internally to remove 'M' prefix
```

**What happens:**

1. Script loads M{mass_point} config from `mass_points_config.json`
2. Discovers all .root files in the EOS directory
3. Generates `file_config.json` with those files
4. Runs standard tau-pair analysis
5. Saves output to `outputs/M{mass_point}/combined/`

### Option B: Default Analysis (Current file_config.json)

```bash
python mc_tau_analysis.py
```

Uses whatever is in `file_config.json` (no mass point switching).

### Option C: List Available Mass Points

```bash
python mc_tau_analysis.py --list
```

Shows M250-M6000 availability.

---

## Setup on lxplus

### Step 1: Update EOS Paths

On lxplus, find the timestamp directories for each mass point:

```bash
# Example for M500
find /eos/cms/store/user/mileva/bsm3g/NANOAODSIM \
  -type d -name "*M-500*" | grep "Run3Summer23_NANOAODv12" | grep "0000"
```

Output will be something like:

```
/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-500.../Run3Summer23_NANOAODv12/250719_153045/0000
```

Update `mass_points_config.json` with the timestamp (`250719_153045`).

### Step 2: Auto-Discover (Optional)

On lxplus, run the discovery script:

```bash
python discover_mass_points.py
```

This scans all NANOAODSIM directories and generates `mass_points_discovered.json` with all paths. You can then manually merge into `mass_points_config.json`.

### Step 3: Verify and Test

```bash
python mc_tau_analysis.py --mass-point 250  # Should work immediately
python mc_tau_analysis.py --mass-point 500  # After updating path in config
```

---

## File Structure

```
NAOD_TAU/
├── mc_tau_analysis.py           # Main script (now mass-point aware)
├── file_config.json             # Auto-generated for selected mass point
├── mass_points_config.json      # Master config with all mass points
├── discover_mass_points.py      # Helper to find all EOS paths
├── helpers/
│   ├── io.py                    # Unchanged (uses file_config.json)
│   ├── mass_points.py           # NEW: Mass point management
│   ├── selection.py
│   ├── plotting.py
│   └── ...
└── outputs/
    ├── M250/
    │   └── combined/            # M250 histograms
    ├── M500/
    │   └── combined/            # M500 histograms
    └── combined/                # Default output (no mass point)
```

---

## Current Status

✅ **M250**: Fully working with verified EOS path
❌ **M500-M6000**: Need `YYYYMMDD_HHMMSS` timestamps in `mass_points_config.json`

### To Enable Other Mass Points

Edit `mass_points_config.json` and replace `YYYYMMDD_HHMMSS` with actual timestamp:

```json
{
  "500": {
    "mass_gev": 500,
    "eos_base_path": "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/.../Run3Summer23_NANOAODv12/250719_153045/0000",
    "enabled": true
  }
}
```

---

## Key Features

- **Single command**: `python mc_tau_analysis.py --mass-point 500`
- **Auto file discovery**: Finds all .root files in the target EOS directory
- **Combined analysis**: Merges all files and produces histograms
- **Isolated output**: Each mass point has its own output directory
- **No code changes**: Just config updates needed

---

## Example Workflow

```bash
# On lxplus
$ python mc_tau_analysis.py --mass-point 250

2026-05-30 16:45:00 - __main__ - INFO - ============================================================
2026-05-30 16:45:00 - __main__ - INFO - MASS POINT ANALYSIS: M250
2026-05-30 16:45:00 - __main__ - INFO - ============================================================
2026-05-30 16:45:01 - __main__ - INFO - ✓ M250: Found 2 .root files
2026-05-30 16:45:02 - __main__ - INFO - Generating file_config.json for M250...
2026-05-30 16:45:02 - __main__ - INFO - Saved M250 config to /path/to/file_config.json
2026-05-30 16:45:03 - __main__ - INFO - Loading file configuration...
2026-05-30 16:45:03 - __main__ - INFO - ✓ Configuration loaded
2026-05-30 16:45:04 - __main__ - INFO - ============================================================
2026-05-30 16:45:04 - __main__ - INFO - COMBINED ANALYSIS MODE - MERGING ALL ROOT FILES
2026-05-30 16:45:04 - __main__ - INFO - ============================================================
...
2026-05-30 17:02:15 - __main__ - INFO - ✓ M250 ANALYSIS COMPLETED SUCCESSFULLY
2026-05-30 17:02:15 - __main__ - INFO -   Output directory: outputs/M250/combined/
```

---

## Troubleshooting

**Error: "No .root files found in {path}"**

- Check EOS path in `mass_points_config.json`
- Verify timestamp directory exists: `ls /eos/cms/store/.../Run3Summer23_NANOAODv12/YYYYMMDD_HHMMSS/0000/`

**Error: "Mass point M{X} not found"**

- Mass point not in `mass_points_config.json`
- Run `python mc_tau_analysis.py --list` to see available mass points

**Error: "Cannot access EOS paths"**

- Only works on lxplus with EOS mounted
- For local development, manually create `file_config.json` with local paths

---

## Next Steps

1. **Update timestamps**: Get actual `YYYYMMDD_HHMMSS` for M500-M6000 on lxplus
2. **Test all mass points**: `python mc_tau_analysis.py --mass-point {M250..M6000}`
3. **Batch analysis**: Create wrapper script to analyze all mass points sequentially
