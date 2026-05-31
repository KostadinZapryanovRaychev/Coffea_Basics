# Mass-Point Analysis Implementation Summary

## What Changed

### Overview

Refactored the tau-pair analysis to be **mass-point aware**, allowing analysis of Z' → 2τ across multiple mass points (M250-M6000) using a single configuration and script.

### New Architecture

```
mc_tau_analysis.py [--mass-point M250]
    ↓
mass_points.py (new helper)
    ↓ (selects mass point config)
mass_points_config.json (master config)
    ↓ (extracts files from EOS)
file_config.json (auto-generated)
    ↓ (standard analysis)
io.py (unchanged)
    ↓
outputs/M{mass_point}/combined/
```

---

## Files Created

### 1. **`mass_points_config.json`**

Master configuration with all 9 mass points (250, 500, 750, 1000, 2000, 3000, 4000, 5000, 6000)

- Mass in GeV
- Event counts
- Memory estimates
- Cross sections
- EOS paths (NANOAODSIM format)
- Enable/disable flags

**Status**: M250 verified working; others need timestamp updates

### 2. **`helpers/mass_points.py`** (New Module)

Utilities for mass point management:

- `load_mass_points_config()` — Load master config
- `get_available_mass_points()` — List available masses
- `validate_mass_point_paths()` — Check EOS access
- `create_mass_point_file_config()` — Generate file_config.json
- `save_mass_point_config()` — Save config to disk

### 3. **`discover_mass_points.py`** (Script)

Auto-discovery of EOS paths for all mass points

- Scans `/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/`
- Finds latest timestamp directories
- Outputs `mass_points_discovered.json`
- **Run on lxplus only** (requires EOS access)

### 4. **`batch_analyze_all_mass_points.py`** (Script)

Batch runner for sequential analysis

- Analyzes M250-M6000 one by one
- Isolated output directories per mass point
- Resume capability (`--start-from M500`)
- Summary report at end

### 5. **`MASS_POINTS_SETUP.md`** (Documentation)

Comprehensive guide:

- Configuration details
- Usage instructions
- Setup procedure on lxplus
- Troubleshooting

### 6. **`QUICKSTART.md`** (Quick Reference)

Fast start guide with key commands

---

## Files Modified

### **`mc_tau_analysis.py`**

**Changes**:

- Added `argparse` argument parsing
- Added `--mass-point` argument for mass point selection
- Added `--list` flag to show available mass points
- Auto-generate `file_config.json` for selected mass point
- Output to mass-point-specific directory (`outputs/M{mass}/`)
- Backward compatible (default behavior unchanged)

**New command line interface**:

```bash
python mc_tau_analysis.py                    # Default (M250)
python mc_tau_analysis.py --mass-point 500  # Analyze M500
python mc_tau_analysis.py --list             # Show available mass points
```

### **`file_config.json`**

- Still contains M250 configuration for default/fallback use
- Auto-generated when `--mass-point` specified
- Unchanged format (backward compatible with `io.py`)

---

## Backward Compatibility

✅ **Fully backward compatible**

- Default behavior: `python mc_tau_analysis.py` still analyzes M250
- Existing `file_config.json` still works
- No changes to `io.py`, `selection.py`, or other helpers
- Can revert to old behavior anytime by removing `--mass-point` argument

---

## Current Status

| Mass Point | Status     | EOS Path                      | Notes                       |
| ---------- | ---------- | ----------------------------- | --------------------------- |
| M250       | ✅ Ready   | `/eos/.../250716_092714/0000` | Fully tested, working       |
| M500       | ⏳ Pending | Needs timestamp               | See mass_points_config.json |
| M750       | ⏳ Pending | Needs timestamp               | See mass_points_config.json |
| M1000      | ⏳ Pending | Needs timestamp               | See mass_points_config.json |
| M2000      | ⏳ Pending | Needs timestamp               | See mass_points_config.json |
| M3000      | ⏳ Pending | Needs timestamp               | See mass_points_config.json |
| M4000      | ⏳ Pending | Needs timestamp               | See mass_points_config.json |
| M5000      | ⏳ Pending | Needs timestamp               | See mass_points_config.json |
| M6000      | ⏳ Pending | Needs timestamp               | See mass_points_config.json |

