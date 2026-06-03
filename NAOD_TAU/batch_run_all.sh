#!/bin/bash
# Quick Reference: Batch Processing All Mass Points
# Run this in your terminal to process all 9 mass points sequentially

cd /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea

echo "==============================================="
echo "TAU PAIR ANALYSIS - BATCH PROCESSING"
echo "Processing 9 mass points (250-6000 GeV)"
echo "==============================================="
echo ""

# Step 1: Activate environment
echo "Step 1: Activating Python environment..."
source .venv_local/bin/activate || source NAOD_TAU/.venv/bin/activate
echo "✓ Environment activated"
echo ""

# Step 2: Setup batch configuration
echo "Step 2: Setting up batch configuration..."
cp NAOD_TAU/file_config_batch_all_mass_points.json NAOD_TAU/file_config.json
echo "✓ Configuration ready with all 9 mass points:"
echo "  - M-250, M-500, M-750, M-1000"
echo "  - M-2000, M-3000, M-4000, M-5000, M-6000"
echo ""

# Step 3: Run batch analysis
echo "Step 3: Starting batch analysis..."
echo "This will process each mass point sequentially"
echo "Typical time: 5-10 minutes per mass point"
echo ""
python NAOD_TAU/batch_runner.py

# Step 4: Compare results
echo ""
echo "Step 4: Generating comparison report..."
python NAOD_TAU/batch_compare_results.py --all

echo ""
echo "==============================================="
echo "✓ BATCH ANALYSIS COMPLETE"
echo "==============================================="
echo ""
echo "Results organized in:"
echo "  NAOD_TAU/outputs/M-250/"
echo "  NAOD_TAU/outputs/M-500/"
echo "  ... (all mass points)"
echo ""
echo "Files generated:"
echo "  - PNG histograms for each mass point"
echo "  - ROOT files for detailed analysis"
echo "  - analysis_summary.txt (summary report)"
echo "  - mass_point_comparison.png (comparison plots)"
echo ""
echo "Next steps:"
echo "  1. Review individual histograms: open NAOD_TAU/outputs/M-XXX/"
echo "  2. Check comparison plots: NAOD_TAU/outputs/mass_point_comparison.png"
echo "  3. Read summary: NAOD_TAU/outputs/analysis_summary.txt"
echo ""
