from pathlib import Path

from coffea.nanoevents import NanoAODSchema, NanoEventsFactory


NanoAODSchema.warn_missing_crossrefs = False

HERE = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT_FILE = PROJECT_ROOT / "nanoaodsim_coffea_1.root"
TREE_NAME = "Events"


def load_events(root_file: Path):
    if not root_file.exists():
        raise FileNotFoundError(f"ROOT file not found: {root_file}")
    return NanoEventsFactory.from_root({str(root_file): TREE_NAME}, schemaclass=NanoAODSchema).events()
