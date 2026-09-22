"""
coffea ProcessorABC version of reco_tau_mass.py / mc_reco_tau_mass.py.

Same selection, same three mass histograms, but run through
coffea.processor.Runner instead of a hand-rolled loop over
file_config.json's entries. The two scripts existed only because data
and MC each had their own config file and output file; here that's
just two entries ("data", "mc") in one fileset dict, and the dataset
name becomes an axis on each histogram (see MuonProcessor in the
coffea docs: https://coffea-hep.readthedocs.io/en/latest/getting_started/index.html),
so run_mass_processor.py gets both sets of histograms from one run.
"""

import awkward as ak
import hist
from coffea import processor

from NAOD_TAU.helpers.tau_collections.reader import get_tau_collection
from NAOD_TAU.helpers.mass import (
    compute_invariant_mass,
    compute_invariant_mass_formula,
    compute_invariant_mass_neutrino_corrected,
)
from NAOD_TAU.helpers.lhe.angles import compute_delta_phi
from NAOD_TAU.helpers.kinematics import compute_pz, compute_delta_r, compute_cos_delta_phi
from NAOD_TAU.reco_tau_mass import (
    select_events_with_two_taus,
    select_leading_tau_pair,
    select_opposite_sign_pairs,
    select_back_to_back_pairs,
    select_kinematic_pairs,
)

HIST_SPECS = {
    "mass": (100, 0, 500),
    "mass_formula": (100, 0, 500),
    "mass_formula_neutrino": (100, 0, 500),
    "pz": (100, -500, 500),
    "delta_r": (64, 0, 6),
    "cos_delta_phi": (100, -1, 1),
    "eta": (60, -2.3, 2.3),
}


def make_histograms():
    histograms = {}
    for name, (bins, low, high) in HIST_SPECS.items():
        histograms[name] = (
            hist.Hist.new.StrCat([], growth=True, name="dataset")
            .Reg(bins, low, high, name=name)
            .Weight()
        )
    return histograms


class MassProcessor(processor.ProcessorABC):
    """Reconstructed-Tau mass + kinematics, same cuts as reco_tau_mass.py."""

    def process(self, events):
        dataset = events.metadata["dataset"]

        taus = select_events_with_two_taus(get_tau_collection(events))
        tau, antitau = select_leading_tau_pair(taus)
        tau, antitau = select_opposite_sign_pairs(tau, antitau)
        tau, antitau = select_back_to_back_pairs(tau, antitau)
        tau, antitau = select_kinematic_pairs(tau, antitau)

        delta_phi = compute_delta_phi(tau, antitau)

        values = {
            "mass": compute_invariant_mass(tau, antitau),
            "mass_formula": compute_invariant_mass_formula(tau, antitau),
            "mass_formula_neutrino": compute_invariant_mass_neutrino_corrected(tau, antitau),
            "pz": compute_pz(tau, antitau),
            "delta_r": compute_delta_r(tau, antitau),
            "cos_delta_phi": compute_cos_delta_phi(delta_phi),
            "eta": ak.concatenate([tau.eta, antitau.eta]),
        }

        histograms = make_histograms()
        for name, hist_obj in histograms.items():
            hist_obj.fill(dataset=dataset, **{name: values[name]})

        return {
            "histograms": histograms,
            "good_pairs": {dataset: len(tau)},
        }

    def postprocess(self, accumulator):
        return accumulator
