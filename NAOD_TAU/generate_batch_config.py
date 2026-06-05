#!/usr/bin/env python3
"""
Generate file_config.json from a list of EOS file paths.
Each file will be processed separately with organized output folders by mass point.
"""

import json
import re
from pathlib import Path

# EOS file paths - one per mass point
EOS_FILES = [
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-250_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_092714/0000/nanoaodsim_coffea_1.root",
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-500_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_100139/0000/nanoaodsim_coffea_1.root",
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-750_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_102612/0000/nanoaodsim_coffea_1.root",
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-1000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_104735/0000/nanoaodsim_coffea_1.root",
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-2000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_111643/0000/nanoaodsim_coffea_1.root",
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-3000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_124833/0000/nanoaodsim_coffea_1.root",
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-4000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_160008/0000/nanoaodsim_coffea_1.root",
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-5000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_130557/0000/nanoaodsim_coffea_1.root",
    "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-6000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250725_100712/0000/nanoaodsim_coffea_1.root",
]

def extract_mass_point(file_path: str) -> str:
    """Extract mass point from file path (e.g., '500', '750', '1000')."""
    match = re.search(r'M-(\d+)', file_path)
    if match:
        return match.group(1)
    return "unknown"

def generate_config(output_file: str = "file_config.json"):
    """
    Generate configuration file with all mass points.
    Each file is marked as enabled and will be processed separately.
    """
    config = {
        "root_files": []
    }
    
    for file_path in EOS_FILES:
        mass = extract_mass_point(file_path)
        name = f"M-{mass}"
        
        config["root_files"].append({
            "name": name,
            "path": file_path,
            "tree": "Events",
            "enabled": True
        })
    
    # Save to file
    config_path = Path(__file__).resolve().parent / output_file
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Generated {output_file} with {len(config['root_files'])} mass points:")
    for entry in config["root_files"]:
        print(f"  - {entry['name']}: {'enabled' if entry['enabled'] else 'disabled'}")
    
    return config_path

if __name__ == "__main__":
    config_file = generate_config()
    print(f"\n✓ Configuration saved to: {config_file}")
    print("\nNext steps:")
    print("1. Review file_config.json")
    print("2. Run: python mc_tau_analysis.py")
    print("   This will process each mass point separately")
    print("3. Results will be saved to: outputs/M-XXX/")
