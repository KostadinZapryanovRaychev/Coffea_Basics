from pathlib import Path
from typing import Optional, Tuple
import logging

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import uproot
from coffea.nanoevents.methods import vector


logger = logging.getLogger(__name__)


def build_root_histogram(name: str, title: str, counts, bin_edges):
    """
    Construct a ROOT histogram object with metadata.
    
    Args:
        name: Histogram identifier
        title: Histogram display title
        counts: Bin contents (array-like)
        bin_edges: Bin edge positions (array-like)
        
    Returns:
        ROOT TH1x histogram object
        
    Raises:
        ValueError: If histogram data is invalid or incompatible
    """
    try:
        counts = np.asarray(counts, dtype=np.float64)
        bin_edges = np.asarray(bin_edges, dtype=np.float64)
        
        if len(counts) != len(bin_edges) - 1:
            raise ValueError(
                f"Bin count mismatch: {len(counts)} counts but {len(bin_edges)-1} expected bins"
            )
        
        if np.any(np.isnan(counts)) or np.any(np.isinf(counts)):
            raise ValueError("Histogram contains NaN or Inf values")
        
        if np.any(np.isnan(bin_edges)) or np.any(np.isinf(bin_edges)):
            raise ValueError("Bin edges contain NaN or Inf values")
        
        ##TODO cos for delta _ phi ( range 1 - 1 200 bins) LHE
        
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
    except (ValueError, TypeError) as e:
        error_msg = (
            f"\n[ERROR] Failed to build ROOT histogram '{name}'\n"
            f"  Title: {title}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Unexpected error building ROOT histogram '{name}'\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def compute_histogram_data(values, bins):
    """
    Compute histogram bin edges and counts from raw values.
    
    Args:
        values: Array-like of numeric values
        bins: Number of bins or bin edges
        
    Returns:
        Tuple of (counts, bin_edges)
        
    Raises:
        ValueError: If values array is invalid or empty
        TypeError: If bins parameter is invalid
    """
    try:
        values = np.asarray(values, dtype=np.float64)
        
        if len(values) == 0:
            raise ValueError("Cannot compute histogram from empty values array")
        
        if np.all(np.isnan(values)):
            raise ValueError("All values are NaN")
        
        # Filter out NaN/Inf for valid min/max
        valid_values = values[np.isfinite(values)]
        if len(valid_values) == 0:
            raise ValueError("No valid (finite) values in input array")
        
        value_min = valid_values.min()
        value_max = valid_values.max()
        
        if value_min == value_max:
            logger.warning(f"⚠ All values are identical ({value_min}). Histogram will be degenerate.")
        
        bin_edges = np.linspace(value_min, value_max, int(bins) + 1)
        counts, _ = np.histogram(values, bins=bin_edges)
        return counts, bin_edges
    except (ValueError, TypeError) as e:
        error_msg = (
            f"\n[ERROR] Failed to compute histogram data\n"
            f"  Values shape: {np.asarray(values).shape}\n"
            f"  Bins: {bins}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Unexpected error computing histogram data\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


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
    """
    Save histogram as PNG image using matplotlib.
    
    Args:
        output_dir: Directory to save PNG file
        stem: Base filename (without .png extension)
        title: Histogram title
        values: Data values to plot
        bin_edges: Bin edge positions
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Bar color (matplotlib color string)
        alpha: Bar transparency (0-1)
        label: Legend label
        
    Raises:
        ValueError: If output directory is invalid
        IOError: If PNG file cannot be written
    """
    try:
        if not output_dir.exists():
            raise ValueError(f"Output directory does not exist: {output_dir}")
        
        if not output_dir.is_dir():
            raise ValueError(f"Output path is not a directory: {output_dir}")
        
        plt.figure(figsize=(8, 5))
        plt.hist(values, bins=bin_edges, color=color, alpha=alpha, label=label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.tight_layout()

        png_path = output_dir / f"{stem}.png"
        
        try:
            plt.savefig(png_path, dpi=150)
            plt.close()
            logger.debug(f"Saved PNG: {png_path}")
        except IOError as io_err:
            plt.close()
            raise IOError(f"Cannot write PNG file: {png_path}\n  Details: {str(io_err)}") from io_err
    except (ValueError, IOError) as e:
        error_msg = (
            f"\n[ERROR] Failed to save PNG histogram '{stem}'\n"
            f"  Title: {title}\n"
            f"  Output dir: {output_dir}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        plt.close()
        raise
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Unexpected error saving PNG histogram '{stem}'\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        plt.close()
        raise RuntimeError(error_msg) from e


def save_root(output_dir: Path, stem: str, counts, bin_edges, title: str):
    """
    Save histogram as ROOT file using uproot.
    
    Args:
        output_dir: Directory to save ROOT file
        stem: Base filename (without .root extension)
        counts: Histogram bin counts
        bin_edges: Histogram bin edges
        title: Histogram title in ROOT file
        
    Raises:
        ValueError: If output directory is invalid
        IOError: If ROOT file cannot be written
    """
    try:
        if not output_dir.exists():
            raise ValueError(f"Output directory does not exist: {output_dir}")
        
        if not output_dir.is_dir():
            raise ValueError(f"Output path is not a directory: {output_dir}")
        
        root_path = output_dir / f"{stem}.root"
        
        try:
            histogram = build_root_histogram(stem, title, counts, bin_edges)
            with uproot.recreate(root_path) as root_file:
                root_file[stem] = histogram
            logger.debug(f"Saved ROOT: {root_path}")
        except IOError as io_err:
            raise IOError(f"Cannot write ROOT file: {root_path}\n  Details: {str(io_err)}") from io_err
    except (ValueError, IOError) as e:
        error_msg = (
            f"\n[ERROR] Failed to save ROOT histogram '{stem}'\n"
            f"  Title: {title}\n"
            f"  Output dir: {output_dir}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Unexpected error saving ROOT histogram '{stem}'\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e





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
    """
    Save overlay histogram (LHE vs GenPart) as PNG image.
    
    Args:
        output_dir: Directory to save PNG file
        stem: Base filename (without .png extension)
        title: Histogram title
        lhe_values: LHE particle data
        gen_values: GenPart particle data
        bin_edges: Bin edge positions
        xlabel: X-axis label
        ylabel: Y-axis label
        
    Raises:
        ValueError: If output directory is invalid
        IOError: If PNG file cannot be written
    """
    try:
        if not output_dir.exists():
            raise ValueError(f"Output directory does not exist: {output_dir}")
        
        plt.figure(figsize=(8, 5))
        plt.hist(lhe_values, bins=bin_edges, color="tab:blue", alpha=0.5, label="LHE")
        plt.hist(gen_values, bins=bin_edges, color="tab:orange", alpha=0.5, label="GenPart")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.tight_layout()

        png_path = output_dir / f"{stem}.png"
        
        try:
            plt.savefig(png_path, dpi=150)
            plt.close()
            logger.debug(f"Saved overlay PNG: {png_path}")
        except IOError as io_err:
            plt.close()
            raise IOError(f"Cannot write PNG file: {png_path}\n  Details: {str(io_err)}") from io_err
    except (ValueError, IOError) as e:
        error_msg = (
            f"\n[ERROR] Failed to save overlay PNG histogram '{stem}'\n"
            f"  Title: {title}\n"
            f"  Output dir: {output_dir}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        plt.close()
        raise
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Unexpected error saving overlay PNG histogram '{stem}'\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        plt.close()
        raise RuntimeError(error_msg) from e


def save_overlay_root(
    output_dir: Path,
    stem: str,
    lhe_counts,
    gen_counts,
    bin_edges,
    root_titles: Tuple[str, str],
):
    """
    Save overlay histogram (LHE vs GenPart) as ROOT file.
    
    Args:
        output_dir: Directory to save ROOT file
        stem: Base filename (without .root extension)
        lhe_counts: LHE histogram bin counts
        gen_counts: GenPart histogram bin counts
        bin_edges: Bin edge positions
        root_titles: Tuple of (lhe_title, gen_title) for ROOT histograms
        
    Raises:
        ValueError: If output directory is invalid
        IOError: If ROOT file cannot be written
    """
    try:
        if not output_dir.exists():
            raise ValueError(f"Output directory does not exist: {output_dir}")
        
        root_path = output_dir / f"{stem}.root"
        
        try:
            lhe_hist = build_root_histogram(f"{stem}_LHE", root_titles[0], lhe_counts, bin_edges)
            gen_hist = build_root_histogram(f"{stem}_GenPart", root_titles[1], gen_counts, bin_edges)
            with uproot.recreate(root_path) as root_file:
                root_file[f"{stem}_LHE"] = lhe_hist
                root_file[f"{stem}_GenPart"] = gen_hist
            logger.debug(f"Saved overlay ROOT: {root_path}")
        except IOError as io_err:
            raise IOError(f"Cannot write ROOT file: {root_path}\n  Details: {str(io_err)}") from io_err
    except (ValueError, IOError) as e:
        error_msg = (
            f"\n[ERROR] Failed to save overlay ROOT histogram '{stem}'\n"
            f"  LHE title: {root_titles[0]}\n"
            f"  GenPart title: {root_titles[1]}\n"
            f"  Output dir: {output_dir}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Unexpected error saving overlay ROOT histogram '{stem}'\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def compute_overlay_histogram_data(lhe_values, gen_values, bins):
    """
    Compute histogram data for overlay (LHE vs GenPart) from raw values.
    
    Args:
        lhe_values: LHE particle data array
        gen_values: GenPart particle data array
        bins: Number of bins or bin edges
        
    Returns:
        Tuple of (lhe_counts, gen_counts, bin_edges)
        
    Raises:
        ValueError: If input arrays are invalid or empty
    """
    try:
        lhe_values = np.asarray(lhe_values, dtype=np.float64)
        gen_values = np.asarray(gen_values, dtype=np.float64)
        
        if len(lhe_values) == 0:
            raise ValueError("LHE values array is empty")
        
        if len(gen_values) == 0:
            raise ValueError("GenPart values array is empty")
        
        combined = np.concatenate([lhe_values, gen_values])
        valid_combined = combined[np.isfinite(combined)]
        
        if len(valid_combined) == 0:
            raise ValueError("No valid (finite) values in combined LHE+GenPart data")
        
        bin_edges = np.linspace(valid_combined.min(), valid_combined.max(), int(bins) + 1)
        lhe_counts, _ = np.histogram(lhe_values, bins=bin_edges)
        gen_counts, _ = np.histogram(gen_values, bins=bin_edges)
        
        return lhe_counts, gen_counts, bin_edges
    except (ValueError, TypeError) as e:
        error_msg = (
            f"\n[ERROR] Failed to compute overlay histogram data\n"
            f"  LHE values shape: {np.asarray(lhe_values).shape}\n"
            f"  GenPart values shape: {np.asarray(gen_values).shape}\n"
            f"  Bins: {bins}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Unexpected error computing overlay histogram data\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e





def build_tau_vectors(parts, mask_minus, mask_plus):
    """
    Build Lorentz vectors for tau pairs.
    
    Args:
        parts: Particle collection (LHEPart or GenPart)
        mask_minus: Boolean mask for tau (pdgId==15) particles
        mask_plus: Boolean mask for anti-tau (pdgId==-15) particles
        
    Returns:
        Tuple of (lep_minus_lv, lep_plus_lv) Lorentz vectors
        
    Raises:
        ValueError: If masks are invalid or particle data is missing
        AttributeError: If required particle attributes are missing
    """
    try:
        lep_minus = parts[mask_minus]
        lep_plus = parts[mask_plus]
        
        # Validate masks produced non-empty selections
        try:
            n_minus = len(lep_minus)
            n_plus = len(lep_plus)
            if n_minus == 0 or n_plus == 0:
                raise ValueError(f"Empty particle selection: {n_minus} minus, {n_plus} plus")
        except TypeError:
            pass  # awkward arrays may not support len()
        
        # Build Lorentz vectors
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
    except (AttributeError, KeyError) as e:
        error_msg = (
            f"\n[ERROR] Missing required particle attributes (pt, eta, phi, mass)\n"
            f"  Details: {str(e)}\n"
            f"  Ensure particle collection has proper kinematic information.\n"
        )
        logger.error(error_msg)
        raise AttributeError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Failed to build Lorentz vectors\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def compute_ditau_kinematics(lep_minus_lv, lep_plus_lv):
    """
    Compute di-tau (tau pair) kinematic properties.
    
    Args:
        lep_minus_lv: Lorentz vector for tau- (pdgId=15)
        lep_plus_lv: Lorentz vector for tau+ (pdgId=-15)
        
    Returns:
        Dictionary with keys:
        - 'pt': Transverse momentum of di-tau
        - 'pz': Longitudinal momentum of di-tau
        - 'eta': Pseudo-rapidity of di-tau
        - 'phi': Azimuthal angle of di-tau
        - 'mass': Invariant mass of di-tau pair
        
    Raises:
        AttributeError: If Lorentz vectors lack required methods
    """
    try:
        ditau = lep_minus_lv + lep_plus_lv
        
        return {
            'pt': ak.to_numpy(ditau.pt),
            'pz': ak.to_numpy(ditau.pz),
            'eta': ak.to_numpy(ditau.eta),
            'phi': ak.to_numpy(ditau.phi),
            'mass': ak.to_numpy(ditau.mass),
        }
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Failed to compute di-tau kinematics\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def compute_delta_angles(lep_minus_lv, lep_plus_lv):
    """
    Compute delta angles between tau pair particles.
    
    Args:
        lep_minus_lv: Lorentz vector for tau- (pdgId=15)
        lep_plus_lv: Lorentz vector for tau+ (pdgId=-15)
        
    Returns:
        Dictionary with keys:
        - 'delta_r': ΔR = sqrt(Δη² + Δφ²) (always positive)
        - 'delta_phi': Δφ = phi(tau-) - phi(tau+) (signed, range [-π, π])
        - 'delta_eta': Δη = eta(tau-) - eta(tau+) (signed, can be positive or negative)
        - 'delta_theta': Δθ = theta(tau-) - theta(tau+) (signed, theta = 2*arctan(exp(-eta)))
        
    Raises:
        RuntimeError: If angle computation fails
    """
    try:
        delta_r = ak.to_numpy(lep_minus_lv.delta_r(lep_plus_lv))
        delta_phi = ak.to_numpy(lep_minus_lv.delta_phi(lep_plus_lv))
        delta_eta = ak.to_numpy(lep_minus_lv.eta - lep_plus_lv.eta)
        
        # Compute delta_theta from pseudo-rapidities
        # theta = 2 * arctan(exp(-eta))
        # delta_theta = theta1 - theta2
        theta_minus = 2.0 * np.arctan(np.exp(-lep_minus_lv.eta))
        theta_plus = 2.0 * np.arctan(np.exp(-lep_plus_lv.eta))
        delta_theta = ak.to_numpy(theta_minus - theta_plus)
        
        return {
            'delta_r': delta_r,
            'delta_phi': delta_phi,
            'delta_eta': delta_eta,
            'delta_theta': delta_theta,
        }
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Failed to compute delta angles\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def save_histogram_suite(output_dir, stem_prefix, label_prefix, ditau_kinematics, delta_angles):
    """
    Save a complete suite of histograms (ditau pt, pz, mass, and delta angles).
    
    Args:
        output_dir: Output directory path
        stem_prefix: Filename prefix (e.g., "hist_tau_gen_parent")
        label_prefix: Label prefix for titles (e.g., "GenPart Parent Taus")
        ditau_kinematics: Dict with keys 'pt', 'pz', 'eta', 'phi', 'mass'
        delta_angles: Dict with keys 'delta_r', 'delta_phi', 'delta_eta', 'delta_theta'
        
    Raises:
        RuntimeError: On save failure
    """
    try:
        shape_bins = 80
        mass_bins = 120

        # Invariant mass
        logger.debug(f"Saving {stem_prefix} invariant mass histogram...")
        counts, bin_edges = compute_histogram_data(ditau_kinematics['mass'], mass_bins)
        save_png(output_dir, f"{stem_prefix}_ditau_mass", f"{label_prefix} Invariant Mass",
            ditau_kinematics['mass'], bin_edges, r"$m(\tau^{-}\tau^{+})$ [GeV]", "Events")
        save_root(output_dir, f"{stem_prefix}_ditau_mass", counts, bin_edges,
             f"{label_prefix} Invariant Mass")

        # DiTau pt
        logger.debug(f"Saving {stem_prefix} ditau pt histogram...")
        counts, bin_edges = compute_histogram_data(ditau_kinematics['pt'], shape_bins)
        save_png(output_dir, f"{stem_prefix}_ditau_pt", f"{label_prefix} Di-tau p_T",
                ditau_kinematics['pt'], bin_edges, r"$p_T(\tau^{-}\tau^{+})$ [GeV]", "Events")
        save_root(output_dir, f"{stem_prefix}_ditau_pt", counts, bin_edges,
                 f"{label_prefix} Di-tau p_T")
        
        # DiTau pz
        logger.debug(f"Saving {stem_prefix} ditau pz histogram...")
        counts, bin_edges = compute_histogram_data(ditau_kinematics['pz'], shape_bins)
        save_png(output_dir, f"{stem_prefix}_ditau_pz", f"{label_prefix} Di-tau p_z",
                ditau_kinematics['pz'], bin_edges, r"$p_z(\tau^{-}\tau^{+})$ [GeV]", "Events")
        save_root(output_dir, f"{stem_prefix}_ditau_pz", counts, bin_edges,
                 f"{label_prefix} Di-tau p_z")
        
        # DeltaR
        logger.debug(f"Saving {stem_prefix} deltaR histogram...")
        counts, bin_edges = compute_histogram_data(delta_angles['delta_r'], shape_bins)
        save_png(output_dir, f"{stem_prefix}_deltaR", f"{label_prefix} $\\Delta R$",
                delta_angles['delta_r'], bin_edges, r"$\Delta R(\tau^{-},\tau^{+})$", "Events")
        save_root(output_dir, f"{stem_prefix}_deltaR", counts, bin_edges,
                 f"{label_prefix} $\\Delta R$")
        
        # DeltaPhi
        logger.debug(f"Saving {stem_prefix} deltaPhi histogram...")
        counts, bin_edges = compute_histogram_data(delta_angles['delta_phi'], shape_bins)
        save_png(output_dir, f"{stem_prefix}_deltaPhi", f"{label_prefix} $\\Delta\\phi$",
                delta_angles['delta_phi'], bin_edges, r"$\Delta \phi(\tau^{-},\tau^{+})$", "Events")
        save_root(output_dir, f"{stem_prefix}_deltaPhi", counts, bin_edges,
                 f"{label_prefix} $\\Delta\\phi$")
        
        # DeltaEta
        logger.debug(f"Saving {stem_prefix} deltaEta histogram...")
        counts, bin_edges = compute_histogram_data(delta_angles['delta_eta'], shape_bins)
        save_png(output_dir, f"{stem_prefix}_deltaEta", f"{label_prefix} $\\Delta\\eta$",
                delta_angles['delta_eta'], bin_edges, r"$\Delta \eta(\tau^{-},\tau^{+})$", "Events")
        save_root(output_dir, f"{stem_prefix}_deltaEta", counts, bin_edges,
                 f"{label_prefix} $\\Delta\\eta$")
        
        # DeltaTheta (NEW)
        logger.debug(f"Saving {stem_prefix} deltaTheta histogram...")
        counts, bin_edges = compute_histogram_data(delta_angles['delta_theta'], shape_bins)
        save_png(output_dir, f"{stem_prefix}_deltaTheta", f"{label_prefix} $\\Delta\\theta$",
                delta_angles['delta_theta'], bin_edges, r"$\Delta \theta(\tau^{-},\tau^{+})$ [rad]", "Events")
        save_root(output_dir, f"{stem_prefix}_deltaTheta", counts, bin_edges,
                 f"{label_prefix} $\\Delta\\theta$")
        
        logger.info(f"✓ Saved histogram suite: {stem_prefix}")
    except Exception as e:
        error_msg = f"\n[ERROR] Failed to save histogram suite '{stem_prefix}': {str(e)}\n"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def create_output_directory(output_dir: Path) -> Path:
    """
    Create output directory for histogram files.
    
    Args:
        output_dir: Path to directory to create
        
    Returns:
        Path object for the created directory
        
    Raises:
        ValueError: If directory cannot be created
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
        return output_dir
    except OSError as e:
        error_msg = f"Cannot create output directory: {output_dir}\n  Details: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def validate_lhe_events(lhe_selected) -> int:
    """
    Validate LHE event selection.
    
    Args:
        lhe_selected: NanoEvents with LHE particles
        
    Returns:
        Number of events in selection
        
    Raises:
        ValueError: If selection is invalid or empty
    """
    try:
        n_events = len(lhe_selected)
        if n_events == 0:
            raise ValueError("LHE selection is empty (0 events)")
        logger.debug(f"Validated {n_events} LHE-selected events")
        return n_events
    except Exception as e:
        error_msg = f"Invalid LHE selection: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def build_lhe_tau_vectors(lhe_selected):
    """
    Build Lorentz vectors for tau- and tau+ from LHEPart collection.
    
    Args:
        lhe_selected: NanoEvents with valid LHE tau pairs
        
    Returns:
        Tuple of (lhe_minus_lv, lhe_plus_lv) Lorentz vectors
        
    Raises:
        RuntimeError: If Lorentz vector construction fails
    """
    try:
        logger.debug("Building LHE Lorentz vectors...")
        lhe_minus_lv, lhe_plus_lv = build_tau_vectors(
            lhe_selected.LHEPart,
            lhe_selected.LHEPart.pdgId == 15,
            lhe_selected.LHEPart.pdgId == -15,
        )
        logger.debug("✓ LHE Lorentz vectors built successfully")
        return lhe_minus_lv, lhe_plus_lv
    except Exception as e:
        error_msg = f"Failed to build LHE Lorentz vectors: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def compute_lhe_ditau_kinematics(lhe_minus_lv, lhe_plus_lv):
    """
    Compute di-tau (tau pair) kinematic properties from LHE.
    
    Args:
        lhe_minus_lv: Lorentz vector for tau- (pdgId=15)
        lhe_plus_lv: Lorentz vector for tau+ (pdgId=-15)
        
    Returns:
        Dictionary with keys 'pt', 'pz', 'eta', 'phi', 'mass'
        
    Raises:
        RuntimeError: If kinematics computation fails
    """
    try:
        logger.debug("Computing LHE di-tau kinematics...")
        lhe_ditau_kinematics = compute_ditau_kinematics(lhe_minus_lv, lhe_plus_lv)
        logger.debug("✓ LHE di-tau kinematics computed")
        return lhe_ditau_kinematics
    except Exception as e:
        error_msg = f"Failed to compute LHE di-tau kinematics: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def compute_lhe_delta_angles(lhe_minus_lv, lhe_plus_lv):
    """
    Compute delta angles (ΔR, Δφ, Δη) between tau pair.
    
    Args:
        lhe_minus_lv: Lorentz vector for tau- (pdgId=15)
        lhe_plus_lv: Lorentz vector for tau+ (pdgId=-15)
        
    Returns:
        Dictionary with keys 'delta_r', 'delta_phi', 'delta_eta'
        
    Raises:
        RuntimeError: If angle computation fails
    """
    try:
        logger.debug("Computing LHE delta angles...")
        lhe_delta_angles = compute_delta_angles(lhe_minus_lv, lhe_plus_lv)
        logger.debug("✓ LHE delta angles computed")
        return lhe_delta_angles
    except Exception as e:
        error_msg = f"Failed to compute LHE delta angles: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def save_lhe_mass_histogram(output_dir: Path, mass):
    """
    Save invariant mass distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        mass: Mass values array
        
    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        logger.debug("Saving LHE invariant mass histogram...")
        counts, bin_edges = compute_histogram_data(mass, bins=120)
        save_png(
            output_dir, 
            "lhe_mass", 
            "LHE Di-tau Invariant Mass",
            mass, 
            bin_edges, 
            r"$m(\tau^{-}\tau^{+})$ [GeV]", 
            "Events"
        )
        save_root(
            output_dir, 
            "lhe_mass", 
            counts, 
            bin_edges,
            "LHE Di-tau Invariant Mass"
        )
        logger.info("✓ Saved LHE mass histogram")
    except Exception as e:
        error_msg = f"Failed to save LHE mass histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def save_lhe_delta_r_histogram(output_dir: Path, delta_r):
    """
    Save ΔR distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        delta_r: Delta R values array
        
    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        logger.debug("Saving LHE ΔR histogram...")
        counts, bin_edges = compute_histogram_data(delta_r, bins=80)
        save_png(
            output_dir, 
            "lhe_delta_r", 
            "LHE $\\Delta R$",
            delta_r, 
            bin_edges, 
            r"$\Delta R(\tau^{-},\tau^{+})$", 
            "Events"
        )
        save_root(
            output_dir, 
            "lhe_delta_r", 
            counts, 
            bin_edges,
            "LHE $\\Delta R$"
        )
        logger.info("✓ Saved LHE ΔR histogram")
    except Exception as e:
        error_msg = f"Failed to save LHE ΔR histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def save_lhe_delta_phi_histogram(output_dir: Path, delta_phi):
    """
    Save Δφ distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        delta_phi: Delta phi values array (range [-π, π])
        
    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        logger.debug("Saving LHE Δφ histogram...")
        counts, bin_edges = compute_histogram_data(delta_phi, bins=80)
        save_png(
            output_dir, 
            "lhe_delta_phi", 
            "LHE $\\Delta\\phi$",
            delta_phi, 
            bin_edges, 
            r"$\Delta \phi(\tau^{-},\tau^{+})$ [rad]", 
            "Events"
        )
        save_root(
            output_dir, 
            "lhe_delta_phi", 
            counts, 
            bin_edges,
            "LHE $\\Delta\\phi$"
        )
        logger.info("✓ Saved LHE Δφ histogram")
    except Exception as e:
        error_msg = f"Failed to save LHE Δφ histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def save_lhe_delta_eta_histogram(output_dir: Path, delta_eta):
    """
    Save Δη distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        delta_eta: Delta eta values array
        
    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        logger.debug("Saving LHE Δη histogram...")
        counts, bin_edges = compute_histogram_data(delta_eta, bins=80)
        save_png(
            output_dir, 
            "lhe_delta_eta", 
            "LHE $\\Delta\\eta$",
            delta_eta, 
            bin_edges, 
            r"$\Delta \eta(\tau^{-},\tau^{+})$", 
            "Events"
        )
        save_root(
            output_dir, 
            "lhe_delta_eta", 
            counts, 
            bin_edges,
            "LHE $\\Delta\\eta$"
        )
        logger.info("✓ Saved LHE Δη histogram")
    except Exception as e:
        error_msg = f"Failed to save LHE Δη histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def make_tau_histogram_lhe(output_dir: Path, lhe_selected):
    """
    Generate LHE tau-pair histograms (mass, ΔR, Δφ, Δη).
    
    Orchestrates the complete LHE histogram generation pipeline:
    1. Create output directory
    2. Validate LHE events
    3. Build Lorentz vectors
    4. Compute kinematics and angles
    5. Save individual histograms
    
    Args:
        output_dir: Directory to save histogram files (PNG and ROOT)
        lhe_selected: NanoEvents with valid LHE tau pairs
        
    Raises:
        ValueError: If output directory cannot be created or events are invalid
        RuntimeError: If histogram generation or file I/O fails
    """
    try:
        logger.info("=" * 60)
        logger.info("GENERATING LHE TAU HISTOGRAMS")
        logger.info("=" * 60)
        
        # Step 1: Create output directory
        create_output_directory(output_dir)
        
        # Step 2: Validate LHE selection
        validate_lhe_events(lhe_selected)
        
        # Step 3: Build Lorentz vectors
        lhe_minus_lv, lhe_plus_lv = build_lhe_tau_vectors(lhe_selected)
        
        # Step 4: Compute kinematics and angles
        lhe_ditau_kinematics = compute_lhe_ditau_kinematics(lhe_minus_lv, lhe_plus_lv)
        lhe_delta_angles = compute_lhe_delta_angles(lhe_minus_lv, lhe_plus_lv)
        
        # Step 5: Save histograms
        save_lhe_mass_histogram(output_dir, lhe_ditau_kinematics['mass'])
        save_lhe_delta_r_histogram(output_dir, lhe_delta_angles['delta_r'])
        save_lhe_delta_phi_histogram(output_dir, lhe_delta_angles['delta_phi'])
        save_lhe_delta_eta_histogram(output_dir, lhe_delta_angles['delta_eta'])
        
        logger.info("=" * 60)
        logger.info("✓ LHE HISTOGRAMS GENERATED SUCCESSFULLY")
        logger.info("=" * 60)
    except Exception as e:
        error_msg = (
            f"\n[ERROR] LHE histogram generation failed\n"
            f"  Output directory: {output_dir}\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

