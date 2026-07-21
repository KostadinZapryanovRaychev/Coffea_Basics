import logging

import awkward as ak

logger = logging.getLogger(__name__)



def select_deep_tau_vse(events, working_point=1):
    """
    SELECT RECONSTRUCTED TAUS USING DEEPTAU VSe ID

    Uses the reconstructed Tau collection and selects taus passing
    the requested DeepTau2018v2p5 electron-rejection working point.

    Working points:
        1 = VVVLoose
        2 = VVLoose
        3 = VLoose
        4 = Loose
        5 = Medium
        6 = Tight
        7 = VTight
        8 = VVTight

    Args:
        events: NanoEvents object with Tau collection.
        working_point: Minimum DeepTau VSe working point.

    Returns:
        Awkward Array of selected taus.

    Raises:
        AttributeError: If Tau collection or DeepTau branch is missing.
        RuntimeError: If selection fails.
    """

    if "Tau" not in events.fields:
        available = list(events.fields)
        error_msg = (
            f"\n[ERROR] Tau collection not found. Available: {available}\n"
        )
        logger.error(error_msg)
        raise AttributeError(error_msg)

    try:
        taus = events.Tau

        if "idDeepTau2018v2p5VSe" not in taus.fields:
            error_msg = (
                "\n[ERROR] Tau.idDeepTau2018v2p5VSe not found.\n"
            )
            logger.error(error_msg)
            raise AttributeError(error_msg)
            # Select taus passing the requested working point
        deep_tau_mask = taus.idDeepTau2018v2p5VSe >= working_point
        selected_taus = taus[deep_tau_mask]

            # Number of selected taus per event
        n_selected_per_event = ak.num(selected_taus, axis=1)

            # Separate events
        events_with_2taus = selected_taus[n_selected_per_event == 2]
        events_with_1tau = selected_taus[n_selected_per_event == 1]

        logger.info(
                f"Events with exactly 2 selected taus: {len(events_with_2taus)}"
        )
        logger.info(
                f"Events with exactly 1 selected tau: {len(events_with_1tau)}"
        )

        print("\n========== FIRST 20 EVENTS WITH 2 TAUS ==========")
        for i, tau in enumerate(events_with_2taus[:20]):
                print(
                    f"Event {i:2d}: "
                    f"pt=({tau.pt[0]:7.2f}, {tau.pt[1]:7.2f}) "
                    f"eta=({tau.eta[0]:6.2f}, {tau.eta[1]:6.2f}) "
                    f"phi=({tau.phi[0]:6.2f}, {tau.phi[1]:6.2f}) "
                    f"DeepTau={list(tau.idDeepTau2018v2p5VSe)}"
                )

        print("\n========== FIRST 20 EVENTS WITH 1 TAU ==========")
        for i, tau in enumerate(events_with_1tau[:20]):
                print(
                    f"Event {i:2d}: "
                    f"pt={tau.pt[0]:7.2f} "
                    f"eta={tau.eta[0]:6.2f} "
                    f"phi={tau.phi[0]:6.2f} "
                    f"DeepTau={tau.idDeepTau2018v2p5VSe[0]}"
                )
        return selected_taus

    except Exception as e:
        error_msg = (
            f"\n[ERROR] DeepTau VSe selection failed.\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e



def load_taus(events):
    """
    LOAD ALL RECONSTRUCTED TAUS (RECO LEVEL)

    Loads the full Tau collection from NanoEvents.
    No selection is applied.

    Args:
        events: NanoEvents object with Tau collection

    Returns:
        events.Tau

    Raises:
        AttributeError: If Tau collection is missing
        RuntimeError: If loading fails
    """

    # Validate Tau exists
    if "Tau" not in events.fields:
        available = list(events.fields)
        error_msg = (
            f"\n[ERROR] Tau collection not found. Available: {available}\n"
            f"Ensure ROOT file contains Tau objects.\n"
        )
        logger.error(error_msg)
        raise AttributeError(error_msg)

    try:
        taus = events.Tau

        logger.info(
            f"Loaded Tau collection with {len(taus)} events"
        )

        return taus

    except Exception as e:
        error_msg = (
            f"\n[ERROR] Loading Tau collection failed.\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


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





