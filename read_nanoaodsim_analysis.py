#!/usr/bin/env python3
"""Minimal tau-only analysis: select LHE/Gen tau pairs and plot a simple histogram.

This file is intentionally reduced: it provides two functions:
- `load_tau_pairs(events)` returns LHE-selected events and Gen-selected events (if present).
- `make_tau_histogram(output_dir, lhe_selected, gen_selected=None)` saves a single
  invariant-mass histogram (LHE, overlay Gen if available).
"""

from pathlib import Path
from typing import Optional

import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
import uproot
from coffea.nanoevents import NanoAODSchema, NanoEventsFactory
from coffea.nanoevents.methods import vector


# Silence warnings about missing crossrefs in small samples
NanoAODSchema.warn_missing_crossrefs = False

HERE = Path(__file__).resolve().parent
ROOT_FILE = HERE / "nanoaodsim_coffea_1.root"
TREE_NAME = "Events"


def build_root_histogram(name: str, title: str, counts, bin_edges):
    counts = np.asarray(counts, dtype=np.float64)
    bin_edges = np.asarray(bin_edges, dtype=np.float64)

    data = np.zeros(len(counts) + 2, dtype=np.float64)
    data[1:-1] = counts
    entries = float(counts.sum())
    centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    sumw = float(counts.sum())
    sumw2 = float(counts.sum())
    sumwx = float(np.sum(counts * centers))
    sumwx2 = float(np.sum(counts * centers * centers))
    sumw2_array = np.zeros(len(counts) + 2, dtype=np.float64)
    sumw2_array[1:-1] = counts

    xaxis = uproot.writing.identify.to_TAxis(
        "xaxis",
        "",
        len(counts),
        float(bin_edges[0]),
        float(bin_edges[-1]),
    )
    return uproot.writing.identify.to_TH1x(
        name,
        title,
        data,
        entries,
        sumw,
        sumw2,
        sumwx,
        sumwx2,
        sumw2_array,
        xaxis,
    )


