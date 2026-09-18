#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import awkward as ak
import numpy as np

from NAOD_TAU.helpers.io import load_events
from NAOD_TAU.helpers.config import load_config, get_enabled_root_files
from NAOD_TAU.helpers.tau_collections.reader import get_tau_collection
from NAOD_TAU.helpers.mass import compute_invariant_mass
from NAOD_TAU.helpers.lhe.angles import compute_delta_phi
from NAOD_TAU.helpers.histograms import make_1d_histogram, save_histograms

OUTPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "reco_tau_mass.root"
DELTA_PHI_MIN = 2.5
TAU_PT_MIN = 20.0
TAU_ETA_MAX = 2.3


def select_events_with_two_taus(taus):
    return taus[ak.num(taus) >= 2]


def select_leading_tau_pair(taus):
    sorted_taus = taus[ak.argsort(taus.pt, ascending=False)]
    tau = sorted_taus[:, 0]
    antitau = sorted_taus[:, 1]
    return tau, antitau


def select_opposite_sign_pairs(tau, antitau):
    mask = (tau.charge * antitau.charge) == -1
    return tau[mask], antitau[mask]


def select_back_to_back_pairs(tau, antitau):
    delta_phi = compute_delta_phi(tau, antitau)
    mask = abs(delta_phi) > DELTA_PHI_MIN
    return tau[mask], antitau[mask]


def select_kinematic_pairs(tau, antitau):
    mask = (
        (tau.pt > TAU_PT_MIN) & (antitau.pt > TAU_PT_MIN)
        & (abs(tau.eta) < TAU_ETA_MAX) & (abs(antitau.eta) < TAU_ETA_MAX)
    )
    return tau[mask], antitau[mask]


def compute_pair_mass(events):
    taus = get_tau_collection(events)
    taus = select_events_with_two_taus(taus)
    tau, antitau = select_leading_tau_pair(taus)
    tau, antitau = select_opposite_sign_pairs(tau, antitau)
    tau, antitau = select_back_to_back_pairs(tau, antitau)
    tau, antitau = select_kinematic_pairs(tau, antitau)

    return compute_invariant_mass(tau, antitau).to_numpy()


def build_histograms(mass):
    mass_h = make_1d_histogram("mass", mass, 100, 0, 300)

    return {
        "reco_tau_mass": mass_h,
    }


def collect_mass_from_files(root_files):
    all_mass = []
    for root_file in root_files:
        print(f"reading: {root_file['path']}")
        events = load_events(root_file["path"], tree_name=root_file["tree"])

        mass = compute_pair_mass(events)
        print(f"{root_file['name']}: {mass.shape[0]} good pairs")

        all_mass.append(mass)

    return np.concatenate(all_mass)


def main():
    config = load_config()
    root_files = get_enabled_root_files(config)

    mass = collect_mass_from_files(root_files)
    print(f"total good pairs across all files: {mass.shape[0]}")

    histograms = build_histograms(mass)

    OUTPUT_ROOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_histograms(str(OUTPUT_ROOT_FILE), histograms)
    print(f"wrote {OUTPUT_ROOT_FILE}")


if __name__ == "__main__":
    main()
