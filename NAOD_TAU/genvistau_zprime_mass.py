import json
import pathlib

import awkward as ak
import numpy as np
import hist
import matplotlib.pyplot as plt
import uproot

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

_WITHROOT = pathlib.Path(__file__).resolve().parent.parent / "WITHROOT"
_raw = json.loads((_WITHROOT / "config.json").read_text())["inputFile"]
fname = _raw if pathlib.Path(_raw).is_absolute() else str((_WITHROOT / _raw).resolve())

factory = NanoEventsFactory.from_root({fname: "Events"}, schemaclass=NanoAODSchema, mode="eager")

events = factory.events()

mynGenVisTau_counts = ak.num(events.GenVisTau)

print(mynGenVisTau_counts.to_list()[:10])
h_allGenVisTau = hist.Hist(hist.axis.Regular(10, 0., 10., name="allGenVisTaus", label=r"GenVis per event"))
h_allGenVisTau.fill(allGenVisTaus=mynGenVisTau_counts)
h_allGenVisTau.plot1d()
plt.ylabel("entries")
plt.clf()

gVT_pt_mask = events.GenVisTau.pt > 20

gVT_status_mask = (events.GenVisTau.status == 0) | (events.GenVisTau.status == 1) | (events.GenVisTau.status == 2) | (events.GenVisTau.status == 10) | (events.GenVisTau.status == 11)

good_GenVisTaus = events.GenVisTau[gVT_status_mask & gVT_pt_mask]

myGenVisTau_pairs = ak.combinations(good_GenVisTaus, 2, axis=1)
myGenVisTau_pairs_counts = ak.num(myGenVisTau_pairs)

h_allGenVisTauPairs = hist.Hist(hist.axis.Regular(10, 0., 10., name="allGenVisTauPairs", label=r"GenVis pairs per event"))
h_allGenVisTauPairs.fill(allGenVisTauPairs=myGenVisTau_pairs_counts)
h_allGenVisTauPairs.plot1d()
plt.ylabel("entries")
plt.clf()

genVisTau1, genVisTau2 = ak.unzip(myGenVisTau_pairs)

gVS_opposite_charge_mask = (genVisTau1.charge * genVisTau2.charge) == -1
genVisTau1 = genVisTau1[gVS_opposite_charge_mask]
genVisTau2 = genVisTau2[gVS_opposite_charge_mask]

genVisTau1_pt, genVisTau2_pt = genVisTau1.pt, genVisTau2.pt
genVisTau1_px, genVisTau2_px = genVisTau1.px, genVisTau2.px
genVisTau1_py, genVisTau2_py = genVisTau1.py, genVisTau2.py
genVisTau1_pz, genVisTau2_pz = genVisTau1.pz, genVisTau2.pz
genVisTau1_phi, genVisTau2_phi = genVisTau1.phi, genVisTau2.phi
genVisTau1_p, genVisTau2_p = genVisTau1.p, genVisTau2.p
genVisTau1_E, genVisTau2_E = genVisTau1.energy, genVisTau2.energy

total_visible_px = genVisTau1.px + genVisTau2.px
total_visible_py = genVisTau1.py + genVisTau2.py
total_visible_pz = genVisTau1.pz + genVisTau2.pz
myGenVisTauMiss_px = -1 * total_visible_px
myGenVisTauMiss_py = -1 * total_visible_py
myGenVisTauMiss_pz = -1 * total_visible_pz
myGenVisTauMiss_pt = np.sqrt(myGenVisTauMiss_px**2 + myGenVisTauMiss_py**2)
myGenVisTauMiss_phi = np.arctan2(myGenVisTauMiss_py, myGenVisTauMiss_px)
myGenVisTauMiss_p = np.sqrt(myGenVisTauMiss_pt**2 + myGenVisTauMiss_pz**2)

h_good_GenVisTaus_pt = hist.Hist(hist.axis.Regular(500, 0., 500., name="goodGenVisTaus", label=r"Good GenVis [GeV]"))
h_good_GenVisTaus_pt.fill(goodGenVisTaus=ak.flatten(good_GenVisTaus.pt))
h_good_GenVisTaus_pt.plot1d()
plt.ylabel("entries / 1 GeV")
plt.clf()

myGenVisTauMiss = ak.zip(
    {
        "px": myGenVisTauMiss_px,
        "py": myGenVisTauMiss_py,
        "pz": ak.zeros_like(myGenVisTauMiss_pz),
        "energy": myGenVisTauMiss_pt,
    },
    with_name="PtEtaPhiMLorentzVector",
)

zPrime_GenVisCand = genVisTau1 + genVisTau2 + myGenVisTauMiss

my_zPrime_GenVisMass = zPrime_GenVisCand.mass

