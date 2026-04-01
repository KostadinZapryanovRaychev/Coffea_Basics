import uproot
from pathlib import Path

fn = Path(__file__).resolve().parent / "nano_dy.root"

print(fn, "\n" + "="*80)

with uproot.open(fn) as f:
    tree = f['Events']
    
    # Read all branches, first 100 events
    arrays = tree.arrays(library='np', entry_stop=100)
    
    # Convert to string and print first 10000 characters
    output = str(arrays)
    print(output[:10000])
    print(f"\n... (total output length: {len(output)} characters)")
