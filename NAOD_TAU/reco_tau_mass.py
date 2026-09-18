#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import awkward as ak

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


def build_histograms(events):
    taus = get_tau_collection(events)
    taus = select_events_with_two_taus(taus)
    tau, antitau = select_leading_tau_pair(taus)
    tau, antitau = select_opposite_sign_pairs(tau, antitau)
    tau, antitau = select_back_to_back_pairs(tau, antitau)
    tau, antitau = select_kinematic_pairs(tau, antitau)

    mass = compute_invariant_mass(tau, antitau).to_numpy()
    print(f"mass array: {mass.shape}, first values: {mass[:5]}")

    mass_h = make_1d_histogram("mass", mass, 100, 0, 300)

    return {
        "reco_tau_mass": mass_h,
    }


def main():
    config = load_config()
    root_file = get_enabled_root_files(config)[0]
    print(f"reading: {root_file['path']}")

    events = load_events(root_file["path"], tree_name=root_file["tree"])
    histograms = build_histograms(events)

    OUTPUT_ROOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_histograms(str(OUTPUT_ROOT_FILE), histograms)
    print(f"wrote {OUTPUT_ROOT_FILE}")


if __name__ == "__main__":
    main()
