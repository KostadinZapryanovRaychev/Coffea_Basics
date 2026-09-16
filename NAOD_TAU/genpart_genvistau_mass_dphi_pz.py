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

IS_LAST_COPY = 1 << 13


def make_histograms(mass_range, pz_range):
    h_mass = hist.Hist(
        hist.axis.Regular(100, *mass_range, name="mass", label="m(#tau#tau) [GeV]"),
    )
    h_mass_vs_cosdphi = hist.Hist(
        hist.axis.Regular(100, *mass_range, name="mass", label="m(#tau#tau) [GeV]"),
        hist.axis.Regular(100, -1.0, 1.0, name="cosdphi", label="cos(#Delta#phi)"),
    )
    h_pz_vs_cosdphi = hist.Hist(
        hist.axis.Regular(100, *pz_range, name="pz", label="p_{z}(#tau#tau) [GeV]"),
        hist.axis.Regular(100, -1.0, 1.0, name="cosdphi", label="cos(#Delta#phi)"),
    )
    return h_mass, h_mass_vs_cosdphi, h_pz_vs_cosdphi


def fill_from_pairs(p1, p2, h_mass, h_mass_vs_cosdphi, h_pz_vs_cosdphi):
    mass = (p1 + p2).mass
    cos_dphi = np.cos(p1.delta_phi(p2))
    pz = p1.pz + p2.pz

    flat_mass = ak.flatten(mass)
    flat_cos_dphi = ak.flatten(cos_dphi)
    flat_pz = ak.flatten(pz)

    h_mass.fill(mass=flat_mass)
    h_mass_vs_cosdphi.fill(mass=flat_mass, cosdphi=flat_cos_dphi)
    h_pz_vs_cosdphi.fill(pz=flat_pz, cosdphi=flat_cos_dphi)

    return ak.sum(ak.num(mass))


# ---- GenPart, last copy taus (pdgId == +-15) ----
gen_part = events.GenPart
last_copy_tau = gen_part[
    (np.abs(gen_part.pdgId) == 15) & ((gen_part.statusFlags & IS_LAST_COPY) != 0)
]

gp_pairs = ak.combinations(last_copy_tau, 2, axis=1)
gp1, gp2 = ak.unzip(gp_pairs)
gp_os_mask = (gp1.pdgId * gp2.pdgId) < 0
gp1, gp2 = gp1[gp_os_mask], gp2[gp_os_mask]

h_mass_genpart, h_mass_vs_cosdphi_genpart, h_pz_vs_cosdphi_genpart = make_histograms(
    (0.0, 300.0), (-500.0, 500.0)
)
n_genpart_pairs = fill_from_pairs(
    gp1, gp2, h_mass_genpart, h_mass_vs_cosdphi_genpart, h_pz_vs_cosdphi_genpart
)
print(f"{n_genpart_pairs} GenPart last-copy tau pairs")

# ---- GenVisTau (visible tau, neutrino excluded) ----
gen_vis_tau = events.GenVisTau

gv_pairs = ak.combinations(gen_vis_tau, 2, axis=1)
gv1, gv2 = ak.unzip(gv_pairs)
gv_os_mask = (gv1.charge * gv2.charge) < 0
gv1, gv2 = gv1[gv_os_mask], gv2[gv_os_mask]

h_mass_genvistau, h_mass_vs_cosdphi_genvistau, h_pz_vs_cosdphi_genvistau = make_histograms(
    (0.0, 300.0), (-500.0, 500.0)
)
n_genvistau_pairs = fill_from_pairs(
    gv1, gv2, h_mass_genvistau, h_mass_vs_cosdphi_genvistau, h_pz_vs_cosdphi_genvistau
)
print(f"{n_genvistau_pairs} GenVisTau pairs")

# ---- reconstructed Tau ----
events_reco = events[ak.num(events.Tau) >= 2]
reco_pairs = ak.combinations(events_reco.Tau, 2, axis=1)
t1, t2 = ak.unzip(reco_pairs)
t_os_mask = (t1.charge * t2.charge) < 0
t1, t2 = t1[t_os_mask], t2[t_os_mask]

h_mass_tau, h_mass_vs_cosdphi_tau, h_pz_vs_cosdphi_tau = make_histograms(
    (0.0, 300.0), (-500.0, 500.0)
)
n_tau_pairs = fill_from_pairs(t1, t2, h_mass_tau, h_mass_vs_cosdphi_tau, h_pz_vs_cosdphi_tau)
print(f"{n_tau_pairs} reconstructed Tau pairs")

pathlib.Path("outputs").mkdir(exist_ok=True)
out_file = "outputs/genpart_genvistau_mass_dphi_pz.root"
with uproot.recreate(out_file) as f_out:
    f_out["h_mass_genpart_lastcopy"] = h_mass_genpart
    f_out["h_mass_vs_cosdphi_genpart_lastcopy"] = h_mass_vs_cosdphi_genpart
    f_out["h_pz_vs_cosdphi_genpart_lastcopy"] = h_pz_vs_cosdphi_genpart

    f_out["h_mass_genvistau"] = h_mass_genvistau
    f_out["h_mass_vs_cosdphi_genvistau"] = h_mass_vs_cosdphi_genvistau
    f_out["h_pz_vs_cosdphi_genvistau"] = h_pz_vs_cosdphi_genvistau

    f_out["h_mass_tau"] = h_mass_tau
    f_out["h_mass_vs_cosdphi_tau"] = h_mass_vs_cosdphi_tau
    f_out["h_pz_vs_cosdphi_tau"] = h_pz_vs_cosdphi_tau

print(f"wrote {out_file}")
