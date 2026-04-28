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
    
    # give me the particle type (as a number) for every LHE particle
    pdg_lhe = events.LHEPart.pdgId
    # we are looking here how much events has 1 tau and how much events has an antitau
    n_minus = ak.sum(pdg_lhe == 15, axis=1)
    n_plus = ak.sum(pdg_lhe == -15, axis=1)

    # print(f"Events with exactly one tau-: {ak.sum(n_minus == 1)}")
    # print(f"Events with exactly one tau+: {ak.sum(n_plus == 1)}")
    # basicly all 60806

    ## this do the real filtration of data containing one tau and one antitau
    lhe_mask = (n_minus == 1) & (n_plus == 1)
    lhe_selected = events[lhe_mask]

    # It converts the Awkward boolean mask into a normal NumPy array. This is useful because some libraries or functions might expect a standard NumPy array instead of an Awkward Array. By converting it to a NumPy array, you can use it in contexts where Awkward Arrays are not supported.
    lhe_mask_np = ak.to_numpy(lhe_mask)

    # analogical to :
    # data = np.array([10, 20, 30, 40])
    # mask = np.array([True, False, True, False])
    # filtered = data[mask]

    gen_selected = None
    if "GenPart" in events.fields:

        # give me the particle type (as a number) for every Gen particle and their status ( Pythia status code, where 23 means "hard process" particle)
        pdg_gen = events.GenPart.pdgId
        status_gen = events.GenPart.status
        # GenPart usually contains several copies of the same tau in the decay chain.
        # Status 23 picks the hard-process tau pair in this sample.
        n_minus_g = ak.sum((pdg_gen == 15) & (status_gen == 23), axis=1)
        n_plus_g = ak.sum((pdg_gen == -15) & (status_gen == 23), axis=1)
        gen_mask = (n_minus_g == 1) & (n_plus_g == 1)
        gen_selected = events[gen_mask]
        # by this mask we select tau that are pairs in event and come from the process hard scattering from the first generation

    # we return the selected events for LHE and Gen, and the mask for LHE as a numpy array (for later use in histograms)
    return lhe_selected, gen_selected, lhe_mask_np


