#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from NAOD_TAU.helpers.io import load_events
from NAOD_TAU.helpers.config import load_config, get_enabled_root_files, DEFAULT_CONFIG_PATH
from NAOD_TAU.helpers.tau_collections.reader import get_tau_collection
from NAOD_TAU.helpers.mass import compute_invariant_mass
from NAOD_TAU.helpers.lhe.angles import compute_delta_phi
from NAOD_TAU.helpers.kinematics import compute_pz, compute_cos_delta_phi
from NAOD_TAU.helpers.histograms import make_1d_histogram, make_2d_histogram, save_histograms
from NAOD_TAU.reco_tau_mass import (
    select_events_with_two_taus,
    select_leading_tau_pair,
    select_opposite_sign_pairs,
)

OUTPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "tau_mass_dphi_pz.root"


def build_histograms(events):
    taus = select_events_with_two_taus(get_tau_collection(events))
    tau, antitau = select_leading_tau_pair(taus)
    tau, antitau = select_opposite_sign_pairs(tau, antitau)
    print(f"opposite-sign leading pairs: {len(tau)}")

    mass = compute_invariant_mass(tau, antitau).to_numpy()
    pz = compute_pz(tau, antitau).to_numpy()
    cos_delta_phi = compute_cos_delta_phi(compute_delta_phi(tau, antitau)).to_numpy()

    return {
        "reco_tau_mass": make_1d_histogram("mass", mass, 100, 0, 500),
        "reco_tau_mass_vs_cos_delta_phi": make_2d_histogram(
            "mass", mass, 100, 0, 500,
            "cos_delta_phi", cos_delta_phi, 100, -1, 1,
        ),
        "reco_tau_pz_vs_cos_delta_phi": make_2d_histogram(
            "pz", pz, 100, -500, 500,
            "cos_delta_phi", cos_delta_phi, 100, -1, 1,
        ),
    }


def main(config_path=DEFAULT_CONFIG_PATH, output_file=OUTPUT_ROOT_FILE):
    config = load_config(config_path)
    root_file = get_enabled_root_files(config)[0]
    print(f"reading: {root_file['path']}")

    events = load_events(root_file["path"], tree_name=root_file["tree"])
    histograms = build_histograms(events)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    save_histograms(str(output_file), histograms)
    print(f"wrote {output_file}")


if __name__ == "__main__":
    main()
