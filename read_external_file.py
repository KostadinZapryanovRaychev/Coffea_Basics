import uproot

# EOS file path on lxplus
fn = "/eos/cms/store/user/mileva/bsm3g/NANO/ZprimeTo2Tau-2Jets_M-1000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250603_104516/0000/nanoaodsim_1.root"

print(f"File path: {fn}\n")
print("="*80 + "\n")

try:
    with uproot.open(fn) as f:
        tree = f['Events']
        
        # Read first 100 events, all branches
        arrays = tree.arrays(library='np', entry_stop=100)
        
        output = str(arrays)
        print(output[:2000])
        
except Exception as e:
    print(f"ERROR: {e}")
