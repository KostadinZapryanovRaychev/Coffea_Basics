from pathlib import Path
import logging

from coffea.nanoevents import NanoAODSchema, NanoEventsFactory


logger = logging.getLogger(__name__)
NanoAODSchema.warn_missing_crossrefs = False

HERE = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT_FILE = PROJECT_ROOT / "nanoaodsim_coffea_1.root"
TREE_NAME = "Events"


def load_events(root_file: Path):
    """
    Load NanoAOD events from a ROOT file.
    
    Args:
        root_file: Path to the ROOT file
        
    Returns:
        NanoEvents object with particle data
        
    Raises:
        FileNotFoundError: If ROOT file does not exist at specified path
        ValueError: If ROOT file is invalid or cannot be read
        RuntimeError: If NanoEventsFactory fails to initialize
    """
    # Validate file existence
    if not root_file.exists():
        error_msg = (
            f"\n[ERROR] ROOT input file not found at: {root_file}\n"
            f"  Expected file: nanoaodsim_coffea_1.root\n"
            f"  Project root: {PROJECT_ROOT}\n"
            f"  Ensure the ROOT file exists in the project directory.\n"
        )
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # Validate file is readable
    try:
        if not root_file.is_file():
            raise ValueError(f"Path exists but is not a file: {root_file}")
        if not root_file.stat().st_size > 0:
            raise ValueError(f"ROOT file is empty (0 bytes): {root_file}")
    except (OSError, ValueError) as e:
        error_msg = (
            f"\n[ERROR] Cannot read ROOT file at: {root_file}\n"
            f"  Details: {str(e)}\n"
            f"  Ensure file is readable and not corrupted.\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    
    # Load events via NanoEventsFactory
    try:
        logger.info(f"Loading NanoAOD events from: {root_file}")
        events = NanoEventsFactory.from_root(
            {str(root_file): TREE_NAME},
            schemaclass=NanoAODSchema
        ).events()
        logger.info(f"✓ Successfully loaded {len(events)} events")
        return events
    except KeyError as e:
        error_msg = (
            f"\n[ERROR] Tree '{TREE_NAME}' not found in ROOT file: {root_file}\n"
            f"  Available trees may differ. Check ROOT file structure.\n"
            f"  Use command: rootinfo {root_file}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"\n[ERROR] NanoEventsFactory failed to load ROOT file: {root_file}\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
            f"  Ensure file is a valid NanoAOD ROOT file with NanoAODSchema.\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
