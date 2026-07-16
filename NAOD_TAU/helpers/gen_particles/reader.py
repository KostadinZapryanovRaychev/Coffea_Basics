import logging

import awkward as ak


logger = logging.getLogger(__name__)


def get_genpart_collection(events):
    """Return the GenPart collection after validating that it exists."""
    if events is None:
        error_msg = "\n[ERROR] Cannot read GenPart from a None events object\n"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if "GenPart" not in events.fields:
        available = list(events.fields)
        error_msg = (
            f"\n[ERROR] GenPart not found. Available: {available}\n"
            "Ensure the input NanoAOD file contains generator particles.\n"
        )
        logger.error(error_msg)
        raise AttributeError(error_msg)

    return events.GenPart


def select_gen_tau_pairs(events):
    """Select events with exactly one tau and one anti-tau in GenPart."""
    genpart = get_genpart_collection(events)
    pdg_ids = genpart.pdgId

    n_tau_minus = ak.sum(pdg_ids == 15, axis=1)
    n_tau_plus = ak.sum(pdg_ids == -15, axis=1)

    gen_mask = (n_tau_minus == 1) & (n_tau_plus == 1)
    gen_selected = events[gen_mask]

    n_selected = ak.sum(gen_mask)
    if n_selected == 0:
        logger.warning("⚠ Warning: No events passed GenPart tau selection!")

    return gen_selected


def load_gen_tau_pairs(events):
    """Validate input and load GenPart tau pairs."""
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

    return select_gen_tau_pairs(events)
