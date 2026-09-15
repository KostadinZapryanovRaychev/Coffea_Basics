import json
import pathlib

import uproot

_WITHROOT = pathlib.Path(__file__).resolve().parent.parent / "WITHROOT"
_raw = json.loads((_WITHROOT / "config.json").read_text())["inputFile"]
fname = _raw if pathlib.Path(_raw).is_absolute() else str((_WITHROOT / _raw).resolve())

try:
    tree = uproot.open(fname)["Events"]
    branch_names = tree.keys()
except Exception as e:
    print(f"failed to open {fname}: {e}")
else:
    out_path = pathlib.Path("outputs/branch_names.txt")
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text("\n".join(branch_names) + "\n")

    print(f"wrote {len(branch_names)} branch names to {out_path}")
