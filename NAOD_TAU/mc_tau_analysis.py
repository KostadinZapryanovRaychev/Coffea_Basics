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
from NAOD_TAU.helpers.gen_particles import load_gen_tau_pairs, make_gen_ditau_histograms
from NAOD_TAU.helpers.tau_collections import (
    get_deep_taus,
    get_tresholded_deep_taus,
    deep_taus_tresholds,
)

from NAOD_TAU.helpers.plotting import get_tau_multiplicity_histogram

from NAOD_TAU.helpers.separate import  get_number_of_taus_per_event

def get_good_deep_taus(events, threshold=1):
    """Select good DeepTau taus based on a threshold."""
    
    print(f"Selecting good DeepTau taus with threshold: {threshold}")
    taus = load_taus(events)
    deepTauVSe = get_deep_taus(taus)
    good_deep_taus = get_tresholded_deep_taus(deepTauVSe, taus, threshold)
    return good_deep_taus


def analyze_combined_files(base_output_dir: Path, config: dict, mass_point: str = "unknown") -> bool:
    """
    Perform combined tau-pair analysis on all enabled ROOT files.
    
    Workflow:
    1. Load events from all enabled ROOT files
    2. Concatenate all events
    3. Select tau pairs from combined events
    4. Generate histograms from combined data
    
    Args:
        base_output_dir: Base output directory
        config: Configuration dictionary
        mass_point: Mass point string (e.g., "500", "750") for histogram titles
        
    Returns:
        True if analysis succeeded, False otherwise
    """
    logger.info("=" * 60)
    logger.info("COMBINED ANALYSIS MODE - MERGING ALL ROOT FILES")
    logger.info("=" * 60)
    
    try:
        # Step 1: Load all enabled events
        try:
            combined_events = load_all_enabled_events(config)
            taus_per_event = get_number_of_taus_per_event(combined_events)
            
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Failed to load events from all files.")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error loading combined events\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            return False
        
        # Step 2: Select tau pairs from combined events
        try:
            # lhe_selected = load_tau_pairs(combined_events)
            # n_selected = len(lhe_selected)
            # logger.info(f"✓ Selected {n_selected} events with tau pairs from combined data")
            # select_deep_tau_vse(combined_events, working_point=deep_taus_tresholds["VVVLoose"])
            print("Selecting good DeepTau taus from combined events...")
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Event selection failed. Check combined data integrity.")
            return False
        except AttributeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Required particle collections missing from ROOT files.")
            return False
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Data processing failed during selection.")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error during tau pair selection\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            return False
        
        # Step 3: Generate histograms from combined data
        try:
            output_dir = get_combined_output_directory(base_output_dir)
            logger.debug(f"Generating histograms for combined data (M={mass_point} GeV)...")
            # make_lhe_ditau_histograms(output_dir, lhe_selected, mass_point)
            get_tau_multiplicity_histogram(output_dir, taus_per_event)
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Output directory validation failed.")
            return False
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Histogram generation failed. Check data quality.")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error during histogram generation\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            return False
        
        logger.info("✓ Successfully completed combined analysis")
        return True
        
    except Exception as e:
        logger.error(
            f"\n[ERROR] Unexpected error in combined analysis\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        return False


def analyze_combined_genpart_files(base_output_dir: Path, config: dict, mass_point: str = "unknown") -> bool:
    """Perform combined generator-particle tau-pair analysis on all enabled ROOT files."""
    logger.info("=" * 60)
    logger.info("COMBINED GENPART ANALYSIS MODE - MERGING ALL ROOT FILES")
    logger.info("=" * 60)

    try:
        try:
            combined_events = load_all_enabled_events(config)
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Failed to load events from all files.")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error loading combined events\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            return False

        try:
            # gen_selected = load_gen_tau_pairs(combined_events)
            # n_selected = len(gen_selected)
            # logger.info(f"✓ Selected {n_selected} events with GenPart tau pairs from combined data")
            print("Selecting good DeepTau taus from combined GenPart events...")
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Event selection failed. Check combined data integrity.")
            return False
        except AttributeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Required GenPart collection missing from ROOT files.")
            return False
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Data processing failed during GenPart selection.")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error during GenPart selection\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            return False

        try:
            output_dir = get_combined_output_directory(base_output_dir)
            logger.debug(f"Generating GenPart histograms for combined data (M={mass_point} GeV)...")
            # make_gen_ditau_histograms(output_dir, gen_selected, mass_point)
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Output directory validation failed.")
            return False
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("GenPart histogram generation failed. Check data quality.")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error during GenPart histogram generation\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            return False

        logger.info("✓ Successfully completed combined GenPart analysis")
        return True

    except Exception as e:
        logger.error(
            f"\n[ERROR] Unexpected error in combined GenPart analysis\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        return False


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
    
    Output structure:
    outputs/
      combined/          (if no --mass-point specified)
        *.png, *.root
      M500/              (if --mass-point 500)
        combined/
          *.png, *.root
    
    Raises:
        SystemExit: On fatal configuration errors (exit code 1)
    """
    parser = argparse.ArgumentParser(
        description="Z' → 2τ tau-pair analysis across mass points (M250-M6000)",
        epilog="Examples:\n"
               "  python mc_tau_analysis.py --mass-point 250\n"
               "  python mc_tau_analysis.py --mass-point M500\n"
               "  python mc_tau_analysis.py  # Default: uses file_config.json\n"
               "  python mc_tau_analysis.py --list  # Show available mass points",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--mass-point',
        type=str,
        dest='mass_point',
        help='Mass point identifier for output organization (e.g., 500, 750)',
        default=None
    )

    parser.add_argument(
        '--genpart',
        action='store_true',
        help='Use GenPart tau selection and GenPart histograms instead of LHEPart',
    )
    
    args = parser.parse_args()
    
    if args.mass_point:
        # Validate mass point is numeric
        try:
            mass_point_value = args.mass_point.lstrip('M').lstrip('m')
            int(mass_point_value)  # Validate it's a number
        except ValueError:
            logger.error(f"Invalid mass point: {args.mass_point}. Must be numeric (e.g., 500, 750)")
            sys.exit(1)
        
        mass_point = mass_point_value
        base_output_dir = HERE / "outputs" / f"M{mass_point}"
        logger.info(f"\n{'='*60}")
        logger.info(f"MASS POINT ANALYSIS: M{mass_point}")
        logger.info(f"{'='*60}")
    else:
        base_output_dir = None
        mass_point = None
    
    try:
        try:
            logger.info("Loading file configuration...")
            config = load_config()
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"\n{str(e)}")
            logger.error("Cannot proceed without valid configuration.")
            sys.exit(1)
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error loading configuration\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            sys.exit(1)
        
        # Base output directory and mass point extraction
        if base_output_dir is None:
            base_output_dir = HERE / "outputs"
            # Extract mass point from first enabled file's path
            enabled_files = config.get('root_files', [])
            if enabled_files and enabled_files[0].get('enabled', True):
                mass_point = extract_mass_point(enabled_files[0].get('path', ''))
            else:
                mass_point = "unknown"
        
        # Perform combined analysis
        try:
            if args.genpart:
                success = analyze_combined_genpart_files(base_output_dir, config, mass_point)
            else:
                success = analyze_combined_files(base_output_dir, config, mass_point)
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("ANALYSIS SUMMARY")
            logger.info("=" * 60)
            
            if success:
                if mass_point != "unknown":
                    logger.info(f"✓ M{mass_point} ANALYSIS COMPLETED SUCCESSFULLY")
                else:
                    logger.info("✓ ANALYSIS COMPLETED SUCCESSFULLY")
                logger.info(f"  Output directory: {base_output_dir / 'combined'}")
            else:
                logger.error("✗ COMBINED ANALYSIS FAILED")
                sys.exit(1)
            
            logger.info("=" * 60)
            
        except KeyboardInterrupt:
            logger.warning("\n[WARNING] Analysis interrupted by user (Ctrl+C)")
            sys.exit(130)
        
    except KeyboardInterrupt:
        logger.warning("\n[WARNING] Analysis interrupted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        logger.error(
            f"\n[FATAL ERROR] Unhandled exception in main workflow\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
