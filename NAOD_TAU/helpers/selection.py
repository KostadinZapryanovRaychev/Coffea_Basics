import logging

import awkward as ak


logger = logging.getLogger(__name__)


def load_tau_pairs(events):
    """
    Filter events to select tau pairs from LHE and GenPart collections.
    
    Selects events with exactly 1 tau (pdgId==15) and 1 anti-tau (pdgId==-15).
    For GenPart, additionally requires status==23 (hard process particles).
    
    Args:
        events: NanoEvents object containing LHEPart and optionally GenPart
        
    Returns:
        Tuple of:
        - lhe_selected: Filtered events with valid LHE tau pairs
        - gen_selected: Filtered events with valid GenPart tau pairs (or None)
        - lhe_mask_np: NumPy boolean array of LHE selection mask
        
    Raises:
        ValueError: If events is None or empty
        AttributeError: If LHEPart collection not found in events
        RuntimeError: If tau pair selection fails due to data issues
    """
    # Validate input
    if events is None:
        error_msg = "\n[ERROR] Cannot process None events object\n"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        n_events = len(events)
        if n_events == 0:
            error_msg = "\n[ERROR] Input events collection is empty (0 events)\n"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info(f"Processing {n_events} input events")
    except TypeError as e:
        error_msg = (
            f"\n[ERROR] Cannot determine event count. Events object may be invalid.\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    
    # Validate LHEPart collection exists
    if "LHEPart" not in events.fields:
        available = list(events.fields)
        error_msg = (
            f"\n[ERROR] LHEPart collection not found in ROOT file.\n"
            f"  Available collections: {available}\n"
            f"  Ensure ROOT file contains LHEPart particles (hard process particles).\n"
        )
        logger.error(error_msg)
        raise AttributeError(error_msg)
    
    # Select LHE tau pairs
    try:
        logger.info("Selecting LHE tau pairs (exactly 1 tau + 1 anti-tau)...")
        pdg_lhe = events.LHEPart.pdgId
        n_minus = ak.sum(pdg_lhe == 15, axis=1)    # Count tau particles
        n_plus = ak.sum(pdg_lhe == -15, axis=1)    # Count anti-tau particles
        lhe_mask = (n_minus == 1) & (n_plus == 1)  # Exactly one pair per event
        lhe_selected = events[lhe_mask]
        lhe_mask_np = ak.to_numpy(lhe_mask)
        
        n_lhe_selected = ak.sum(lhe_mask)
        logger.info(f"Selected {n_lhe_selected} events with valid LHE tau pairs (from {n_events} total)")
        
        if n_lhe_selected == 0:
            logger.warning("⚠ Warning: No events selected with LHE tau pairs. Analysis may be empty.")
    except Exception as e:
        error_msg = (
            f"\n[ERROR] LHE tau pair selection failed.\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
            f"  Check LHEPart collection structure and pdgId availability.\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    # Try to select GenPart tau pairs (optional)
    gen_selected = None
    if "GenPart" in events.fields:
        try:
            logger.info("GenPart found. Selecting GenPart tau pairs (status==23 hard process)...")
            pdg_gen = events.GenPart.pdgId
            status_gen = events.GenPart.status
            n_minus_g = ak.sum((pdg_gen == 15) & (status_gen == 23), axis=1)
            n_plus_g = ak.sum((pdg_gen == -15) & (status_gen == 23), axis=1)
            gen_mask = (n_minus_g == 1) & (n_plus_g == 1)
            gen_selected = events[gen_mask]
            
            n_gen_selected = ak.sum(gen_mask)
            logger.info(f"Selected {n_gen_selected} events with valid GenPart tau pairs")
            
            if n_gen_selected == 0:
                logger.warning("⚠ Warning: No events selected with GenPart tau pairs. Overlay plots will be empty.")
        except Exception as e:
            logger.warning(
                f"⚠ GenPart tau pair selection failed (will skip GenPart analysis):\n"
                f"  Exception type: {type(e).__name__}\n"
                f"  Details: {str(e)}\n"
            )
            gen_selected = None
    else:
        logger.info("GenPart collection not found. Will create LHE-only histograms.")
    
    return lhe_selected, gen_selected, lhe_mask_np
