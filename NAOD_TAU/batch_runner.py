#!/usr/bin/env python3
"""
Batch runner for processing multiple mass points one at a time.
Processes each mass point separately and organizes outputs.
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent


def load_config(config_file: str = "file_config.json") -> Dict:
    """Load configuration from file."""
    config_path = HERE / config_file
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise


def process_mass_point(file_entry: Dict, mass_point: str) -> bool:
    """
    Process a single mass point file.
    
    Args:
        file_entry: Configuration entry for the file
        mass_point: Mass point string (e.g., "500")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import analysis modules
        sys.path.insert(0, str(PROJECT_ROOT))
        from NAOD_TAU.helpers.io import (
            load_events,
            get_output_directory_for_file,
            extract_mass_point
        )
        from NAOD_TAU.helpers.selection import load_tau_pairs
        from NAOD_TAU.helpers.lhe_ditau_candidates import make_lhe_ditau_histograms
        
        logger.info("=" * 70)
        logger.info(f"Processing mass point M-{mass_point}")
        logger.info("=" * 70)
        
        # Get file path
        file_path = PROJECT_ROOT / file_entry['path']
        tree_name = file_entry.get('tree', 'Events')
        
        # Check if file exists
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        # Load events
        logger.info(f"Loading events from: {file_path}")
        events = load_events(root_file=file_path, tree_name=tree_name)
        logger.info(f"✓ Loaded {len(events)} events")
        
        # Select tau pairs
        logger.info("Selecting tau pairs...")
        lhe_selected = load_tau_pairs(events)
        n_selected = len(lhe_selected)
        logger.info(f"✓ Selected {n_selected} events with tau pairs")
        
        if n_selected == 0:
            logger.warning("No tau pairs found in this file")
            return False
        
        # Create output directory
        output_dir = HERE / "outputs" / f"M-{mass_point}"
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving histograms to: {output_dir}")
        
        # Generate histograms
        logger.info("Generating histograms...")
        make_lhe_ditau_histograms(output_dir, lhe_selected, mass_point)
        logger.info(f"✓ Histograms saved to {output_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing M-{mass_point}: {str(e)}", exc_info=True)
        return False


def run_batch_analysis(config_file: str = "file_config.json"):
    """
    Run analysis for all enabled mass points sequentially.
    
    Args:
        config_file: Path to configuration file
    """
    try:
        # Load configuration
        config = load_config(config_file)
        enabled_files = [f for f in config['root_files'] if f.get('enabled', True)]
        
        if not enabled_files:
            logger.error("No enabled files found in configuration")
            return False
        
        logger.info(f"\nBatch Analysis Mode")
        logger.info(f"Processing {len(enabled_files)} mass points sequentially\n")
        
        # Process each mass point
        successful = 0
        failed = 0
        failed_masses = []
        
        for idx, file_entry in enumerate(enabled_files, start=1):
            mass = file_entry.get('name', '').replace('M-', '')
            
            logger.info(f"\n[{idx}/{len(enabled_files)}] {file_entry['name']}")
            
            success = process_mass_point(file_entry, mass)
            
            if success:
                successful += 1
                logger.info(f"✓ M-{mass} completed successfully")
            else:
                failed += 1
                failed_masses.append(mass)
                logger.warning(f"✗ M-{mass} failed")
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("BATCH ANALYSIS SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total processed: {len(enabled_files)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        
        if failed_masses:
            logger.warning(f"Failed mass points: {', '.join([f'M-{m}' for m in failed_masses])}")
        
        logger.info(f"\nResults saved to: {HERE}/outputs/M-*/")
        logger.info("\nTo compare all mass points:")
        logger.info("  python batch_compare_results.py")
        
        return failed == 0
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch process multiple mass points from configuration file"
    )
    parser.add_argument(
        '--config', 
        default='file_config.json',
        help='Configuration file (default: file_config.json)'
    )
    parser.add_argument(
        '--mass-point',
        help='Process only specific mass point (e.g., "500")'
    )
    
    args = parser.parse_args()
    
    success = run_batch_analysis(args.config)
    sys.exit(0 if success else 1)
