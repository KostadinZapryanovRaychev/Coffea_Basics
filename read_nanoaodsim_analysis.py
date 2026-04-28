#!/usr/bin/env python3
"""Minimal tau-only analysis: select LHE/Gen tau pairs and plot a simple histogram.

This file is intentionally reduced: it provides two functions:
- `load_tau_pairs(events)` returns LHE-selected events and Gen-selected events (if present).
- `make_tau_histogram(output_dir, lhe_selected, gen_selected=None)` saves a single
  invariant-mass histogram (LHE, overlay Gen if available).
"""

from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
from coffea.nanoevents import NanoAODSchema, NanoEventsFactory
from coffea.nanoevents.methods import vector


# Silence warnings about missing crossrefs in small samples
NanoAODSchema.warn_missing_crossrefs = False

HERE = Path(__file__).resolve().parent
ROOT_FILE = HERE / "nanoaodsim_coffea_1.root"
TREE_NAME = "Events"


def load_events(root_file: Path):
    if not root_file.exists():
        raise FileNotFoundError(f"ROOT file not found: {root_file}")
    return (
        NanoEventsFactory.from_root({str(root_file): TREE_NAME}, schemaclass=NanoAODSchema)
        .events()
    )


def load_tau_pairs(events):
    """Return (lhe_selected, gen_selected_or_None, event_mask_numpy).

    - `lhe_selected` contains only events with exactly one tau- (pdgId==15)
      and one tau+ (pdgId==-15) in the `LHEPart` collection.
    - `gen_selected` is the analogous selection on `GenPart` if present,
      otherwise None.
    - `event_mask_numpy` is a boolean numpy array for the LHE selection.
    """
    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")

    pdg_lhe = events.LHEPart.pdgId
    n_minus = ak.sum(pdg_lhe == 15, axis=1)
    n_plus = ak.sum(pdg_lhe == -15, axis=1)
    lhe_mask = (n_minus == 1) & (n_plus == 1)
    lhe_selected = events[lhe_mask]
    lhe_mask_np = ak.to_numpy(lhe_mask)

    gen_selected = None
    if "GenPart" in events.fields:
        pdg_gen = events.GenPart.pdgId
        status_gen = events.GenPart.status
        # GenPart usually contains several copies of the same tau in the decay chain.
        # Status 23 picks the hard-process tau pair in this sample.
        n_minus_g = ak.sum((pdg_gen == 15) & (status_gen == 23), axis=1)
        n_plus_g = ak.sum((pdg_gen == -15) & (status_gen == 23), axis=1)
        gen_mask = (n_minus_g == 1) & (n_plus_g == 1)
        gen_selected = events[gen_mask]
        # by this mask we select tau that are pairs in event and come from the process hard scattering

    return lhe_selected, gen_selected, lhe_mask_np


def make_tau_histogram(output_dir: Path, lhe_selected, gen_selected=None):
    """Make a simple invariant-mass histogram for LHE taus and optional Gen taus.

    Saves `outputs/hist_tau_mass.png` (overlaying Gen if available).
    """
    output_dir.mkdir(exist_ok=True)

    def mass_from_parts(parts, mask_minus, mask_plus):
        lep_minus = parts[mask_minus]
        lep_plus = parts[mask_plus]

        lep_minus_lv = ak.zip(
            {"pt": lep_minus.pt, "eta": lep_minus.eta, "phi": lep_minus.phi, "mass": lep_minus.mass},
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )
        lep_plus_lv = ak.zip(
            {"pt": lep_plus.pt, "eta": lep_plus.eta, "phi": lep_plus.phi, "mass": lep_plus.mass},
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )

        return ak.to_numpy((lep_minus_lv[:, 0] + lep_plus_lv[:, 0]).mass)

    lhe_masses = mass_from_parts(
        lhe_selected.LHEPart,
        lhe_selected.LHEPart.pdgId == 15,
        lhe_selected.LHEPart.pdgId == -15,
    )

    plt.figure(figsize=(8, 5))
    bins = 60
    plt.hist(lhe_masses, bins=bins, color="tab:blue", alpha=0.7, label="LHE")

    if gen_selected is not None:
        gen_masses = mass_from_parts(
            gen_selected.GenPart,
            (gen_selected.GenPart.pdgId == 15) & (gen_selected.GenPart.status == 23),
            (gen_selected.GenPart.pdgId == -15) & (gen_selected.GenPart.status == 23),
        )
        plt.hist(gen_masses, bins=bins, color="tab:orange", alpha=0.5, label="GenPart")

    plt.xlabel("Ditau mass [GeV]")
    plt.ylabel("Events")
    plt.title("Ditau invariant-mass (LHE, overlay Gen if present)")
    plt.legend()
    plt.tight_layout()

    outp = output_dir / "hist_tau_mass.png"
    plt.savefig(outp, dpi=150)
    plt.close()
    print(f"Saved: {outp}")


def main():
    events = load_events(ROOT_FILE)
    lhe_selected, gen_selected, lhe_mask = load_tau_pairs(events)
    print(f"Events with exactly one LHE tau- and one LHE tau+: {len(lhe_selected)}")
    if gen_selected is not None:
        print(f"Events with exactly one GenPart tau- and tau+: {len(gen_selected)}")

    output_dir = HERE / "outputs"
    make_tau_histogram(output_dir, lhe_selected, gen_selected=gen_selected)


if __name__ == "__main__":
    main()
