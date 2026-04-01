import uproot
from pathlib import Path

fn = Path(__file__).resolve().parent / "nano_dy.root"

print(fn, "\n" + "="*80)

with uproot.open(fn) as f:
    tree = f['Events']
    
    arrays = tree.arrays(library='np', entry_stop=100)
    
    output = str(arrays)
    print(output[:1000])
