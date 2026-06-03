from pathlib import Path
import logging
import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
from .image_processing import save_png , compute_histogram_data, save_2d_histogram_png


logger = logging.getLogger(__name__)

bin_size = 120


def _convert_mass_point_to_float(mass_point: str) -> float:
    """
    Convert mass point string to float value for calculations.
    
    Args:
        mass_point: Mass point string (e.g., "500", "750", "unknown")
        
    Returns:
        Float value of mass point, or default value if "unknown"
    """
    if mass_point == "unknown":
        return 500.0  # Default mass point for unknown cases
    try:
        return float(mass_point)
    except ValueError:
        logger.warning(f"Could not parse mass point '{mass_point}', using default 500 GeV")
        return 500.0


def _get_histogram_ranges(mass_point: str) -> dict:
    """
    Calculate dynamic histogram ranges based on mass point.
    
    For Z' → 2τ analysis, ranges scale with the parent particle mass.
    
    Args:
        mass_point: Mass point string (e.g., "500", "750")
        
    Returns:
        Dictionary with histogram configuration ranges:
        {
            'invariant_mass_max': 2 * mass_point,
            'pt_max': 0.6 * mass_point,
            'pz_max': 1.5 * mass_point,
            'delta_r_max': 6.0,  # Fixed for angular separation
            'delta_eta_max': 7.5,  # Fixed for pseudorapidity
            'delta_phi_bins': 60,  # Fixed bin count
            'cos_delta_phi_bins': 100  # Fixed bin count
        }
    """
    M = _convert_mass_point_to_float(mass_point)
    
    return {
        'invariant_mass_max': 2.0 * M,      # Range: 0 to 2*M
        'pt_max': 0.6 * M,                   # Range: 0 to 0.6*M (approximate max tau pT)
        'pz_max': 1.5 * M,                   # Range: -1.5*M to 1.5*M (longitudinal momentum)
        'delta_r_max': 6.0,                  # Fixed: angular separation saturates
        'delta_eta_max': 7.5,                # Fixed: pseudorapidity range
        'delta_phi_bins': 60,                # Fixed: adequate phi binning
        'cos_delta_phi_bins': 100            # Fixed: cos(phi) is bounded [-1, 1]
    }

def get_mass_his(output_dir: Path, mass, mass_point: str = "unknown"):
    """
    Save invariant mass distribution histogram for LHE tau pairs.
    
    Range scales with mass point: 0 to 2*M for mass point M.
    
    Args:
        output_dir: Output directory
        mass: Mass values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
        
    Returns:
        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output

    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        ranges = _get_histogram_ranges(mass_point)
        counts , bin_edges = compute_histogram_data(
            mass, 
            bins=250,
            bin_edge_min=0,
            bin_edge_max=ranges['invariant_mass_max']
        )
        title = f"LHE Taus Pair Invariant Mass (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_mass",
            title,
            mass,
            bin_edges,
            r"$m(\tau^{-}\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_mass", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE mass histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_tau_pt_his(output_dir: Path, pt, mass_point: str = "unknown"):
    """
    Save pt distribution histogram for LHE tau pairs.
    
    Range scales with mass point: 0 to 0.6*M for mass point M.
    
    Args:
        output_dir: Output directory
        pt: Pt values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        ranges = _get_histogram_ranges(mass_point)
        counts , bin_edges = compute_histogram_data(
            pt,
            bins=bin_size,
            bin_edge_min=0,
            bin_edge_max=ranges['pt_max']
        )
        title = f"LHE Tau Pt Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_pt",
            title,
            pt,
            bin_edges,
            r"$p_{T}(\tau^{-}\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_pt", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE pt histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
