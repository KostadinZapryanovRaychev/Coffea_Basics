import numpy as np


def compute_invariant_mass(a, b):
    return (a + b).mass


def compute_px(a):
    return a.pt * np.cos(a.phi)


def compute_py(a):
    return a.pt * np.sin(a.phi)


def compute_pz(a):
    return a.pt * np.sinh(a.eta)


def compute_energy(a):
    return np.sqrt(compute_px(a) ** 2 + compute_py(a) ** 2 + compute_pz(a) ** 2 + a.mass ** 2)


def compute_missing_pt(a, b):
    px = compute_px(a) + compute_px(b)
    py = compute_py(a) + compute_py(b)
    return np.sqrt(px ** 2 + py ** 2)


def compute_invariant_mass_neutrino_corrected(a, b):
    energy = compute_energy(a) + compute_energy(b) + compute_missing_pt(a, b)
    pz = compute_pz(a) + compute_pz(b)
    return np.sqrt(np.maximum(0.0, energy ** 2 - pz ** 2))


def compute_invariant_mass_formula(a, b):
    energy = compute_energy(a) + compute_energy(b)
    px = compute_px(a) + compute_px(b)
    py = compute_py(a) + compute_py(b)
    pz = compute_pz(a) + compute_pz(b)
    return np.sqrt(np.maximum(0.0, energy ** 2 - px ** 2 - py ** 2 - pz ** 2))
