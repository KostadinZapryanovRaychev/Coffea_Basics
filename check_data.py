import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

import uproot
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from pathlib import Path

fn = Path(__file__).resolve().parent / "nano_dy.root"

print("\n" + "="*80)
print("ROOT FILE DATA (uproot) - FIRST 10 EVENTS")
print("="*80 + "\n")

with uproot.open(fn) as f:
    tree = f['Events']
    raw = tree.arrays(['Muon_pt', 'Muon_eta', 'Muon_phi', 'Muon_charge'], 
                      entry_start=0, entry_stop=10, library='np')
    
    for evt in range(10):
        n_muons = len(raw['Muon_pt'][evt])
        print(f"Event {evt}: {n_muons} muons")
        if n_muons > 0:
            print(f"  pt:     {raw['Muon_pt'][evt]}")
            print(f"  eta:    {raw['Muon_eta'][evt]}")
            print(f"  phi:    {raw['Muon_phi'][evt]}")
            print(f"  charge: {raw['Muon_charge'][evt]}")
        print()

print("\n" + "="*80)
print("COFFEA DATA (NanoEvents) - FIRST 10 EVENTS")
print("="*80 + "\n")

events = NanoEventsFactory.from_root({str(fn): "Events"}, schemaclass=NanoAODSchema).events()
muons = events.Muon

for evt in range(10):
    n_muons = len(muons[evt])
    print(f"Event {evt}: {n_muons} muons")
    if n_muons > 0:
        print(f"  pt:     {ak.to_numpy(muons[evt].pt)}")
        print(f"  eta:    {ak.to_numpy(muons[evt].eta)}")
        print(f"  phi:    {ak.to_numpy(muons[evt].phi)}")
        print(f"  charge: {ak.to_numpy(muons[evt].charge)}")
    print()
