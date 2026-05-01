#!/usr/bin/env python3
"""Count initial taus from LHE particles event by event in nanoaodsim_coffea_1.root.

The script uses NanoEventsFactory + NanoAODSchema, which is the Coffea-recommended
way to read CMS-style NanoAOD ROOT files as awkward arrays.
"""

from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
from coffea.nanoevents import NanoAODSchema, NanoEventsFactory
from coffea.nanoevents.methods import vector


# Silence warnings about cross references that are not present in this sample.
NanoAODSchema.warn_missing_crossrefs = False

# Locate the ROOT file next to this script.
HERE = Path(__file__).resolve().parent
ROOT_FILE = HERE / "nanoaodsim_coffea_1.root"
TREE_NAME = "Events"


def load_events(root_file: Path):
    if not root_file.exists():
        raise FileNotFoundError(f"ROOT file not found: {root_file}")

    events = NanoEventsFactory.from_root(
        str(root_file),
        treepath=TREE_NAME,
        schemaclass=NanoAODSchema,
        metadata={"dataset": root_file.stem},
    ).events()

    return events


def count_lhe_taus_per_event(events):
    """Return per-event counts of LHE particles with |pdgId| == 15."""
    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")

    tau_mask = abs(events.LHEPart.pdgId) == 15
    return ak.to_numpy(ak.sum(tau_mask, axis=1))

def select_events_with_one_tau_pair(events):
    """Return mask + filtered info for events with exactly 1 tau+ and 1 tau- in LHEPart."""

    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")

    pdg = events.LHEPart.pdgId

    tau_plus_mask = pdg == 15
    tau_minus_mask = pdg == -15

    n_tau_plus = ak.sum(tau_plus_mask, axis=1)
    n_tau_minus = ak.sum(tau_minus_mask, axis=1)

    event_mask = (n_tau_plus == 1) & (n_tau_minus == 1)

    filtered_events = events[event_mask]

    return filtered_events, ak.to_numpy(event_mask)


