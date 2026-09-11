"""
GenVisTau counterpart of tau_pog_mass_2d.py.

Reconstructs the Z' candidate mass the same way as genvistau_zprime_mass.py
does for h_my_zPrime_GenVisMass (missing 4-vector with pz=0, E=|pT_miss|,
i.e. Eq. 1 of arXiv:2412.04357), but restricted to events that actually
contain a tau AND an anti-tau, then fills a 2D histogram of that mass vs
the leading GenVisTau's pT -- same idea as tau_pog_mass_2d.py, one level
up in the simulation chain (truth-level visible taus instead of
reconstructed ones).
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

gvt = events.GenVisTau

# only events that contain at least one tau (charge < 0) AND one
# anti-tau (charge > 0) among their GenVisTau
has_tau = ak.any(gvt.charge < 0, axis=1)
has_antitau = ak.any(gvt.charge > 0, axis=1)
gvt = gvt[has_tau & has_antitau]
print(f"{ak.sum(has_tau & has_antitau)} events with a tau and an anti-tau")

# every opposite-sign GenVisTau pair in each remaining event
pairs = ak.combinations(gvt, 2, axis=1)
tau1, tau2 = ak.unzip(pairs)
os_mask = (tau1.charge * tau2.charge) == -1
tau1, tau2 = tau1[os_mask], tau2[os_mask]
print(f"{ak.sum(ak.num(tau1))} opposite-sign GenVisTau pairs")

# missing momentum: opposite of the two visible taus' combined pT, pz=0
# -- same construction as h_my_zPrime_GenVisMass in genvistau_zprime_mass.py
miss_px = -(tau1.px + tau2.px)
miss_py = -(tau1.py + tau2.py)
miss_pt = np.sqrt(miss_px**2 + miss_py**2)

missing = ak.zip(
    {
        "px": miss_px,
        "py": miss_py,
        "pz": ak.zeros_like(miss_pt),
        "energy": miss_pt,
    },
    with_name="PtEtaPhiMLorentzVector",
)

zPrime = tau1 + tau2 + missing
mass = zPrime.mass

# pT of the leading (bigger) GenVisTau of the pair
lead_pt = np.maximum(tau1.pt, tau2.pt)

h2 = hist.Hist(
    hist.axis.Regular(100, 0.0, 500.0, name="mass", label="m(tau tau) [GeV], pz_miss=0"),
    hist.axis.Regular(100, 0.0, 500.0, name="leadpt", label="leading GenVisTau p_{T} [GeV]"),
)
h2.fill(mass=ak.flatten(mass), leadpt=ak.flatten(lead_pt))

pathlib.Path("outputs").mkdir(exist_ok=True)
out_file = "outputs/genvistau_mass_2d.root"
with uproot.recreate(out_file) as f_out:
    f_out["h2_mass_vs_leadpt"] = h2

print(f"wrote {out_file}")
print('to view with only "Entries" in the stat box, in ROOT run:')
print('  gStyle->SetOptStat("e"); h2_mass_vs_leadpt->Draw("COLZ");')
