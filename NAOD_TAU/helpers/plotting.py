from pathlib import Path
import logging
import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
from .image_processing import save_png , compute_histogram_data


logger = logging.getLogger(__name__)

def get_mass_his(output_dir: Path, mass):
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
  
def get_parent_part_pt_his(output_dir: Path, pt):
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

def get_parent_part_pz_his(output_dir: Path, pz):
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
    

def save_lhe_histogram_rapidity(output_dir: Path, rapidity_values):
    """
    Save rapidity distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        rapidity_values: Calculated rapidity values (numpy array or awkward array)
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(rapidity_values, bins=100, bin_edge_min=-5, bin_edge_max=5)
        save_png(
            output_dir,
            "lhe_rapidity",
            "LHE Taus Rapidity Distribution",
            rapidity_values,
            bin_edges,
            r"$y(\tau^{-}\tau^{+})$",
            "Events",
        )
        return "lhe_rapidity", "LHE Taus Rapidity Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE rapidity histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_lhe_histogram_eta(output_dir: Path, eta):
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

def save_lhe_delta_phi_pair_histogram(output_dir: Path, delta_phi):
    """
    Save delta-phi distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        delta_phi: Delta-phi values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(delta_phi, bins=60, bin_edge_min=-3.2, bin_edge_max=3.2)
        save_png(
            output_dir,
            "lhe_delta_phi",
            "LHE Taus Pair Delta Phi",
            delta_phi,
            bin_edges,
            r"$\Delta\phi(\tau^{-}\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_delta_phi", "LHE Taus Pair Delta Phi", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_lhe_delta_phi_lepton_pair_histogram(output_dir: Path, lhe_minus_lv, lhe_plus_lv):
    """
    Save delta-phi distribution histogram for lepton pairs (tau- vs tau+).
    
    Args:
        output_dir: Output directory
        lhe_minus_lv: Lorentz vectors for tau-
        lhe_plus_lv: Lorentz vectors for tau+
    Returns:
        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        delta_phi = lhe_minus_lv.phi - lhe_plus_lv.phi
        counts , bin_edges = compute_histogram_data(delta_phi, bins=60, bin_edge_min=-3.2, bin_edge_max=3.2)
        save_png(
            output_dir,
            "lhe_delta_phi_lepton_pair",
            "LHE Lepton Pair Delta Phi",
            delta_phi,
            bin_edges,
            r"$\Delta\phi(\tau^{-} - \tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_delta_phi_lepton_pair", "LHE Lepton Pair Delta Phi", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-phi lepton pair histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_lhe_delta_eta_lepton_pair_histogram(output_dir: Path, lhe_minus_lv, lhe_plus_lv):
    """
    Save delta-eta distribution histogram for lepton pairs (tau- vs tau+).
    
    Args:
        output_dir: Output directory
        lhe_minus_lv: Lorentz vectors for tau-
        lhe_plus_lv: Lorentz vectors for tau+
    Returns:
        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        delta_eta = lhe_minus_lv.eta - lhe_plus_lv.eta
        counts , bin_edges = compute_histogram_data(delta_eta, bins=1000, bin_edge_min=-10, bin_edge_max=10)
        save_png(
            output_dir,
            "lhe_delta_eta_lepton_pair",
            "LHE Lepton Pair Delta Eta",
            delta_eta,
            bin_edges,
            r"$\Delta\eta(\tau^{-} - \tau^{+})$",
            "Events",
        )
        return "lhe_delta_eta_lepton_pair", "LHE Lepton Pair Delta Eta", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-eta lepton pair histogram: {str(e)}"
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
   
