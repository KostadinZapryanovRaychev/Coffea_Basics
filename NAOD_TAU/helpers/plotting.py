from pathlib import Path
import logging

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
from coffea.nanoevents.methods import vector

from .root_writer import save_lhe_histograms_root
from .validation import create_output_directory, validate_lhe_events


logger = logging.getLogger(__name__)


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


def save_lhe_mass_histogram(output_dir: Path, mass):
    """
    Save invariant mass distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        mass: Mass values array
        
    Returns:
        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output

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
            "Events",
        )
        return "lhe_mass", "LHE Di-tau Invariant Mass", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE mass histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def save_lhe_cos_delta_eta_histogram(output_dir: Path, delta_eta):
    """
    Save cos(Δη) distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        delta_eta: Delta eta values array
        
    Returns:
        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output

    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        logger.debug("Saving LHE cos(Δη) histogram...")
        cos_delta_eta = np.cos(delta_eta)
        counts, bin_edges = compute_histogram_data(cos_delta_eta, bins=80)
        save_png(
            output_dir,
            "lhe_cos_delta_eta",
            "LHE $\\cos(\\Delta\\eta)$",
            cos_delta_eta,
            bin_edges,
            r"$\cos(\Delta \eta(\tau^{-},\tau^{+}))$",
            "Events",
        )
        logger.info("✓ Saved LHE cos(Δη) histogram")
        return "lhe_cos_delta_eta", "LHE $\\cos(\\Delta\\eta)$", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE cos(Δη) histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def save_png(output_dir: Path, histogram_name: str, title: str, values, bin_edges, xlabel: str, ylabel: str):
    """
    Save a histogram as a PNG file.
    
    Args:
        output_dir: Directory to save the PNG file
        histogram_name: Base name for the histogram (without extension)
        title: Title of the histogram
        values: Array of values to histogram
        bin_edges: Edges of the histogram bins
        xlabel: Label for x-axis
        ylabel: Label for y-axis
    Raises:        RuntimeError: If saving the PNG file fails
    """
    try:
        plt.figure(figsize=(8, 6))
        plt.hist(values, bins=bin_edges, histtype='stepfilled', color='blue', alpha=0.7)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True, linestyle='--', alpha=0.5)
        png_path = output_dir / f"{histogram_name}.png"
        plt.savefig(png_path)
        plt.close()
        logger.debug(f"Saved PNG histogram: {png_path}")
    except Exception as e:
        error_msg = f"Failed to save PNG histogram '{histogram_name}': {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    

def compute_lhe_tau_minus_kinematics(lhe_minus_lv):
    """
    Compute kinematic properties for tau- from LHE Lorentz vector.
    
    Args:
        lhe_minus_lv: Lorentz vector for tau- (pdgId=15)
    Returns:
        Dictionary with keys:
        - 'pt': Transverse momentum of tau-
        - 'pz': Longitudinal momentum of tau-
        - 'eta': Pseudo-rapidity of tau-
        - 'phi': Azimuthal angle of tau-
        - 'mass': Mass of tau-
    Raises:       RuntimeError: If kinematic computation fails      
    """
    try:
        return {
            'pt': ak.to_numpy(lhe_minus_lv.pt),
            'pz': ak.to_numpy(lhe_minus_lv.pz),
            'eta': ak.to_numpy(lhe_minus_lv.eta),
            'phi': ak.to_numpy(lhe_minus_lv.phi),
            'mass': ak.to_numpy(lhe_minus_lv.mass),
        }
    except Exception as e:
        error_msg = f"Failed to compute tau- kinematics: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e    
    
def compute_lhe_tau_plus_kinematics(lhe_plus_lv):
    """
    Compute kinematic properties for tau+ from LHE Lorentz vector.
    
    Args:
        lhe_plus_lv: Lorentz vector for tau+ (pdgId=-15)
    Returns:
        Dictionary with keys:
        - 'pt': Transverse momentum of tau+
        - 'pz': Longitudinal momentum of tau+
        - 'eta': Pseudo-rapidity of tau+
        - 'phi': Azimuthal angle of tau+
        - 'mass': Mass of tau+
    Raises:       RuntimeError: If kinematic computation fails      
    """
    try:
        return {
            'pt': ak.to_numpy(lhe_plus_lv.pt),
            'pz': ak.to_numpy(lhe_plus_lv.pz),
            'eta': ak.to_numpy(lhe_plus_lv.eta),
            'phi': ak.to_numpy(lhe_plus_lv.phi),
            'mass': ak.to_numpy(lhe_plus_lv.mass),
        }
    except Exception as e:
        error_msg = f"Failed to compute tau+ kinematics: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e