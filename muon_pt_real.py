import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
from pathlib import Path


def read_muon_pt(filepath):
    """
    Read muon pT values from a ROOT file using Coffea.
    
    Parameters:
    -----------
    filepath : str or Path
        Absolute or relative path to the ROOT file
    
    Returns:
    --------
    dict : Contains muon pT data and statistics
    """
    
    fn = Path(filepath)
    
    if not fn.exists():
        raise FileNotFoundError(f"File not found: {fn}")

    print(f"File: {fn}\n")
    print("="*80 + "\n")
    
    events = NanoEventsFactory.from_root(
        {str(fn): "Events"},
        schemaclass=NanoAODSchema
    ).events()
    
    muons = events.Muon
    
    event_count = 0
    for evt_idx in range(len(events)):
        n_muons = len(muons[evt_idx])
        if n_muons > 0:
            pt_values = ak.to_numpy(muons[evt_idx].pt)
            print(f"Event {evt_idx}: {n_muons} muon(s)")
            for muon_idx, pt in enumerate(pt_values):
                print(f"  Muon {muon_idx}: pT = {pt:.2f} GeV")
            event_count += 1
    
    # Get all pT values
    all_muon_pts = ak.flatten(muons.pt)
    all_muon_pts_numpy = ak.to_numpy(all_muon_pts)
    
    print("pT DISTRIBUTION")
    print("="*80 + "\n")
    
    bins = [0, 10, 20, 30, 50, 100, 200, 500]
    counts, _ = np.histogram(all_muon_pts_numpy, bins=bins)
    for i in range(len(bins)-1):
        print(f"  {bins[i]:3d} - {bins[i+1]:3d} GeV: {counts[i]:3d} muons")
    
    # Return data as dictionary
    return {
        'all_pt': all_muon_pts_numpy,
        'total_muons': len(all_muon_pts_numpy),
        'events_with_muons': event_count,
        'min_pt': all_muon_pts_numpy.min(),
        'max_pt': all_muon_pts_numpy.max(),
        'mean_pt': all_muon_pts_numpy.mean(),
        'median_pt': np.median(all_muon_pts_numpy)
    }


if __name__ == "__main__":
    filepath = "/Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea/nano_dy.root"
    result = read_muon_pt(filepath)