def get_anti_tau_pt_his(output_dir: Path, pt, mass_point: str = "unknown"):
    """
    Save pt distribution histogram for LHE anti-tau pairs.
    
    Range scales with mass point: 0 to 0.6*M for mass point M.
    
    Args:
        output_dir: Output directory
        pt: Pt values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        ranges = _get_histogram_ranges(mass_point)
        counts , bin_edges = compute_histogram_data(
            pt,
            bins=bin_size,
            bin_edge_min=0,
            bin_edge_max=ranges['pt_max']
        )
        title = f"LHE Anti-Tau Pt Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_antitau_pt",
            title,
            pt,
            bin_edges,
            r"$p_{T}(\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_antitau_pt", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE anti-tau pt histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_tau_pz_his(output_dir: Path, pz, mass_point: str = "unknown"):
    """
    Save pz distribution histogram for LHE tau pairs.
    
    Range scales with mass point: -1.5*M to 1.5*M for mass point M.
    
    Args:
        output_dir: Output directory
        pz: Pz values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        ranges = _get_histogram_ranges(mass_point)
        pz_max = ranges['pz_max']
        counts , bin_edges = compute_histogram_data(
            pz,
            bins=bin_size,
            bin_edge_min=-pz_max,
            bin_edge_max=pz_max
        )
        title = f"LHE Taus Pz Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_pz",
            title,
            pz,
            bin_edges,
            r"$p_{z}(\tau^{-}\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_pz", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE pz histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_anti_tau_pz_his(output_dir: Path, pz, mass_point: str = "unknown"):
    """
    Save pz distribution histogram for LHE anti-tau pairs.
    
    Range scales with mass point: -1.5*M to 1.5*M for mass point M.
    
    Args:
        output_dir: Output directory
        pz: Pz values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        ranges = _get_histogram_ranges(mass_point)
        pz_max = ranges['pz_max']
        counts , bin_edges = compute_histogram_data(
            pz,
            bins=bin_size,
            bin_edge_min=-pz_max,
            bin_edge_max=pz_max
        )
        title = f"LHE Anti-Tau Pz Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_antitau_pz",
            title,
            pz,
            bin_edges,
            r"$p_{z}(\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_antitau_pz", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE anti-tau pz histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_tau_eta_his(output_dir: Path, eta, mass_point: str = "unknown"):
    """
    Get eta distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        eta: Eta values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(eta, bins=bin_size, bin_edge_min=-3, bin_edge_max=3)
        title = f"LHE Tau Eta Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_eta_tau",
            title,
            eta,
            bin_edges,
            r"$\eta(\tau^{-}\tau^{+})$",
            "Events",
        )
        return "lhe_eta_tau", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_anti_tau_eta_his(output_dir: Path, eta, mass_point: str = "unknown"):
    """
    Get eta distribution histogram for LHE anti-tau pairs.
    
    Args:
        output_dir: Output directory
        eta: Eta values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(eta, bins=bin_size, bin_edge_min=-3, bin_edge_max=3)
        title = f"LHE Anti-Tau Eta Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_eta_anti_tau",
            title,
            eta,
            bin_edges,
            r"$\eta(\tau^{+})$",
            "Events",
        )
        return "lhe_eta_anti_tau", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_tau_phi_his(output_dir: Path, phi, mass_point: str = "unknown"):
    """
    Get phi distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        phi: Phi values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(phi, bins=bin_size, bin_edge_min=-np.pi, bin_edge_max=np.pi)
        title = f"LHE Tau Phi Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_phi_tau",
            title,
            phi,
            bin_edges,
            r"$\phi(\tau^{-}\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_phi_tau", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_anti_tau_phi_his(output_dir: Path, phi, mass_point: str = "unknown"):
    """
    Get phi distribution histogram for LHE anti-tau pairs.
    
    Args:
        output_dir: Output directory
        phi: Phi values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(phi, bins=bin_size, bin_edge_min=-np.pi, bin_edge_max=np.pi)
        title = f"LHE Anti-Tau Phi Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_phi_anti_tau",
            title,
            phi,
            bin_edges,
            r"$\phi(\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_phi_anti_tau", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE anti-tau phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_delta_phi_ditau_difference_his(output_dir: Path, delta_phi, mass_point: str = "unknown"):
    """
    Save delta-phi distribution histogram for LHE tau pairs.
    
    Range is fixed: -π to π (angular separation is independent of mass point).
    
    Args:
        output_dir: Output directory
        delta_phi: Delta-phi values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """  
    try:
        ranges = _get_histogram_ranges(mass_point)
        counts , bin_edges = compute_histogram_data(
            delta_phi,
            bins=ranges['delta_phi_bins'],
            bin_edge_min=-np.pi,
            bin_edge_max=np.pi
        )
        title = f"LHE Di Tau Phi Difference (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_delta_phi",
            title,
            delta_phi,
            bin_edges,
            r"$\Delta\phi(\tau^{-}\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_delta_phi", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e 

def get_cos_delta_phi_his(output_dir: Path, delta_phi, mass_point: str = "unknown"):
    """
    Save cos(delta-phi) distribution histogram for LHE tau pairs.
    
    Range is fixed: -1 to 1 (cosine is bounded). Bins adjusted for mass point.

    Args:
        output_dir: Output directory
        delta_phi: Delta-phi values array
        mass_point: Mass point string (e.g., "500", "750") for histogram title

    Returns:
        Tuple of (histogram_name, title, counts, bin_edges)
        for combined ROOT output

    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        ranges = _get_histogram_ranges(mass_point)
        
        # Compute cos(delta_phi)
        cos_delta_phi = np.cos(delta_phi)

        # Histogram data with mass-point-aware binning
        counts, bin_edges = compute_histogram_data(
            cos_delta_phi,
            bins=ranges['cos_delta_phi_bins'],
            bin_edge_min=-1,
            bin_edge_max=1,
        )

        # Save histogram image
        title = f"LHE Di-Tau Cos(Delta Phi) (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_cos_delta_phi",
            title,
            cos_delta_phi,
            bin_edges,
            r"$\cos(\Delta\phi(\tau^{-}\tau^{+}))$",
            "Events",
        )

        return (
            "lhe_cos_delta_phi",
            title,
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save LHE cos(delta-phi) histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_delta_r_ditau_difference_his(output_dir: Path, lhe_minus_lv, lhe_plus_lv, mass_point: str = "unknown"):
    """
    Save delta-R distribution histogram for LHE tau pairs.
    
    Range is fixed: 2 to 6 (angular separation is independent of mass point).
    
    Args:
        output_dir: Output directory
        lhe_minus_lv: Lorentz vectors for tau-
        lhe_plus_lv: Lorentz vectors for tau+
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        ranges = _get_histogram_ranges(mass_point)
        delta_r = np.sqrt((lhe_minus_lv.eta - lhe_plus_lv.eta)**2 + (lhe_minus_lv.phi - lhe_plus_lv.phi)**2)
        counts , bin_edges = compute_histogram_data(
            delta_r,
            bins=bin_size,
            bin_edge_min=2,
            bin_edge_max=ranges['delta_r_max']
        )
        title = f"LHE Di Tau Delta R (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_delta_r_ditau_pair",
            title,
            delta_r,
            bin_edges,
            r"$\Delta R(\tau^{-}\tau^{+})$",
            "Events",
        )
        return "lhe_delta_r_ditau_pair", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-R di-tau pair histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_delta_eta_ditau_difference_his(output_dir: Path, lhe_minus_lv, lhe_plus_lv, mass_point: str = "unknown"):
    """
    Save delta-eta distribution histogram for lepton pairs (tau- vs tau+).
    
    Range is fixed: -7.5 to 7.5 (pseudorapidity difference is independent of mass point).
    
    Args:
        output_dir: Output directory
        lhe_minus_lv: Lorentz vectors for tau-
        lhe_plus_lv: Lorentz vectors for tau+
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:
        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        ranges = _get_histogram_ranges(mass_point)
        delta_eta = lhe_minus_lv.eta - lhe_plus_lv.eta
        counts , bin_edges = compute_histogram_data(
            delta_eta,
            bins=bin_size,
            bin_edge_min=-ranges['delta_eta_max'],
            bin_edge_max=ranges['delta_eta_max']
        )
        title = f"LHE Di Tau Delta Eta (M={mass_point} GeV)"
        save_png(
            output_dir,
            "lhe_delta_eta_ditau_pair",
            title,
            delta_eta,
            bin_edges,
            r"$\Delta\eta(\tau^{-} - \tau^{+})$",
            "Events",
        )
        return "lhe_delta_eta_ditau_pair", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-eta di-tau pair histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_delta_r_vs_delta_phi_2d_his(output_dir: Path, lhe_minus_lv, lhe_plus_lv, mass_point: str = "unknown"):
    """
    Save a 2D histogram of delta_R vs delta_phi for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        lhe_minus_lv: Lorentz vectors for tau-
        lhe_plus_lv: Lorentz vectors for tau+
        mass_point: Mass point string (e.g., "500", "750") for histogram title
    Returns:
        None (2D histogram is saved as PNG only, not included in ROOT output)
    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        delta_r = np.sqrt((lhe_minus_lv.eta - lhe_plus_lv.eta)**2 + (lhe_minus_lv.phi - lhe_plus_lv.phi)**2)
        delta_phi = lhe_minus_lv.phi - lhe_plus_lv.phi
        
        # Normalize delta_phi to [-pi, pi] range
        delta_phi = np.arctan2(np.sin(delta_phi), np.cos(delta_phi))
        
        title = f"LHE Di-Tau Delta R vs Delta Phi (M={mass_point} GeV)"
        ranges = _get_histogram_ranges(mass_point)
        save_2d_histogram_png(
            output_dir,
            "lhe_delta_r_vs_delta_phi_2d",
            title,
            delta_phi,
            delta_r,
            x_bins=10,
            y_bins=10,
            x_min=-np.pi,
            x_max=np.pi,
            y_min=2,
            y_max=ranges['delta_r_max'],
            xlabel=r"$\Delta\phi(\tau^{-}\tau^{+})$ [rad]",
            ylabel=r"$\Delta R(\tau^{-}\tau^{+})$",
        )
        return None  # 2D histograms not saved to ROOT
    except Exception as e:
        error_msg = f"Failed to save LHE 2D delta-R vs delta-phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
