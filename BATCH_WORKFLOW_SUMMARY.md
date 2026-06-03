# Complete Batch Processing Workflow

## Your Setup

You have **9 mass points** of Z' → ττ events:

- M-250 GeV
- M-500 GeV
- M-750 GeV
- M-1000 GeV
- M-2000 GeV
- M-3000 GeV
- M-4000 GeV
- M-5000 GeV
- M-6000 GeV

Each will be:

1. ✅ Processed individually
2. ✅ Saved in separate folder (`outputs/M-XXX/`)
3. ✅ Generated with tau pair histograms + statistics
4. ✅ Compared across all mass points

---

## Quick Start (5 minutes)

### Option A: Automated (Recommended)

```bash
cd /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea
bash NAOD_TAU/batch_run_all.sh
```

Done! Results will be in `NAOD_TAU/outputs/`

### Option B: Manual Steps

**1. Activate environment**

```bash
cd /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea
source .venv_local/bin/activate
```

**2. Copy batch configuration**

```bash
cp NAOD_TAU/file_config_batch_all_mass_points.json NAOD_TAU/file_config.json
```

**3. Process all mass points**

```bash
python NAOD_TAU/batch_runner.py
```

(Takes ~1-2 hours total)

**4. Generate comparison plots**

```bash
python NAOD_TAU/batch_compare_results.py --all
```

---

## Output Structure

After batch processing, you'll have:

```
NAOD_TAU/outputs/
├── M-250/
│   ├── lhe_mass.png                    ← Mass distribution with statistics
│   ├── lhe_tau_pt.png                  ← τ⁻ pT distribution
│   ├── lhe_antitau_pt.png              ← τ⁺ pT distribution
│   ├── lhe_tau_eta.png, lhe_tau_phi.png
│   ├── lhe_antitau_eta.png, lhe_antitau_phi.png
│   ├── lhe_delta_r_ditau_pair.png      ← τ pair separation
│   ├── lhe_delta_phi.png               ← Angular difference
│   ├── lhe_delta_eta_ditau_pair.png
│   ├── lhe_cos_delta_phi.png
│   ├── lhe_delta_r_vs_delta_phi_2d.png ← 2D distribution
│   ├── tau_pair_histograms.root        ← ROOT file for detailed analysis
│
├── M-500/  (same structure)
├── M-750/  (same structure)
├── M-1000/ (same structure)
├── M-2000/ (same structure)
├── M-3000/ (same structure)
├── M-4000/ (same structure)
├── M-5000/ (same structure)
├── M-6000/ (same structure)
│
├── analysis_summary.txt                ← Summary statistics for all mass points
└── mass_point_comparison.png           ← Overlaid comparison plots
```

---

## Key Features of Generated Plots

Every PNG histogram includes:

```
Title:        "LHE τ⁻ Transverse Momentum Distribution (M=500 GeV)"
Axes:         Properly labeled with units
Statistics:
  • Events analyzed: 12,345
  • Particles analyzed: 24,690
  • Particles in histogram: 24,690
```

The statistics box shows:

- **Events**: Total number of events processed
- **Particles**: Total particles of this type
- **In histogram**: Actual entries in the plot

---

## Analysis Workflow

### Individual Mass Point Analysis

```bash
# View all histograms for M-500
open NAOD_TAU/outputs/M-500/

# Or list them
ls -la NAOD_TAU/outputs/M-500/*.png
```

Each PNG displays:

- Particle count
- Event count
- Distribution shape
- Statistical information

### Compare Across Mass Points

```bash
# Generate comparison report
python NAOD_TAU/batch_compare_results.py --report

# View summary
cat NAOD_TAU/outputs/analysis_summary.txt

# View comparison plots
open NAOD_TAU/outputs/mass_point_comparison.png
```

This shows:

- How distributions change with mass
- Trends in tau pair properties
- File sizes and statistics

### Advanced: ROOT Analysis

```bash
# Examine ROOT files directly
root NAOD_TAU/outputs/M-500/tau_pair_histograms.root
# or in Python:
import uproot
with uproot.open("NAOD_TAU/outputs/M-500/tau_pair_histograms.root") as f:
    print(f.keys())
    hist = f["lhe_mass"]
    # Your analysis here
```

---

## Timing

| Task                   | Time           |
| ---------------------- | -------------- |
| Setup                  | 1 min          |
| Process M-250          | 5-8 min        |
| Process M-500          | 5-8 min        |
| ... (each mass point)  | ~6 min avg     |
| **Total for 9 points** | **~1.5 hours** |
| Generate comparisons   | 5 min          |

---

## Customization

### Process Only Specific Mass Points

Edit `NAOD_TAU/file_config.json`:

```json
{
  "root_files": [
    {
      "name": "M-500",
      "path": "...",
      "enabled": true // ✓ Process
    },
    {
      "name": "M-750",
      "path": "...",
      "enabled": false // ✗ Skip
    }
  ]
}
```

Then run: `python batch_runner.py`

### Regenerate Configuration

```bash
python NAOD_TAU/generate_batch_config.py
```

This creates fresh `file_config.json` with current EOS paths.

---

## Troubleshooting

### "File not found" errors

- Ensure EOS is mounted: `ls /eos/cms/store/...`
- Check network connectivity
- Try on LXPLUS if running locally

### Processing hangs

- Check memory: `top` or `Activity Monitor`
- Try processing fewer mass points at once
- Increase timeout in `batch_runner.py`

### No output generated

- Check logs: run with `2>&1 | tee batch.log`
- Verify tau pair selection: check event counts in log
- Ensure output directory is writable: `ls -la NAOD_TAU/outputs/`

---

## Next Steps After Batch Processing

1. **Visualize Results**

   ```bash
   open NAOD_TAU/outputs/M-500/
   ```

2. **Study Mass Dependence**
   - Open comparison plots
   - Note trends in distributions
   - Calculate ratios across mass points

3. **Statistical Analysis**

   ```bash
   python NAOD_TAU/batch_compare_results.py --all
   cat NAOD_TAU/outputs/analysis_summary.txt
   ```

4. **Custom Analysis**
   - Load ROOT files in Python/ROOT
   - Perform differential studies
   - Generate publication plots

5. **Merge Results**
   - Combine mass points for overall analysis
   - Create mass-weighted distributions
   - Parameterize mass dependence

---

## Files Created

| File                                     | Purpose                         |
| ---------------------------------------- | ------------------------------- |
| `generate_batch_config.py`               | Generate config from EOS paths  |
| `batch_runner.py`                        | Main batch processing script    |
| `batch_compare_results.py`               | Comparison & summary generation |
| `batch_run_all.sh`                       | One-command batch runner        |
| `BATCH_PROCESSING.md`                    | Detailed batch documentation    |
| `file_config_batch_all_mass_points.json` | Pre-configured batch config     |

---

## Documentation

- [BATCH_PROCESSING.md](BATCH_PROCESSING.md) — Detailed batch workflow guide
- [README.md](README.md) — General setup and usage
- Source: `batch_runner.py`, `batch_compare_results.py`

---

## Questions?

See: [BATCH_PROCESSING.md](BATCH_PROCESSING.md) for detailed documentation
