import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

import awkward as ak
import numpy as np
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema


def read_muon_pt(filepath):
    """
    Read muon pT values from a ROOT file using Coffea (LXPLUS/EOS safe).
    """

    print(f"File: {filepath}\n")
    print("=" * 80 + "\n")

    # Load events (works with EOS via XRootD)
    events = NanoEventsFactory.from_root(
        filepath,
        schemaclass=NanoAODSchema,
        entry_stop=1000  # change or remove for full file
    ).events()

    # Access muons
    muons = events.Muon

    # Flatten all muon pT values
    all_muon_pts = ak.flatten(muons.pt)
    all_muon_pts = ak.to_numpy(all_muon_pts)

    print("pT DISTRIBUTION")
    print("=" * 80 + "\n")

    if len(all_muon_pts) == 0:
        print("No muons found in this sample.")
        return {}

    bins = [0, 10, 20, 30, 50, 100, 200, 500]
    counts, _ = np.histogram(all_muon_pts, bins=bins)

    for i in range(len(bins) - 1):
        print(f"{bins[i]:3d} - {bins[i+1]:3d} GeV: {counts[i]:5d} muons")

    print("\nSUMMARY")
    print("=" * 80)
    print(f"Total muons: {len(all_muon_pts)}")
    print(f"Min pT: {all_muon_pts.min():.2f}")
    print(f"Max pT: {all_muon_pts.max():.2f}")
    print(f"Mean pT: {all_muon_pts.mean():.2f}")

    return {
        "total_muons": len(all_muon_pts),
        "min_pt": float(all_muon_pts.min()),
        "max_pt": float(all_muon_pts.max()),
        "mean_pt": float(all_muon_pts.mean()),
    }


if __name__ == "__main__":

    # ✅ USE EOS/XROOTD PATH (NOT /eos/...)
    filepath = "/eos/cms/store/user/mileva/bsm3g/NANO/ZprimeTo2Tau-2Jets_M-1000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250603_104516/0000/nanoaodsim_1.root"

    result = read_muon_pt(filepath)
    print("\nRESULT:")
    print(result)