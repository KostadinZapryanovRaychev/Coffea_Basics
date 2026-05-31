#!/usr/bin/env python3
"""NAOD_TAU tau-pair analysis entrypoint with combined data from all ROOT files."""

from pathlib import Path
import sys
import logging
import argparse

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Default level: show WARNING and above
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
    get_combined_output_directory
)
from NAOD_TAU.helpers.selection import load_tau_pairs
from NAOD_TAU.helpers.lhe_ditau_candidates import make_lhe_ditau_histograms
from NAOD_TAU.helpers.mass_points import (
    get_available_mass_points,
    save_mass_point_config,
    validate_mass_point_paths
)


def analyze_combined_files(base_output_dir: Path, config: dict) -> bool:
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
        
    Returns:
        True if analysis succeeded, False otherwise
    """
    logger.info("=" * 60)
    logger.info("COMBINED ANALYSIS MODE - MERGING ALL ROOT FILES")
    logger.info("=" * 60)
    
    try:
        # Step 1: Load all enabled events
        try:
            logger.debug("Loading events from all enabled ROOT files...")
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
        
        # Step 2: Select tau pairs from combined events
        try:
            logger.debug("Selecting tau pairs from combined events...")
            lhe_selected = load_tau_pairs(combined_events)
            n_selected = len(lhe_selected)
            logger.info(f"✓ Selected {n_selected} events with tau pairs from combined data")
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
            logger.debug(f"Generating histograms for combined data...")
            make_lhe_ditau_histograms(output_dir, lhe_selected)
            logger.info(f"✓ Histograms saved to: {output_dir}")
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


def main():
    """
    Execute tau-pair analysis with combined data from all enabled files.
    
    Supports single mass point analysis via --mass-point argument:
        python mc_tau_analysis.py --mass-point 250
        python mc_tau_analysis.py --mass-point M500
        python mc_tau_analysis.py  # Uses default file_config.json
    
    Workflow:
    1. Parse command-line arguments (--mass-point optional)
    2. If mass point specified, generate file_config.json for that mass point
    3. Load configuration from file_config.json
    4. Load events from all enabled ROOT files
    5. Concatenate all events
    6. Filter events with valid tau pairs
    7. Generate combined histograms (PNG and ROOT formats)
    
    Output structure:
    outputs/
      M250/       (if --mass-point 250)
        combined/
          *.png, *.root
      M500/
        ...
      combined/   (if no mass point specified)
        *.png, *.root
    
    Raises:
        SystemExit: On fatal configuration errors (exit code 1)
    """
    # Parse command-line arguments
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
        help='Analyze specific mass point (e.g., 250, 500, M750, etc.)',
        default=None
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available mass points and exit'
    )
    
    args = parser.parse_args()
    
    # Handle --list
    if args.list:
        available = get_available_mass_points()
        logger.info("Available mass points:")
        for mp in available:
            logger.info(f"  M{mp}")
        sys.exit(0)
    
    # Setup mass point if specified
    if args.mass_point:
        # Normalize mass point (remove 'M' prefix if present)
        mass_point = args.mass_point.lstrip('M').lstrip('m')
        
        logger.info(f"\n{'='*60}")
        logger.info(f"MASS POINT ANALYSIS: M{mass_point}")
        logger.info(f"{'='*60}")
        
        try:
            # Validate paths exist
            if not validate_mass_point_paths(mass_point):
                logger.error(f"Cannot access EOS paths for M{mass_point}")
                logger.error("Check that you're on lxplus with EOS access")
                sys.exit(1)
            
            # Generate and save file_config.json for this mass point
            logger.info(f"Generating file_config.json for M{mass_point}...")
            save_mass_point_config(mass_point)
            
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            sys.exit(1)
        except FileNotFoundError as e:
            logger.error(f"\n[ERROR] {str(e)}")
            logger.error(f"Mass point M{mass_point} not found in mass_points_config.json")
            sys.exit(1)
        except Exception as e:
            logger.error(
                f"\n[ERROR] Failed to setup M{mass_point}\n"
                f"  Exception: {type(e).__name__}: {str(e)}\n"
            )
            sys.exit(1)
    
    try:
        # Load configuration
        try:
            logger.info("Loading file configuration...")
            config = load_config()
            logger.info(f"✓ Configuration loaded")
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
        
        # Base output directory (with mass point subdirectory if specified)
        if args.mass_point:
            mass_point = args.mass_point.lstrip('M').lstrip('m')
            base_output_dir = HERE / "outputs" / f"M{mass_point}"
        else:
            base_output_dir = HERE / "outputs"
        
        # Perform combined analysis
        try:
            success = analyze_combined_files(base_output_dir, config)
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("ANALYSIS SUMMARY")
            logger.info("=" * 60)
            
            if success:
                if args.mass_point:
                    logger.info(f"✓ M{mass_point} ANALYSIS COMPLETED SUCCESSFULLY")
                else:
                    logger.info("✓ COMBINED ANALYSIS COMPLETED SUCCESSFULLY")
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