def lorentz_vector_demo_for_muon_events(events, max_events=5):
    """Build Lorentz vectors for muon-pair events and compute key observables."""
    muon_events, _ = select_events_with_one_mumu_pair(events)
    if len(muon_events) > 0:
        selected_events = muon_events
        neg_pdg, pos_pdg = 13, -13
        pair_label = "mu- and mu+"
        object_label = "dimuon"
    else:
        tau_events, _ = select_events_with_one_tau_pair(events)
        if len(tau_events) == 0:
            raise ValueError("No events with exactly one opposite-sign lepton pair were found")
        selected_events = tau_events
        neg_pdg, pos_pdg = 15, -15
        pair_label = "tau- and tau+"
        object_label = "ditau"

    pdg = selected_events.LHEPart.pdgId
    lep_minus = selected_events.LHEPart[pdg == neg_pdg]
    lep_plus = selected_events.LHEPart[pdg == pos_pdg]

    lep_minus_lv = ak.zip(
        {
            "pt": lep_minus.pt,
            "eta": lep_minus.eta,
            "phi": lep_minus.phi,
            "mass": lep_minus.mass,
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )
    #TODO to check if with=name consinst as reserved keyword PtEtaPhiMLorentzVector
    #TODO each line to be known what exactly does
    lep_plus_lv = ak.zip(
        {
            "pt": lep_plus.pt,
            "eta": lep_plus.eta,
            "phi": lep_plus.phi,
            "mass": lep_plus.mass,
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )

    lep_minus_lv = lep_minus_lv[:, 0] 
    lep_plus_lv = lep_plus_lv[:, 0]

    dilepton_lv = lep_minus_lv + lep_plus_lv
    dilepton_mass = dilepton_lv.mass
    dilepton_pt = dilepton_lv.pt
    delta_r = lep_minus_lv.delta_r(lep_plus_lv)
    delta_phi = lep_minus_lv.delta_phi(lep_plus_lv)

    n_show = min(max_events, len(selected_events))
    print(f"\nLorentzVector demo (first events with exactly one {pair_label}):")
    for i in range(n_show):
        print(
            f"Event {i}: m_{object_label}={dilepton_mass[i]:.3f} GeV, "
            f"pt_{object_label}={dilepton_pt[i]:.3f} GeV, "
            f"deltaR={delta_r[i]:.3f}, deltaPhi={delta_phi[i]:.3f}"
        )

    return {
        "lep_minus": lep_minus_lv,
        "lep_plus": lep_plus_lv,
        "dilepton": dilepton_lv,
        "dilepton_mass": dilepton_mass,
        "dilepton_pt": dilepton_pt,
        "delta_r": delta_r,
        "delta_phi": delta_phi,
        "object_label": object_label,
    }


def save_basic_histograms(
    output_dir: Path,
    lhe_tau_counts,
    tau_events,
    electron_events,
    muon_events,
    lorentz_results,
):
    """Create and save a few basic histograms to output_dir."""
    output_dir.mkdir(exist_ok=True)

    # 1) LHE tau multiplicity
    plt.figure(figsize=(8, 5))
    max_count = int(np.max(lhe_tau_counts)) if len(lhe_tau_counts) else 0
    bins = np.arange(-0.5, max_count + 1.5, 1.0)
    plt.hist(
        lhe_tau_counts,
        bins=bins,
        color="steelblue",
        edgecolor="black",
        alpha=0.9,
    )
    plt.xlabel("Number of LHE taus per event (|pdgId| = 15)")
    plt.ylabel("Number of events")
    plt.title("LHE tau multiplicity per event")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    p1 = output_dir / "hist_lhe_tau_multiplicity.png"
    plt.savefig(p1, dpi=150)
    plt.close()

    # 2) Selected event counts per channel
    labels = ["tau+tau-", "e+e-", "mu+mu-"]
    values = [len(tau_events), len(electron_events), len(muon_events)]
    plt.figure(figsize=(7, 5))
    plt.bar(labels, values, color=["tab:blue", "tab:orange", "tab:green"], edgecolor="black")
    plt.ylabel("Number of selected events")
    plt.title("Events with exactly one opposite-sign LHE pair")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    p2 = output_dir / "hist_selected_channel_counts.png"
    plt.savefig(p2, dpi=150)
    plt.close()

    # 3) Dilepton mass
    dilepton_mass = np.asarray(ak.to_numpy(lorentz_results["dilepton_mass"]))
    plt.figure(figsize=(8, 5))
    plt.hist(dilepton_mass, bins=60, color="mediumpurple", edgecolor="black", alpha=0.9)
    plt.xlabel(f"{lorentz_results['object_label']} mass [GeV]")
    plt.ylabel("Events")
    plt.title(f"{lorentz_results['object_label'].capitalize()} mass distribution")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    p3 = output_dir / f"hist_{lorentz_results['object_label']}_mass.png"
    plt.savefig(p3, dpi=150)
    plt.close()

    # 4) Dilepton pT
    dilepton_pt = np.asarray(ak.to_numpy(lorentz_results["dilepton_pt"]))
    plt.figure(figsize=(8, 5))
    plt.hist(dilepton_pt, bins=60, color="teal", edgecolor="black", alpha=0.9)
    plt.xlabel(f"{lorentz_results['object_label']} pT [GeV]")
    plt.ylabel("Events")
    plt.title(f"{lorentz_results['object_label'].capitalize()} pT distribution")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    p4 = output_dir / f"hist_{lorentz_results['object_label']}_pt.png"
    plt.savefig(p4, dpi=150)
    plt.close()

    # 5) DeltaR
    delta_r = np.asarray(ak.to_numpy(lorentz_results["delta_r"]))
    plt.figure(figsize=(8, 5))
    plt.hist(delta_r, bins=60, color="indianred", edgecolor="black", alpha=0.9)
    plt.xlabel(r"$\Delta R(\ell^{-}, \ell^{+})$")
    plt.ylabel("Events")
    plt.title(f"{lorentz_results['object_label'].capitalize()} DeltaR distribution")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    p5 = output_dir / f"hist_{lorentz_results['object_label']}_deltaR.png"
    plt.savefig(p5, dpi=150)
    plt.close()

    print(f"Saved: {p1}")
    print(f"Saved: {p2}")
    print(f"Saved: {p3}")
    print(f"Saved: {p4}")
    print(f"Saved: {p5}")


def main():
    """Load the file and make histogram of LHE tau multiplicity per event."""
    events = load_events(ROOT_FILE)
    lhe_tau_counts = count_lhe_taus_per_event(events)
    print(f"Total events: {len(lhe_tau_counts)}")
    filtered_events, _ = select_events_with_one_tau_pair(events)
    print(f"Number of events with exactly 1 tau+ and 1 tau- in LHEPart: {len(filtered_events)}")
    lorentz_results = lorentz_vector_demo_for_muon_events(events, max_events=5)
    print(
        f"Computed {lorentz_results['object_label']} masses for "
        f"{len(lorentz_results['dilepton_mass'])} selected events"
    )

    output_dir = HERE / "outputs"
    save_basic_histograms(
        output_dir=output_dir,
        lhe_tau_counts=lhe_tau_counts,
        tau_events=filtered_events,
        lorentz_results=lorentz_results,
    )


if __name__ == "__main__":
    main()