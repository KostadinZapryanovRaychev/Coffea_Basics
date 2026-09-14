#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from NAOD_TAU.helpers.io import load_events
from NAOD_TAU.helpers.config import load_config, get_enabled_root_files
from NAOD_TAU.helpers.lhe import (
    select_lhe_tau_pairs,
    get_lhe_tau,
    get_lhe_antitau,
    compute_ditau_mass,
    compute_delta_phi,
)
from NAOD_TAU.helpers.histograms import (
    make_1d_histogram,
    make_2d_histogram,
    save_histograms,
)

OUTPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "lhe_histograms.root"


def build_lhe_histograms(events):
    selected = select_lhe_tau_pairs(events)
    tau = get_lhe_tau(selected)
    antitau = get_lhe_antitau(selected)

    mass = compute_ditau_mass(tau, antitau).to_numpy()
    delta_phi = compute_delta_phi(tau, antitau).to_numpy()

    mass_h = make_1d_histogram("mass", mass, 100, 0, 1000)
    delta_phi_h = make_1d_histogram("delta_phi", delta_phi, 64, -3.2, 3.2)
    mass_vs_delta_phi_h = make_2d_histogram(
        "mass", mass, 100, 0, 1000,
        "delta_phi", delta_phi, 64, -3.2, 3.2,
    )

    return {
        "lhe_mass": mass_h,
        "lhe_delta_phi": delta_phi_h,
        "lhe_mass_vs_delta_phi": mass_vs_delta_phi_h,
    }


def main():
    config = load_config()
    root_file = get_enabled_root_files(config)[0]
    events = load_events(root_file["path"], tree_name=root_file["tree"])
    histograms = build_lhe_histograms(events)

    OUTPUT_ROOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_histograms(str(OUTPUT_ROOT_FILE), histograms)


if __name__ == "__main__":
    main()
