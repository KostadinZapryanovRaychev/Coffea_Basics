"""
Mass point configuration and discovery helper.

Manages Z' → 2τ analysis across multiple mass points (M250-M6000).
Integrates with existing file_config.json and io.py infrastructure.
"""

from pathlib import Path
import json
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parents[1]
MASS_POINTS_CONFIG_FILE = HERE / "mass_points_config.json"


def load_mass_points_config(config_path: Path = MASS_POINTS_CONFIG_FILE) -> Dict:
    """Load the master mass_points_config.json."""
    if not config_path.exists():
        raise FileNotFoundError(f"Mass points config not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


def get_available_mass_points() -> List[str]:
    """Return list of available mass points (e.g., ['250', '500', ...])."""
    config = load_mass_points_config()
    return sorted(config['mass_points'].keys())


def get_mass_point_info(mass_point: str) -> Dict:
    """Get configuration for a specific mass point."""
    config = load_mass_points_config()
    
    if mass_point not in config['mass_points']:
        raise ValueError(
            f"Mass point M{mass_point} not found. "
            f"Available: {', '.join(get_available_mass_points())}"
        )
    
    return config['mass_points'][mass_point]


def validate_mass_point_paths(mass_point: str) -> bool:
    """
    Validate that mass point EOS paths are accessible.
    
    Returns True if paths exist and contain .root files.
    """
    info = get_mass_point_info(mass_point)
    base_path = Path(info['eos_base_path'])
    
    if not base_path.exists():
        logger.error(f"EOS path not found: {base_path}")
        return False
    
    root_files = list(base_path.glob("*.root"))
    if not root_files:
        logger.error(f"No .root files found in: {base_path}")
        return False
    
    logger.info(f"✓ M{mass_point}: Found {len(root_files)} .root files")
    return True


def create_mass_point_file_config(mass_point: str) -> Dict:
    """
    Generate file_config.json format from mass_point configuration.
    
    Returns a config dictionary suitable for io.load_config().
    """
    info = get_mass_point_info(mass_point)
    base_path = Path(info['eos_base_path'])
    
    # Find all .root files in the directory
    root_files = sorted(base_path.glob("*.root"))
    
    if not root_files:
        raise FileNotFoundError(
            f"No ROOT files found in {base_path} for M{mass_point}"
        )
    
    # Create file entries
    file_entries = []
    for idx, root_file in enumerate(root_files, start=1):
        file_entries.append({
            "name": f"ZprimeTo2Tau_M{mass_point}_{idx}",
            "path": str(root_file),  # Absolute path
            "tree": "Events",
            "description": f"Z' → 2τ M={info['mass_gev']} GeV - File {idx}",
            "enabled": True
        })
    
    return {
        "root_files": file_entries,
        "notes": (
            f"Auto-generated for M{mass_point}. "
            f"N_events={info['n_events']}, "
            f"Memory={info['memory_mb']:.1f}MB. "
            f"Paths point to /eos/cms/store/user/mileva/bsm3g/NANOAODSIM"
        )
    }


def save_mass_point_config(mass_point: str, output_path: Path = None) -> Path:
    """
    Save mass point configuration to file_config.json.
    
    Args:
        mass_point: Mass point to generate config for
        output_path: Where to save file_config.json (default: NAOD_TAU/file_config.json)
    
    Returns:
        Path to saved config file
    """
    if output_path is None:
        output_path = HERE / "file_config.json"
    
    config = create_mass_point_file_config(mass_point)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Saved M{mass_point} config to {output_path}")
    return output_path
