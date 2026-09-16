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

events = events[ak.num(events.Tau) >= 2]
print(f"{len(events)} events with >= 2 taus")

pairs = ak.combinations(events.Tau, 2, axis=1)
tau1, tau2 = ak.unzip(pairs)
os_mask = (tau1.charge * tau2.charge) == -1
tau1, tau2 = tau1[os_mask], tau2[os_mask]

ditau_mass = (tau1 + tau2).mass

dphi = tau1.delta_phi(tau2)
cos_dphi = np.cos(dphi)

ditau_pz = tau1.pz + tau2.pz

n_pairs = ak.sum(ak.num(ditau_mass))
print(f"{n_pairs} opposite-sign tau pairs")

flat_mass = ak.flatten(ditau_mass)
flat_cos_dphi = ak.flatten(cos_dphi)
flat_pz = ak.flatten(ditau_pz)

h_mass = hist.Hist(
    hist.axis.Regular(100, 0.0, 300.0, name="mass", label="m(#tau#tau) [GeV]"),
)
h_mass.fill(mass=flat_mass)

h_mass_vs_cosdphi = hist.Hist(
    hist.axis.Regular(100, 0.0, 300.0, name="mass", label="m(#tau#tau) [GeV]"),
    hist.axis.Regular(100, -1.0, 1.0, name="cosdphi", label="cos(#Delta#phi)"),
)
h_mass_vs_cosdphi.fill(mass=flat_mass, cosdphi=flat_cos_dphi)

h_pz_vs_cosdphi = hist.Hist(
    hist.axis.Regular(100, -500.0, 500.0, name="pz", label="p_{z}(#tau#tau) [GeV]"),
    hist.axis.Regular(100, -1.0, 1.0, name="cosdphi", label="cos(#Delta#phi)"),
)
h_pz_vs_cosdphi.fill(pz=flat_pz, cosdphi=flat_cos_dphi)

pathlib.Path("outputs").mkdir(exist_ok=True)
out_file = "outputs/tau_mass_dphi_pz.root"
with uproot.recreate(out_file) as f_out:
    f_out["h_mass_tau"] = h_mass
    f_out["h_mass_vs_cosdphi_tau"] = h_mass_vs_cosdphi
    f_out["h_pz_vs_cosdphi_tau"] = h_pz_vs_cosdphi

print(f"wrote {out_file}")
