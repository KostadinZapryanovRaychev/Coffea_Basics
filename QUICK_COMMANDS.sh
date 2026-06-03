#!/usr/bin/env bash
# QUICK COMMAND REFERENCE - TAU PAIR BATCH ANALYSIS
# Copy and paste these commands in your terminal

# ============================================================
# SETUP
# ============================================================

# Navigate to project
cd /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea

# Activate Python environment
source .venv_local/bin/activate


# ============================================================
# BATCH PROCESSING (9 MASS POINTS)
# ============================================================

# Option A: ONE COMMAND (Recommended)
bash NAOD_TAU/batch_run_all.sh

# Option B: MANUAL STEPS
# Step 1: Setup config
cp NAOD_TAU/file_config_batch_all_mass_points.json NAOD_TAU/file_config.json

# Step 2: Process all mass points (~1.5 hours)
python NAOD_TAU/batch_runner.py

# Step 3: Generate comparisons (~5 min)
python NAOD_TAU/batch_compare_results.py --all


# ============================================================
# VIEW RESULTS
# ============================================================

# See all outputs
open NAOD_TAU/outputs/

# View specific mass point
open NAOD_TAU/outputs/M-500/

# View summary report
cat NAOD_TAU/outputs/analysis_summary.txt

# View comparison plots
open NAOD_TAU/outputs/mass_point_comparison.png


# ============================================================
# PROCESS SPECIFIC MASS POINTS ONLY
# ============================================================

# Edit config to disable mass points
nano NAOD_TAU/file_config.json
# Set "enabled": false for mass points to skip

# Then run
python NAOD_TAU/batch_runner.py


# ============================================================
# ADVANCED: CUSTOM ANALYSIS
# ============================================================

# Load and analyze ROOT file in Python
python << 'EOF'
import uproot

with uproot.open("NAOD_TAU/outputs/M-500/tau_pair_histograms.root") as f:
    print("Available histograms:")
    print(f.keys())
    
    # Example: access mass histogram
    hist = f["lhe_mass"]
    counts = hist.values()
    edges = hist.axes[0].edges
    print(f"Mass histogram: {len(counts)} bins, {sum(counts)} events")
EOF

# Or in ROOT
root NAOD_TAU/outputs/M-500/tau_pair_histograms.root


# ============================================================
# TROUBLESHOOTING
# ============================================================

# Check EOS access
ls /eos/cms/store/user/mileva/bsm3g/NANOAODSIM/

# Monitor processing
python NAOD_TAU/batch_runner.py 2>&1 | tee batch.log

# Check disk space
du -sh NAOD_TAU/outputs/

# List all PNG files generated
find NAOD_TAU/outputs -name "*.png" | wc -l

# Check ROOT files
find NAOD_TAU/outputs -name "*.root" | xargs ls -lh


# ============================================================
# HELPFUL ONE-LINERS
# ============================================================

# Count histograms per mass point
for dir in NAOD_TAU/outputs/M-*/; do echo "$dir: $(ls $dir/*.png 2>/dev/null | wc -l) PNG files"; done

# View file sizes
du -sh NAOD_TAU/outputs/M-*/ | sort -h

# Check events processed (from ROOT files)
for file in NAOD_TAU/outputs/M-*/tau_pair_histograms.root; do 
    mass=$(basename $(dirname $file))
    echo "$mass: $(root -b -q -x $file 2>/dev/null | grep -c entries)"
done

# Copy results for backup
cp -r NAOD_TAU/outputs ~/Desktop/tau_analysis_backup


# ============================================================
# DOCUMENTATION
# ============================================================

# Read full batch guide
cat NAOD_TAU/BATCH_PROCESSING.md

# Read workflow summary
cat BATCH_WORKFLOW_SUMMARY.md

# Read implementation summary
cat IMPLEMENTATION_SUMMARY.md

# Read main README
cat NAOD_TAU/README.md

# ============================================================
# NOTE: Adjust paths if needed for your system
# ============================================================
