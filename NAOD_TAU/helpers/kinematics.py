import numpy as np


def compute_pz(a, b):
    return a.pz + b.pz


def compute_delta_r(a, b):
    return a.delta_r(b)


def compute_cos_delta_phi(delta_phi):
    return np.cos(delta_phi)
