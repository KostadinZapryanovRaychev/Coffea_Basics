# Batch Processing Multiple Mass Points

This guide explains how to process all 9 mass points (250 GeV to 6000 GeV) sequentially, with results organized by mass point.

## Quick Start

### 1. Generate Configuration

```bash
# Generate file_config.json with all 9 mass points
python NAOD_TAU/generate_batch_config.py
```

This creates `file_config.json` with:

- All 9 EOS file paths (250, 500, 750, 1000, 2000, 3000, 4000, 5000, 6000 GeV)
- Each mass point marked as enabled
- Output folders named by mass point: `M-250`, `M-500`, etc.

### 2. Run Batch Analysis

```bash
# Process all mass points one by one
python NAOD_TAU/batch_runner.py
```

This will:

- Process each mass point sequentially
- Create `outputs/M-XXX/` folder for each mass point
- Save histograms (PNG + ROOT) in each folder
- Display progress and status for each mass point

**Typical processing time:** ~5-10 minutes per mass point (depending on file size and system)

### 3. Compare Results Across Mass Points

```bash
# Generate summary report
python NAOD_TAU/batch_compare_results.py --report

# Generate comparison plots
python NAOD_TAU/batch_compare_results.py --compare

# Generate both
python NAOD_TAU/batch_compare_results.py --all
```

## Output Structure

After running batch analysis:

```
NAOD_TAU/
├── outputs/
│   ├── M-250/
│   │   ├── lhe_mass.png
│   │   ├── lhe_tau_pt.png
│   │   ├── lhe_antitau_pt.png
│   │   ├── ... (all histograms for M-250)
│   │   └── tau_pair_histograms.root
│   ├── M-500/
│   │   ├── lhe_mass.png
│   │   ├── lhe_tau_pt.png
│   │   ├── ... (all histograms for M-500)
│   │   └── tau_pair_histograms.root
│   ├── M-750/
│   ├── M-1000/
│   ├── M-2000/
│   ├── M-3000/
│   ├── M-4000/
│   ├── M-5000/
│   ├── M-6000/
│   ├── analysis_summary.txt
│   └── mass_point_comparison.png
```

## Workflow

### Step-by-Step

1. **Generate Configuration**

   ```bash
   python NAOD_TAU/generate_batch_config.py
   ```

   Review the generated `file_config.json` to ensure all mass points are listed.

2. **Process Batch**

   ```bash
   python NAOD_TAU/batch_runner.py
   ```

   Sit back and wait. Each mass point is processed individually with status updates.

3. **Analyze Individual Mass Point**

   ```bash
   # View histograms for M-500
   open NAOD_TAU/outputs/M-500/
   ```

   Each folder contains all histograms with statistics displayed.

4. **Compare All Mass Points**
   ```bash
   python NAOD_TAU/batch_compare_results.py --all
   ```
   Generates:
   - `analysis_summary.txt`: Text summary of all mass points
   - `mass_point_comparison.png`: Overlay comparison plots

## Key Features

### Individual Analysis

- Each mass point has its own folder with complete histogram set
- Statistics displayed on each PNG (events, particles)
- ROOT files for further ROOT-based analysis

### Batch Comparison

- Automatically detects all processed mass points
- Generates comparison plots showing mass dependence
- Creates summary report with file sizes and statistics

### Progress Tracking

- Real-time logging of each mass point
- Status updates during processing
- Final summary with success/failure counts

## Configuration File Format

`file_config.json` structure:

```json
{
  "root_files": [
    {
      "name": "M-500",
      "path": "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/..../nanoaodsim_coffea_1.root",
      "tree": "Events",
      "enabled": true
    },
    ...
  ]
}
```

- `name`: Used for output folder name
- `path`: EOS file path (absolute path works)
- `tree`: ROOT tree name (usually "Events")
- `enabled`: Set to `false` to skip a mass point

### Enable/Disable Mass Points

To process only specific mass points, edit `file_config.json`:

```json
{
  "root_files": [
    {
      "name": "M-500",
      "path": "...",
      "enabled": true // Process
    },
    {
      "name": "M-750",
      "path": "...",
      "enabled": false // Skip
    }
  ]
}
```

Then run: `python NAOD_TAU/batch_runner.py`

## Advanced Options

### Process Specific Mass Point Only

Edit `file_config.json` to disable all others, then run:

```bash
python NAOD_TAU/batch_runner.py
```

### Generate Custom Configuration

You can manually edit `file_config.json` to:

- Add/remove mass points
- Change output folder names
- Enable/disable specific files

### Combine All Results

After all mass points are processed:

```bash
python NAOD_TAU/batch_compare_results.py --all
```

This creates comparison plots showing tau pair properties across mass points.

## Troubleshooting

### File Not Found

If a file path doesn't work:

1. Check that EOS is mounted (check if `/eos/...` is accessible)
2. Verify path is correct in `file_config.json`
3. Mark as `"enabled": false` to skip and continue

### Out of Memory

If processing fails:

- Process fewer mass points at a time
- Reduce histogram bin counts (edit `plotting.py`)
- Process on a machine with more RAM

### Results Not Generated

Check the log output:

```bash
python NAOD_TAU/batch_runner.py 2>&1 | tee batch_analysis.log
```

This saves logs to `batch_analysis.log` for troubleshooting.

## Analysis Tips

### Comparing Mass Dependence

1. Process all mass points using batch runner
2. Generate comparison plots: `python batch_compare_results.py --compare`
3. Look for trends in histogram distributions
4. Use ROOT files for detailed statistical tests

### Individual Mass Point Deep Dive

```bash
# View all histograms for M-500
ls -la NAOD_TAU/outputs/M-500/

# Open ROOT file in ROOT
root NAOD_TAU/outputs/M-500/tau_pair_histograms.root
```

### Custom Analysis Script

Create a custom analysis script that loads ROOT files:

```python
import uproot

# Load all mass points
for mass in [250, 500, 750, 1000, 2000, 3000, 4000, 5000, 6000]:
    root_file = f"NAOD_TAU/outputs/M-{mass}/tau_pair_histograms.root"
    with uproot.open(root_file) as f:
        # Your custom analysis here
        pass
```

## See Also

- [Main README](README.md) - General setup and usage
- [file_config.json](file_config.json) - Configuration reference
- `batch_runner.py` - Source code for batch processing
- `batch_compare_results.py` - Source code for comparison plots
