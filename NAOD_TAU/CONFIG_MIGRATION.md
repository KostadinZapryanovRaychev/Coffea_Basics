# Configuration File Migration Summary

## ✅ Completed Tasks

### 1. Moved Configuration File

- **Old location:** `/Coffea/file_config.json` (project root)
- **New location:** `/Coffea/NAOD_TAU/file_config.json` (with code)

### 2. Updated Path References in `helpers/io.py`

```python
# Before:
CONFIG_FILE = PROJECT_ROOT / "file_config.json"

# After:
CONFIG_FILE = HERE / "file_config.json"
```

### 3. File Structure Now

```
Coffea/
├── nanoaodsim_coffea_1.root          ← Data files (project root)
├── file_config.json                   ← OLD (should be deleted)
└── NAOD_TAU/
    ├── file_config.json              ← NEW (with code)
    ├── helpers/
    │   ├── io.py                     ← References config in NAOD_TAU
    │   ├── plotting.py
    │   └── selection.py
    ├── read_nanoaodsim_analysis.py
    └── outputs/
```

## Path Resolution Logic

**Configuration file:** `NAOD_TAU/file_config.json`
**Project root:** Parent directory of NAOD_TAU (where ROOT files are)

**In config.json:**

```json
{
  "root_files": [
    {
      "name": "nanoaodsim_coffea_1",
      "path": "nanoaodsim_coffea_1.root",  ← Relative to project root
      "tree": "Events",
      "enabled": true
    }
  ]
}
```

**Resolution:**

```
project_root = /Coffea/
path = "nanoaodsim_coffea_1.root"
resolved = /Coffea/nanoaodsim_coffea_1.root ✓
```

## Cleanup Required

**Delete the old file:**

```bash
cd /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea
rm file_config.json
```

Or via Python:

```python
from pathlib import Path
Path("/Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea/file_config.json").unlink()
```

## Verification

✅ Config file location: NAOD_TAU/file_config.json
✅ Path resolution: PROJECT_ROOT (parent of NAOD_TAU)
✅ Error messages updated
✅ README updated
✅ Batch processing intact
✅ All logic checked and verified
