import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Disable warnings for missing cross references
NanoAODSchema.warn_missing_crossrefs = False

# Path setup
HERE = Path(__file__).resolve().parent
fname = HERE / "nano_dy.root"

# Ensure file exists
if not fname.exists():
    raise FileNotFoundError(f"{fname} not found")

print(f"Loading data from {fname}...")

# Load events using Coffea + NanoEvents
events = NanoEventsFactory.from_root(
    {str(fname): "Events"},
    schemaclass=NanoAODSchema,
    metadata={"dataset": "DYJets"},
).events()

print(f"Total number of events: {len(events)}")

if "Muon" not in events.fields:
    raise AttributeError("Muon branch not present in data")

events_with_2plus_muons = events[ak.num(events.Muon) >= 2]
print(f"Events with at least 2 muons: {len(events_with_2plus_muons)}")

num_muons_per_event = ak.num(events_with_2plus_muons.Muon)
print(f"\nDistribution of number of muons per event:")
unique_counts = np.unique(ak.to_numpy(num_muons_per_event), return_counts=True)
for n_muons, count in zip(unique_counts[0], unique_counts[1]):
    print(f"  {n_muons} muons: {count} events")

positive_muons = events_with_2plus_muons.Muon[events_with_2plus_muons.Muon.charge > 0]
negative_muons = events_with_2plus_muons.Muon[events_with_2plus_muons.Muon.charge < 0]

has_positive = ak.num(positive_muons) >= 1
has_negative = ak.num(negative_muons) >= 1
opposite_charge_mask = has_positive & has_negative

filtered_events = events_with_2plus_muons[opposite_charge_mask]
print(f"Events with at least 2 muons with opposite charges: {len(filtered_events)}")

num_muons_filtered = ak.num(filtered_events.Muon)
print(f"\nDistribution of number of muons per event (after opposite charge filter):")
unique_counts_filtered = np.unique(ak.to_numpy(num_muons_filtered), return_counts=True)
for n_muons, count in zip(unique_counts_filtered[0], unique_counts_filtered[1]):
    print(f"  {n_muons} muons: {count} events")

# Calculate delta Phi between the two muons in each event
muon1_phi = filtered_events.Muon[:, 0].phi
muon2_phi = filtered_events.Muon[:, 1].phi

# Calculate delta phi (difference in azimuthal angle)
delta_phi = muon1_phi - muon2_phi

# Normalize delta_phi to be in range [-pi, pi]
delta_phi = np.arctan2(np.sin(delta_phi), np.cos(delta_phi))

# Convert to numpy array
delta_phi_array = ak.to_numpy(delta_phi)

print(f"\nDelta Phi values for the {len(delta_phi_array)} events:")
for i, dphi in enumerate(delta_phi_array):
    print(f"  Event {i+1}: Δφ = {dphi:.3f} rad ({np.degrees(dphi):.1f}°)")

# Get pT values for both muons
muon1_pt = ak.to_numpy(filtered_events.Muon[:, 0].pt)
muon2_pt = ak.to_numpy(filtered_events.Muon[:, 1].pt)

# Create arrays for 2D histogram
# We'll have 2 points per event (one for each muon)
delta_phi_all = np.concatenate([delta_phi_array, delta_phi_array])
pt_all = np.concatenate([muon1_pt, muon2_pt])

print(f"\nCreating 2D histogram with {len(delta_phi_all)} data points...")

# Create 2D histogram
fig, ax = plt.subplots(figsize=(12, 8))

# Create the 2D histogram
hist = ax.hist2d(delta_phi_all, pt_all, 
                 bins=[20, 30], 
                 range=[[-np.pi, np.pi], [0, 100]],
                 cmap='viridis',
                 cmin=1)

# Add colorbar
cbar = plt.colorbar(hist[3], ax=ax)
cbar.set_label('Number of Muons', fontsize=12)

# Labels and title
ax.set_xlabel('Δφ between muons [rad]', fontsize=12)
ax.set_ylabel('Muon pT [GeV]', fontsize=12)
ax.set_title('2D Distribution: Muon pT vs Δφ\n(Events with ≥2 muons with opposite charges)', 
             fontsize=14, fontweight='bold')

# Add grid
ax.grid(True, alpha=0.3, linestyle='--')

# Add pi labels on x-axis
ax.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
ax.set_xticklabels(['-π', '-π/2', '0', 'π/2', 'π'])

plt.tight_layout()

# Save plot
outdir = HERE / "outputs"
outdir.mkdir(exist_ok=True)
outpath = outdir / "muon_pt_vs_delta_phi_2d.png"
plt.savefig(outpath, dpi=150)
print(f"\n2D Histogram saved to: {outpath}")

# Also create individual 1D histograms for delta phi
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Delta Phi histogram
ax1.hist(delta_phi_array, bins=20, range=(-np.pi, np.pi), 
         color='coral', alpha=0.7, edgecolor='black')
ax1.set_xlabel('Δφ between muons [rad]', fontsize=12)
ax1.set_ylabel('Number of Events', fontsize=12)
ax1.set_title('Δφ Distribution', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
ax1.set_xticklabels(['-π', '-π/2', '0', 'π/2', 'π'])

# pT histogram
ax2.hist(pt_all, bins=30, range=(0, 100), 
         color='steelblue', alpha=0.7, edgecolor='black')
ax2.set_xlabel('Muon pT [GeV]', fontsize=12)
ax2.set_ylabel('Number of Muons', fontsize=12)
ax2.set_title('Muon pT Distribution', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)

plt.tight_layout()

outpath2 = outdir / "delta_phi_and_pt_1d.png"
plt.savefig(outpath2, dpi=150)
print(f"1D Histograms saved to: {outpath2}")

# Show plots
plt.show()

print("\nDone!")


