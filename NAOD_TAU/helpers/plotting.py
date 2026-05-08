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


def make_all_tau_histograms(output_dir: Path, events):
    """
    Create and save histograms for ALL tau particles in the dataset.
    
    Analyzes the complete LHEPart collection BEFORE any pair selection.
    This shows the tau kinematic distributions across all events.
    Saves all histograms to a single combined ROOT file.
    
    Args:
        output_dir: Directory to save histograms
        events: NanoEvents object with LHEPart collection (all events, no selection)
        
    Raises:
        RuntimeError: If histogram creation fails
    """
    try:
        # Get all tau and anti-tau particles from LHEPart
        if "LHEPart" not in events.fields:
            logger.warning("⚠ LHEPart not found, skipping tau histograms")
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
        
        # Calculate rapidity: y = 0.5 * ln((E + pz) / (E - pz))
        # where E = sqrt(p_total^2 + m_tau^2), p_total = sqrt(pt^2 + pz^2)
        m_tau = 1.777  # tau mass in GeV
        p_total = np.sqrt(taus_pt**2 + taus_pz**2)
        energy = np.sqrt(p_total**2 + m_tau**2)
        # Avoid division by zero and log of negative/zero by adding small epsilon
        taus_rapidity = 0.5 * np.log((energy + taus_pz) / (energy - taus_pz))
        
        total_taus = len(taus_pt)
        logger.info(f"Analyzing {total_taus} tau particles from all events...")
        
        # Collect histogram specs
        histogram_specs = []
        
        try:
            # pT distribution
            counts, bin_edges = compute_histogram_data(taus_pt, bins=100, bin_edge_min=0, bin_edge_max=500)
            save_png(
                output_dir,
                "all_taus_pt",
                "All Tau Particles: pT Distribution",
                taus_pt,
                bin_edges,
                r"$p_T(\tau)$ [GeV]",
                "Tau count",
            )
            histogram_specs.append(("all_taus_pt", "All Tau Particles: pT Distribution", counts, bin_edges))
            logger.info("✓ Saved tau pT histogram")
        except Exception as e:
            logger.error(f"Failed to save tau pT histogram: {str(e)}")
        
        try:
            # eta distribution
            counts, bin_edges = compute_histogram_data(taus_eta, bins=100, bin_edge_min=-10, bin_edge_max=10)
            save_png(
                output_dir,
                "all_taus_eta",
                "All  Tau Particles: η Distribution",
                taus_eta,
                bin_edges,
                r"$\eta(\tau)$",
                "Tau count",
            )
            histogram_specs.append(("all_taus_eta", "All Tau Particles: η Distribution", counts, bin_edges))
            logger.info("✓ Saved tau eta histogram")
        except Exception as e:
            logger.error(f"Failed to save tau eta histogram: {str(e)}")
        
        try:
            # phi distribution
            counts, bin_edges = compute_histogram_data(taus_phi, bins=100, bin_edge_min=-3.2, bin_edge_max=3.2)
            save_png(
                output_dir,
                "all_taus_phi",
                "All Tau Particles: φ Distribution",
                taus_phi,
                bin_edges,
                r"$\phi(\tau)$ [rad]",
                "Tau count",
            )
            histogram_specs.append(("all_taus_phi", "All Tau Particles: φ Distribution", counts, bin_edges))
            logger.info("✓ Saved tau phi histogram")
        except Exception as e:
            logger.error(f"Failed to save tau phi histogram: {str(e)}")
        
        try:
            # rapidity distribution
            counts, bin_edges = compute_histogram_data(taus_rapidity, bins=100, bin_edge_min=-5, bin_edge_max=5)
            save_png(
                output_dir,
                "all_taus_rapidity",
                "All Tau Particles: Rapidity Distribution",
                taus_rapidity,
                bin_edges,
                r"$y(\tau)$",
                "Tau count",
            )
            histogram_specs.append(("all_taus_rapidity", "All Tau Particles: Rapidity Distribution", counts, bin_edges))
            logger.info("✓ Saved tau rapidity histogram")
        except Exception as e:
            logger.error(f"Failed to save tau rapidity histogram: {str(e)}")

        try:
            # pz distribution
            counts, bin_edges = compute_histogram_data(taus_pz, bins=100, bin_edge_min=-500, bin_edge_max=500)
            save_png(
                output_dir,
                "all_taus_pz",
                "All Tau Particles: pz Distribution",
                taus_pz,
                bin_edges,
                r"$p_z(\tau)$ [GeV]",
                "Tau count",
            )
            histogram_specs.append(("all_taus_pz", "All Tau Particles: pz Distribution", counts, bin_edges))
            logger.info("✓ Saved tau pz histogram")
        except Exception as e:
            logger.error(f"Failed to save tau pz histogram: {str(e)}")
        
        # Save all histograms to combined ROOT file
        if histogram_specs:
            save_lhe_histograms_root(output_dir, "all_taus", histogram_specs)
            logger.info(f"✓ Saved combined ROOT file with {len(histogram_specs)} tau histograms")
        
        logger.info(f"✓ Completed tau analysis for {total_taus} particles")
        
    except Exception as e:
        error_msg = f"Error in make_all_tau_histograms: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def compute_histogram_data(values, bins , bin_edge_min=None, bin_edge_max=None):
    """
    Compute histogram bin edges and counts from values.
    
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
    
def save_tau_pt_distribution(output_dir: Path, lhe_parts):
    """
    Plot the transverse momentum (pt) distribution directly
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
        
        # Extract pt values
        pt_minus = ak.flatten(tau_minus.pt)
        pt_plus = ak.flatten(tau_plus.pt)

        # Combine both tau species into one distribution
        pt = ak.to_numpy(
            ak.concatenate([pt_minus, pt_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            pt,
            bins=200,
            bin_edge_min=0,
            bin_edge_max=250
        )

        # Save histogram image
        save_png(
            output_dir,
            "tau_pt",
            "Tau Transverse Momentum Distribution",
            pt,
            bin_edges,
            r"$p_{T}(\tau)$ [GeV]",
            "Events",
        )

        return (
            "tau_pt",
            "Tau Transverse Momentum Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save tau pt histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_tau_eta_distribution(output_dir: Path, lhe_parts):
    """
    Plot the pseudorapidity (eta) distribution directly
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
        
        # Extract eta values
        eta_minus = ak.flatten(tau_minus.eta)
        eta_plus = ak.flatten(tau_plus.eta)

        # Combine both tau species into one distribution
        eta = ak.to_numpy(
            ak.concatenate([eta_minus, eta_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            eta,
            bins=200,
            bin_edge_min=-10,
            bin_edge_max=10
        )

        # Save histogram image
        save_png(
            output_dir,
            "tau_eta",
            "Tau Pseudorapidity Distribution",
            eta,
            bin_edges,
            r"$\eta(\tau)$",
            "Events",
        )

        return (
            "tau_eta",
            "Tau Pseudorapidity Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save tau eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_tau_phi_distribution(output_dir: Path, lhe_parts):
    """
    Plot the azimuthal angle (phi) distribution directly
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
        
        # Extract phi values
        phi_minus = ak.flatten(tau_minus.phi)
        phi_plus = ak.flatten(tau_plus.phi)

        # Combine both tau species into one distribution
        phi = ak.to_numpy(
            ak.concatenate([phi_minus, phi_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            phi,
            bins=200,
            bin_edge_min=-3.2,
            bin_edge_max=3.2
        )

        # Save histogram image
        save_png(
            output_dir,
            "tau_phi",
            "Tau Azimuthal Angle Distribution",
            phi,
            bin_edges,
            r"$\phi(\tau)$ [rad]",
            "Events",
        )

        return (
            "tau_phi",
            "Tau Azimuthal Angle Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save tau phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_tau_pz_distribution(output_dir: Path, lhe_parts):
    """
    Plot the longitudinal momentum (pz) distribution directly
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
        
        # Extract pz values
        pz_minus = ak.flatten(tau_minus.pz)
        pz_plus = ak.flatten(tau_plus.pz)

        # Combine both tau species into one distribution
        pz = ak.to_numpy(
            ak.concatenate([pz_minus, pz_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            pz,
            bins=200,
            bin_edge_min=-2000,
            bin_edge_max=2000
        )

        # Save histogram image
        save_png(
            output_dir,
            "tau_pz",
            "Tau Longitudinal Momentum Distribution",
            pz,
            bin_edges,
            r"$p_{z}(\tau)$ [GeV]",
            "Events",
        )

        return (
            "tau_pz",
            "Tau Longitudinal Momentum Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save tau pz histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_tau_rapidity_distribution(output_dir: Path, lhe_parts):
    """
    Plot the rapidity distribution directly
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
        
        # Extract rapidity values
        rapidity_minus = ak.flatten(tau_minus.rapidity)
        rapidity_plus = ak.flatten(tau_plus.rapidity)

        # Combine both tau species into one distribution
        rapidity = ak.to_numpy(
            ak.concatenate([rapidity_minus, rapidity_plus])
        )

        # Compute histogram
        counts, bin_edges = compute_histogram_data(
            rapidity,
            bins=200,
            bin_edge_min=-10,
            bin_edge_max=10
        )

        # Save histogram image
        save_png(
            output_dir,
            "tau_rapidity",
            "Tau Rapidity Distribution",
            rapidity,
            bin_edges,
            r"Rapidity $y(\tau)$",
            "Events",
        )

        return (
            "tau_rapidity",
            "Tau Rapidity Distribution",
            counts,
            bin_edges,
        )

    except Exception as e:
        error_msg = f"Failed to save tau rapidity histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def make_tau_histograms(output_dir: Path, lhe_taus):
    """
    Create and save histograms for tau kinematic distributions
    directly from the LHE particle collection before Lorentz vector construction.
    
    Args:
        output_dir: Directory to save histograms
        lhe_taus: LHE particle collection (lhe_selected.LHEPart)
    Raises:        RuntimeError: If histogram creation or saving fails
    """    
    try:
        save_tau_pt_distribution(output_dir, lhe_taus)
        save_tau_eta_distribution(output_dir, lhe_taus)
        save_tau_phi_distribution(output_dir, lhe_taus)
        save_tau_pz_distribution(output_dir, lhe_taus)
        save_tau_rapidity_distribution(output_dir, lhe_taus)
        # rapidity is calculated in make_all_tau_histograms() instead
    except Exception as e:
        error_msg = f"Unexpected error in make_tau_histograms: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e        

def make_pair_tau_histograms_lhe(output_dir: Path, lhe_selected):
    """
    Create and save histograms for LHE-selected tau pairs.
    Saves all histograms to a single combined ROOT file.
    
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
        
        # Inspect first 5 lhe_plus_lv entries
        # print(f"\n=== COMBINED LORENTZ VECTORS (first 5) ===")
        # print(lhe_minus_lv[0])
        # print(lhe_plus_lv[0])
        # Lorentz vectors are created successfully
        # print(f"===========================================\n")

        # Collect all histogram specs
        histogram_specs = []
        
        # for all pairs (candidates for mother particle / Z')
        histogram_specs.append(save_lhe_mass_histogram(output_dir, (lhe_minus_lv + lhe_plus_lv).mass))
        histogram_specs.append(save_lhe_phi_histogram_by_default_method(output_dir, (lhe_minus_lv + lhe_plus_lv).phi))

        histogram_specs.append(save_lhe_histogram_pt(output_dir, (lhe_minus_lv + lhe_plus_lv).pt))
        histogram_specs.append(save_lhe_histogram_pz(output_dir, (lhe_minus_lv + lhe_plus_lv).pz))
        histogram_specs.append(save_lhe_histogram_etha(output_dir, (lhe_minus_lv + lhe_plus_lv).eta))
        # Calculate rapidity from energy and pz: y = 0.5 * ln((E + pz) / (E - pz))
        combined_vec = lhe_minus_lv + lhe_plus_lv
        combined_rapidity = 0.5 * np.log((combined_vec.energy + combined_vec.pz) / (combined_vec.energy - combined_vec.pz))
        histogram_specs.append(save_lhe_histogram_rapidity(output_dir, combined_rapidity))
        #TODO to ask what is rapidity
        
        histogram_specs.append(save_lhe_delta_phi_lepton_pair_histogram(output_dir, lhe_minus_lv, lhe_plus_lv))
        histogram_specs.append(save_lhe_delta_eta_lepton_pair_histogram(output_dir, lhe_minus_lv, lhe_plus_lv))
        histogram_specs.append(save_lhe_delta_phi_pair_histogram(output_dir, lhe_minus_lv.phi - lhe_plus_lv.phi))
        
        # Save all histograms to combined ROOT file
        save_lhe_histograms_root(output_dir, "tau_pair_histograms", histogram_specs)
        logger.info(f"✓ Saved combined ROOT file with {len(histogram_specs)} tau pair histograms")
        
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
  