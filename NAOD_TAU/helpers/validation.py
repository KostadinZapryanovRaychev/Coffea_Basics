import logging
import sys
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)


def create_output_directory(output_dir: Path) -> Path:
    """Create the output directory if needed and return it."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
        return output_dir
    except OSError as e:
        error_msg = f"Cannot create output directory: {output_dir}\n  Details: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e

def validate_lhe_events(lhe_selected) -> None:
    """
    Validate LHE event selection.
    
    Args:
        lhe_selected: NanoEvents with LHE particles
        
    Returns:
        Number of events in selection
        
    Raises:
        ValueError: If selection is invalid or empty
    """
    try:
        n_events = len(lhe_selected)
        if n_events == 0:
            raise ValueError("LHE selection is empty (0 events)")
        logger.debug(f"Validated {n_events} LHE-selected events")
        return n_events
    except Exception as e:
        error_msg = f"Invalid LHE selection: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e