---

## Usage Quick Reference

### Single Mass Point Analysis

```bash
python mc_tau_analysis.py --mass-point 250
python mc_tau_analysis.py --mass-point M500
```

### Batch Analysis

```bash
# All mass points (M250-M6000)
python batch_analyze_all_mass_points.py

# Selected mass points
python batch_analyze_all_mass_points.py --mass-points 250 500 750

# Resume from specific point
python batch_analyze_all_mass_points.py --start-from M500
```

### Discovery

```bash
# On lxplus: auto-find all paths
python discover_mass_points.py

# Creates mass_points_discovered.json
# Copy paths to mass_points_config.json
```

---

## Next Steps (To Enable All Mass Points)

### On lxplus:

1. **Auto-discover** (recommended):

   ```bash
   python discover_mass_points.py
   ```

2. **Or manually** find timestamps:

   ```bash
   # For each mass point M500, M750, etc.
   find /eos/cms/store/user/mileva/bsm3g/NANOAODSIM \
     -type d -path "*M-500*Run3Summer23_NANOAODv12*0000"
   ```

3. **Update** `mass_points_config.json`:

   ```json
   {
     "500": {
       "eos_base_path": "/eos/.../M-500.../Run3Summer23_NANOAODv12/YYYYMMDD_HHMMSS/0000",
       "enabled": true
     }
   }
   ```

4. **Test**:

   ```bash
   python mc_tau_analysis.py --mass-point 500
   ```

5. **Batch process**:
   ```bash
   python batch_analyze_all_mass_points.py
   ```

---

## File Structure (Updated)

```
NAOD_TAU/
├── mc_tau_analysis.py                    [MODIFIED: Added --mass-point]
├── file_config.json                      [Default M250]
├── mass_points_config.json               [NEW: Master config]
├── discover_mass_points.py               [NEW: Auto-discovery]
├── batch_analyze_all_mass_points.py      [NEW: Batch runner]
├── MASS_POINTS_SETUP.md                  [NEW: Detailed docs]
├── QUICKSTART.md                         [NEW: Quick start]
├── helpers/
│   ├── mass_points.py                    [NEW: Mass point utilities]
│   ├── io.py                             [UNCHANGED]
│   ├── selection.py                      [UNCHANGED]
│   ├── plotting.py                       [UNCHANGED]
│   └── ...
├── outputs/
│   ├── M250/
│   │   └── combined/
│   ├── M500/
│   │   └── combined/
│   └── ...
└── ...
```

---

## Key Design Decisions

1. **Single config file** (`mass_points_config.json`): Master source for all mass points
2. **Dynamic file discovery**: Auto-finds .root files in EOS directory
3. **Auto-generated `file_config.json`**: No manual per-mass-point config needed
4. **Mass-specific output dirs**: Keep analyses organized (`outputs/M250/`, `outputs/M500/`, etc.)
5. **Backward compatible**: Default behavior unchanged for existing workflows
6. **Optional batch runner**: Separate script for all-at-once processing

---

## Testing Status

✅ **Code structure**: Created and verified
✅ **M250 integration**: Working (verified on lxplus)
⏳ **M500-M6000**: Awaiting timestamp updates in `mass_points_config.json`

---

## Troubleshooting

| Problem                | Solution                                            |
| ---------------------- | --------------------------------------------------- |
| "No .root files found" | Update timestamp in `mass_points_config.json`       |
| "Mass point not found" | Run `python mc_tau_analysis.py --list`              |
| "Cannot access EOS"    | Script only works on lxplus with mounted EOS        |
| Want local testing?    | Manually create `file_config.json` with local paths |

---

## References

- **Quick Start**: See `QUICKSTART.md`
- **Complete Guide**: See `MASS_POINTS_SETUP.md`
- **Code**: `helpers/mass_points.py` for implementation details
