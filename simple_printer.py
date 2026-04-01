import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

import uproot
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from pathlib import Path

fn = Path(__file__).resolve().parent / "nano_dy.root"

print("\n" + "="*80)
print("ROOT FILE DATA (uproot)")
print("="*80 + "\n")

# with uproot.open(fn) as f:
#     tree = f['Events']
#     raw = tree.arrays(['Muon_pt', 'Muon_eta', 'Muon_phi', 'Muon_charge'], 
#                       entry_start=0, entry_stop=10, library='np')
#     print(raw)

print("\n" + "="*80)
print("COFFEA DATA (NanoEvents)")
print("="*80 + "\n")

events = NanoEventsFactory.from_root({str(fn): "Events"}, schemaclass=NanoAODSchema).events()
muons = events.Muon
print(events.Muon)
