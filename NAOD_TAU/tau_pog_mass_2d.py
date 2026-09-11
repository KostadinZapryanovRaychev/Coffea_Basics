"""
Python/coffea counterpart of WITHROOT/TauPogMass.C's 2D histogram.

Same idea, same architecture (reads the input file from
WITHROOT/config.json, like genvistau_zprime_mass.py), but using coffea's
awkward-array way of doing it instead of the C++ TTreeReader loop:

  1. keep only events with >= 2 reconstructed taus (events.Tau)
  2. take every opposite-sign tau pair, compute its plain invariant mass
     (no neutrino correction -- same "visible mass" as TauPogMass.C)
  3. fill a 2D histogram: x = di-tau mass, y = pT of the leading
     (higher-pT) tau in the pair
"""

import json
import pathlib

import awkward as ak
import numpy as np
import hist
import uproot

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

_WITHROOT = pathlib.Path(__file__).resolve().parent.parent / "WITHROOT"
_raw = json.loads((_WITHROOT / "config.json").read_text())["inputFile"]
fname = _raw if pathlib.Path(_raw).is_absolute() else str((_WITHROOT / _raw).resolve())

factory = NanoEventsFactory.from_root({fname: "Events"}, schemaclass=NanoAODSchema, mode="eager")
events = factory.events()
print(f"{len(events)} events in file")

# 1) keep only events with >= 2 reconstructed taus
events = events[ak.num(events.Tau) >= 2]
print(f"{len(events)} events with >= 2 taus")

# every opposite-sign pair of taus in each remaining event
pairs = ak.combinations(events.Tau, 2, axis=1)
tau1, tau2 = ak.unzip(pairs)
os_mask = (tau1.charge * tau2.charge) == -1
tau1, tau2 = tau1[os_mask], tau2[os_mask]

# plain (visible) invariant mass -- coffea adds the two 4-vectors for you
ditau_mass = (tau1 + tau2).mass

# pT of the leading (bigger) tau of the pair
lead_pt = np.maximum(tau1.pt, tau2.pt)

n_pairs = ak.sum(ak.num(ditau_mass))
print(f"{n_pairs} opposite-sign tau pairs")

# 2) 2D histogram: mass (x) vs leading tau pT (y)
h2 = hist.Hist(
    hist.axis.Regular(100, 0.0, 300.0, name="mass", label="m(tau tau) [GeV]"),
    hist.axis.Regular(100, 0.0, 300.0, name="leadpt", label="leading tau p_{T} [GeV]"),
)
h2.fill(mass=ak.flatten(ditau_mass), leadpt=ak.flatten(lead_pt))

pathlib.Path("outputs").mkdir(exist_ok=True)
out_file = "outputs/tau_pog_mass_2d.root"
with uproot.recreate(out_file) as f_out:
    f_out["h2_mass_vs_leadpt"] = h2

print(f"wrote {out_file}")
