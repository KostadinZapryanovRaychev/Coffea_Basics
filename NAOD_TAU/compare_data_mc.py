#!/usr/bin/env python3

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
PLOT_DIR = OUTPUT_DIR / "comparison"

FILE_PAIRS = [
    ("reco_tau_mass.root", "mc_reco_tau_mass.root"),
    ("reco_tau_dphi_pt.root", "mc_reco_tau_dphi_pt.root"),
    ("tau_mass_dphi_pz.root", "mc_tau_mass_dphi_pz.root"),
]


def get_1d_histogram_names(root_file):
    return [
        key.split(";")[0]
        for key, class_name in root_file.classnames().items()
        if class_name.startswith("TH1")
    ]


def read_normalized(root_file, name):
    values, edges = root_file[name].to_numpy()
    total = values.sum()
    return (values / total if total > 0 else values), edges


def save_overlay(name, data_hist, mc_hist):
    data_values, edges = data_hist
    mc_values, _ = mc_hist
    centers = 0.5 * (edges[:-1] + edges[1:])

    fig, ax = plt.subplots()
    ax.step(centers, data_values, where="mid", label="data")
    ax.step(centers, mc_values, where="mid", label="MC")
    ax.set_xlabel(name)
    ax.set_ylabel("fraction of entries")
    ax.legend()

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(PLOT_DIR / f"{name}.png")
    plt.close(fig)


def compare_files(data_name, mc_name):
    with uproot.open(OUTPUT_DIR / data_name) as data_file, uproot.open(OUTPUT_DIR / mc_name) as mc_file:
        shared = set(get_1d_histogram_names(data_file)) & set(get_1d_histogram_names(mc_file))
        for name in sorted(shared):
            save_overlay(name, read_normalized(data_file, name), read_normalized(mc_file, name))
            print(f"saved {PLOT_DIR / (name + '.png')}")


def main():
    for data_name, mc_name in FILE_PAIRS:
        if not (OUTPUT_DIR / data_name).exists() or not (OUTPUT_DIR / mc_name).exists():
            print(f"skipping {data_name} / {mc_name}: file missing")
            continue
        compare_files(data_name, mc_name)


if __name__ == "__main__":
    main()
