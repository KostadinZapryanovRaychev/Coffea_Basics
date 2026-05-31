#!/usr/bin/env python3
"""
Batch analysis script to process all mass points sequentially.

Analyzes M250-M6000 one by one, saving results to separate output directories.
Usage:
    python batch_analyze_all_mass_points.py
    python batch_analyze_all_mass_points.py --mass-points 250 500 750
"""

from pathlib import Path
import subprocess
import sys
import logging
import argparse
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
MC_TAU_ANALYSIS = HERE / "mc_tau_analysis.py"

# Default mass points
DEFAULT_MASS_POINTS = ["250", "500", "750", "1000", "2000", "3000", "4000", "5000", "6000"]


def analyze_single_mass_point(mass_point: str) -> bool:
    """
    Run analysis for a single mass point.
    
    Returns True if successful, False otherwise.
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Starting analysis for M{mass_point}")
    logger.info(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(MC_TAU_ANALYSIS), "--mass-point", mass_point],
            cwd=str(HERE),
            timeout=3600  # 1 hour timeout per mass point
        )
        
        if result.returncode == 0:
            logger.info(f"✓ M{mass_point} completed successfully")
            return True
        else:
            logger.error(f"✗ M{mass_point} failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"✗ M{mass_point} timed out (>1 hour)")
        return False
    except Exception as e:
        logger.error(f"✗ M{mass_point} error: {str(e)}")
        return False


def main():
    """Run batch analysis of specified or all mass points."""
    parser = argparse.ArgumentParser(
        description="Batch analysis of Z' → 2τ for all/selected mass points",
        epilog="Examples:\n"
               "  python batch_analyze_all_mass_points.py\n"
               "  python batch_analyze_all_mass_points.py --mass-points 250 500 750",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--mass-points',
        nargs='+',
        type=str,
        help='Specific mass points to analyze (default: all)',
        default=None
    )
    
    parser.add_argument(
        '--start-from',
        type=str,
        help='Start from a specific mass point (useful for resuming)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Determine which mass points to analyze
    if args.mass_points:
        mass_points = [mp.lstrip('M').lstrip('m') for mp in args.mass_points]
    else:
        mass_points = DEFAULT_MASS_POINTS
    
    logger.info(f"Batch analysis configuration:")
    logger.info(f"  Mass points: {', '.join('M' + mp for mp in mass_points)}")
    logger.info(f"  Analysis script: {MC_TAU_ANALYSIS}")
    logger.info(f"  Output base: {HERE / 'outputs'}")
    
    # Filter by start-from if specified
    if args.start_from:
        start_idx = 0
        start_mp = args.start_from.lstrip('M').lstrip('m')
        try:
            start_idx = mass_points.index(start_mp)
            logger.info(f"  Resuming from M{start_mp} (index {start_idx})")
        except ValueError:
            logger.error(f"Mass point M{start_mp} not in list")
            sys.exit(1)
        
        mass_points = mass_points[start_idx:]
    
    # Run analysis for each mass point
    results = {}
    total = len(mass_points)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"BATCH ANALYSIS START")
    logger.info(f"Total mass points: {total}")
    logger.info(f"{'='*70}\n")
    
    for idx, mass_point in enumerate(mass_points, start=1):
        logger.info(f"[{idx}/{total}] Processing M{mass_point}...")
        success = analyze_single_mass_point(mass_point)
        results[mass_point] = success
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"BATCH ANALYSIS COMPLETE")
    logger.info(f"{'='*70}\n")
    
    successful = sum(1 for v in results.values() if v)
    failed = total - successful
    
    logger.info("Results Summary:")
    logger.info(f"  ✓ Successful: {successful}/{total}")
    logger.info(f"  ✗ Failed: {failed}/{total}\n")
    
    for mass_point in mass_points:
        status = "✓" if results[mass_point] else "✗"
        logger.info(f"  {status} M{mass_point}")
    
    logger.info(f"\n{'='*70}")
    
    # Output directory summary
    logger.info("\nOutput Directories:")
    for mass_point in mass_points:
        if results[mass_point]:
            output_dir = HERE / "outputs" / f"M{mass_point}" / "combined"
            if output_dir.exists():
                n_files = len(list(output_dir.glob("*")))
                logger.info(f"  M{mass_point}: {output_dir} ({n_files} files)")
    
    logger.info(f"\n{'='*70}\n")
    
    # Exit code
    if failed > 0:
        logger.error(f"{failed} mass point(s) failed. Check logs above.")
        sys.exit(1)
    else:
        logger.info("All mass points processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
