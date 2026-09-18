#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import awkward as ak

from NAOD_TAU.helpers.io import load_events
from NAOD_TAU.helpers.config import load_config, get_enabled_root_files
from NAOD_TAU.helpers.tau_collections.reader import get_tau_collection
from NAOD_TAU.helpers.lhe.angles import compute_delta_phi
from NAOD_TAU.helpers.histograms import make_1d_histogram, compute_auto_range, save_histograms

OUTPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "reco_tau_dphi_pt.root"


def select_leading_tau_pair(taus):
    paired = taus[ak.num(taus) >= 2]
    print(f"events with >= 2 taus: {len(paired)}")
    tau = paired[:, 0]
    antitau = paired[:, 1]
    return tau, antitau


def build_histograms(events):
    print(f"total events: {len(events)}")
    taus = get_tau_collection(events)
    print(f"nTau field present, total taus across all events: {ak.sum(ak.num(taus))}")

    tau, antitau = select_leading_tau_pair(taus)
    print(f"leading tau pairs: {len(tau)}")

    delta_phi = compute_delta_phi(tau, antitau).to_numpy()
    print(f"delta_phi array: {delta_phi.shape}, first values: {delta_phi[:5]}")

    pt = ak.concatenate([tau.pt, antitau.pt]).to_numpy()
    print(f"pt array: {pt.shape}, first values: {pt[:5]}")

    delta_phi_h = make_1d_histogram("delta_phi", delta_phi, 64, -3.2, 3.2)

    pt_low, pt_high = compute_auto_range(pt)
    pt_h = make_1d_histogram("pt", pt, 100, pt_low, pt_high)

    return {
        "reco_tau_delta_phi": delta_phi_h,
        "reco_tau_pt": pt_h,
    }


def main():
    config = load_config()
    root_file = get_enabled_root_files(config)[0]
    print(f"reading: {root_file['path']}")

    events = load_events(root_file["path"], tree_name=root_file["tree"])
    print(f"available fields: {list(events.fields)}")

    histograms = build_histograms(events)

    OUTPUT_ROOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_histograms(str(OUTPUT_ROOT_FILE), histograms)
    print(f"wrote {OUTPUT_ROOT_FILE}")


if __name__ == "__main__":
    main()
