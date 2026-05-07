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


from NAOD_TAU.helpers.io import HERE, load_events, load_config, iterate_all_enabled_root_files
from NAOD_TAU.helpers.plotting import make_pair_tau_histograms_lhe, make_raw_tau_histograms
from NAOD_TAU.helpers.selection import load_tau_pairs


def get_output_directory_for_file(base_output_dir: Path, file_entry: dict) -> Path:
    """
    Create file-specific output directory name.
    
    Args:
        base_output_dir: Base output directory (typically HERE / "outputs")
        file_entry: File entry from configuration
        
    Returns:
        File-specific output directory path
    """
    file_name = file_entry.get('name', file_entry['path']).replace('.root', '')
    output_dir = base_output_dir / file_name
    return output_dir


def analyze_single_file(file_path: Path, tree_name: str, file_entry: dict, 
                        base_output_dir: Path, file_index: int, total_files: int) -> bool:
    """
    Perform complete analysis on a single ROOT file.
    
    Workflow:
    1. Load events from file
    2. Select tau pairs
    3. Generate histograms
    
    Args:
        file_path: Path to ROOT file
        tree_name: Name of tree in ROOT file
        file_entry: Configuration entry for this file
        base_output_dir: Base output directory
        file_index: Current file index (1-based)
        total_files: Total number of files to process
        
    Returns:
        True if analysis succeeded, False if skipped with warning
    """
    file_name = file_entry.get('name', file_entry['path'])
    logger.info("=" * 60)
    logger.info(f"FILE [{file_index}/{total_files}]: {file_name}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Load events from ROOT file
        try:
            logger.debug(f"Loading events from: {file_path}")
            events = load_events(root_file=file_path, tree_name=tree_name)
        except FileNotFoundError as e:
            logger.error(f"\n{str(e)}")
            logger.warning(f"⚠ Skipping file {file_name} (file not found)")
            return False
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Input file validation failed. Check file integrity and format.")
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("NanoEventsFactory initialization failed. Check ROOT file structure.")
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error loading events\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        
        # Step 2: Select tau pairs
        try:
            lhe_taus, gen_taus, _ = load_tau_pairs(events)
            lhe_selected, gen_selected, _ = load_tau_pairs(events)
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Event selection failed. Check input data integrity.")
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        except AttributeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Required particle collections missing from ROOT file.")
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Data processing failed during selection.")
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error during tau pair selection\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        
        # Step 3: Generate LHE histograms
        try:
            output_dir = get_output_directory_for_file(base_output_dir, file_entry)
            make_raw_tau_histograms(output_dir, lhe_taus)
            make_pair_tau_histograms_lhe(output_dir, lhe_selected)
        except ValueError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Output directory validation failed.")
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        except RuntimeError as e:
            logger.error(f"\n{str(e)}")
            logger.error("Histogram generation failed. Check data quality.")
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        except Exception as e:
            logger.error(
                f"\n[ERROR] Unexpected error during histogram generation\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            logger.warning(f"⚠ Skipping file {file_name}")
            return False
        
        logger.info(f"✓ Successfully analyzed: {file_name}")
        return True
        
    except Exception as e:
        logger.error(
            f"\n[ERROR] Unexpected error in file analysis\n"
            f"  File: {file_name}\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        return False


def main():
    """
    Execute batch tau-pair analysis on all enabled files from configuration.
    
    Workflow:
    1. Load configuration from file_config.json
    2. Iterate through all enabled files
    3. For each file:
       - Load NanoAOD events
       - Filter events with valid tau pairs
       - Generate histograms (PNG and ROOT formats)
    
    Output structure:
    outputs/
      file1_name/
        *.png, *.root
      file2_name/
        *.png, *.root
    
    Raises:
        SystemExit: On fatal configuration errors (exit code 1)
    """
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
        
        # Base output directory
        base_output_dir = HERE / "outputs"
        
        # Process all enabled files
        files_processed = 0
        files_succeeded = 0
        files_skipped = 0
        
        try:
            for file_index, (file_path, tree_name, file_entry) in enumerate(
                iterate_all_enabled_root_files(config), start=1
            ):
                files_processed += 1
                success = analyze_single_file(
                    file_path, tree_name, file_entry, 
                    base_output_dir, file_index, len(config['root_files'])
                )
                if success:
                    files_succeeded += 1
                else:
                    files_skipped += 1
        except KeyboardInterrupt:
            logger.warning("\n[WARNING] Batch analysis interrupted by user (Ctrl+C)")
            sys.exit(130)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("BATCH ANALYSIS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"  Total files processed: {files_processed}")
        logger.info(f"  ✓ Succeeded: {files_succeeded}")
        logger.info(f"  ⚠ Skipped: {files_skipped}")
        logger.info("=" * 60)
        
        if files_succeeded == 0:
            logger.error("No files were successfully analyzed. Check configuration and data.")
            sys.exit(1)
        
        logger.info("✓ BATCH ANALYSIS COMPLETED")
        
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