def make_tau_histogram(output_dir: Path, lhe_selected, gen_selected=None):
    """Make three simple histograms for LHE taus and optional Gen taus:
    - Delta R (ΔR)
    - Absolute Delta Phi (|Δφ|)
    - Absolute Delta pseudorapidity (|Δη|)

    Saves files in `outputs/`.
    """

    # ensure output directory exists if no such it creates it
    output_dir.mkdir(exist_ok=True)
    

    # with this function we build Lorentz vectors for the selected tau- and tau+ particles, both for LHE and Gen (if available). We use the `ak.zip` function to create a new Awkward Array that combines the pt, eta, phi, and mass of the selected particles into a single array of Lorentz vectors. The `with_name="PtEtaPhiMLorentzVector"` argument tells Awkward to treat these as Lorentz vectors, which allows us to easily calculate quantities like ΔR and Δφ later on.
    def build_lv(parts, mask_minus, mask_plus):
        lep_minus = parts[mask_minus]
        lep_plus = parts[mask_plus]
        

        # builds Lorentz vectors for the selected tau- and tau+ particles, both for LHE and Gen (if available). We use the `ak.zip` function to create a new Awkward Array that combines the pt, eta, phi, and mass of the selected particles into a single array of Lorentz vectors. The `with_name="PtEtaPhiMLorentzVector"` argument tells Awkward to treat these as Lorentz vectors, which allows us to easily calculate quantities like ΔR and Δφ later on.
        # https://coffea-hep.readthedocs.io/en/latest/search.html?q=Lorentz 
        # if we get inside vector code we see that we really initilize a Lorentz vector with pt, eta, phi and mass. So we can use all the methods of Lorentz vectors on these objects (like delta_r, delta_phi, etc.)
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
        
        # “take the first τ⁻ in every event” 
        return lep_minus_lv[:, 0], lep_plus_lv[:, 0]

    # LHE deltas
    lhe_minus_lv, lhe_plus_lv = build_lv(
        lhe_selected.LHEPart, lhe_selected.LHEPart.pdgId == 15, lhe_selected.LHEPart.pdgId == -15
    )
    lhe_delta_r = ak.to_numpy(lhe_minus_lv.delta_r(lhe_plus_lv))
    lhe_delta_phi = ak.to_numpy(abs(lhe_minus_lv.delta_phi(lhe_plus_lv)))
    lhe_delta_eta = ak.to_numpy(abs(lhe_minus_lv.eta - lhe_plus_lv.eta))

    bins_dr = 60
    plt.figure(figsize=(8, 5))
    plt.hist(lhe_delta_r, bins=bins_dr, color="tab:blue", alpha=0.7, label="LHE")
    plt.xlabel(r"$\Delta R(\tau^{-},\tau^{+})$")
    plt.ylabel("Events")
    plt.title("LHE ditau DeltaR")
    plt.legend()
    plt.tight_layout()
    out_dr = output_dir / "hist_tau_deltaR.png"
    plt.savefig(out_dr, dpi=150)
    plt.close()
    print(f"Saved: {out_dr}")

    plt.figure(figsize=(8, 5))
    plt.hist(lhe_delta_phi, bins=60, color="tab:blue", alpha=0.7, label="LHE")
    plt.xlabel(r"$|\Delta \phi(\tau^{-},\tau^{+})|$")
    plt.ylabel("Events")
    plt.title("LHE ditau |DeltaPhi|")
    plt.legend()
    plt.tight_layout()
    out_dphi = output_dir / "hist_tau_deltaPhi.png"
    plt.savefig(out_dphi, dpi=150)
    plt.close()
    print(f"Saved: {out_dphi}")

    plt.figure(figsize=(8, 5))
    plt.hist(lhe_delta_eta, bins=60, color="tab:blue", alpha=0.7, label="LHE")
    plt.xlabel(r"$|\Delta \eta(\tau^{-},\tau^{+})|$")
    plt.ylabel("Events")
    plt.title("LHE ditau |DeltaEta|")
    plt.legend()
    plt.tight_layout()
    out_deta = output_dir / "hist_tau_deltaEta.png"
    plt.savefig(out_deta, dpi=150)
    plt.close()
    print(f"Saved: {out_deta}")

    # If Gen selected, overlay Gen histograms on same plots (appending)
    if gen_selected is not None:
        gen_minus_lv, gen_plus_lv = build_lv(
            gen_selected.GenPart,
            (gen_selected.GenPart.pdgId == 15) & (gen_selected.GenPart.status == 23),
            (gen_selected.GenPart.pdgId == -15) & (gen_selected.GenPart.status == 23),
        )
        gen_delta_r = ak.to_numpy(gen_minus_lv.delta_r(gen_plus_lv))
        gen_delta_phi = ak.to_numpy(abs(gen_minus_lv.delta_phi(gen_plus_lv)))
        gen_delta_eta = ak.to_numpy(abs(gen_minus_lv.eta - gen_plus_lv.eta))

        # overlay on DeltaR
        plt.figure(figsize=(8, 5))
        plt.hist(lhe_delta_r, bins=bins_dr, color="tab:blue", alpha=0.5, label="LHE")
        plt.hist(gen_delta_r, bins=bins_dr, color="tab:orange", alpha=0.5, label="GenPart")
        plt.xlabel(r"$\Delta R(\tau^{-},\tau^{+})$")
        plt.ylabel("Events")
        plt.title("Ditau DeltaR (LHE vs GenPart)")
        plt.legend()
        plt.tight_layout()
        out_dr2 = output_dir / "hist_tau_deltaR_LHE_vs_Gen.png"
        plt.savefig(out_dr2, dpi=150)
        plt.close()
        print(f"Saved: {out_dr2}")

        # overlay on |DeltaPhi|
        plt.figure(figsize=(8, 5))
        plt.hist(lhe_delta_phi, bins=60, color="tab:blue", alpha=0.5, label="LHE")
        plt.hist(gen_delta_phi, bins=60, color="tab:orange", alpha=0.5, label="GenPart")
        plt.xlabel(r"$|\Delta \phi(\tau^{-},\tau^{+})|$")
        plt.ylabel("Events")
        plt.title("Ditau |DeltaPhi| (LHE vs GenPart)")
        plt.legend()
        plt.tight_layout()
        out_dphi2 = output_dir / "hist_tau_deltaPhi_LHE_vs_Gen.png"
        plt.savefig(out_dphi2, dpi=150)
        plt.close()
        print(f"Saved: {out_dphi2}")

        # overlay on |DeltaEta|
        plt.figure(figsize=(8, 5))
        plt.hist(lhe_delta_eta, bins=60, color="tab:blue", alpha=0.5, label="LHE")
        plt.hist(gen_delta_eta, bins=60, color="tab:orange", alpha=0.5, label="GenPart")
        plt.xlabel(r"$|\Delta \eta(\tau^{-},\tau^{+})|$")
        plt.ylabel("Events")
        plt.title("Ditau |DeltaEta| (LHE vs GenPart)")
        plt.legend()
        plt.tight_layout()
        out_deta2 = output_dir / "hist_tau_deltaEta_LHE_vs_Gen.png"
        plt.savefig(out_deta2, dpi=150)
        plt.close()
        print(f"Saved: {out_deta2}")


def main():
    events = load_events(ROOT_FILE)
    lhe_selected, gen_selected, lhe_mask = load_tau_pairs(events)
    # print(f"Events with exactly one LHE tau- and one LHE tau+: {len(lhe_selected)}")
    # if gen_selected is not None:
    #     print(f"Events with exactly one GenPart tau- and tau+: {len(gen_selected)}")

    # output_dir = HERE / "outputs"
    # make_tau_histogram(output_dir, lhe_selected, gen_selected=gen_selected)


if __name__ == "__main__":
    main()


#TODO the histograms output to become root file and to be written as that
#TODO to make histograms for green things in the pictures in from the table of Roumyana cabinet
#TODO to find how make mutual chats in mattermost

#LHE particles comes from the first initial collisions - Gen particles are the result of the hadronization and decay of the LHE particles. So Gen particles are more realistic and closer to what we can measure in the detector, while LHE particles are more theoretical and represent the initial conditions of the collision.
#TODO to write all this in overleave 