def save_png_and_root(output_dir: Path, stem: str, png_title: str, values, *, bins, xlabel: str, ylabel: str, color: str = "tab:blue", alpha: float = 0.7, label: str = "LHE", root_title: Optional[str] = None):
    values = np.asarray(values, dtype=np.float64)
    bin_edges = np.linspace(values.min(), values.max(), int(bins) + 1)
    counts, _ = np.histogram(values, bins=bin_edges)

    plt.figure(figsize=(8, 5))
    plt.hist(values, bins=bin_edges, color=color, alpha=alpha, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(png_title)
    plt.legend()
    plt.tight_layout()

    png_path = output_dir / f"{stem}.png"
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")

    root_path = output_dir / f"{stem}.root"
    histogram = build_root_histogram(stem, root_title or png_title, counts, bin_edges)
    with uproot.recreate(root_path) as root_file:
        root_file[stem] = histogram
    print(f"Saved: {root_path}")


def save_overlay_png_and_root(
    output_dir: Path,
    stem: str,
    png_title: str,
    lhe_values,
    gen_values,
    *,
    bins,
    xlabel: str,
    ylabel: str,
    root_titles: tuple[str, str],
):
    lhe_values = np.asarray(lhe_values, dtype=np.float64)
    gen_values = np.asarray(gen_values, dtype=np.float64)
    combined = np.concatenate([lhe_values, gen_values])
    bin_edges = np.linspace(combined.min(), combined.max(), int(bins) + 1)
    lhe_counts, _ = np.histogram(lhe_values, bins=bin_edges)
    gen_counts, _ = np.histogram(gen_values, bins=bin_edges)

    plt.figure(figsize=(8, 5))
    plt.hist(lhe_values, bins=bin_edges, color="tab:blue", alpha=0.5, label="LHE")
    plt.hist(gen_values, bins=bin_edges, color="tab:orange", alpha=0.5, label="GenPart")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(png_title)
    plt.legend()
    plt.tight_layout()

    png_path = output_dir / f"{stem}.png"
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")

    root_path = output_dir / f"{stem}.root"
    lhe_hist = build_root_histogram(f"{stem}_LHE", root_titles[0], lhe_counts, bin_edges)
    gen_hist = build_root_histogram(f"{stem}_GenPart", root_titles[1], gen_counts, bin_edges)
    with uproot.recreate(root_path) as root_file:
        root_file[f"{stem}_LHE"] = lhe_hist
        root_file[f"{stem}_GenPart"] = gen_hist
    print(f"Saved: {root_path}")


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
    output_dir.mkdir(parents=True, exist_ok=True)
    

    # with this function we build Lorentz vectors for the selected tau- and tau+ particles, both for LHE and Gen (if available). We use the `ak.zip` function to create a new Awkward Array that combines the pt, eta, phi, and mass of the selected particles into a single array of Lorentz vectors. The `with_name="PtEtaPhiMLorentzVector"` argument tells Awkward to treat these as Lorentz vectors, which allows us to easily calculate quantities like ΔR and Δφ later on.
    def build_lv(parts, mask_minus, mask_plus):
        # reverse particles because 
        lep_plus  = parts[mask_minus]
        lep_minus = parts[mask_plus]
        

        # builds Lorentz vectors for the selected tau- and tau+ particles, both for LHE and Gen (if available). We use the `ak.zip` function to create a new Awkward Array that combines the pt, eta, phi, and mass of the selected particles into a single array of Lorentz vectors. The `with_name="PtEtaPhiMLorentzVector"` argument tells Awkward to treat these as Lorentz vectors, which allows us to easily calculate quantities like ΔR and Δφ later on.
        # https://coffea-hep.readthedocs.io/en/latest/search.html?q=Lorentz 
        # if we get inside vector code we see that we really initilize a Lorentz vector with pt, eta, phi and mass. So we can use all the methods of Lorentz vectors on these objects (like delta_r, delta_phi, etc.)
        # we give the 4 elements pt , eta ,phi and mass,
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
        
        # “take the first τ⁻ and t+ in every event” 
        # why we take the first
        return lep_minus_lv[:, 0], lep_plus_lv[:, 0]
    # Physical meaning of the three LHE histograms:
    # DeltaR = sqrt((Delta eta)^2 + (Delta phi)^2): overall angular distance between the two taus.
    # Large DeltaR means back-to-back taus; small DeltaR means boosted/collimated taus.
    # DeltaPhi measures separation in the transverse plane: near pi = opposite directions, small = same direction.
    # DeltaEta measures separation along the beam axis: large |DeltaEta| = one tau forward and one backward.
    # LHE is the ideal hard-scattering picture, so it shows the clean theoretical tau-pair topology.
    lhe_minus_lv, lhe_plus_lv = build_lv(
        lhe_selected.LHEPart, lhe_selected.LHEPart.pdgId == 15, lhe_selected.LHEPart.pdgId == -15
    )
    # distance between two particles in the eta-phi space, defined as ΔR = sqrt((Δη)² + (Δφ)²). It is a commonly used metric in particle physics to quantify how close two particles are in the detector. A smaller ΔR indicates that the particles are closer together, while a larger ΔR indicates that they are farther apart.
    lhe_delta_r = ak.to_numpy(lhe_minus_lv.delta_r(lhe_plus_lv))

    # Δφ is the difference in the azimuthal angle (φ) between two particles. The azimuthal angle is measured in the plane perpendicular to the beam axis, and it ranges from -π to π. The absolute value of Δφ (|Δφ|) is often used to quantify how separated two particles are in this angular dimension. A smaller |Δφ| indicates that the particles are closer together in the azimuthal direction, while a larger |Δφ| indicates that they are farther apart.
    lhe_delta_phi = ak.to_numpy(abs(lhe_minus_lv.delta_phi(lhe_plus_lv)))
    # Δη is the difference in pseudorapidity (η) between two particles. Pseudorapidity is a spatial coordinate that describes the angle of a particle relative to the beam axis. The absolute value of Δη (|Δη|) is used to quantify how separated two particles are in this dimension. A smaller |Δη| indicates that the particles are closer together in pseudorapidity, while a larger |Δη| indicates that they are farther apart.
    lhe_delta_eta = ak.to_numpy(abs(lhe_minus_lv.eta - lhe_plus_lv.eta))

    bins_dr = 60
    save_png_and_root(
        output_dir,
        "hist_tau_deltaR",
        "LHE ditau DeltaR",
        lhe_delta_r,
        bins=bins_dr,
        xlabel=r"$\Delta R(\tau^{-},\tau^{+})$",
        ylabel="Events",
        root_title="LHE ditau DeltaR",
    )

    save_png_and_root(
        output_dir,
        "hist_tau_deltaPhi",
        "LHE ditau |DeltaPhi|",
        lhe_delta_phi,
        bins=60,
        xlabel=r"$|\Delta \phi(\tau^{-},\tau^{+})|$",
        ylabel="Events",
        root_title="LHE ditau |DeltaPhi|",
    )

    save_png_and_root(
        output_dir,
        "hist_tau_deltaEta",
        "LHE ditau |DeltaEta|",
        lhe_delta_eta,
        bins=60,
        xlabel=r"$|\Delta \eta(\tau^{-},\tau^{+})|$",
        ylabel="Events",
        root_title="LHE ditau |DeltaEta|",
    )

    if gen_selected is not None:
        # GenPart adds showering/decays, so it is closer to realistic event structure than LHE.
        # If Gen is broader than LHE, it usually means radiation and decay effects have spread the angles.
        # If Gen is shifted relative to LHE, it can indicate boosts or additional event activity.
        gen_minus_lv, gen_plus_lv = build_lv(
            gen_selected.GenPart,
            (gen_selected.GenPart.pdgId == 15) & (gen_selected.GenPart.status == 23),
            (gen_selected.GenPart.pdgId == -15) & (gen_selected.GenPart.status == 23),
        )
        gen_delta_r = ak.to_numpy(gen_minus_lv.delta_r(gen_plus_lv))
        gen_delta_phi = ak.to_numpy(abs(gen_minus_lv.delta_phi(gen_plus_lv)))
        gen_delta_eta = ak.to_numpy(abs(gen_minus_lv.eta - gen_plus_lv.eta))

        # Overlay on DeltaR: most important plot for tau-pair topology.
        save_overlay_png_and_root(
            output_dir,
            "hist_tau_deltaR_LHE_vs_Gen",
            "Ditau DeltaR (LHE vs GenPart)",
            lhe_delta_r,
            gen_delta_r,
            bins=bins_dr,
            xlabel=r"$\Delta R(\tau^{-},\tau^{+})$",
            ylabel="Events",
            root_titles=("LHE ditau DeltaR", "GenPart ditau DeltaR"),
        )

        # Overlay on |DeltaPhi|: near pi means back-to-back in the transverse plane.
        save_overlay_png_and_root(
            output_dir,
            "hist_tau_deltaPhi_LHE_vs_Gen",
            "Ditau |DeltaPhi| (LHE vs GenPart)",
            lhe_delta_phi,
            gen_delta_phi,
            bins=60,
            xlabel=r"$|\Delta \phi(\tau^{-},\tau^{+})|$",
            ylabel="Events",
            root_titles=("LHE ditau |DeltaPhi|", "GenPart ditau |DeltaPhi|"),
        )

        # Overlay on |DeltaEta|: shows forward/backward separation along the beam direction.
        save_overlay_png_and_root(
            output_dir,
            "hist_tau_deltaEta_LHE_vs_Gen",
            "Ditau |DeltaEta| (LHE vs GenPart)",
            lhe_delta_eta,
            gen_delta_eta,
            bins=60,
            xlabel=r"$|\Delta \eta(\tau^{-},\tau^{+})|$",
            ylabel="Events",
            root_titles=("LHE ditau |DeltaEta|", "GenPart ditau |DeltaEta|"),
        )


def main():
    events = load_events(ROOT_FILE)
    lhe_selected, gen_selected, lhe_mask = load_tau_pairs(events)
    # print(f"Events with exactly one LHE tau- and one LHE tau+: {len(lhe_selected)}")
    # if gen_selected is not None:
    #     print(f"Events with exactly one GenPart tau- and tau+: {len(gen_selected)}")

    output_dir = HERE / "outputs"
    make_tau_histogram(output_dir, lhe_selected, gen_selected=gen_selected)


if __name__ == "__main__":
    main()



# if you want to see the root files in histograms
# root 
# TFile f("hist_tau_deltaR.root");
# f.ls();
# TH1* h = (TH1*)f.Get("hist_tau_deltaR");
# h->Draw();

#TODO to make histograms for green things in the pictures in from the table of Roumyana cabinet
#TODO to find how make mutual chats in mattermost

#LHE particles comes from the first initial collisions - Gen particles are the result of the hadronization and decay of the LHE particles. So Gen particles are more realistic and closer to what we can measure in the detector, while LHE particles are more theoretical and represent the initial conditions of the collision.
#TODO to write all this in overleave 