import awkward as ak


def load_tau_pairs(events):
    """Return (lhe_selected, gen_selected_or_None, event_mask_numpy)."""
    if "LHEPart" not in events.fields:
        raise AttributeError("LHEPart collection not found in this ROOT file")

    pdg_lhe = events.LHEPart.pdgId
    n_minus = ak.sum(pdg_lhe == 15, axis=1)
    n_plus = ak.sum(pdg_lhe == -15, axis=1)
    lhe_mask = (n_minus == 1) & (n_plus == 1)
    lhe_selected = events[lhe_mask]
    lhe_mask_np = ak.to_numpy(lhe_mask)

    gen_selected = None
    if "GenPart" in events.fields:
        pdg_gen = events.GenPart.pdgId
        status_gen = events.GenPart.status
        n_minus_g = ak.sum((pdg_gen == 15) & (status_gen == 23), axis=1)
        n_plus_g = ak.sum((pdg_gen == -15) & (status_gen == 23), axis=1)
        gen_mask = (n_minus_g == 1) & (n_plus_g == 1)
        gen_selected = events[gen_mask]

    return lhe_selected, gen_selected, lhe_mask_np
