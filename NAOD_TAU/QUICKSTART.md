# Quick Start: Mass-Point Analysis

## Immediate Usage (No Setup Needed)

### M250 Only (Currently Works)

```bash
cd NAOD_TAU
python mc_tau_analysis.py
# OR explicitly
python mc_tau_analysis.py --mass-point 250
```

Output: `outputs/M250/combined/*.png` and `*.root`

---

## Full Setup (All Mass Points)

### On lxplus (with EOS access):

**Step 1: Find all mass point directories**

```bash
python discover_mass_points.py
```

This auto-scans and creates `mass_points_discovered.json`.

**Step 2: Update config**

```bash
# Copy discovered paths to mass_points_config.json
# Or manually verify each path exists:
find /eos/cms/store/user/mileva/bsm3g/NANOAODSIM \
  -type d -path "*M-500*Run3Summer23_NANOAODv12*0000" \
  | head -1
```

**Step 3: Analyze any mass point**

```bash
python mc_tau_analysis.py --mass-point 500
python mc_tau_analysis.py --mass-point 750
# ... etc
```

**Step 4: Batch analyze all**

```bash
python batch_analyze_all_mass_points.py
```

---

## Key Commands

| Command                                                         | Purpose                     |
| --------------------------------------------------------------- | --------------------------- |
| `python mc_tau_analysis.py`                                     | Analyze M250 (default)      |
| `python mc_tau_analysis.py --mass-point 500`                    | Analyze M500                |
| `python mc_tau_analysis.py --list`                              | Show available mass points  |
| `python discover_mass_points.py`                                | Auto-find all EOS paths     |
| `python batch_analyze_all_mass_points.py`                       | Run M250-M6000 sequentially |
| `python batch_analyze_all_mass_points.py --mass-points 250 500` | Run selected mass points    |

---

## Files Modified/Created

### New Files

- `mass_points_config.json` — Master mass point config
- `helpers/mass_points.py` — Mass point utilities
- `discover_mass_points.py` — Auto-discovery script
- `batch_analyze_all_mass_points.py` — Batch runner
- `MASS_POINTS_SETUP.md` — Detailed documentation

### Modified Files

- `mc_tau_analysis.py` — Added `--mass-point` argument
- `file_config.json` — Auto-generated per mass point

### Unchanged

- `helpers/io.py` — Still uses `file_config.json`
- `helpers/selection.py`, `plotting.py`, etc. — No changes

---

## Current Status

✅ **M250**: Working immediately
⏳ **M500-M6000**: Need timestamp in `mass_points_config.json`

Example timestamp from lxplus:

```
/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/.../Run3Summer23_NANOAODv12/250716_092714/0000
                                                                           ↑
                                                                    Timestamp here
```

---

## Troubleshooting

**Error: "No .root files found"**
→ Check timestamp in `mass_points_config.json` matches actual EOS path

**Error: "Mass point M500 not found"**
→ Update `mass_points_config.json` with actual paths

**Works on lxplus, fails locally?**
→ You need EOS access. Create `file_config.json` manually with local file paths.

---

See `MASS_POINTS_SETUP.md` for complete documentation.
