from pathlib import Path
import json
import logging

from coffea.nanoevents import NanoAODSchema, NanoEventsFactory


logger = logging.getLogger(__name__)
NanoAODSchema.warn_missing_crossrefs = False

HERE = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = HERE / "file_config.json"


def load_config(config_path: Path = CONFIG_FILE):
    """
    Load file configuration from JSON.
    
    Args:
        config_path: Path to the JSON configuration file
        
    Returns:
        Dictionary with 'root_files' list containing file configurations
        
    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If config file is invalid or malformed JSON
    """
    if not config_path.exists():
        error_msg = (
            f"\n[ERROR] Configuration file not found at: {config_path}\n"
                f"  Expected: file_config.json in NAOD_TAU folder\n"
            f"  Create a JSON file with root file paths and metadata.\n"
        )
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'root_files' not in config or not isinstance(config['root_files'], list):
            raise ValueError("Config must contain 'root_files' list")
        
        if len(config['root_files']) == 0:
            raise ValueError("Config 'root_files' list is empty")
        
        logger.debug(f"Loaded configuration from: {config_path}")
        return config
    except json.JSONDecodeError as e:
        error_msg = (
            f"\n[ERROR] Configuration file is not valid JSON: {config_path}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Failed to load configuration: {config_path}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def get_enabled_root_files(config: dict):
    """
    Extract enabled root files from configuration.
    
    Args:
        config: Configuration dictionary from load_config()
        
    Returns:
        List of enabled root file entries
        
    Raises:
        ValueError: If no enabled files found
    """
    enabled_files = [
        f for f in config['root_files']
        if f.get('enabled', True)  # Default to enabled if not specified
    ]
    
    if not enabled_files:
        error_msg = (
            "\n[ERROR] No enabled ROOT files found in configuration.\n"
            "  Check file_config.json and set 'enabled': true for at least one file.\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.debug(f"Found {len(enabled_files)} enabled ROOT file(s)")
    return enabled_files


def get_root_file_path(file_entry: dict, project_root: Path = PROJECT_ROOT):
    """
    Resolve ROOT file path from configuration entry.
    
    Args:
        file_entry: Configuration entry with 'path' and optionally 'name'
        project_root: Project root directory for relative path resolution
        
    Returns:
        Resolved Path object
        
    Raises:
        ValueError: If path cannot be resolved or file doesn't exist
    """
    try:
        file_path_str = file_entry.get('path')
        if not file_path_str:
            raise ValueError("File entry missing 'path' field")
        
        file_path = project_root / file_path_str
        
        if not file_path.exists():
            error_msg = (
                f"\n[ERROR] ROOT file not found: {file_path}\n"
                f"  Config path: {file_entry.get('path')}\n"
                f"  Project root: {project_root}\n"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.debug(f"Resolved file path: {file_path}")
        return file_path
    except (KeyError, TypeError) as e:
        error_msg = f"\n[ERROR] Invalid file entry in configuration: {str(e)}\n"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def get_first_enabled_root_file(config: dict = None):
    """
    Get the first enabled ROOT file from configuration.
    
    Convenience function for single-file analysis.
    
    Args:
        config: Configuration dictionary. If None, loaded from CONFIG_FILE.
        
    Returns:
        Tuple of (file_path, tree_name, file_entry)
        
    Raises:
        ValueError: If no enabled files found or config invalid
        FileNotFoundError: If file path doesn't exist
    """
    if config is None:
        config = load_config()
    
    enabled_files = get_enabled_root_files(config)
    file_entry = enabled_files[0]
    
    file_path = get_root_file_path(file_entry)
    tree_name = file_entry.get('tree', 'Events')
    
    logger.info(
        f"Using ROOT file: {file_entry.get('name', file_entry['path'])}\n"
        f"  Path: {file_path}\n"
        f"  Tree: {tree_name}"
    )
    
    return file_path, tree_name, file_entry


def iterate_all_enabled_root_files(config: dict = None):
    """
    Iterate through all enabled ROOT files from configuration.
    
    Yields fully resolved file information for batch processing.
    
    Args:
        config: Configuration dictionary. If None, loaded from CONFIG_FILE.
        
    Yields:
        Tuple of (file_path, tree_name, file_entry) for each enabled file
        
    Raises:
        ValueError: If config is invalid or no enabled files found
        FileNotFoundError: If any file path doesn't exist
    """
    if config is None:
        config = load_config()
    
    enabled_files = get_enabled_root_files(config)
    
    logger.info(f"Processing {len(enabled_files)} enabled ROOT file(s)")
    
    for idx, file_entry in enumerate(enabled_files, start=1):
        try:
            file_path = get_root_file_path(file_entry)
            tree_name = file_entry.get('tree', 'Events')
            file_name = file_entry.get('name', file_entry['path'])
            
            logger.info(
                f"\n[{idx}/{len(enabled_files)}] Processing file: {file_name}\n"
                f"  Path: {file_path}\n"
                f"  Tree: {tree_name}"
            )
            
            yield file_path, tree_name, file_entry
        except (FileNotFoundError, ValueError) as e:
            logger.warning(f"Skipping file entry: {str(e)}")
            continue


def load_events(root_file: Path = None, tree_name: str = "Events", config: dict = None):
    """
    Load NanoAOD events from a ROOT file.
    
    Can be called in three ways:
    1. load_events() - uses first enabled file from config
    2. load_events(Path('/path/to/file.root')) - specify file explicitly
    3. load_events(root_file=Path(...), tree_name='TreeName') - specify file and tree
    
    Args:
        root_file: Path to the ROOT file. If None, loads from config.
        tree_name: Name of the tree in ROOT file (default: "Events")
        config: Configuration dictionary. If None, loaded from CONFIG_FILE.
        
    Returns:
        NanoEvents object with particle data
        
    Raises:
        FileNotFoundError: If ROOT file does not exist at specified path
        ValueError: If ROOT file is invalid or cannot be read
        RuntimeError: If NanoEventsFactory fails to initialize
    """
    # If file not specified, load from config
    if root_file is None:
        try:
            root_file, tree_name, file_entry = get_first_enabled_root_file(config)
        except (ValueError, FileNotFoundError) as e:
            logger.error(str(e))
            raise
    
    # Validate file existence
    if not root_file.exists():
        error_msg = (
            f"\n[ERROR] ROOT input file not found at: {root_file}\n"
            f"  Check file path and ensure it exists.\n"
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
            {str(root_file): tree_name},
            schemaclass=NanoAODSchema
        ).events()
        logger.info(f"✓ Successfully loaded {len(events)} events")
        return events
    except KeyError as e:
        error_msg = (
            f"\n[ERROR] Tree '{tree_name}' not found in ROOT file: {root_file}\n"
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
