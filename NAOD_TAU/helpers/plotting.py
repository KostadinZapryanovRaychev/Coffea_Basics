from pathlib import Path
import logging
import awkward as ak
import matplotlib.pyplot as plt
import numpy as np

from .root_writer import save_lhe_histograms_root
from .validation import create_output_directory, validate_lhe_events
from .image_processing import save_png
from .z_prime_candidate import check_zprime_candidates
from .vector_builder import build_tau_vectors

logger = logging.getLogger(__name__)


def make_raw_all_tau_histograms(output_dir: Path, events):
    """
    Create and save histograms for ALL tau particles in the dataset.
    
    Analyzes the complete LHEPart collection BEFORE any pair selection.
    This shows the raw tau kinematic distributions across all events.
    
    Args:
        output_dir: Directory to save histograms
        events: NanoEvents object with LHEPart collection (all events, no selection)
        
    Raises:
        RuntimeError: If histogram creation fails
    """
    try:
        # Get all tau and anti-tau particles from LHEPart
        if "LHEPart" not in events.fields:
            logger.warning("⚠ LHEPart not found, skipping raw tau histograms")
            return
        
        pdg_lhe = events.LHEPart.pdgId
        
        # Select all tau (15) and anti-tau (-15) particles
        tau_mask = (pdg_lhe == 15) | (pdg_lhe == -15)
        taus_all = events.LHEPart[tau_mask]
        
        # Flatten to get single array of all tau particles across all events
        taus_pt = ak.flatten(taus_all.pt)
        taus_eta = ak.flatten(taus_all.eta)
        taus_phi = ak.flatten(taus_all.phi)
        taus_pz = ak.flatten(taus_all.pz)
        
        total_taus = len(taus_pt)
        logger.info(f"Analyzing {total_taus} raw tau particles from all events...")
        
        # Create histograms
        try:
            # pT distribution
            counts, bin_edges = compute_histogram_data(taus_pt, bins=100, bin_edge_min=0, bin_edge_max=500)
            save_png(
                output_dir,
                "raw_all_taus_pt",
                "All Raw Tau Particles: pT Distribution",
                taus_pt,
                bin_edges,
                r"$p_T(\tau)$ [GeV]",
                "Tau count",
            )
            logger.info("✓ Saved raw tau pT histogram")
        except Exception as e:
            logger.error(f"Failed to save raw tau pT histogram: {str(e)}")
        
        try:
            # eta distribution
            counts, bin_edges = compute_histogram_data(taus_eta, bins=100, bin_edge_min=-10, bin_edge_max=10)
            save_png(
                output_dir,
                "raw_all_taus_eta",
                "All Raw Tau Particles: η Distribution",
                taus_eta,
                bin_edges,
                r"$\eta(\tau)$",
                "Tau count",
            )
            logger.info("✓ Saved raw tau eta histogram")
        except Exception as e:
            logger.error(f"Failed to save raw tau eta histogram: {str(e)}")
        
        try:
            # phi distribution
            counts, bin_edges = compute_histogram_data(taus_phi, bins=100, bin_edge_min=-3.2, bin_edge_max=3.2)
            save_png(
                output_dir,
                "raw_all_taus_phi",
                "All Raw Tau Particles: φ Distribution",
                taus_phi,
                bin_edges,
                r"$\phi(\tau)$ [rad]",
                "Tau count",
            )
            logger.info("✓ Saved raw tau phi histogram")
        except Exception as e:
            logger.error(f"Failed to save raw tau phi histogram: {str(e)}")
        
        try:
            # pz distribution
            counts, bin_edges = compute_histogram_data(taus_pz, bins=100, bin_edge_min=-500, bin_edge_max=500)
            save_png(
                output_dir,
                "raw_all_taus_pz",
                "All Raw Tau Particles: pz Distribution",
                taus_pz,
                bin_edges,
                r"$p_z(\tau)$ [GeV]",
                "Tau count",
            )
            logger.info("✓ Saved raw tau pz histogram")
        except Exception as e:
            logger.error(f"Failed to save raw tau pz histogram: {str(e)}")
        
        logger.info(f"✓ Completed raw tau analysis for {total_taus} particles")
        
    except Exception as e:
        error_msg = f"Error in make_raw_all_tau_histograms: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


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
    
