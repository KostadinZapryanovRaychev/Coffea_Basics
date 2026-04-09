#!/usr/bin/env python3
"""Read all muon transverse momentum values from nanoaodsim_coffea_1.root using Coffea.

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


def get_all_muon_pt(events):
    """Return all muon pt values flattened into a one-dimensional array."""
    if "Muon" not in events.fields:
        raise AttributeError("Muon collection not found in this ROOT file")

    muons = events.Muon
    muon_pt = muons.pt
    all_muon_pt = ak.flatten(muon_pt)
    return ak.to_numpy(all_muon_pt)


def main():
    """Load the file, extract muon pt values, and print a short summary."""
    events = load_events(ROOT_FILE)
    muon_pt = get_all_muon_pt(events)
    output_dir = HERE / "outputs"
    output_dir.mkdir(exist_ok=True)
    histogram_path = output_dir / "muon_pt_histogram.png"

    print(f"ROOT file: {ROOT_FILE}")
    print(f"Tree name: {TREE_NAME}")
    print(f"Number of events: {len(events)}")
    print(f"Total number of muons: {len(muon_pt)}")

    if len(muon_pt) == 0:
        print("No muons were found in the file.")
        return

    print(f"Minimum muon pt: {muon_pt.min():.3f} GeV")
    print(f"Maximum muon pt: {muon_pt.max():.3f} GeV")
    print(f"Mean muon pt: {muon_pt.mean():.3f} GeV")

    plt.figure(figsize=(8, 5))
    plt.hist(muon_pt, bins=80, range=(0, min(float(muon_pt.max()), 200.0)), color="steelblue", edgecolor="black")
    plt.xlabel("Muon $p_T$ [GeV]")
    plt.ylabel("Number of muons")
    plt.title("Muon transverse momentum distribution")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(histogram_path, dpi=150)
    plt.close()

    print(f"Saved histogram: {histogram_path}")
    print("\nAll muon pt values:")
    print(muon_pt)


if __name__ == "__main__":
    main()
