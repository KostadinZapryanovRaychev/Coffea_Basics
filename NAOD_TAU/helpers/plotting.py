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


def check_zprime_candidates(mass_values, output_dir: Path = None, mass_threshold_range=(100, 5000)):
    """
    Analyze invariant mass distribution to identify Z' (hypothetical mother particle) candidates.
    Creates a visualization of the mass distribution with Z' mass window highlighted.
    
    The simplest check: find the mass distribution peak and report statistics.
    A clear peak in the mass distribution indicates potential Z' decay events.
    
    Args:
        mass_values: Array of di-tau invariant mass values
        output_dir: Optional output directory to save Z' candidate plot (PNG)
        mass_threshold_range: Mass window (min, max) in GeV for Z' hypothesis. Default (100, 5000) GeV.
        
    Returns:
        Dictionary with Z' candidate analysis:
        {
            'total_events': int,
            'events_in_window': int,
            'window_percentage': float,
            'mass_mean': float,
            'mass_median': float,
            'mass_std': float,
            'mass_mode_bin': float (bin center with most events),
            'is_zprime_candidate': bool (True if >10% events in mass window)
        }
    """
    try:
        mass_array = np.asarray(mass_values, dtype=np.float64)
        mass_array = mass_array[np.isfinite(mass_array)]
        
        total = len(mass_array)
        if total == 0:
            return {
                'total_events': 0,
                'events_in_window': 0,
                'window_percentage': 0.0,
                'mass_mean': np.nan,
                'mass_median': np.nan,
                'mass_std': np.nan,
                'mass_mode_bin': np.nan,
                'is_zprime_candidate': False,
            }
        
        # Count events in mass window
        in_window = np.sum((mass_array >= mass_threshold_range[0]) & (mass_array <= mass_threshold_range[1]))
        window_pct = 100.0 * in_window / total if total > 0 else 0.0
        
        # Find mode (bin with most counts)
        counts, bin_edges = np.histogram(mass_array, bins=100)
        mode_bin_idx = np.argmax(counts)
        mode_mass = (bin_edges[mode_bin_idx] + bin_edges[mode_bin_idx + 1]) / 2.0
        
        result = {
            'total_events': int(total),
            'events_in_window': int(in_window),
            'window_percentage': float(window_pct),
            'mass_mean': float(np.mean(mass_array)),
            'mass_median': float(np.median(mass_array)),
            'mass_std': float(np.std(mass_array)),
            'mass_mode_bin': float(mode_mass),
            'is_zprime_candidate': bool(window_pct > 10.0),  # Heuristic: >10% in mass window suggests Z' signal
        }
        
        logger.info(
            f"\n[Z' CANDIDATE ANALYSIS]\n"
            f"  Total events: {result['total_events']}\n"
            f"  Events in window [{mass_threshold_range[0]}, {mass_threshold_range[1]}] GeV: {result['events_in_window']} ({result['window_percentage']:.1f}%)\n"
            f"  Mass mean: {result['mass_mean']:.1f} GeV | median: {result['mass_median']:.1f} GeV | std: {result['mass_std']:.1f} GeV\n"
            f"  Mass mode (peak): {result['mass_mode_bin']:.1f} GeV\n"
            f"  ✓ Z' CANDIDATE: {result['is_zprime_candidate']} (>10% signal in mass window)\n"
        )
        
        # Create Z' candidate visualization if output_dir provided
        if output_dir is not None:
            try:
                _plot_zprime_candidates(output_dir, mass_array, result, mass_threshold_range)
            except Exception as e:
                logger.warning(f"Could not create Z' candidate plot: {str(e)}")
        
        return result
    except Exception as e:
        logger.error(f"Error in check_zprime_candidates: {str(e)}")
        return {'is_zprime_candidate': False, 'error': str(e)}


