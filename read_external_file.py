from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

fn = "https://cms-xpog.docs.cern.ch/autoDoc/NanoAODv12/2022/2023/doc_DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8_Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2.html"


def read_external_file(file_path):
    try:
        events = NanoEventsFactory.from_root(
            file_path,
            schemaclass=NanoAODSchema,
            entry_stop=100
        ).events()
        return events.fields
    except Exception as e:
        print(f"ERROR: {e}")
        return None

read_external_file(fn)