h_my_zPrime_GenVisMass = hist.Hist(hist.axis.Regular(5000, 0., 5000., name="zPrime_GenVisMass", label=r" [GeV] no selection and pz=0"))
h_my_zPrime_GenVisMass.fill(zPrime_GenVisMass=ak.flatten(my_zPrime_GenVisMass))
h_my_zPrime_GenVisMass.plot1d()
plt.ylabel("events/1 GeV")
plt.clf()

myGenVisTauMissP = ak.zip(
    {
        "px": myGenVisTauMiss_px,
        "py": myGenVisTauMiss_py,
        "pz": myGenVisTauMiss_pz,
        "energy": myGenVisTauMiss_p,
    },
    with_name="PtEtaPhiMLorentzVector",
)

zPrime_GenVisCandP = genVisTau1 + genVisTau2 + myGenVisTauMissP

my_zPrime_GenVisMassP = zPrime_GenVisCandP.mass

h_my_zPrime_GenVisMassP = hist.Hist(hist.axis.Regular(5000, 0., 5000., name="zPrime_GenVisMassP", label=r" [GeV] no selection and pz!=0"))
h_my_zPrime_GenVisMassP.fill(zPrime_GenVisMassP=ak.flatten(my_zPrime_GenVisMassP))
h_my_zPrime_GenVisMassP.plot1d()
plt.ylabel("events/1 GeV")
plt.clf()

myGenPart_neutrinos = events.GenPart[(abs(events.GenPart.pdgId) == 12) | (abs(events.GenPart.pdgId) == 14) | (abs(events.GenPart.pdgId) == 16)]

met_p = ak.sum(myGenPart_neutrinos.p, axis=1)
met_px = ak.sum(myGenPart_neutrinos.px, axis=1)
met_py = ak.sum(myGenPart_neutrinos.py, axis=1)
met_pz = ak.sum(myGenPart_neutrinos.pz, axis=1)
met_pt = np.sqrt(met_px**2 + met_py**2)
met_phi = np.arctan2(met_py, met_px)
_, met_p_b = ak.broadcast_arrays(genVisTau1_p, met_p)
_, met_px_b = ak.broadcast_arrays(genVisTau1_px, met_px)
_, met_py_b = ak.broadcast_arrays(genVisTau1_py, met_py)
_, met_pz_b = ak.broadcast_arrays(genVisTau1_pz, met_pz)
_, met_pt_b = ak.broadcast_arrays(genVisTau1_pt, met_pt)
_, met_phi_b = ak.broadcast_arrays(genVisTau1_phi, met_phi)

myGenVisTauMissNeu = ak.zip(
    {
        "px": met_px_b,
        "py": met_py_b,
        "pz": met_pz_b,
        "energy": met_p_b,
    },
    with_name="PtEtaPhiMLorentzVector",
)

zPrime_GenVisCandNeu = genVisTau1 + genVisTau2 + myGenVisTauMissNeu

my_zPrime_GenVisMassNeu = zPrime_GenVisCandNeu.mass

h_my_zPrime_GenVisMassNeu = hist.Hist(hist.axis.Regular(5000, 0., 5000., name="zPrime_GenVisMassNeu", label=r" [GeV] no selection and neutrino"))
h_my_zPrime_GenVisMassNeu.fill(zPrime_GenVisMassNeu=ak.flatten(my_zPrime_GenVisMassNeu))
h_my_zPrime_GenVisMassNeu.plot1d()
plt.ylabel("events/1 GeV")
plt.clf()

pathlib.Path("myTestOut").mkdir(exist_ok=True)
with uproot.recreate("myTestOut/myGenVisTau_output.root") as f_out:
    f_out["myAnaFolder/h_allGenVisTau"] = h_allGenVisTau
    f_out["myAnaFolder/h_allGenVisTauPairs"] = h_allGenVisTauPairs
    f_out["myAnaFolder/h_good_GenVisTaus_pt"] = h_good_GenVisTaus_pt
    f_out["myAnaFolder/h_my_zPrime_GenVisMass"] = h_my_zPrime_GenVisMass
    f_out["myAnaFolder/h_my_zPrime_GenVisMassP"] = h_my_zPrime_GenVisMassP
    f_out["myAnaFolder/h_my_zPrime_GenVisMassNeu"] = h_my_zPrime_GenVisMassNeu
    print("saving h_allGenVisTau in output.root")
    print("saving h_allGenVisTauPairs in output.root")
    print("saving h_good_GenVisTaus_pt in output.root")
    print("saving h_my_zPrime_GenVisMass in output.root")
    print("saving h_my_zPrime_GenVisMassP in output.root")
    print("saving h_my_zPrime_GenVisMassNeu in output.root")
