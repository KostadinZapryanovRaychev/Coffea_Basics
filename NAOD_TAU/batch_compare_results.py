#!/usr/bin/env python3
"""
Compare and visualize results across all mass points.
Creates comparison plots showing how tau pair properties vary with mass point.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent


def load_root_histogram(root_file_path: str, histogram_name: str) -> tuple:
    """
    Load histogram data from ROOT file.
    
    Returns:
        Tuple of (bin_centers, counts, bin_edges)
    """
    try:
        import uproot
        with uproot.open(root_file_path) as f:
            hist = f[histogram_name]
            counts = hist.values()
            edges = hist.axes[0].edges
            centers = 0.5 * (edges[:-1] + edges[1:])
            return centers, counts, edges
    except Exception as e:
        logger.warning(f"Could not load {histogram_name} from {root_file_path}: {e}")
        return None, None, None


def extract_mass_points() -> Dict[str, Path]:
    """
    Find all mass point output directories.
    
    Returns:
        Dictionary: {"500": Path(...), "750": Path(...), ...}
    """
    outputs_dir = HERE / "outputs"
    mass_points = {}
    
    if not outputs_dir.exists():
        logger.error(f"Outputs directory not found: {outputs_dir}")
        return mass_points
    
    for folder in sorted(outputs_dir.glob("M-*")):
        if folder.is_dir():
            mass = folder.name.replace("M-", "")
            mass_points[mass] = folder
    
    logger.info(f"Found {len(mass_points)} mass points: {', '.join(sorted(mass_points.keys()))}")
    return mass_points


def create_comparison_plot(
    histogram_names: List[str],
    output_file: str = "mass_point_comparison.png"
):
    """
    Create comparison plots for key histograms across mass points.
    
    Args:
        histogram_names: List of histogram names to compare (e.g., ["lhe_mass", "lhe_tau_pt"])
        output_file: Output PNG file name
    """
    mass_points = extract_mass_points()
    
    if not mass_points:
        logger.warning("No mass point data found to compare")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Tau Pair Properties vs Mass Point", fontsize=16, fontweight='bold')
    
    axes = axes.flatten()
    
    for idx, hist_name in enumerate(histogram_names[:4]):
        ax = axes[idx]
        
        for mass in sorted(mass_points.keys(), key=int):
            mass_folder = mass_points[mass]
            root_file = mass_folder / "tau_pair_histograms.root"
            
            if not root_file.exists():
                logger.warning(f"ROOT file not found for M-{mass}")
                continue
            
            centers, counts, edges = load_root_histogram(str(root_file), hist_name)
            
            if centers is not None and counts is not None:
                ax.plot(centers, counts, marker='o', label=f"M-{mass}", linewidth=2, markersize=4)
        
        ax.set_xlabel("Value", fontsize=11)
        ax.set_ylabel("Counts", fontsize=11)
        ax.set_title(f"Histogram: {hist_name}", fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = HERE / "outputs" / output_file
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    logger.info(f"✓ Saved comparison plot: {output_path}")
    plt.close()


def create_summary_report():
    """Create a text summary of all processed mass points."""
    mass_points = extract_mass_points()
    
    if not mass_points:
        logger.warning("No mass point data found")
        return
    
    report_path = HERE / "outputs" / "analysis_summary.txt"
    
    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("TAU PAIR ANALYSIS SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Total mass points processed: {len(mass_points)}\n")
        f.write(f"Mass points: {', '.join(sorted(mass_points.keys(), key=int))}\n\n")
        
        for mass in sorted(mass_points.keys(), key=int):
            mass_folder = mass_points[mass]
            f.write(f"\nMass Point M-{mass}\n")
            f.write(f"  Output directory: {mass_folder}\n")
            
            # Count PNG files
            png_files = list(mass_folder.glob("*.png"))
            f.write(f"  Histograms (PNG): {len(png_files)}\n")
            
            # Check ROOT file
            root_file = mass_folder / "tau_pair_histograms.root"
            if root_file.exists():
                size_mb = root_file.stat().st_size / (1024 * 1024)
                f.write(f"  ROOT file: tau_pair_histograms.root ({size_mb:.2f} MB)\n")
            
            if png_files:
                f.write("  PNG files:\n")
                for png in sorted(png_files)[:5]:  # Show first 5
                    f.write(f"    - {png.name}\n")
                if len(png_files) > 5:
                    f.write(f"    ... and {len(png_files) - 5} more\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("Analysis completed. All results organized by mass point.\n")
        f.write("=" * 70 + "\n")
    
    logger.info(f"✓ Saved summary report: {report_path}")
    
    # Also print to console
    with open(report_path, 'r') as f:
        print(f.read())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare results across mass points")
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate summary report'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Generate comparison plots'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate both report and plots'
    )
    
    args = parser.parse_args()
    
    # Default: show report
    if not any([args.report, args.compare, args.all]):
        args.report = True
    
    if args.report or args.all:
        create_summary_report()
    
    if args.compare or args.all:
        logger.info("Generating comparison plots...")
        # Compare key histograms
        create_comparison_plot(["lhe_mass", "lhe_tau_pt", "lhe_antitau_pt", "lhe_delta_r_ditau_pair"])
