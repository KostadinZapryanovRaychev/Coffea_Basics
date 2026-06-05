from pathlib import Path
import logging
import numpy as np
from .root_writer import save_lhe_histograms_root
from .validation import  validate_lhe_events
from .vector_builder import build_tau_vectors

from .plotting import (
    get_mass_his,
    get_tau_pt_his,
    get_anti_tau_pt_his,
    get_tau_pz_his,
    get_anti_tau_pz_his,
    get_tau_eta_his,
    get_anti_tau_eta_his,
    get_tau_phi_his,
    get_anti_tau_phi_his,
    get_delta_phi_ditau_difference_his,
    get_delta_eta_ditau_difference_his,
    get_cos_delta_phi_his,
    get_delta_r_ditau_difference_his,
    get_delta_r_vs_delta_phi_2d_his

)


logger = logging.getLogger(__name__)


def make_lhe_ditau_histograms(output_dir: Path, lhe_selected, mass_point: str = "unknown"):
    """
    Create and save histograms for LHE-selected tau pairs.
    Saves all histograms to a single combined ROOT file.
    
    Args:
        output_dir: Directory to save histograms
        lhe_selected: NanoEvents with LHE-selected tau pairs
        mass_point: Mass point string (e.g., "500", "750") for histogram titles
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
        
        # Calculate statistics for plots
        num_events = len(lhe_selected)
        num_tau_minus = len(lhe_minus_lv)
        num_tau_plus = len(lhe_plus_lv)
        num_tau_pairs = min(num_tau_minus, num_tau_plus)
        
        histogram_specs = []
        histogram_specs.append(get_mass_his(output_dir, (lhe_minus_lv + lhe_plus_lv).mass, mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_tau_pt_his(output_dir, lhe_minus_lv.pt, mass_point, num_events=num_events, num_particles=num_tau_minus))
        histogram_specs.append(get_anti_tau_pt_his(output_dir, lhe_plus_lv.pt, mass_point, num_events=num_events, num_particles=num_tau_plus))
        histogram_specs.append(get_tau_pz_his(output_dir, lhe_minus_lv.pz, mass_point, num_events=num_events, num_particles=num_tau_minus))
        histogram_specs.append(get_anti_tau_pz_his(output_dir, lhe_plus_lv.pz, mass_point, num_events=num_events, num_particles=num_tau_plus))
        histogram_specs.append(get_tau_eta_his(output_dir, lhe_minus_lv.eta, mass_point, num_events=num_events, num_particles=num_tau_minus))
        histogram_specs.append(get_anti_tau_eta_his(output_dir, lhe_plus_lv.eta, mass_point, num_events=num_events, num_particles=num_tau_plus))
        histogram_specs.append(get_tau_phi_his(output_dir, lhe_minus_lv.phi, mass_point, num_events=num_events, num_particles=num_tau_minus))
        histogram_specs.append(get_anti_tau_phi_his(output_dir, lhe_plus_lv.phi, mass_point, num_events=num_events, num_particles=num_tau_plus))

        histogram_specs.append(get_delta_phi_ditau_difference_his(output_dir, (lhe_minus_lv.phi - lhe_plus_lv.phi), mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_cos_delta_phi_his(output_dir, (lhe_minus_lv.phi - lhe_plus_lv.phi), mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_delta_eta_ditau_difference_his(output_dir, lhe_minus_lv, lhe_plus_lv, mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_delta_r_ditau_difference_his(output_dir, lhe_minus_lv, lhe_plus_lv, mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_delta_r_vs_delta_phi_2d_his(output_dir, lhe_minus_lv, lhe_plus_lv, mass_point, num_events=num_events, num_particles=num_tau_pairs))
        
        save_lhe_histograms_root(output_dir, "tau_pair_histograms", histogram_specs)
        
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
  