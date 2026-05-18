import logging

import awkward as ak

## logger takes the name of file in this case (selection.py)
logger = logging.getLogger(__name__)


def select_lhe_tau_pairs(events):
    """
    SELECT LHE TAU PAIRS (LAYER 1: PARTON LEVEL)
    
    This is the THEORETICAL/GENERATOR level before parton shower.
    LHE = Les Houches Event (parton-level representation)
    
    WHAT IT DOES:
    - Counts tau (pdgId=-15) and anti-tau (pdgId=15) in LHEPart collection
    - Requires exactly 1 tau + 1 anti-tau per event
    - This is the "truth" before any shower/radiation effects
    
    Args:
        events: NanoEvents object with LHEPart collection
        
    Returns:
        Tuple of (selected_events)
        
    Raises:
        AttributeError: If LHEPart not found
        RuntimeError: If selection fails
    """
    # Validate LHEPart exists
    if "LHEPart" not in events.fields:
        available = list(events.fields)
        error_msg = (
            f"\n[ERROR] LHEPart not found. Available: {available}\n"
            f"Ensure ROOT file contains LHEPart (parton-level particles).\n"
        )
        logger.error(error_msg)
        raise AttributeError(error_msg)
    
    try:
        pdg_lhe = events.LHEPart.pdgId

        #TODO to ask Hadjiiska if this is correct tau and anti-tau definition

        # axis=1 garantees we count taus per event (not globally)
        n_tau = ak.sum(pdg_lhe == -15, axis=1)      
        n_antitau = ak.sum(pdg_lhe == 15, axis=1)
        
        lhe_mask = (n_tau == 1) & (n_antitau == 1)
        lhe_selected = events[lhe_mask]
        lhe_mask_np = ak.to_numpy(lhe_mask)
        
        n_selected = ak.sum(lhe_mask)
        
        if n_selected == 0:
            logger.warning("⚠ Warning: No events passed LHE selection!")
            
        return lhe_selected
        
    except Exception as e:
        error_msg = (
            f"\n[ERROR] LHE tau pair selection failed.\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def load_tau_pairs(events):
    """
    Load tau pairs from LHEPart collections.
    """    
    if events is None:
        error_msg = "\n[ERROR] Cannot process None events object\n"
        logger.error(error_msg)
        raise ValueError(error_msg)
    try:
        n_events = len(events)
        if n_events == 0:
            error_msg = "\n[ERROR] Input events collection is empty\n"
            logger.error(error_msg)
            raise ValueError(error_msg)
    except TypeError as e:
        error_msg = (
            f"\n[ERROR] Cannot determine event count.\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    lhe_selected = select_lhe_tau_pairs(events)
    return lhe_selected


