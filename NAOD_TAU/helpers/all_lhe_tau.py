from pathlib import Path
import logging
import numpy as np
import awkward as ak
from .root_writer import save_lhe_histograms_root
from .image_processing import save_png , compute_histogram_data


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
            counts, bin_edges = compute_histogram_data(taus_pt, bins=1000, bin_edge_min=0, bin_edge_max=500)
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
            counts, bin_edges = compute_histogram_data(taus_eta, bins=1000, bin_edge_min=-5, bin_edge_max=5)
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
            counts, bin_edges = compute_histogram_data(taus_phi, bins=1000, bin_edge_min=-3.2, bin_edge_max=3.2)
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
            counts, bin_edges = compute_histogram_data(taus_rapidity, bins=1000, bin_edge_min=-5, bin_edge_max=5)
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
            counts, bin_edges = compute_histogram_data(taus_pz, bins=1000, bin_edge_min=-500, bin_edge_max=500)
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