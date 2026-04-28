#!/usr/bin/env python3
"""Count initial taus from LHE particles event by event in nanoaodsim_coffea_1.root.

The script uses NanoEventsFactory + NanoAODSchema, which is the Coffea-recommended
way to read CMS-style NanoAOD ROOT files as awkward arrays.
"""

from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
from coffea.nanoevents import NanoAODSchema, NanoEventsFactory
from coffea.nanoevents.methods import vector


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
    

    events = NanoEventsFactory.from_root(
        {str(root_file): TREE_NAME},
        schemaclass=NanoAODSchema,
        metadata={"dataset": root_file.stem},
    ).events()
    # Number of events loaded: 60806
    # print(f"Number of events loaded: {len(events)}")
    # print(events[0])
    # {SoftActivityJetHT5: ??, GenVtx: {x: ??, y: ??, ...}, GenPart: ??, ...} - It does NOT read all data from the ROOT file immediately It only loads data when you actually use it
    # print(ak.to_list(events.GenPart.pdgId[0]))
    # [5, -5, 15, -15, 15, -15, 5114, 2, -5, 513, 3, 21, 21, 21, -1, -16, 111, 211, 16, 11, -12, 5122, 11, -11, 511, 22, 22, 4122, 411, -411, 11, -11, -11, 12, 13, -14]
    # GenPart contains not just initial particles, but a full “particle genealogy” of the event (initial + intermediate + final). ids of them
    return events


def count_lhe_taus_per_event(events):
    """Return per-event counts of LHE particles with |pdgId| == 15."""
    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")
    
    # Proton collision
    # ↓
    # Hard scattering (matrix element)
    # ↓  ← THIS IS LHEPart LEVEL
    # LHE particles
    # ↓
    # Parton shower (gluon radiation)
    # ↓
    # Hadronization
    # ↓
    # Stable particles (what detectors see)
    # counts = ak.num(events.LHEPart.pdgId, axis=1)
    # print(f"First 10 events: {counts[:10]}")
    # Every event has exactly 4 LHE particles (at least for the first 10 events)
    # First 10 events: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

    tau_mask = abs(events.LHEPart.pdgId) == 15
    return ak.to_numpy(ak.sum(tau_mask, axis=1))

def select_events_with_one_tau_pair(events):
    """Return mask + filtered info for events with exactly 1 tau+ and 1 tau- in LHEPart."""

    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")

    pdg = events.LHEPart.pdgId

    # TODO :LHEPart_status	Int_t	LHE particle status; -1:incoming, 1:outgoing this to be checked (I want to take the child particles)

    # Count tau+ (15) and tau- (-15)
    # TODO GenPart_statusFlags	UShort_t	gen status flags stored bitwise, bits are: 0 : isPrompt, 1 : isDecayedLeptonHadron, 2 : isTauDecayProduct, 3 : isPromptTauDecayProduct, 4 : isDirectTauDecayProduct, 5 : isDirectPromptTauDecayProduct, 6 : isDirectHadronDecayProduct, 7 : isHardProcess, 8 : fromHardProcess, 9 : isHardProcessTauDecayProduct, 10 : isDirectHardProcessTauDecayProduct, 11 : fromHardProcessBeforeFSR, 12 : isFirstCopy, 13 : isLastCopy, 14 : isLastCopyBeforeFSR,
    # should be searched if it is prompted (both should be prompted) and if it is the first copy (both should be the first copy)
    # also is first isFirstCopy to be checked 
    tau_plus_mask = pdg == 15
    tau_minus_mask = pdg == -15

    n_tau_plus = ak.sum(tau_plus_mask, axis=1)
    n_tau_minus = ak.sum(tau_minus_mask, axis=1)

    # Select events with exactly 1 +tau and 1 -tau
    event_mask = (n_tau_plus == 1) & (n_tau_minus == 1)

    # Apply mask to events
    filtered_events = events[event_mask]

    return filtered_events, ak.to_numpy(event_mask)

