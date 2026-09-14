from .reader import get_lhepart_collection


def get_lhe_tau(events):
    lhepart = get_lhepart_collection(events)
    return lhepart[lhepart.pdgId == 15][:, 0]


def get_lhe_antitau(events):
    lhepart = get_lhepart_collection(events)
    return lhepart[lhepart.pdgId == -15][:, 0]


def compute_ditau_mass(tau, antitau):
    return (tau + antitau).mass
