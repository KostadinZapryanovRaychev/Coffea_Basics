from pathlib import Path
import logging
import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
from .image_processing import save_png , compute_histogram_data, save_2d_histogram_png


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
        counts , bin_edges = compute_histogram_data(mass, bins=2500 , bin_edge_min=0, bin_edge_max=500)
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

def get_tau_pt_his(output_dir: Path, pt):
    """
    Save pt distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        pt: Pt values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(pt, bins=2500, bin_edge_min=0, bin_edge_max=300)
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
    
def get_anti_tau_pt_his(output_dir: Path, pt):
    """
    Save pt distribution histogram for LHE anti-tau pairs.
    
    Args:
        output_dir: Output directory
        pt: Pt values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(pt, bins=2500, bin_edge_min=0, bin_edge_max=300)
        save_png(
            output_dir,
            "lhe_antitau_pt",
            "LHE Anti-Tau Pt Distribution",
            pt,
            bin_edges,
            r"$p_{T}(\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_antitau_pt", "LHE Anti-Tau Pt Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE anti-tau pt histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_tau_pz_his(output_dir: Path, pz):
    """
    Save pz distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        pz: Pz values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(pz, bins=2500, bin_edge_min=-1500, bin_edge_max=1500)
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

def get_anti_tau_pz_his(output_dir: Path, pz):
    """
    Save pz distribution histogram for LHE anti-tau pairs.
    
    Args:
        output_dir: Output directory
        pz: Pz values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(pz, bins=2500, bin_edge_min=-1500, bin_edge_max=1500)
        save_png(
            output_dir,
            "lhe_antitau_pz",
            "LHE Anti-Tau Pz Distribution",
            pz,
            bin_edges,
            r"$p_{z}(\tau^{+})$ [GeV]",
            "Events",
        )
        return "lhe_antitau_pz", "LHE Anti-Tau Pz Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE anti-tau pz histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_tau_eta_his(output_dir: Path, eta):
    """
    Get eta distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        eta: Eta values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(eta, bins=2500, bin_edge_min=-3, bin_edge_max=3)
        save_png(
            output_dir,
            "lhe_eta_tau",
            "LHE Tau Eta Distribution",
            eta,
            bin_edges,
            r"$\eta(\tau^{-}\tau^{+})$",
            "Events",
        )
        return "lhe_eta_tau", "LHE Tau Eta Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_anti_tau_eta_his(output_dir: Path, eta):
    """
    Get eta distribution histogram for LHE anti-tau pairs.
    
    Args:
        output_dir: Output directory
        eta: Eta values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(eta, bins=2500, bin_edge_min=-3, bin_edge_max=3)
        save_png(
            output_dir,
            "lhe_eta_anti_tau",
            "LHE Anti-Tau Eta Distribution",
            eta,
            bin_edges,
            r"$\eta(\tau^{+})$",
            "Events",
        )
        return "lhe_eta_anti_tau", "LHE Anti-Tau Eta Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"Failed to save LHE eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_tau_phi_his(output_dir: Path, phi):
    """
    Get phi distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        phi: Phi values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(phi, bins=2500, bin_edge_min=-np.pi, bin_edge_max=np.pi)
        save_png(
            output_dir,
            "lhe_phi_tau",
            "LHE Tau Phi Distribution",
            phi,
            bin_edges,
            r"$\phi(\tau^{-}\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_phi_tau", "LHE Tau Phi Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_anti_tau_phi_his(output_dir: Path, phi):
    """
    Get phi distribution histogram for LHE anti-tau pairs.
    
    Args:
        output_dir: Output directory
        phi: Phi values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(phi, bins=2500, bin_edge_min=-np.pi, bin_edge_max=np.pi)
        save_png(
            output_dir,
            "lhe_phi_anti_tau",
            "LHE Anti-Tau Phi Distribution",
            phi,
            bin_edges,
            r"$\phi(\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_phi_anti_tau", "LHE Anti-Tau Phi Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE anti-tau phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_delta_phi_ditau_difference_his(output_dir: Path, delta_phi):
    """
    Save delta-phi distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        delta_phi: Delta-phi values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """  
    try:
        counts , bin_edges = compute_histogram_data(delta_phi, bins=60 , bin_edge_min=-np.pi, bin_edge_max=np.pi)
        save_png(
            output_dir,
            "lhe_delta_phi",
            "LHE Di Tau Phi Difference",
            delta_phi,
            bin_edges,
            r"$\Delta\phi(\tau^{-}\tau^{+})$ [rad]",
            "Events",
        )
        return "lhe_delta_phi", "LHE Di Tau Phi Difference", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e 

def get_cos_delta_phi_his(output_dir: Path, delta_phi):
    """
    Save cos(delta-phi) distribution histogram for LHE tau pairs.

    Args:
        output_dir: Output directory
        delta_phi: Delta-phi values array

    Returns:
        Tuple of (histogram_name, title, counts, bin_edges)
        for combined ROOT output

    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        # Compute cos(delta_phi)
        cos_delta_phi = np.cos(delta_phi)

        # Histogram data
        counts, bin_edges = compute_histogram_data(
            cos_delta_phi,
            bins=100,
            bin_edge_min=-1,
            bin_edge_max=1,
        )

        # Save histogram image
        save_png(
            output_dir,
            "lhe_cos_delta_phi",
            "LHE Di-Tau Cos(Delta Phi)",
            cos_delta_phi,
            bin_edges,
            r"$\cos(\Delta\phi(\tau^{-}\tau^{+}))$",
            "Events",
        )

        return (
            "lhe_cos_delta_phi",
            "LHE Di-Tau Cos(Delta Phi)",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save LHE cos(delta-phi) histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_delta_r_ditau_difference_his(output_dir: Path, lhe_minus_lv, lhe_plus_lv):
    """
    Save delta-R distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        lhe_minus_lv: Lorentz vectors for tau-
        lhe_plus_lv: Lorentz vectors for tau+
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        delta_r = np.sqrt((lhe_minus_lv.eta - lhe_plus_lv.eta)**2 + (lhe_minus_lv.phi - lhe_plus_lv.phi)**2)
        counts , bin_edges = compute_histogram_data(delta_r, bins=2500, bin_edge_min=2, bin_edge_max=6)
        save_png(
            output_dir,
            "lhe_delta_r_ditau_pair",
            "LHE Di Tau Delta R",
            delta_r,
            bin_edges,
            r"$\Delta R(\tau^{-}\tau^{+})$",
            "Events",
        )
        return "lhe_delta_r_ditau_pair", "LHE Di Tau Delta R", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-R di-tau pair histogram: {str(e)}"
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

        counts , bin_edges = compute_histogram_data(pz, bins=2500, bin_edge_min=-1500, bin_edge_max=1500)
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


def get_delta_eta_ditau_difference_his(output_dir: Path, lhe_minus_lv, lhe_plus_lv):
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
        counts , bin_edges = compute_histogram_data(delta_eta, bins=1000, bin_edge_min=-7.5, bin_edge_max=7.5)
        save_png(
            output_dir,
            "lhe_delta_eta_ditau_pair",
            "LHE Di Tau Delta Eta",
            delta_eta,
            bin_edges,
            r"$\Delta\eta(\tau^{-} - \tau^{+})$",
            "Events",
        )
        return "lhe_delta_eta_ditau_pair", "LHE Di Tau Delta Eta", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE delta-eta di-tau pair histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_eta_tau_his(output_dir: Path, eta):
    """
    Get eta distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        eta: Eta values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(eta, bins=1000, bin_edge_min=-5, bin_edge_max=5)
        save_png(
            output_dir,
            "lhe_eta_tau",
            "LHE Tau Eta Distribution",
            eta,
            bin_edges,
            r"$\eta(\tau^{-}\tau^{+})$",
            "Events",
        )
        return "lhe_eta_tau", "LHE Tau Eta Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_eta_anti_tau_his(output_dir: Path, eta):
    """
    Get eta distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        eta: Eta values array
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(eta, bins=1000, bin_edge_min=-5, bin_edge_max=5)
        save_png(
            output_dir,
            "lhe_eta_anti_tau",
            "LHE Anti-Tau Eta Distribution",
            eta,
            bin_edges,
            r"$\eta(\tau^{-}\tau^{+})$",
            "Events",
        )
        return "lhe_eta_anti_tau", "LHE Anti-Tau Eta Distribution", counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save LHE eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def get_eta_his(output_dir: Path, eta):
    """
    Get eta distribution histogram for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        eta: Eta values array                       
    Returns:        Tuple of (histogram_name, title, counts, bin_edges) for combined ROOT output
    Raises:        RuntimeError: If histogram save fails
    """
    try:
        counts , bin_edges = compute_histogram_data(eta, bins=1000, bin_edge_min=-18, bin_edge_max=18)
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

def get_delta_r_vs_delta_phi_2d_his(output_dir: Path, lhe_minus_lv, lhe_plus_lv):
    """
    Save a 2D histogram of delta_R vs delta_phi for LHE tau pairs.
    
    Args:
        output_dir: Output directory
        lhe_minus_lv: Lorentz vectors for tau-
        lhe_plus_lv: Lorentz vectors for tau+
    Returns:
        Tuple of (histogram_name, title) for combined ROOT output
    Raises:
        RuntimeError: If histogram save fails
    """
    try:
        delta_r = np.sqrt((lhe_minus_lv.eta - lhe_plus_lv.eta)**2 + (lhe_minus_lv.phi - lhe_plus_lv.phi)**2)
        delta_phi = lhe_minus_lv.phi - lhe_plus_lv.phi
        
        # Normalize delta_phi to [-pi, pi] range
        delta_phi = np.arctan2(np.sin(delta_phi), np.cos(delta_phi))
        
        save_2d_histogram_png(
            output_dir,
            "lhe_delta_r_vs_delta_phi_2d",
            "LHE Di-Tau Delta R vs Delta Phi",
            delta_phi,
            delta_r,
            x_bins=10,
            y_bins=10,
            x_min=-np.pi,
            x_max=np.pi,
            y_min=0,
            y_max=6,
            xlabel=r"$\Delta\phi(\tau^{-}\tau^{+})$ [rad]",
            ylabel=r"$\Delta R(\tau^{-}\tau^{+})$",
        )
        return "lhe_delta_r_vs_delta_phi_2d", "LHE Di-Tau Delta R vs Delta Phi"
    except Exception as e:
        error_msg = f"Failed to save LHE 2D delta-R vs delta-phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