def select_events_with_one_ee_pair(events):
    """Select events with exactly 1 electron (11) and 1 positron (-11) in LHEPart."""

    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")

    pdg = events.LHEPart.pdgId

    # Electron and positron masks
    e_minus_mask = pdg == 11
    e_plus_mask = pdg == -11

    n_e_minus = ak.sum(e_minus_mask, axis=1)
    n_e_plus = ak.sum(e_plus_mask, axis=1)

    # exactly 1 electron and 1 positron
    event_mask = (n_e_minus == 1) & (n_e_plus == 1)

    filtered_events = events[event_mask]

    return filtered_events, ak.to_numpy(event_mask)


def select_events_with_one_mumu_pair(events):
    """Select events with exactly 1 mu- (13) and 1 mu+ (-13) in LHEPart."""

    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")

    pdg = events.LHEPart.pdgId

    mu_minus_mask = pdg == 13
    mu_plus_mask = pdg == -13

    n_mu_minus = ak.sum(mu_minus_mask, axis=1)
    n_mu_plus = ak.sum(mu_plus_mask, axis=1)

    event_mask = (n_mu_minus == 1) & (n_mu_plus == 1)

    filtered_events = events[event_mask]

    return filtered_events, ak.to_numpy(event_mask)


def lorentz_vector_demo_for_muon_events(events, max_events=5):
    """Build Lorentz vectors for muon-pair events and compute key observables.

    This example uses LHEPart (generator-level) muons to show how Coffea vector
    methods work with awkward arrays.
    """
    muon_events, _ = select_events_with_one_mumu_pair(events)
    if len(muon_events) > 0:
        selected_events = muon_events
        neg_pdg, pos_pdg = 13, -13
        pair_label = "mu- and mu+"
        object_label = "dimuon"
    else:
        # This sample has no muon-pair LHE events, so fall back to tau pairs.
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

    # One negative and one positive lepton per selected event, so index 0 is safe.
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


def main():
    """Load the file and make histogram of LHE tau multiplicity per event."""
    events = load_events(ROOT_FILE)
    lhe_tau_counts = count_lhe_taus_per_event(events)
    print(f"Total events: {len(lhe_tau_counts)}")
    filtered_events, event_mask = select_events_with_one_tau_pair(events)
    print(f"Number of events with exactly 1 tau+ and 1 tau- in LHEPart: {len(filtered_events)}")

    electron_events, electron_mask = select_events_with_one_ee_pair(events)
    print(f"Number of events with exactly 1 electron and 1 positron in LHEPart: {len(electron_events)}")
    muon_events, muon_mask = select_events_with_one_mumu_pair(events)
    print(f"Number of events with exactly 1 mu- and 1 mu+ in LHEPart: {len(muon_events)}")
    lorentz_results = lorentz_vector_demo_for_muon_events(events, max_events=5)
    print(
        f"Computed {lorentz_results['object_label']} masses for "
        f"{len(lorentz_results['dilepton_mass'])} selected events"
    )
    # output_dir = HERE / "outputs"
    # output_dir.mkdir(exist_ok=True)
    # counts_path = output_dir / "lhe_tau_counts_per_event.txt"
    # counts_plot_path = output_dir / "lhe_tau_multiplicity_all_events.png"

    # with counts_path.open("w", encoding="utf-8") as handle:
    #     for count in lhe_tau_counts:
    #         handle.write(f"{int(count)}\n")

    # plt.figure(figsize=(8, 5))
    # max_count = int(lhe_tau_counts.max())
    # bins = range(0, max_count + 2)
    # plt.hist(lhe_tau_counts, bins=bins, align="left", rwidth=0.85, color="steelblue", edgecolor="black")
    # plt.xlabel("Number of LHE taus per event (|pdgId| = 15)")
    # plt.ylabel("Number of events")
    # plt.title("LHE tau multiplicity per event (all events)")
    # plt.xticks(range(0, max_count + 1))
    # plt.grid(alpha=0.25)
    # plt.tight_layout()
    # plt.savefig(counts_plot_path, dpi=150)
    # plt.close()

    # print(f"Total events: {len(lhe_tau_counts)}")
    # print(f"Saved LHE tau counts per event to: {counts_path}")
    # print(f"Saved LHE tau multiplicity histogram to: {counts_plot_path}")
    # print(f"Min LHE taus per event: {int(lhe_tau_counts.min())}")
    # print(f"Max LHE taus per event: {int(lhe_tau_counts.max())}")


if __name__ == "__main__":
    main()
