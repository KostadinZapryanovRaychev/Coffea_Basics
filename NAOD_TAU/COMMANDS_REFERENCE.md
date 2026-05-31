# Mass-Point Analysis: Command Reference

## Current Status (May 30, 2026)

✅ **M250**: Fully working - ready to use immediately
❌ **M500-M6000**: Need EOS path updates

---

## Immediate Usage (M250)

```bash
cd NAOD_TAU
python mc_tau_analysis.py
```

✅ Works immediately (verified on lxplus)

- Input: `/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/.../M-250.../250716_092714/0000/`
- Output: `outputs/M250/combined/*.png` and `*.root`

---

## Using Other Mass Points (After Setup)

### Step 1: Get EOS Paths (on lxplus)

**Option A: Auto-discover** (recommended)

```bash
python discover_mass_points.py
cat mass_points_discovered.json
```

**Option B: Manual lookup for specific mass point**

```bash
# For M500
find /eos/cms/store/user/mileva/bsm3g/NANOAODSIM \
  -type d -name "*M-500*" -path "*Run3Summer23_NANOAODv12*0000" | head -1

# Output should look like:
# /eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-500_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250719_153045/0000
```

### Step 2: Update `mass_points_config.json`

Open `mass_points_config.json` and replace the timestamp placeholders:

**Before**:

```json
{
  "500": {
    "eos_base_path": "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/.../Run3Summer23_NANOAODv12/YYYYMMDD_HHMMSS/0000",
    "enabled": false
  }
}
```

**After** (using example from Step 1):

```json
{
  "500": {
    "eos_base_path": "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-500_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250719_153045/0000",
    "enabled": true
  }
}
```

### Step 3: Run Analysis for That Mass Point

```bash
python mc_tau_analysis.py --mass-point 500
```

Output: `outputs/M500/combined/`

---

## Batch Commands

### List All Mass Points

```bash
python mc_tau_analysis.py --list
```

Output:

```
Available mass points:
  M250
  M500
  M750
  M1000
  M2000
  M3000
  M4000
  M5000
  M6000
```

### Analyze Single Mass Point

```bash
python mc_tau_analysis.py --mass-point 250
python mc_tau_analysis.py --mass-point M500   # M prefix optional
python mc_tau_analysis.py --mass-point 750
```

### Batch Analyze All (After All Paths Updated)

```bash
python batch_analyze_all_mass_points.py
```

Analyzes M250-M6000 sequentially, saves results to:

- `outputs/M250/combined/`
- `outputs/M500/combined/`
- ...
- `outputs/M6000/combined/`

### Batch Analyze Selected Mass Points

```bash
python batch_analyze_all_mass_points.py --mass-points 250 500 750
```

### Resume Batch Analysis

```bash
# If batch analysis stopped at M1000, resume from there
python batch_analyze_all_mass_points.py --start-from M1000
```

---

## Typical Workflow on lxplus

### First Time Setup

```bash
# 1. Get all EOS paths
python discover_mass_points.py

# 2. Review discovered paths
cat mass_points_discovered.json

# 3. Update config (edit mass_points_config.json)
# Copy paths from discovered JSON, update "enabled": true

# 4. Test one mass point
python mc_tau_analysis.py --mass-point 500

# 5. If step 4 works, batch process all
python batch_analyze_all_mass_points.py
```

### Later Usage

```bash
# Analyze single mass point
python mc_tau_analysis.py --mass-point 500

# Analyze all
python batch_analyze_all_mass_points.py

# Analyze selected only
python batch_analyze_all_mass_points.py --mass-points 250 500 1000
```

---

## Output Structure

After running analysis:

```
outputs/
├── M250/
│   └── combined/
│       ├── tau_pair_histograms.png
│       ├── tau_pair_histograms.root
│       └── [other histogram files]
├── M500/
│   └── combined/
│       ├── tau_pair_histograms.png
│       └── ...
├── ...
└── M6000/
    └── combined/
        └── ...
```

Each mass point has isolated output directory.

---

## Common Issues & Solutions

### Issue: "No .root files found"

```
[ERROR] No ROOT files found in /eos/cms/store/.../YYYYMMDD_HHMMSS/0000
```

**Solution**: Timestamp in `mass_points_config.json` is wrong.

- Get correct timestamp: `find /eos/cms/store/user/mileva/bsm3g/NANOAODSIM -name "*M-500*" ...`
- Update `mass_points_config.json`
- Try again

### Issue: "Mass point M500 not found"

```
Mass point M500 not found. Available: ['250', '500', ...]
```

**Solution**: Mass point config missing or `enabled` is `false`.

- Check `mass_points_config.json` has the mass point
- Set `"enabled": true`
- Try again

### Issue: "Cannot access EOS paths"

```
[ERROR] Cannot access EOS paths for M250
Check that you're on lxplus with EOS access
```

**Solution**: Script requires lxplus environment.

- Only runs on lxplus with `/eos/cms/store/` mounted
- For local dev: manually create `file_config.json` with local file paths

### Issue: Analysis runs slow

```
Loading 97458 events...
[takes very long time]
```

**Solution**: Normal for large datasets. Progress logged as analysis runs.

- Each mass point takes 5-30 minutes depending on size
- M250 (97k events) ≈ 10-15 minutes
- Batch mode processes sequentially (not parallel)

---

## Configuration Files Explained

### `mass_points_config.json` (Master Config)

Contains metadata for all 9 mass points:

- Mass in GeV
- Number of events
- Memory needed
- Cross sections
- **EOS paths** (needs YYYYMMDD_HHMMSS updates)
- Enable/disable flags

**Edit this to enable/disable mass points and update paths.**

### `file_config.json` (Auto-Generated)

Generated dynamically when `--mass-point` specified.

```json
{
  "root_files": [
    {
      "name": "ZprimeTo2Tau_M250_1",
      "path": "/eos/cms/store/.../nanoaodsim_coffea_1.root",
      "tree": "Events",
      "enabled": true
    },
    ...
  ]
}
```

**Do NOT edit manually** - auto-generated per mass point.

### `mass_points_discovered.json` (Discovery Output)

Generated by `discover_mass_points.py` on lxplus.
Shows all discovered mass points and their actual EOS paths.
Use this to populate `mass_points_config.json`.

---

## Verification Checklist

Before running batch analysis:

- [ ] Can access `/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/`
- [ ] Found all 9 mass point directories
- [ ] Updated `mass_points_config.json` with actual EOS paths
- [ ] Tested `python mc_tau_analysis.py --mass-point 250` → ✓ works
- [ ] Tested `python mc_tau_analysis.py --mass-point 500` → ✓ works
- [ ] Ready to run: `python batch_analyze_all_mass_points.py`

---

## More Information

- **Quick Start**: See `QUICKSTART.md`
- **Complete Setup**: See `MASS_POINTS_SETUP.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Source Code**: See `helpers/mass_points.py`

---

## Questions?

1. **How do I know which timestamp is correct?**
   - Use `discover_mass_points.py` to find it automatically
   - Or use `find` command to look in `/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/`

2. **Can I analyze multiple mass points in parallel?**
   - Current: Sequential only (batch runner does one-by-one)
   - Could be extended: Modify `batch_analyze_all_mass_points.py` to use `ProcessPoolExecutor`

3. **Can I combine results from multiple mass points?**
   - Each has isolated output in `outputs/M{mass}/combined/`
   - Post-processing script needed to merge across mass points

4. **What if analysis fails partway?**
   - Use `--start-from M{mass}` to resume from that point
   - Example: `python batch_analyze_all_mass_points.py --start-from M750`
