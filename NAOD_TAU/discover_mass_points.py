#!/usr/bin/env python3
"""
Discovery script to find all mass point NANOAODSIM directories on EOS.
Outputs a JSON map of mass points to their file paths.

Run once on lxplus to generate the mass_points_config.json template.
"""

from pathlib import Path
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mass points to find
MASS_POINTS = ["250", "500", "750", "1000", "2000", "3000", "4000", "5000", "6000"]
BASE_EOS_PATH = "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM"


def find_mass_point_directory(mass_point: str) -> dict:
    """
    Find the NANOAODSIM directory for a given mass point.
    
    Returns dict with:
    - mass_point: Mass value (e.g., "250")
    - base_path: Full EOS directory containing .root files
    - files: List of ROOT files found
    """
    search_pattern = f"ZprimeTo2Tau-2Jets_M-{mass_point}_TuneCP5*madgraphMLM*"
    search_path = f"{BASE_EOS_PATH}/{search_pattern}*"
    
    logger.info(f"Searching for M{mass_point}: {search_path}")
    
    try:
        # Find directories matching the pattern
        result = subprocess.run(
            ["find", BASE_EOS_PATH, "-type", "d", "-name", f"*M-{mass_point}*"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            logger.error(f"Error searching for M{mass_point}: {result.stderr}")
            return None
        
        directories = result.stdout.strip().split('\n')
        
        # Filter for NANOAODSIM and find the one with /0000/ subdirectory
        nanoaod_dirs = [d for d in directories if 'Run3Summer23_NANOAODv12' in d and '0000' in d]
        
        if not nanoaod_dirs:
            logger.warning(f"No NANOAODSIM directory found for M{mass_point}")
            return None
        
        # Use the first match (usually most recent)
        base_path = nanoaod_dirs[0]
        
        # List ROOT files in the directory
        root_files = []
        if Path(base_path).exists():
            root_files = [f.name for f in Path(base_path).glob("*.root")]
        
        result = {
            "mass_point": mass_point,
            "base_path": base_path,
            "xrootd_path": base_path.replace("/eos/cms/store", "root://eoscms.cern.ch//store"),
            "files_found": len(root_files),
            "root_files": root_files
        }
        
        logger.info(f"✓ M{mass_point}: {base_path}")
        logger.info(f"  Files: {root_files}")
        
        return result
        
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout searching for M{mass_point}")
        return None
    except Exception as e:
        logger.error(f"Error for M{mass_point}: {str(e)}")
        return None


def main():
    logger.info("Discovering all mass points on EOS...")
    logger.info(f"Base path: {BASE_EOS_PATH}\n")
    
    mass_point_data = {}
    
    for mass_point in MASS_POINTS:
        data = find_mass_point_directory(mass_point)
        if data:
            mass_point_data[mass_point] = data
    
    # Save to JSON
    output_file = Path(__file__).parent / "mass_points_discovered.json"
    
    with open(output_file, 'w') as f:
        json.dump(mass_point_data, f, indent=2)
    
    logger.info(f"\n✓ Discovery complete. Results saved to: {output_file}")
    logger.info(f"Found {len(mass_point_data)}/{len(MASS_POINTS)} mass points")
    
    return output_file


if __name__ == "__main__":
    main()
