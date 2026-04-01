import uproot
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from pathlib import Path

fn = Path(__file__).resolve().parent / "nano_dy.root"

print("\n" + "="*80)
print("ROOT FILE DATA (uproot)")
print("="*80 + "\n")

with uproot.open(fn) as f:
    tree = f['Events']
    raw = tree.arrays(['Muon_pt', 'Muon_eta', 'Muon_phi', 'Muon_charge'], 
                      entry_start=0, entry_stop=10, library='np')
    
    for evt_idx in range(10):
        nmu = len(raw['Muon_pt'][evt_idx])
        if nmu > 0:
            print(f"Event {evt_idx}:")
            print(f"  pt:     {raw['Muon_pt'][evt_idx]}")
            print(f"  eta:    {raw['Muon_eta'][evt_idx]}")
            print(f"  phi:    {raw['Muon_phi'][evt_idx]}")
            print(f"  charge: {raw['Muon_charge'][evt_idx]}")

print("\n" + "="*80)
print("COFFEA DATA (NanoEvents)")
print("="*80 + "\n")

events = NanoEventsFactory.from_root({str(fn): "Events"}, schemaclass=NanoAODSchema).events()
muons = events.Muon

for evt_idx in range(10):
    nmu = len(muons[evt_idx])
    if nmu > 0:
        print(f"Event {evt_idx}:")
        print(f"  pt:     {ak.to_numpy(muons[evt_idx].pt)}")
        print(f"  eta:    {ak.to_numpy(muons[evt_idx].eta)}")
        print(f"  phi:    {ak.to_numpy(muons[evt_idx].phi)}")
        print(f"  charge: {ak.to_numpy(muons[evt_idx].charge)}")
