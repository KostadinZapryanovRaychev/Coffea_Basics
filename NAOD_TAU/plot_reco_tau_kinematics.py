#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import uproot

INPUT_ROOT_FILE = Path(__file__).resolve().parent / "outputs" / "reco_tau_kinematics.root"
OUTPUT_PNG_FILE = Path(__file__).resolve().parent / "outputs" / "reco_tau_kinematics.png"

HISTOGRAM_COLORS = {
    "reco_tau_mass": "tab:blue",
    "reco_tau_pz": "tab:red",
    "reco_tau_delta_r": "tab:green",
    "reco_tau_cos_delta_phi": "tab:orange",
    "reco_tau_eta": "tab:purple",
}


def main():
    f = uproot.open(INPUT_ROOT_FILE)

    fig, axes = plt.subplots(len(HISTOGRAM_COLORS), 1, figsize=(8, 4 * len(HISTOGRAM_COLORS)))

    for ax, (name, color) in zip(axes, HISTOGRAM_COLORS.items()):
        values, edges = f[name].to_numpy()
        ax.step(edges[:-1], values, where="post", color=color)
        ax.set_title(name)

    fig.tight_layout()
    fig.savefig(OUTPUT_PNG_FILE)
    print(f"wrote {OUTPUT_PNG_FILE}")


if __name__ == "__main__":
    main()
