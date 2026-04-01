from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

fn = "root://cms-xrd-global.cern.ch//eos/cms/store/user/mileva/bsm3g/NANO/ZprimeTo2Tau-2Jets_M-1000_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250603_104516/0000/nanoaodsim_1.root"

print(f"File path: {fn}\n")
print("="*80 + "\n")

try:
    events = NanoEventsFactory.from_root(
        fn,
        schemaclass=NanoAODSchema,
        entry_stop=100
    ).events()

    print(events.fields)      

except Exception as e:
    print(f"ERROR: {e}")


