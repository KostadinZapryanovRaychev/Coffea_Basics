#!/usr/bin/env python3
"""Count the reconstructed taus event by event in nanoaodsim_coffea_1.root using Coffea.

The script uses NanoEventsFactory + NanoAODSchema, which is the Coffea-recommended
way to read CMS-style NanoAOD ROOT files as awkward arrays.
"""

from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
from coffea.nanoevents import NanoAODSchema, NanoEventsFactory


# Silence warnings about cross references that are not present in this sample.
NanoAODSchema.warn_missing_crossrefs = False

# Locate the ROOT file next to this script.
HERE = Path(__file__).resolve().parent
ROOT_FILE = HERE / "nanoaodsim_coffea_1.root"
TREE_NAME = "Events"


def load_events(root_file: Path):
    """Open the ROOT file and return a NanoEvents object."""
    if not root_file.exists():
        raise FileNotFoundError(f"ROOT file not found: {root_file}")

    return NanoEventsFactory.from_root(
        {str(root_file): TREE_NAME},
        schemaclass=NanoAODSchema,
        metadata={"dataset": root_file.stem},
    ).events()


def count_taus_per_event(events):
    """Return the number of taus in each event."""
    if "Tau" not in events.fields:
        raise AttributeError("Tau collection not found in this ROOT file")

    return ak.to_numpy(ak.num(events.Tau))


def get_tau_pt_values(events):
    """Return all tau pT values flattened into a one-dimensional NumPy array."""
    if "Tau" not in events.fields:
        raise AttributeError("Tau collection not found in this ROOT file")

    return ak.to_numpy(ak.flatten(events.Tau.pt))


def main():
    """Load the file and print the tau count for each event."""
    events = load_events(ROOT_FILE)
    tau_counts = count_taus_per_event(events)
    first_1000_events = events[:1000]
    first_1000_tau_counts = tau_counts[:1000]
    first_1000_tau_pts = get_tau_pt_values(first_1000_events)
    output_dir = HERE / "outputs"
    output_dir.mkdir(exist_ok=True)
    counts_path = output_dir / "tau_counts_per_event.txt"
    counts_plot_path = output_dir / "tau_counts_first_1000_events.png"
    pt_plot_path = output_dir / "tau_pt_first_1000_events.png"

    with counts_path.open("w", encoding="utf-8") as handle:
        for count in tau_counts:
            handle.write(f"{int(count)}\n")

    event_numbers = list(range(1, len(first_1000_tau_counts) + 1))

    plt.figure(figsize=(10, 4))
    plt.bar(event_numbers, first_1000_tau_counts, color="darkorange", edgecolor="black")
    plt.xlabel("Event number")
    plt.ylabel("Number of taus")
    plt.title("Tau multiplicity in the first 1000 events")
    plt.xlim(1, 1000)
    plt.tight_layout()
    plt.savefig(counts_plot_path, dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.hist(first_1000_tau_pts, bins=40, color="steelblue", edgecolor="black")
    plt.xlabel("Tau $p_T$ [GeV]")
    plt.ylabel("Number of taus")
    plt.title("Tau transverse momentum in the first 1000 events")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(pt_plot_path, dpi=150)
    plt.close()

    print(f"Total events: {len(tau_counts)}")
    print(f"Saved per-event tau counts to: {counts_path}")
    print(f"Saved first-1000 tau count plot to: {counts_plot_path}")
    print(f"Saved first-1000 tau pT plot to: {pt_plot_path}")
    print("First 20 event tau counts:")
    print(first_1000_tau_counts[:20])


if __name__ == "__main__":
    main()
