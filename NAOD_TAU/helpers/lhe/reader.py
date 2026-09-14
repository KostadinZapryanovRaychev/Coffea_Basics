import awkward as ak


def get_lhepart_collection(events):
    return events.LHEPart


def select_lhe_tau_pairs(events):
    lhepart = get_lhepart_collection(events)
    pdg_ids = lhepart.pdgId

    n_tau_minus = ak.sum(pdg_ids == 15, axis=1)
    n_tau_plus = ak.sum(pdg_ids == -15, axis=1)

    lhe_mask = (n_tau_minus == 1) & (n_tau_plus == 1)
    return events[lhe_mask]
