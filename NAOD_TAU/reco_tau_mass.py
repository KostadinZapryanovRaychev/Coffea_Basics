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
from NAOD_TAU.helpers.mass import (
    compute_invariant_mass,
    compute_invariant_mass_formula,
    compute_invariant_mass_neutrino_corrected,
)
from NAOD_TAU.helpers.lhe.angles import compute_delta_phi
from NAOD_TAU.helpers.kinematics import compute_pz, compute_delta_r, compute_cos_delta_phi
from NAOD_TAU.helpers.histograms import make_1d_histogram, save_histograms

OUTPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "reco_tau_mass.root"
DELTA_PHI_MIN = 2.5
TAU_PT_MIN = 20.0
TAU_ETA_MAX = 2.3

# id identification 
# missing energy to checked 
# the exact how the mass is reconstructed 


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


def compute_pair_kinematics(events):
    taus = get_tau_collection(events)
    taus = select_events_with_two_taus(taus)
    tau, antitau = select_leading_tau_pair(taus)
    tau, antitau = select_opposite_sign_pairs(tau, antitau)
    tau, antitau = select_back_to_back_pairs(tau, antitau)
    tau, antitau = select_kinematic_pairs(tau, antitau)

    delta_phi = compute_delta_phi(tau, antitau)

    return {
        "mass": compute_invariant_mass(tau, antitau).to_numpy(),
        "mass_formula": compute_invariant_mass_formula(tau, antitau).to_numpy(),
        "mass_formula_neutrino": compute_invariant_mass_neutrino_corrected(tau, antitau).to_numpy(),
        "pz": compute_pz(tau, antitau).to_numpy(),
        "delta_r": compute_delta_r(tau, antitau).to_numpy(),
        "cos_delta_phi": compute_cos_delta_phi(delta_phi).to_numpy(),
        "tau_eta": ak.concatenate([tau.eta, antitau.eta]).to_numpy(),
    }


def build_histograms(kinematics):
    return {
        "reco_tau_mass": make_1d_histogram("mass", kinematics["mass"], 100, 0, 500),
        "reco_tau_mass_formula": make_1d_histogram("mass_formula", kinematics["mass_formula"], 100, 0, 500),
        "reco_tau_mass_formula_neutrino": make_1d_histogram("mass_formula_neutrino", kinematics["mass_formula_neutrino"], 100, 0, 500),
        "reco_tau_pz": make_1d_histogram("pz", kinematics["pz"], 100, -500, 500),
        "reco_tau_delta_r": make_1d_histogram("delta_r", kinematics["delta_r"], 64, 0, 6),
        "reco_tau_cos_delta_phi": make_1d_histogram("cos_delta_phi", kinematics["cos_delta_phi"], 100, -1, 1),
        "reco_tau_eta": make_1d_histogram("eta", kinematics["tau_eta"], 60, -TAU_ETA_MAX, TAU_ETA_MAX),
    }


def collect_kinematics_from_files(root_files):
    accumulated = {}
    for root_file in root_files:
        print(f"reading: {root_file['path']}")
        events = load_events(root_file["path"], tree_name=root_file["tree"])

        kinematics = compute_pair_kinematics(events)
        print(f"{root_file['name']}: {kinematics['mass'].shape[0]} good pairs")

        for key, values in kinematics.items():
            accumulated.setdefault(key, []).append(values)

    return {key: np.concatenate(values) for key, values in accumulated.items()}


def main():
    config = load_config()
    root_files = get_enabled_root_files(config)

    kinematics = collect_kinematics_from_files(root_files)
    print(f"total good pairs across all files: {kinematics['mass'].shape[0]}")
    print(f"max |mass - mass_formula|: {np.max(np.abs(kinematics['mass'] - kinematics['mass_formula']))}")

    histograms = build_histograms(kinematics)

    OUTPUT_ROOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_histograms(str(OUTPUT_ROOT_FILE), histograms)
    print(f"wrote {OUTPUT_ROOT_FILE}")


if __name__ == "__main__":
    main()
