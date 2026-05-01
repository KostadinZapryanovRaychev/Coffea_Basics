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
    - Counts tau (pdgId=15) and anti-tau (pdgId=-15) in LHEPart collection
    - Requires exactly 1 tau + 1 anti-tau per event
    - This is the "truth" before any shower/radiation effects
    
    LOGICAL POSITION IN PARTICLE CHAIN:
    LHE (Parton level) -> [Parton Shower] -> GenPart -> [Hadronization] -> Reco
                ↑ YOU ARE HERE
    
    Args:
        events: NanoEvents object with LHEPart collection
        
    Returns:
        Tuple of (selected_events, selection_mask_numpy)
        
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
        # Get PDG IDs from LHE particles
        pdg_lhe = events.LHEPart.pdgId
        
        # Count tau (15) and anti-tau (-15) per event
        n_tau = ak.sum(pdg_lhe == 15, axis=1)        # pdgId=+15
        n_antitau = ak.sum(pdg_lhe == -15, axis=1)   # pdgId=-15
        
        # Selection: exactly 1 tau + 1 anti-tau per event
        lhe_mask = (n_tau == 1) & (n_antitau == 1)
        lhe_selected = events[lhe_mask]
        lhe_mask_np = ak.to_numpy(lhe_mask)
        
        n_selected = ak.sum(lhe_mask)
        
        if n_selected == 0:
            logger.warning("⚠ Warning: No events passed LHE selection!")
            
        return lhe_selected, lhe_mask_np
        
    except Exception as e:
        error_msg = (
            f"\n[ERROR] LHE tau pair selection failed.\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def select_gen_tau_pairs(events, status_code=23):
    """
    SELECT GenPart TAU PAIRS (LAYER 2: GENERATOR LEVEL AFTER SHOWER)
    
    This is AFTER parton shower and radiation, but BEFORE hadronization.
    GenPart = all generator-level particles with status codes.
    
    WHAT IT DOES:
    - Counts tau and anti-tau in GenPart with specific status code
    - status=23: Hard process particles (outgoing from interaction)
    - Requires exactly 1 tau + 1 anti-tau per event
    
    LOGICAL POSITION IN PARTICLE CHAIN:
    LHE -> [Parton Shower] -> GenPart -> [Hadronization] -> Reco
                               ↑ YOU ARE HERE (after shower, before hadronization)
    
    COMMON STATUS CODES:
    - status=23: Hard process (primary outgoing particles)
    - status=1:  Stable final state (what actually reaches detector)
    - status=2:  Decayed particle
    
    Args:
        events: NanoEvents object with GenPart collection
        status_code: Integer status code to filter (default=23, hard process)
        
    Returns:
        Tuple of (selected_events, selection_mask_numpy) or (None, None) if GenPart missing
        
    Raises:
        RuntimeError: If GenPart selection fails
    """
    # Check if GenPart exists
    if "GenPart" not in events.fields:
        return None, None
    
    try:
        # Get PDG IDs and status from GenPart
        pdg_gen = events.GenPart.pdgId
        status_gen = events.GenPart.status
        
        # Count tau/anti-tau with matching status per event
        n_tau = ak.sum((pdg_gen == 15) & (status_gen == status_code), axis=1)
        n_antitau = ak.sum((pdg_gen == -15) & (status_gen == status_code), axis=1)
        
        # Selection: exactly 1 tau + 1 anti-tau per event
        gen_mask = (n_tau == 1) & (n_antitau == 1)
        gen_selected = events[gen_mask]
        gen_mask_np = ak.to_numpy(gen_mask)
        
        n_selected = ak.sum(gen_mask)
        
        if n_selected == 0:
            logger.warning("⚠ Warning: No events passed GenPart selection!")
            
        return gen_selected, gen_mask_np
        
    except Exception as e:
        logger.warning(
            f"⚠ GenPart selection failed (skipping):\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        return None, None


def load_tau_pairs(events):
    """
    ORCHESTRATOR FUNCTION - Calls all particle level selections
    
    This function coordinates the selection across all physics layers:
    
    WORKFLOW:
    1. Input validation
    2. Call LHE selection (LAYER 1: Parton level)
    3. Call GenPart selection (LAYER 2: Generator level after shower)
    4. Return results from all layers
    
    LOGICAL FLOW:
    
    Input Events
        ↓
    [LAYER 1: LHE Selection] ← Parton level, before shower
        ↓ Filtered events
    [LAYER 2: GenPart Selection] ← After shower, before hadronization  
        ↓ Filtered events
    Returned to caller for analysis
    
    Args:
        events: NanoEvents object containing LHEPart and optionally GenPart
        
    Returns:
        Tuple of (lhe_selected, gen_selected, lhe_mask_numpy):
        - lhe_selected: Events passing LHE tau pair selection
        - gen_selected: Events passing GenPart tau pair selection (or None)
        - lhe_mask_numpy: Boolean mask array of LHE selection
        
    Raises:
        ValueError: If input validation fails
        AttributeError: If LHEPart missing
    """
    # ========== INPUT VALIDATION ==========
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
    
    # ========== LAYER 1: LHE SELECTION ==========
    lhe_selected, lhe_mask_np = select_lhe_tau_pairs(events)
    
    # ========== LAYER 2: GenPart SELECTION (optional) ==========
    gen_selected, gen_mask_np = select_gen_tau_pairs(events, status_code=23)
    
    return lhe_selected, gen_selected, lhe_mask_np