def _plot_zprime_candidates(output_dir: Path, mass_array, result, mass_threshold_range):
    """
    Create a visualization of the invariant mass distribution for Z' candidates.
    Highlights the Z' mass window and shows peak/mean markers.
    
    Args:
        output_dir: Output directory to save the plot
        mass_array: Array of mass values
        result: Dictionary with analysis results from check_zprime_candidates
        mass_threshold_range: Mass window tuple (min, max) in GeV
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Create histogram
        counts, bin_edges, patches = ax.hist(
            mass_array, 
            bins=150, 
            histtype='stepfilled', 
            color='steelblue', 
            alpha=0.7,
            edgecolor='navy',
            linewidth=1.5,
            label='All events'
        )
        
        # Highlight Z' mass window
        for i, patch in enumerate(patches):
            bin_center = (bin_edges[i] + bin_edges[i+1]) / 2.0
            if mass_threshold_range[0] <= bin_center <= mass_threshold_range[1]:
                patch.set_facecolor('orangered')
                patch.set_alpha(0.8)
        
        # Add vertical lines for peak and mean
        ax.axvline(result['mass_mode_bin'], color='red', linestyle='--', linewidth=2.5, 
                   label=f"Peak: {result['mass_mode_bin']:.1f} GeV")
        ax.axvline(result['mass_mean'], color='green', linestyle='--', linewidth=2.5, 
                   label=f"Mean: {result['mass_mean']:.1f} GeV")
        
        # Shade the Z' window region
        ax.axvspan(mass_threshold_range[0], mass_threshold_range[1], alpha=0.15, color='orange', 
                   label=f"Z' window [{mass_threshold_range[0]}, {mass_threshold_range[1]}] GeV")
        
        # Add statistics text box
        zprime_status = "✓ Z' CANDIDATE" if result['is_zprime_candidate'] else "✗ No Z' signal"
        stats_text = (
            f"Z' Candidate Analysis\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Total events: {result['total_events']:,}\n"
            f"Events in window: {result['events_in_window']:,} ({result['window_percentage']:.1f}%)\n"
            f"Mean: {result['mass_mean']:.1f} ± {result['mass_std']:.1f} GeV\n"
            f"Median: {result['mass_median']:.1f} GeV\n"
            f"Mode: {result['mass_mode_bin']:.1f} GeV\n"
            f"\n{zprime_status}\n"
            f"(>10% in window)"
        )
        
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                family='monospace')
        
        # Formatting
        ax.set_xlabel(r"$m(\tau^{-}\tau^{+})$ [GeV]", fontsize=12, fontweight='bold')
        ax.set_ylabel("Events", fontsize=12, fontweight='bold')
        ax.set_title("Z' Candidate Analysis: Di-tau Invariant Mass Distribution", 
                     fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='upper left', fontsize=10, framealpha=0.95)
        ax.grid(True, linestyle='--', alpha=0.4)
        
        # Save figure
        zprime_plot_path = output_dir / "zprime_candidate_analysis.png"
        plt.tight_layout()
        plt.savefig(zprime_plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✓ Saved Z' candidate plot: {zprime_plot_path}")
        
    except Exception as e:
        logger.error(f"Error creating Z' candidate plot: {str(e)}")
        raise RuntimeError(f"Failed to create Z' candidate plot: {str(e)}") from e




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
        
        # Compute di-tau invariant mass for Z' candidate check
        ditau_mass = (lhe_minus_lv + lhe_plus_lv).mass
        
        # for all pairs (candidates for mother particle / Z')
        save_lhe_mass_histogram(output_dir, ditau_mass)
        save_lhe_phi_histogram_by_default_method(output_dir, (lhe_minus_lv + lhe_plus_lv).phi)
        save_lhe_histogram_pz(output_dir, (lhe_minus_lv + lhe_plus_lv).pz)
        save_lhe_histogram_pt(output_dir, (lhe_minus_lv + lhe_plus_lv).pt)
        save_lhe_histogram_etha(output_dir, (lhe_minus_lv + lhe_plus_lv).eta)
        
        # for lepton pairs (tau- vs tau+)
        save_lhe_delta_phi_lepton_pair_histogram(output_dir, lhe_minus_lv, lhe_plus_lv)
        save_lhe_delta_eta_lepton_pair_histogram(output_dir, lhe_minus_lv, lhe_plus_lv)
        
        # Check for Z' candidates: analyze invariant mass distribution with visualization
        check_zprime_candidates(ditau_mass, output_dir=output_dir, mass_threshold_range=(100, 5000))
        
    except ValueError as e:
        logger.error(f"\n{str(e)}")
        raise ValueError(str(e)) from e
    except RuntimeError as e:
        logger.error(f"\n{str(e)}")
        raise RuntimeError(str(e)) from e
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