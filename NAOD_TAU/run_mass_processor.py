#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import uproot
from coffea import processor
from coffea.nanoevents import NanoAODSchema

from NAOD_TAU.helpers.config import load_config, get_enabled_root_files
from NAOD_TAU.processors.mass_processor import MassProcessor

DATA_CONFIG_PATH = Path(__file__).resolve().parent / "file_config.json"
MC_CONFIG_PATH = Path(__file__).resolve().parent / "file_config_mc.json"
OUTPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "mass_processor.root"


def build_fileset():
    """{"data": {"files": {path: "Events", ...}}, "mc": {...}}, coffea's
    fileset format: one entry per dataset name, each holding the ROOT
    files (and tree name) that belong to it."""
    fileset = {}
    for dataset, config_path in [("data", DATA_CONFIG_PATH), ("mc", MC_CONFIG_PATH)]:
        root_files = get_enabled_root_files(load_config(config_path))
        fileset[dataset] = {"files": {f["path"]: f["tree"] for f in root_files}}
    return fileset


def save_histograms(histograms, datasets):
    OUTPUT_ROOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with uproot.recreate(str(OUTPUT_ROOT_FILE)) as f:
        for name, hist_obj in histograms.items():
            for dataset in datasets:
                f[f"reco_tau_{name}_{dataset}"] = hist_obj[{"dataset": dataset}]
    print(f"wrote {OUTPUT_ROOT_FILE}")


def main():
    fileset = build_fileset()
    for dataset, entry in fileset.items():
        print(f"{dataset}: {list(entry['files'].keys())}")

    runner = processor.Runner(
        executor=processor.IterativeExecutor(),
        schema=NanoAODSchema,
    )
    result = runner(fileset, processor_instance=MassProcessor())

    print(f"good pairs: {result['good_pairs']}")
    save_histograms(result["histograms"], list(fileset.keys()))


if __name__ == "__main__":
    main()
