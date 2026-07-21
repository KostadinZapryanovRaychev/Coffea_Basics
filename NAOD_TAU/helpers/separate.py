import logging

import awkward as ak

logger = logging.getLogger(__name__)

import numpy as np


def get_number_of_taus_per_event(events):
    """
    Count reconstructed taus per event and prepare histogram-ready data.

    Returns:
        dict containing:
            - event_index: Event indices
            - n_taus: Number of taus per event
            - histogram: Dictionary {n_taus: n_events}
    """

    if "Tau" not in events.fields:
        available = list(events.fields)
        raise AttributeError(
            f"\n[ERROR] Tau collection not found. Available: {available}\n"
        )

    n_taus = ak.to_numpy(ak.num(events.Tau, axis=1))

    event_index = np.arange(len(n_taus))

    unique, counts = np.unique(n_taus, return_counts=True)

    histogram = {
        int(n): int(c)
        for n, c in zip(unique, counts)
    }

    result = {
        "event_index": event_index,
        "n_taus": n_taus,
        "n_taus_per_event": n_taus,
        "histogram": histogram,
    }

    print("\n===== First 20 events =====")
    for evt, n in zip(event_index[:20], n_taus[:20]):
        print(f"Event {evt:5d}: {n} tau(s)")

    print("\n===== Tau multiplicity =====")
    for n, c in histogram.items():
        print(f"{n} tau(s): {c} events")

    return result