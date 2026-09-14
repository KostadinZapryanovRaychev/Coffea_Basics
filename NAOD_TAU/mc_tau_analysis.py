#!/usr/bin/env python3
"""NAOD_TAU tau-pair analysis entrypoint with combined data from all ROOT files."""

"""Orchestrator file"""

from pathlib import Path
import sys
import logging
import argparse

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("NAOD_TAU.helpers.io").setLevel(logging.INFO)
logging.getLogger("NAOD_TAU.helpers.plotting").setLevel(logging.INFO)

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))


from NAOD_TAU.helpers.io import (
    HERE, 
    load_config, 
    load_all_enabled_events,
    get_combined_output_directory,
    extract_mass_point
)
from NAOD_TAU.helpers.selection import load_tau_pairs, load_taus,select_deep_tau_vse
from NAOD_TAU.helpers.lhe_ditau_candidates import make_lhe_ditau_histograms, make_tau_collection_histograms
from NAOD_TAU.helpers.tau_collections import (
    get_deep_taus,
    get_tresholded_deep_taus,
    deep_taus_tresholds,
)

from NAOD_TAU.helpers.plotting import get_tau_multiplicity_histogram

from NAOD_TAU.helpers.separate import  get_number_of_taus_per_event

def main():
    """
    Execute tau-pair analysis with combined data from all enabled files.
    
    Mass point is automatically extracted from ROOT file paths in file_config.json.
    Optional --mass-point argument can organize output by mass point directory.
    
    Usage:
        python mc_tau_analysis.py                # Auto-detect mass point from config
        python mc_tau_analysis.py --mass-point 500  # Organize output in outputs/M500/
    
    Workflow:
    1. Load configuration from file_config.json
    2. Load events from all enabled ROOT files
    3. Concatenate all events
    4. Filter events with valid tau pairs
    5. Extract mass point from file paths (or use --mass-point if provided)
    6. Generate combined histograms (PNG and ROOT formats)
    
    7. Save histograms in outputs/M{mass_point}/ directory
    """

    config = load_config()
    events = load_all_enabled_events(config)



if __name__ == "__main__":
    main()
