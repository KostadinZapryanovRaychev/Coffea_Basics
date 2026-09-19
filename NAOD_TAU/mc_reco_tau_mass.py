#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from NAOD_TAU.reco_tau_mass import main

MC_CONFIG_PATH = Path(__file__).resolve().parent / "file_config_mc.json"
MC_OUTPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "mc_reco_tau_mass.root"


if __name__ == "__main__":
    main(MC_CONFIG_PATH, MC_OUTPUT_ROOT_FILE)
