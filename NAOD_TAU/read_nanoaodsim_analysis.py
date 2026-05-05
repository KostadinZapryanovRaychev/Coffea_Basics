#!/usr/bin/env python3
"""NAOD_TAU tau-pair analysis entrypoint with comprehensive error handling."""

## _init_ is used to marke each of helpers io helpers plotting so on import places

from pathlib import Path
import sys
import logging

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


from NAOD_TAU.helpers.io import ROOT_FILE, HERE, load_events
from NAOD_TAU.helpers.plotting import make_tau_histogram
from NAOD_TAU.helpers.selection import load_tau_pairs


def main():
    """
    Execute the complete tau-pair analysis workflow.
    
    Workflow:
    1. Load NanoAOD events from ROOT file
    2. Filter events with valid tau pairs
    3. Generate histograms (PNG and ROOT formats)
    
    Raises:
        SystemExit: On fatal errors (exit code 1)
    """
    try:
        # Step 1: Load events from ROOT file
        try:
            events = load_events(ROOT_FILE)
        except FileNotFoundError as e:
            logger.error(f"\n{str(e)}")
            sys.exit(1)
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Input file validation failed. Check file integrity and format.")
            sys.exit(1)
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("NanoEventsFactory initialization failed. Check ROOT file structure.")
            sys.exit(1)
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error loading events\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            sys.exit(1)
        
        # Step 2: Select tau pairs
        try:
            lhe_selected, gen_selected, _ = load_tau_pairs(events)
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Event selection failed. Check input data integrity.")
            sys.exit(1)
        except AttributeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Required particle collections missing from ROOT file.")
            sys.exit(1)
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Data processing failed during selection.")
            sys.exit(1)
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error during tau pair selection\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            sys.exit(1)
        
        # Step 3: Generate histograms
        try:
            output_dir = HERE / "outputs"
            make_tau_histogram(output_dir, lhe_selected, gen_selected=gen_selected)
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Output directory validation failed.")
            sys.exit(1)
        except IOError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Cannot write histogram files. Check disk space and permissions.")
            sys.exit(1)
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Histogram generation failed. Check data quality.")
            sys.exit(1)
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error during histogram generation\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            sys.exit(1)
        
        # Analysis completed successfully
        logger.info("=" * 60)
        logger.info("✓ ANALYSIS COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
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