def save_raw_tau_pt_distribution(output_dir: Path, lhe_parts):
    """
    Plot the raw transverse momentum (pt) distribution directly
    from the awkward-array particle collection before Lorentz
    vector construction.

    Args:
        output_dir: Directory where the histogram will be saved
        lhe_parts: LHE particle collection (lhe_selected.LHEPart)

    Returns:
        Tuple of (histogram_name, title, counts, bin_edges)

    Raises:
        RuntimeError: If histogram creation fails
    """
    try:
        
        tau_minus = lhe_parts[lhe_parts.pdgId == 15]
        tau_plus = lhe_parts[lhe_parts.pdgId == -15]
        
        # Extract raw pt values
        raw_pt_minus = ak.flatten(tau_minus.pt)
        raw_pt_plus = ak.flatten(tau_plus.pt)

        # Combine both tau species into one distribution
        raw_pt = ak.to_numpy(
            ak.concatenate([raw_pt_minus, raw_pt_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            raw_pt,
            bins=200,
            bin_edge_min=0,
            bin_edge_max=250
        )

        # Save histogram image
        save_png(
            output_dir,
            "raw_tau_pt",
            "Raw Tau Transverse Momentum Distribution",
            raw_pt,
            bin_edges,
            r"$p_{T}(\tau)$ [GeV]",
            "Events",
        )

        return (
            "raw_tau_pt",
            "Raw Tau Transverse Momentum Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save raw tau pt histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_raw_tau_eta_distribution(output_dir: Path, lhe_parts):
    """
    Plot the raw pseudorapidity (eta) distribution directly
    from the awkward-array particle collection before Lorentz
    vector construction.

    Args:
        output_dir: Directory where the histogram will be saved
        lhe_parts: LHE particle collection (lhe_selected.LHEPart)
    Returns:        Tuple of (histogram_name, title, counts, bin_edges)
    Raises:        RuntimeError: If histogram creation fails
    """
    try:
        tau_minus = lhe_parts[lhe_parts.pdgId == 15]
        tau_plus = lhe_parts[lhe_parts.pdgId == -15]
        
        # Extract raw eta values
        raw_eta_minus = ak.flatten(tau_minus.eta)
        raw_eta_plus = ak.flatten(tau_plus.eta)

        # Combine both tau species into one distribution
        raw_eta = ak.to_numpy(
            ak.concatenate([raw_eta_minus, raw_eta_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            raw_eta,
            bins=200,
            bin_edge_min=-10,
            bin_edge_max=10
        )

        # Save histogram image
        save_png(
            output_dir,
            "raw_tau_eta",
            "Raw Tau Pseudorapidity Distribution",
            raw_eta,
            bin_edges,
            r"$\eta(\tau)$",
            "Events",
        )

        return (
            "raw_tau_eta",
            "Raw Tau Pseudorapidity Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save raw tau eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_raw_tau_phi_distribution(output_dir: Path, lhe_parts):
    """
    Plot the raw azimuthal angle (phi) distribution directly
    from the awkward-array particle collection before Lorentz
    vector construction.

    Args:
        output_dir: Directory where the histogram will be saved
        lhe_parts: LHE particle collection (lhe_selected.LHEPart)
    Returns:        Tuple of (histogram_name, title, counts, bin_edges)
    Raises:        RuntimeError: If histogram creation fails
    """
    try:
        tau_minus = lhe_parts[lhe_parts.pdgId == 15]
        tau_plus = lhe_parts[lhe_parts.pdgId == -15]
        
        # Extract raw phi values
        raw_phi_minus = ak.flatten(tau_minus.phi)
        raw_phi_plus = ak.flatten(tau_plus.phi)

        # Combine both tau species into one distribution
        raw_phi = ak.to_numpy(
            ak.concatenate([raw_phi_minus, raw_phi_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            raw_phi,
            bins=200,
            bin_edge_min=-3.2,
            bin_edge_max=3.2
        )

        # Save histogram image
        save_png(
            output_dir,
            "raw_tau_phi",
            "Raw Tau Azimuthal Angle Distribution",
            raw_phi,
            bin_edges,
            r"$\phi(\tau)$ [rad]",
            "Events",
        )

        return (
            "raw_tau_phi",
            "Raw Tau Azimuthal Angle Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save raw tau phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
def save_raw_tau_pz_distribution(output_dir: Path, lhe_parts):
    """
    Plot the raw longitudinal momentum (pz) distribution directly
    from the awkward-array particle collection before Lorentz
    vector construction.

    Args:
        output_dir: Directory where the histogram will be saved
        lhe_parts: LHE particle collection (lhe_selected.LHEPart)
    Returns:        Tuple of (histogram_name, title, counts, bin_edges)
    Raises:        RuntimeError: If histogram creation fails
    """
    try:
        tau_minus = lhe_parts[lhe_parts.pdgId == 15]
        tau_plus = lhe_parts[lhe_parts.pdgId == -15]
        
        # Extract raw pz values
        raw_pz_minus = ak.flatten(tau_minus.pz)
        raw_pz_plus = ak.flatten(tau_plus.pz)

        # Combine both tau species into one distribution
        raw_pz = ak.to_numpy(
            ak.concatenate([raw_pz_minus, raw_pz_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            raw_pz,
            bins=200,
            bin_edge_min=-2000,
            bin_edge_max=2000
        )

        # Save histogram image
        save_png(
            output_dir,
            "raw_tau_pz",
            "Raw Tau Longitudinal Momentum Distribution",
            raw_pz,
            bin_edges,
            r"$p_{z}(\tau)$ [GeV]",
            "Events",
        )

        return (
            "raw_tau_pz",
            "Raw Tau Longitudinal Momentum Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save raw tau pz histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
  

def make_raw_tau_histograms(output_dir: Path, lhe_taus):
    """
    Create and save histograms for raw tau kinematic distributions
    directly from the LHE particle collection before Lorentz vector construction.
    
    Args:
        output_dir: Directory to save histograms
        lhe_taus: LHE particle collection (lhe_selected.LHEPart)
    Raises:        RuntimeError: If histogram creation or saving fails
    """    
    try:
        save_raw_tau_pt_distribution(output_dir, lhe_taus)
        save_raw_tau_eta_distribution(output_dir, lhe_taus)
        save_raw_tau_phi_distribution(output_dir, lhe_taus)
        save_raw_tau_pz_distribution(output_dir, lhe_taus)
    except Exception as e:
        error_msg = f"Unexpected error in make_raw_tau_histograms: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e        

def make_pair_tau_histograms_lhe(output_dir: Path, lhe_selected):
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
        validate_lhe_events(lhe_selected)
        
        lhe_minus_lv, lhe_plus_lv = build_tau_vectors(
             lhe_selected.LHEPart,
             lhe_selected.LHEPart.pdgId == 15,
             lhe_selected.LHEPart.pdgId == -15)
        
        
        # for all pairs (candidates for mother particle / Z')
        save_lhe_mass_histogram(output_dir, (lhe_minus_lv + lhe_plus_lv).mass)
        save_lhe_phi_histogram_by_default_method(output_dir, (lhe_minus_lv + lhe_plus_lv).phi)
        save_lhe_histogram_pt(output_dir, (lhe_minus_lv + lhe_plus_lv).pt)
        save_lhe_histogram_pz(output_dir, (lhe_minus_lv + lhe_plus_lv).pz)
        save_lhe_histogram_etha(output_dir, (lhe_minus_lv + lhe_plus_lv).eta)
        
        
        # for lepton pairs (tau- vs tau+)
        save_lhe_delta_phi_lepton_pair_histogram(output_dir, lhe_minus_lv, lhe_plus_lv)
        save_lhe_delta_eta_lepton_pair_histogram(output_dir, lhe_minus_lv, lhe_plus_lv)
        
        # Check for Z' candidates: analyze invariant mass distribution with visualization
        # check_zprime_candidates((lhe_minus_lv + lhe_plus_lv).mass, output_dir=output_dir, mass_threshold_range=(100, 5000))
        
    except ValueError as e:
        logger.error(f"\n{str(e)}")
        raise ValueError(str(e)) from e
    except RuntimeError as e:
        logger.error(f"\n{str(e)}")
        raise RuntimeError(str(e)) from e
    except Exception as e:
        error_msg = f"Unexpected error in make_pair_tau_histograms_lhe: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
  