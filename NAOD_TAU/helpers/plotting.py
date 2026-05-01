from pathlib import Path
from typing import Optional, Tuple

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import uproot
from coffea.nanoevents.methods import vector


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


def compute_histogram_data(values, bins):
    """Compute histogram bin edges and counts from raw values."""
    values = np.asarray(values, dtype=np.float64)
    bin_edges = np.linspace(values.min(), values.max(), int(bins) + 1)
    counts, _ = np.histogram(values, bins=bin_edges)
    return counts, bin_edges


def save_png(
    output_dir: Path,
    stem: str,
    title: str,
    values,
    bin_edges,
    xlabel: str,
    ylabel: str,
    color: str = "tab:blue",
    alpha: float = 0.7,
    label: str = "LHE",
):
    """Save histogram as PNG image."""
    plt.figure(figsize=(8, 5))
    plt.hist(values, bins=bin_edges, color=color, alpha=alpha, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()

    png_path = output_dir / f"{stem}.png"
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


def save_root(output_dir: Path, stem: str, counts, bin_edges, title: str):
    """Save histogram as ROOT file."""
    root_path = output_dir / f"{stem}.root"
    histogram = build_root_histogram(stem, title, counts, bin_edges)
    with uproot.recreate(root_path) as root_file:
        root_file[stem] = histogram
    print(f"Saved: {root_path}")





def save_overlay_png(
    output_dir: Path,
    stem: str,
    title: str,
    lhe_values,
    gen_values,
    bin_edges,
    xlabel: str,
    ylabel: str,
):
    """Save overlay histogram (LHE vs GenPart) as PNG image."""
    plt.figure(figsize=(8, 5))
    plt.hist(lhe_values, bins=bin_edges, color="tab:blue", alpha=0.5, label="LHE")
    plt.hist(gen_values, bins=bin_edges, color="tab:orange", alpha=0.5, label="GenPart")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()

    png_path = output_dir / f"{stem}.png"
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


def save_overlay_root(
    output_dir: Path,
    stem: str,
    lhe_counts,
    gen_counts,
    bin_edges,
    root_titles: Tuple[str, str],
):
    """Save overlay histogram (LHE vs GenPart) as ROOT file."""
    root_path = output_dir / f"{stem}.root"
    lhe_hist = build_root_histogram(f"{stem}_LHE", root_titles[0], lhe_counts, bin_edges)
    gen_hist = build_root_histogram(f"{stem}_GenPart", root_titles[1], gen_counts, bin_edges)
    with uproot.recreate(root_path) as root_file:
        root_file[f"{stem}_LHE"] = lhe_hist
        root_file[f"{stem}_GenPart"] = gen_hist
    print(f"Saved: {root_path}")


def compute_overlay_histogram_data(lhe_values, gen_values, bins):
    """Compute histogram data for overlay (LHE vs GenPart) from raw values."""
    lhe_values = np.asarray(lhe_values, dtype=np.float64)
    gen_values = np.asarray(gen_values, dtype=np.float64)
    combined = np.concatenate([lhe_values, gen_values])
    bin_edges = np.linspace(combined.min(), combined.max(), int(bins) + 1)
    lhe_counts, _ = np.histogram(lhe_values, bins=bin_edges)
    gen_counts, _ = np.histogram(gen_values, bins=bin_edges)
    return lhe_counts, gen_counts, bin_edges





def build_tau_vectors(parts, mask_minus, mask_plus):
    lep_plus = parts[mask_minus]
    lep_minus = parts[mask_plus]

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
    return lep_minus_lv[:, 0], lep_plus_lv[:, 0]


def make_tau_histogram(output_dir: Path, lhe_selected, gen_selected=None):
    output_dir.mkdir(parents=True, exist_ok=True)

    lhe_minus_lv, lhe_plus_lv = build_tau_vectors(
        lhe_selected.LHEPart,
        lhe_selected.LHEPart.pdgId == 15,
        lhe_selected.LHEPart.pdgId == -15,
    )
    lhe_delta_r = ak.to_numpy(lhe_minus_lv.delta_r(lhe_plus_lv))
    lhe_delta_phi = ak.to_numpy(abs(lhe_minus_lv.delta_phi(lhe_plus_lv)))
    lhe_delta_eta = ak.to_numpy(abs(lhe_minus_lv.eta - lhe_plus_lv.eta))

    bins_dr = 60
    
    # DeltaR: compute once, save in both formats
    counts, bin_edges = compute_histogram_data(lhe_delta_r, bins_dr)
    save_png(output_dir, "hist_tau_deltaR", "LHE ditau DeltaR", lhe_delta_r, bin_edges, r"$\Delta R(\tau^{-},\tau^{+})$", "Events")
    save_root(output_dir, "hist_tau_deltaR", counts, bin_edges, "LHE ditau DeltaR")
    
    # DeltaPhi: compute once, save in both formats
    counts, bin_edges = compute_histogram_data(lhe_delta_phi, 60)
    save_png(output_dir, "hist_tau_deltaPhi", "LHE ditau |DeltaPhi|", lhe_delta_phi, bin_edges, r"$|\Delta \phi(\tau^{-},\tau^{+})|$", "Events")
    save_root(output_dir, "hist_tau_deltaPhi", counts, bin_edges, "LHE ditau |DeltaPhi|")
    
    # DeltaEta: compute once, save in both formats
    counts, bin_edges = compute_histogram_data(lhe_delta_eta, 60)
    save_png(output_dir, "hist_tau_deltaEta", "LHE ditau |DeltaEta|", lhe_delta_eta, bin_edges, r"$|\Delta \eta(\tau^{-},\tau^{+})|$", "Events")
    save_root(output_dir, "hist_tau_deltaEta", counts, bin_edges, "LHE ditau |DeltaEta|")

    if gen_selected is not None:
        gen_minus_lv, gen_plus_lv = build_tau_vectors(
            gen_selected.GenPart,
            (gen_selected.GenPart.pdgId == 15) & (gen_selected.GenPart.status == 23),
            (gen_selected.GenPart.pdgId == -15) & (gen_selected.GenPart.status == 23),
        )
        gen_delta_r = ak.to_numpy(gen_minus_lv.delta_r(gen_plus_lv))
        gen_delta_phi = ak.to_numpy(abs(gen_minus_lv.delta_phi(gen_plus_lv)))
        gen_delta_eta = ak.to_numpy(abs(gen_minus_lv.eta - gen_plus_lv.eta))

        # DeltaR overlay: compute once, save in both formats
        lhe_counts, gen_counts, bin_edges = compute_overlay_histogram_data(lhe_delta_r, gen_delta_r, bins_dr)
        save_overlay_png(output_dir, "hist_tau_deltaR_LHE_vs_Gen", "Ditau DeltaR (LHE vs GenPart)", lhe_delta_r, gen_delta_r, bin_edges, r"$\Delta R(\tau^{-},\tau^{+})$", "Events")
        save_overlay_root(output_dir, "hist_tau_deltaR_LHE_vs_Gen", lhe_counts, gen_counts, bin_edges, ("LHE ditau DeltaR", "GenPart ditau DeltaR"))
        
        # DeltaPhi overlay: compute once, save in both formats
        lhe_counts, gen_counts, bin_edges = compute_overlay_histogram_data(lhe_delta_phi, gen_delta_phi, 60)
        save_overlay_png(output_dir, "hist_tau_deltaPhi_LHE_vs_Gen", "Ditau |DeltaPhi| (LHE vs GenPart)", lhe_delta_phi, gen_delta_phi, bin_edges, r"$|\Delta \phi(\tau^{-},\tau^{+})|$", "Events")
        save_overlay_root(output_dir, "hist_tau_deltaPhi_LHE_vs_Gen", lhe_counts, gen_counts, bin_edges, ("LHE ditau |DeltaPhi|", "GenPart ditau |DeltaPhi|"))
        
        # DeltaEta overlay: compute once, save in both formats
        lhe_counts, gen_counts, bin_edges = compute_overlay_histogram_data(lhe_delta_eta, gen_delta_eta, 60)
        save_overlay_png(output_dir, "hist_tau_deltaEta_LHE_vs_Gen", "Ditau |DeltaEta| (LHE vs GenPart)", lhe_delta_eta, gen_delta_eta, bin_edges, r"$|\Delta \eta(\tau^{-},\tau^{+})|$", "Events")
        save_overlay_root(output_dir, "hist_tau_deltaEta_LHE_vs_Gen", lhe_counts, gen_counts, bin_edges, ("LHE ditau |DeltaEta|", "GenPart ditau |DeltaEta|"))
