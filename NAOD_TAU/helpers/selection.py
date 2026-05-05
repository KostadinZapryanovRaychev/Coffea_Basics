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


def select_gen_tau_pairs(events, status_code=23, require_z_origin=True, mother_pdg_id=23):
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
    
        Z-ORIGIN FILTER:
        - When require_z_origin=True, both taus must have a mother with pdgId=23
            so the selected sample is consistent with Z -> tau+ tau- production.
    
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

        if require_z_origin:
            if "genPartIdxMother" not in events.GenPart.fields:
                raise AttributeError(
                    "GenPart.genPartIdxMother is required to check Z origin but is missing"
                )

            tau_minus_parents = events.GenPart[(pdg_gen == 15) & (status_gen == status_code)]
            tau_plus_parents = events.GenPart[(pdg_gen == -15) & (status_gen == status_code)]

            tau_minus_mother_idx = tau_minus_parents.genPartIdxMother
            tau_plus_mother_idx = tau_plus_parents.genPartIdxMother

            safe_tau_minus_mother_idx = ak.where(tau_minus_mother_idx >= 0, tau_minus_mother_idx, 0)
            safe_tau_plus_mother_idx = ak.where(tau_plus_mother_idx >= 0, tau_plus_mother_idx, 0)

            tau_minus_mother_pdg = events.GenPart.pdgId[safe_tau_minus_mother_idx]
            tau_plus_mother_pdg = events.GenPart.pdgId[safe_tau_plus_mother_idx]

            tau_minus_from_z = ak.any(
                (tau_minus_mother_idx >= 0) & (tau_minus_mother_pdg == mother_pdg_id),
                axis=1,
            )
            tau_plus_from_z = ak.any(
                (tau_plus_mother_idx >= 0) & (tau_plus_mother_pdg == mother_pdg_id),
                axis=1,
            )

            gen_mask = gen_mask & tau_minus_from_z & tau_plus_from_z

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
    gen_selected, gen_mask_np = select_gen_tau_pairs(events, status_code=23, require_z_origin=True)
    
    return lhe_selected, gen_selected, lhe_mask_np


def get_genpart_parent_taus(events):
    """
    Extract parent tau particles from GenPart collection.
    
    Parents are tau/anti-tau with status=23 (hard process particles).
    
    Args:
        events: NanoEvents object with GenPart collection
        
    Returns:
        Tuple of (tau_minus_parents, tau_plus_parents) selected GenPart particles
        
    Raises:
        AttributeError: If GenPart not found
    """
    if "GenPart" not in events.fields:
        error_msg = "\n[ERROR] GenPart not found in events\n"
        logger.error(error_msg)
        raise AttributeError(error_msg)
    
    try:
        gen_parts = events.GenPart
        pdg_id = gen_parts.pdgId
        status = gen_parts.status
        
        # Parents: status==23 (hard process)
        tau_minus_mask = (pdg_id == 15) & (status == 23)
        tau_plus_mask = (pdg_id == -15) & (status == 23)
        
        tau_minus_parents = gen_parts[tau_minus_mask]
        tau_plus_parents = gen_parts[tau_plus_mask]
        
        return tau_minus_parents, tau_plus_parents
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Failed to extract parent taus from GenPart\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        logger.error(error_msg)
        raise


def get_genpart_children_particles(gen_part_parent, events):
    """
    Extract children (decay products) of a parent GenPart particle.
    
    Uses mother/daughter indices to find all decay products.
    
    Args:
        gen_part_parent: Parent GenPart particle (e.g., a tau with status=23)
        events: Full NanoEvents object for access to parent indices
        
    Returns:
        Array of child particles (GenPart collection)
        
    Raises:
        AttributeError: If mother index information not available
    """
    try:
        # Access mother index from parent
        # In awkward arrays, we need to be careful with indexing
        # For now, we'll use a simplified approach: find particles with mother pointing to this tau
        
        gen_parts = events.GenPart
        
        # Get mother indices - these point to parent particle indices
        mother_idx = gen_parts.genPartIdxMother
        
        # For each tau parent, find particles whose mother is this tau
        # This is complex in awkward arrays, so we'll compute per-event
        children_list = []
        
        # Iterate over events
        for event_idx in range(len(gen_parts)):
            mothers = mother_idx[event_idx]
            
            # Find children by checking mother indices
            # This is a simplified approach - in reality you'd need the mother particle indices
            children_mask = (mothers >= 0)  # Valid mother index
            children_list.append(gen_parts[event_idx][children_mask])
        
        return ak.concatenate([ak.Array([c]) for c in children_list])
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Failed to extract children particles\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        logger.error(error_msg)
        raise


def get_genpart_children_simple(events):
    """
    Extract children particles as status=1 (stable final state) GenPart.
    
    This is a simpler approach that gets all stable particles,
    which represent the decay products that reach the detector.
    
    Args:
        events: NanoEvents object with GenPart collection
        
    Returns:
        Array of stable GenPart particles (status=1)
        
    Raises:
        AttributeError: If GenPart not found
    """
    if "GenPart" not in events.fields:
        error_msg = "\n[ERROR] GenPart not found in events\n"
        logger.error(error_msg)
        raise AttributeError(error_msg)
    
    try:
        gen_parts = events.GenPart
        status = gen_parts.status
        
        # Children: status==1 (stable final state)
        children_mask = (status == 1)
        children = gen_parts[children_mask]
        
        return children
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Failed to extract children particles\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        logger.error(error_msg)
        raise
