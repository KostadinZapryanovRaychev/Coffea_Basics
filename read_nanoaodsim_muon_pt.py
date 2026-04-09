#!/usr/bin/env python3
"""Count initial taus from LHE particles event by event in nanoaodsim_coffea_1.root.

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


def count_lhe_taus_per_event(events):
    """Return per-event counts of LHE particles with |pdgId| == 15."""
    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")

    tau_mask = abs(events.LHEPart.pdgId) == 15
    return ak.to_numpy(ak.sum(tau_mask, axis=1))


def main():
    """Load the file and make histogram of LHE tau multiplicity per event."""
    events = load_events(ROOT_FILE)
    lhe_tau_counts = count_lhe_taus_per_event(events)
    output_dir = HERE / "outputs"
    output_dir.mkdir(exist_ok=True)
    counts_path = output_dir / "lhe_tau_counts_per_event.txt"
    counts_plot_path = output_dir / "lhe_tau_multiplicity_all_events.png"

    with counts_path.open("w", encoding="utf-8") as handle:
        for count in lhe_tau_counts:
            handle.write(f"{int(count)}\n")

    plt.figure(figsize=(8, 5))
    max_count = int(lhe_tau_counts.max())
    bins = range(0, max_count + 2)
    plt.hist(lhe_tau_counts, bins=bins, align="left", rwidth=0.85, color="steelblue", edgecolor="black")
    plt.xlabel("Number of LHE taus per event (|pdgId| = 15)")
    plt.ylabel("Number of events")
    plt.title("LHE tau multiplicity per event (all events)")
    plt.xticks(range(0, max_count + 1))
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(counts_plot_path, dpi=150)
    plt.close()

    print(f"Total events: {len(lhe_tau_counts)}")
    print(f"Saved LHE tau counts per event to: {counts_path}")
    print(f"Saved LHE tau multiplicity histogram to: {counts_plot_path}")
    print(f"Min LHE taus per event: {int(lhe_tau_counts.min())}")
    print(f"Max LHE taus per event: {int(lhe_tau_counts.max())}")


if __name__ == "__main__":
    main()
