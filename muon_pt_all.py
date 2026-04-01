import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

# Absolute path
fn = "/Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea/nano_dy.root"

print(f"Reading file: {fn}\n")
print("="*80)
print("ALL MUON pT VALUES")
print("="*80 + "\n")

# Load events
events = NanoEventsFactory.from_root(
    {str(fn): "Events"},
    schemaclass=NanoAODSchema
).events()

muons = events.Muon

# Print all muon pT values with event info
for evt_idx in range(len(events)):
    n_muons = len(muons[evt_idx])
    if n_muons > 0:
        pt_values = ak.to_numpy(muons[evt_idx].pt)
        print(f"Event {evt_idx}: {n_muons} muon(s)")
        for muon_idx, pt in enumerate(pt_values):
            print(f"  Muon {muon_idx}: pT = {pt:.3f} GeV")
        print()

# Print summary
print("="*80)
print("SUMMARY")
print("="*80)
all_muon_pts = ak.flatten(muons.pt)
all_muon_pts_numpy = ak.to_numpy(all_muon_pts)

print(f"\nTotal muons: {len(all_muon_pts_numpy)}")
print(f"Min pT: {all_muon_pts_numpy.min():.3f} GeV")
print(f"Max pT: {all_muon_pts_numpy.max():.3f} GeV")
print(f"Mean pT: {all_muon_pts_numpy.mean():.3f} GeV")
print(f"\nAll muon pT values:\n{all_muon_pts_numpy}")
