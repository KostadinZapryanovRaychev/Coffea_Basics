from pathlib import Path
import logging

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
from coffea.nanoevents.methods import vector

from .root_writer import save_lhe_histograms_root
from .validation import create_output_directory, validate_lhe_events
from .image_processing import save_png


logger = logging.getLogger(__name__)


def compute_histogram_data(values, bins , bin_edge_min=None, bin_edge_max=None):
    """
    Compute histogram bin edges and counts from raw values.
    
    Args:
        values: Array-like of numeric values
        bins: Number of bins or bin edges
        bin_edge_min: Minimum value for bin edges
        bin_edge_max: Maximum value for bin edges

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
        
        
        
        
        
        bin_edges = np.linspace(bin_edge_min, bin_edge_max, int(bins) + 1)
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
        counts , bin_edges = compute_histogram_data(mass, bins=100 , bin_edge_min=0, bin_edge_max=500)
        save_png(
            output_dir,
            "lhe_mass",
            "LHE Taus Pair Invariant Mass",
            mass,
            bin_edges,
            r"$m(\tau^{-}\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_mass", "LHE Taus Pair Invariant Mass", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE mass histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
def save_lhe_phi_histogram_by_default_method(output_dir: Path, phi):
    """
    Save phi distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        phi: Phi values array
    Returns:
        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(phi, bins=2500, bin_edge_min=-3.2, bin_edge_max=3.2)
        save_png(
            output_dir,
            "lhe_phi",
            "LHE Taus Pair Phi Distribution",
            phi,
            bin_edges,
            r"$\phi(\tau^{-}\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_phi", "LHE Taus Pair Phi Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
def save_lhe_phi_naturally(output_dir: Path ,lhe_minus_lv, lhe_plus_lv):
    """
    Save phi distribution histogram for LHE tau pairs using natural method.
    
    Args:
        output_dir: Output directory
        lhe_minus_lv: Lorentz vectors for tau-
        lhe_plus_lv: Lorentz vectors for tau+
    Returns:
        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        phi = lhe_minus_lv.phi - lhe_plus_lv.phi
        counts , bin_edges = compute_histogram_data(phi, bins=100, bin_edge_min=-3.2, bin_edge_max=3.2)
        save_png(
            output_dir,
            "lhe_phi_natural",
            "LHE Taus Pair Phi Distribution (Natural Method)",
            phi,
            bin_edges,
            r"$\phi(\tau^{-}\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_phi_natural", "LHE Taus Pair Phi Distribution (Natural Method)", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE phi histogram (natural method): {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
def save_lhe_histogram_pz(output_dir: Path, pz):
    """
    Save pz distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        pz: Pz values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:

        counts , bin_edges = compute_histogram_data(pz, bins=2500, bin_edge_min=-2000, bin_edge_max=2000)
        save_png(
            output_dir,
            "lhe_pz",
            "LHE Taus Pz Distribution",
            pz,
            bin_edges,
            r"$p_{z}(\tau^{-}\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_pz", "LHE Taus Pz Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE pz histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
def save_lhe_histogram_pt(output_dir: Path, pt):
    """
    Save pt distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        pt: Pt values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(pt, bins=2500, bin_edge_min=0, bin_edge_max=0.01)
        save_png(
            output_dir,
            "lhe_pt",
            "LHE Taus Pt Distribution",
            pt,
            bin_edges,
            r"$p_{T}(\tau^{-}\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_pt", "LHE Taus Pt Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE pt histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e    
     
def save_lhe_histogram_etha(output_dir: Path, eta):
    """
    Save eta distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        eta: Eta values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(eta, bins=1000, bin_edge_min=-20, bin_edge_max=20)
        save_png(
            output_dir,
            "lhe_eta",
            "LHE Taus Eta Distribution",
            eta,
            bin_edges,
            r"$\eta(\tau^{-}\tau^{+})$",
            "Events",
        )
        return "lhe_eta", "LHE Taus Eta Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def make_tau_histogram_lhe(output_dir: Path, lhe_selected):
    """
    Create and save histograms for LHE-selected tau pairs.
    
    Args:
        output_dir: Directory to save histograms
        lhe_selected: NanoEvents with LHE-selected tau pairs
    Raises:
        ValueError: If LHE selection is invalid
        RuntimeError: If histogram creation or saving fails
    """
    try:
        n_events = validate_lhe_events(lhe_selected)
        print(f"Processing {n_events} LHE-selected events for histogramming...")
        
        lhe_minus_lv, lhe_plus_lv = build_tau_vectors(
             lhe_selected.LHEPart,
             lhe_selected.LHEPart.pdgId == 15,
             lhe_selected.LHEPart.pdgId == -15,
        )
        # for all particles 
        save_lhe_mass_histogram(output_dir, (lhe_minus_lv + lhe_plus_lv).mass)
        save_lhe_phi_histogram_by_default_method(output_dir, (lhe_minus_lv + lhe_plus_lv).phi)
        save_lhe_phi_naturally(output_dir, lhe_minus_lv, lhe_plus_lv)
        save_lhe_histogram_pz(output_dir, (lhe_minus_lv + lhe_plus_lv).pz)
        save_lhe_histogram_pt(output_dir, (lhe_minus_lv + lhe_plus_lv).pt)
        save_lhe_histogram_etha(output_dir, (lhe_minus_lv + lhe_plus_lv).eta)
    except ValueError as e:
        logger.error(f"\n{str(e)}")
        raise ValueError(str(e)) from e
    except RuntimeError as e:
        logger.error(f"\n{str(e)}")
        raise RuntimeError(str(e)) from e
    except Exception as e:
        error_msg = f"Unexpected error in make_tau_histogram_lhe: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e