"""
DATA TRANSFORMATION DEMO
Shows how data flows through the pipeline:
RAW ROOT FILE → AWKWARD ARRAYS → SELECTED DATA
"""

import uproot
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
fn = HERE / "nano_dy.root"

if not fn.exists():
    raise FileNotFoundError(f"{fn} not found")

print("\n" + "="*80)
print("STEP 1: RAW DATA FROM ROOT FILE (uproot)")
print("="*80)

# Read RAW data directly from ROOT
with uproot.open(fn) as f:
    tree = f['Events']
    raw_data = tree.arrays(
        ['Muon_pt', 'Muon_eta', 'Muon_phi', 'Muon_mass', 'Muon_charge'],
        entry_start=0,
        entry_stop=10,
        library='np'
    )
    
    print("Raw data keys:", raw_data.keys())

# events = NanoEventsFactory.from_root(
#     {str(fn): "Events"},
#     schemaclass=NanoAODSchema
# ).events()

# muons_ak = events.Muon


