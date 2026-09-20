#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import awkward as ak

from NAOD_TAU.helpers.io import load_events
from NAOD_TAU.helpers.config import load_config, get_enabled_root_files
from NAOD_TAU.helpers.gen_particles.reader import get_genpart_collection
from NAOD_TAU.helpers.gen_kinematics import compute_kinematics, build_histograms, extract_mass_point
from NAOD_TAU.helpers.histograms import save_histograms

MC_CONFIG_PATH = Path(__file__).resolve().parent / "file_config_mc.json"
OUTPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "genpart_kinematics.root"
IS_LAST_COPY = 1 << 13


def select_last_copy_taus(genpart):
    is_last_copy = (genpart.statusFlags & IS_LAST_COPY) != 0
    return genpart[is_last_copy & (abs(genpart.pdgId) == 15)]


def select_events_with_one_pair(taus):
    n_tau = ak.sum(taus.pdgId == 15, axis=1)
    n_antitau = ak.sum(taus.pdgId == -15, axis=1)
    return taus[(n_tau == 1) & (n_antitau == 1)]


def get_tau(taus):
    return taus[taus.pdgId == 15][:, 0]


def get_antitau(taus):
    return taus[taus.pdgId == -15][:, 0]


def main():
    config = load_config(MC_CONFIG_PATH)
    root_file = get_enabled_root_files(config)[0]
    print(f"reading: {root_file['path']}")

    events = load_events(root_file["path"], tree_name=root_file["tree"])
    genpart = get_genpart_collection(events)

    taus = select_events_with_one_pair(select_last_copy_taus(genpart))
    tau = get_tau(taus)
    antitau = get_antitau(taus)
    print(f"events with one last-copy tau and one anti-tau: {len(tau)}")

    mass_point = extract_mass_point(root_file["path"])
    kinematics = compute_kinematics(tau, antitau)
    histograms = build_histograms(kinematics, "gen", mass_point)

    OUTPUT_ROOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_histograms(str(OUTPUT_ROOT_FILE), histograms)
    print(f"wrote {OUTPUT_ROOT_FILE}")


if __name__ == "__main__":
    main()
