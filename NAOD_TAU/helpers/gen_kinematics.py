import re

import awkward as ak

from NAOD_TAU.helpers.histograms import make_1d_histogram, make_2d_histogram

DEFAULT_MASS_POINT = 500.0


def extract_mass_point(path):
    match = re.search(r"M-(\d+)", path)
    return float(match.group(1)) if match else DEFAULT_MASS_POINT


def to_numpy(values):
    return ak.to_numpy(values)


def compute_kinematics(tau, antitau):
    return {
        "tau_pt": to_numpy(tau.pt),
        "antitau_pt": to_numpy(antitau.pt),
        "tau_pz": to_numpy(tau.pz),
        "antitau_pz": to_numpy(antitau.pz),
        "tau_eta": to_numpy(tau.eta),
        "antitau_eta": to_numpy(antitau.eta),
        "tau_phi": to_numpy(tau.phi),
        "antitau_phi": to_numpy(antitau.phi),
        "mass": to_numpy((tau + antitau).mass),
        "delta_phi": to_numpy(tau.phi - antitau.phi),
        "delta_eta": to_numpy(tau.eta - antitau.eta),
        "delta_r": to_numpy(tau.delta_r(antitau)),
    }


def get_1d_specs(mass_point):
    return [
        ("tau_pt", 120, 0, 0.6 * mass_point),
        ("antitau_pt", 120, 0, 0.6 * mass_point),
        ("tau_pz", 120, -1.5 * mass_point, 1.5 * mass_point),
        ("antitau_pz", 120, -1.5 * mass_point, 1.5 * mass_point),
        ("tau_eta", 120, -3, 3),
        ("antitau_eta", 120, -3, 3),
        ("tau_phi", 120, -3.2, 3.2),
        ("antitau_phi", 120, -3.2, 3.2),
        ("mass", 250, 0, 2.0 * mass_point),
        ("delta_phi", 120, -6.4, 6.4),
        ("delta_eta", 120, -7.5, 7.5),
        ("delta_r", 120, 0, 6),
    ]


def build_histograms(kinematics, prefix, mass_point):
    histograms = {}
    for key, bins, low, high in get_1d_specs(mass_point):
        histograms[f"{prefix}_{key}"] = make_1d_histogram(key, kinematics[key], bins, low, high)

    histograms[f"{prefix}_delta_r_vs_delta_phi"] = make_2d_histogram(
        "delta_r", kinematics["delta_r"], 120, 0, 6,
        "delta_phi", kinematics["delta_phi"], 120, -6.4, 6.4,
    )
    return histograms
