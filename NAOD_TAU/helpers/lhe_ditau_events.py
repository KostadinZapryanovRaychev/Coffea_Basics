from pathlib import Path
import logging
import numpy as np
from .root_writer import save_lhe_histograms_root
from .validation import  validate_lhe_events
from .vector_builder import build_tau_vectors

from .plotting import (
    get_mass_his,
    get_parent_part_pt_his,
    get_parent_part_pz_his,

    save_lhe_phi_histogram_by_default_method,
    save_lhe_histogram_pz,
    save_lhe_histogram_eta,
    save_lhe_histogram_rapidity,
    save_lhe_delta_phi_lepton_pair_histogram,
    save_lhe_delta_eta_lepton_pair_histogram,
    save_lhe_delta_phi_pair_histogram,
)


logger = logging.getLogger(__name__)


def make_lhe_ditau_histograms(output_dir: Path, lhe_selected):
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
        histogram_specs.append(get_mass_his(output_dir, (lhe_minus_lv + lhe_plus_lv).mass))
        histogram_specs.append(get_parent_part_pt_his(output_dir, (lhe_minus_lv + lhe_plus_lv).pt))
        histogram_specs.append(get_parent_part_pz_his(output_dir, (lhe_minus_lv + lhe_plus_lv).pz))

        # histogram_specs.append(get_parent_part_phi_his(output_dir, (lhe_minus_lv + lhe_plus_lv).phi))
        # histogram_specs.append(save_lhe_histogram_eta(output_dir, (lhe_minus_lv + lhe_plus_lv).eta))
        # Calculate rapidity from energy and pz: y = 0.5 * ln((E + pz) / (E - pz))
        # combined_vec = lhe_minus_lv + lhe_plus_lv
        # combined_rapidity = 0.5 * np.log((combined_vec.energy + combined_vec.pz) / (combined_vec.energy - combined_vec.pz))
        # histogram_specs.append(save_lhe_histogram_rapidity(output_dir, combined_rapidity))
        #TODO to ask what is rapidity
        # histogram_specs.append(save_lhe_delta_phi_lepton_pair_histogram(output_dir, lhe_minus_lv, lhe_plus_lv))
        # histogram_specs.append(save_lhe_delta_eta_lepton_pair_histogram(output_dir, lhe_minus_lv, lhe_plus_lv))
        # histogram_specs.append(save_lhe_delta_phi_pair_histogram(output_dir, lhe_minus_lv.phi - lhe_plus_lv.phi))
        
        save_lhe_histograms_root(output_dir, "tau_pair_histograms", histogram_specs)
        logger.info(f"✓ Saved combined ROOT file with {len(histogram_specs)} tau pair histograms")
        
        
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
  