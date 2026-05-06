# NAOD_TAU

Tau-pair NanoAOD analysis framework.

## Quick Setup

**Option A: CERN LCG** (if available)

```bash
source setup.sh
python read_nanoaodsim_analysis.py
```

**Option B1: Local Python venv** (recommended)

```bash
cd ..  # Go to project root
bash NAOD_TAU/setup_option_b_venv.sh
source .venv_local/bin/activate
python NAOD_TAU/read_nanoaodsim_analysis.py
```

**Option B2: Conda** (if conda installed)

```bash
cd ..  # Go to project root
bash NAOD_TAU/setup_option_b_conda.sh
conda activate naod-tau
python NAOD_TAU/read_nanoaodsim_analysis.py
```

👉 **See [SETUP_OPTIONS.md](SETUP_OPTIONS.md) for detailed instructions**

## Structure

- `read_nanoaodsim_analysis.py` is the entrypoint.
- `helpers/io.py` loads NanoEvents from the ROOT file.
- `helpers/selection.py` performs the LHE/Gen tau-pair selection.
- `helpers/plotting.py` builds the matplotlib PNGs and matching ROOT histograms.

## Run

From the project root:

```bash
python NAOD_TAU/read_nanoaodsim_analysis.py
```

or as a module:

```bash
python -m NAOD_TAU.read_nanoaodsim_analysis
```

## File Configuration

The analysis reads files from **`NAOD_TAU/file_config.json`**. This allows batch processing of multiple files without code changes. File paths in the config are relative to the project root.

**Example configuration:**

```json
{
  "root_files": [
    {
      "name": "nanoaodsim_coffea_1",
      "path": "nanoaodsim_coffea_1.root",
      "tree": "Events",
      "enabled": true
    },
    {
      "name": "nanoaodsim_coffea_2",
      "path": "nanoaodsim_coffea_2.root",
      "tree": "Events",
      "enabled": false
    }
  ]
}
```

**Fields:**

- `name`: Display name for the file (used in output directory)
- `path`: Relative path from project root
- `tree`: ROOT tree name (default: "Events")
- `enabled`: Process this file (true/false)

**Features:**

- Add/remove files by editing JSON
- Enable/disable files without deleting entries
- Process multiple files in one run
- Each file gets its own output directory

## Batch Processing

The analysis automatically processes **all enabled files** from `file_config.json`:

1. Loads each file sequentially
2. Selects tau pairs
3. Generates histograms in separate output directories
4. Reports summary with success/skip counts

Example output structure:

```
NAOD_TAU/outputs/
├── nanoaodsim_coffea_1/
│   ├── lhe_mass.png
│   ├── lhe_pt.png
│   ├── lhe_delta_r.png
│   ├── lhe_delta_phi.png
│   ├── lhe_cos_delta_eta.png
│   ├── lhe_histograms.root
│   └── ...
└── nanoaodsim_coffea_2/
    ├── lhe_mass.png
   ├── lhe_histograms.root
    └── ...
```

## Outputs

Histograms are written to `NAOD_TAU/outputs/` in per-file directories:

- **PNG files** for quick visual inspection (matplotlib)
- **One ROOT file per sample** for detailed analysis (ROOT/TBrowser)

Each enabled file in `file_config.json` gets its own output directory:

```
outputs/
  file1_name/
    lhe_mass.png
      lhe_pt.png
    lhe_delta_r.png
    lhe_delta_phi.png
      lhe_cos_delta_eta.png
      lhe_histograms.root
  file2_name/
      (same histograms for file 2, with one combined ROOT file)
```

**LHE-Only Analysis (Current):**

The current analysis plots LHE particles (parton-level, before shower):

- `lhe_mass` — Di-tau invariant mass distribution
- `lhe_pt` — Di-tau transverse momentum distribution
- `lhe_delta_r` — ΔR between tau- and tau+
- `lhe_delta_phi` — Azimuthal angle difference (signed, range [-π, π])
- `lhe_cos_delta_eta` — Cosine of the pseudorapidity difference

## load_events -- what we load in load events actually ? in essence

COLLISION EVENT CHAIN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generate in MadGraph5 -- pp -> Z(some) --> tau+ tau- and this is saved in for instance file.lhe

1. TWO PROTONS COLLIDE at LHC
   Proton + Proton → COLLISION
2. INSIDE: Quarks/Gluons interact (parton collision)
   Quark + Quark → NEW PARTICLES (tau pairs, W boson, etc.)
3. PARTON LEVEL ← THIS IS LHE (Les Houches Event)
   ✓ Pure theoretical prediction
   ✓ No shower, no radiation yet
   ✓ "Clean" particles from the interaction
4. PARTON SHOWER (QCD radiation) - **PYTHIA8**
   Particles emit additional gluons/photons as they move
   Like an explosion of extra particles

   Provided to **Pythia8** for further hadronization and processing

5. HADRONIZATION (Confinement) - **PYTHIA8**
   Quarks/Gluons CANNOT exist alone in nature
   They group into COLORLESS hadrons:
   - Quarks → Pions, Kaons, protons, etc.
   - Taus → Still taus (leptons don't hadronize)

   ← THIS IS **Pythia GenPart** (GENERATOR LEVEL)

6. DECAY (Unstable particles break apart)
   Tau → electrons/muons + neutrinos
   W boson → leptons + neutrinos
7. DETECTOR INTERACTION
   Particles hit detector:
   - Electrons/Muons → "tracks" (curved paths)
   - Photons → energy in calorimeter
   - Jets → clusters from hadrons

   ← THIS IS RECONSTRUCTED LEVEL (Reco)

8. RECONSTRUCTION (Physicists rebuild particles)
   "I see a track, a photon, and some energy..."
   "That must be a tau decay!"

In our file .root that is currently under analysis it has been written info from madGraph5 , Pythia and more using CMSSW.

## What the plots mean

- **LHE Level**: Parton-level tau pairs (before shower)
- **Pythia GenPart Parent Level**: Hard-process taus from Pythia8 (after parton shower, before hadronization)
- **Pythia GenPart Children Level**: Stable decay products from Pythia8 hadronization

- `m(τ⁻τ⁺)` is the **invariant mass** of the tau pair, built from the Lorentz-vector sum of the two taus at each level. This reveals the mass of the mother particle (e.g., Z boson) that produced the tau pair.
- `p_T`, `p_z`, `η`, `φ`, `ΔR`, `Δφ`, `Δη`, and `Δθ` describe the pair kinematics and angular separation.
- **Signed** `Δφ`, `Δη`, and `Δθ` keep the asymmetry information that was previously lost when absolute values were used. This shows directional preferences in tau-pair production.

## read_nanoaodsim_analysis.py — Main Analysis Engine (Current Status)

**Purpose:** Batch processor for LHE tau-pair analysis. Orchestrates the complete workflow: file loading → event selection → histogram generation.

**Current Capability:** LHE-only parton-level tau-pair analysis with both 1D and 2D correlation histograms.

### Workflow (What It Does)

The script executes a three-stage pipeline for each enabled ROOT file:

```
1. LOAD CONFIGURATION
   └─ Read NAOD_TAU/file_config.json
   └─ Validate file entries (name, path, tree, enabled flag)

2. FOR EACH ENABLED FILE:
   ├─ LOAD EVENTS
   │  └─ Read NanoAOD ROOT file using uproot + coffea
   │  └─ Construct NanoEvents with Lorentz vectors
   │
   ├─ SELECT TAU PAIRS
   │  └─ Filter LHE particles (pdgId=15, status=1)
   │  └─ Match tau⁻ (pdgId=15) with tau⁺ (pdgId=-15)
   │  └─ Create paired tau-pair dataset
   │
   └─ GENERATE HISTOGRAMS
      ├─ Compute Lorentz vectors for tau pairs
      ├─ Calculate kinematics: pT, pz, η, φ, m (invariant mass)
      ├─ Calculate angular separations: ΔR, Δφ, Δη
      │
      ├─ CREATE 1D HISTOGRAMS:
      │  ├─ lhe_mass.png         — Di-tau invariant mass (50-500 GeV)
      │  ├─ lhe_pt.png           — Di-tau transverse momentum
      │  ├─ lhe_delta_r.png      — Angular separation ΔR(τ⁻,τ⁺)
      │  ├─ lhe_delta_phi.png    — Azimuthal angle difference [-π, π]
      │  └─ lhe_cos_delta_eta.png — Pseudorapidity cosine difference
      │
      ├─ CREATE 2D CORRELATION HISTOGRAMS:
      │  ├─ lhe_delta_phi_vs_mass.png   — Δφ (x) vs M (y) heatmap
      │  ├─ lhe_delta_r_vs_mass.png     — ΔR (x) vs M (y) heatmap
      │  └─ lhe_delta_eta_vs_mass.png   — Δη (x) vs M (y) heatmap
      │
      └─ COMBINE INTO ROOT FILE:
         └─ lhe_histograms.root
            ├─ 5× TH1 histograms (1D)
            └─ 3× TH2 histograms (2D correlations)

3. REPORT SUMMARY
   └─ Files processed, succeeded, and skipped
   └─ Exit with appropriate code (0 = success, 1 = failure)
```

### Key Features

**Batch Processing:**

- Processes all "enabled" files from `file_config.json` in a single run
- Each file gets its own output directory: `outputs/{file_name}/`
- Graceful error handling: skips failed files, continues with next

**Output Generation:**

- **PNG files** (8 total per sample):
  - 5× individual 1D histograms for visual inspection
  - 3× 2D correlation plots with color heatmap (viridis)
  - Size: 8×5 inches at 150 dpi
- **Single ROOT file per sample** (`lhe_histograms.root`):
  - Contains all 8 histograms as separate objects (5× TH1 + 3× TH2)
  - Readable in ROOT/TBrowser for detailed analysis
  - Proper axis labels and metadata

**Error Handling:**

- Configuration loading errors → Exit with code 1
- File not found → Skip file, continue processing
- Data structure errors → Skip file, continue processing
- I/O errors (disk/permissions) → Skip file, continue processing
- User interrupt (Ctrl+C) → Exit with code 130

### Function Breakdown

| Function                                 | Role                                                             |
| ---------------------------------------- | ---------------------------------------------------------------- |
| `load_config()`                          | Reads `file_config.json`, validates structure                    |
| `iterate_all_enabled_root_files(config)` | Generator yielding (path, tree, entry) for each enabled file     |
| `analyze_single_file()`                  | Main workhorse: loads file → selects taus → generates histograms |
| `get_output_directory_for_file()`        | Creates per-file output directory using filename                 |
| `make_tau_histogram_lhe()`               | Calls all 8 histogram generators, writes combined ROOT file      |
| `main()`                                 | Orchestrator: loads config → loops files → reports summary       |

### Output Structure

```
NAOD_TAU/outputs/
├── nanoaodsim_coffea_1/
│   ├── lhe_mass.png              (1D histogram)
│   ├── lhe_pt.png                (1D histogram)
│   ├── lhe_delta_r.png           (1D histogram)
│   ├── lhe_delta_phi.png         (1D histogram)
│   ├── lhe_cos_delta_eta.png     (1D histogram)
│   ├── lhe_delta_phi_vs_mass.png (2D scatter/heatmap) ← NEW
│   ├── lhe_delta_r_vs_mass.png   (2D scatter/heatmap) ← NEW
│   ├── lhe_delta_eta_vs_mass.png (2D scatter/heatmap) ← NEW
│   └── lhe_histograms.root       (5× TH1 + 3× TH2)
│
├── nanoaodsim_coffea_2/
│   └── (same structure as above)
│
└── ...
```

### Current Status — LHE-Only Analysis

**Enabled:** ✅ LHE particle-level tau-pair analysis

- Parton-level taus (generator truth before shower)
- Direct correlation with hard-process kinematics
- Ideal for:
  - Model comparisons (theory vs simulation)
  - Cross-section studies
  - Resonance searches

**Disabled:** ⛔ GenPart and Reco (postponed)

- GenPart (Pythia after hadronization) — Can be enabled later
- Reco (detector-level) — Can be added after physics validation

### Batch Processing Example

If `file_config.json` has 3 files (all enabled):

```
python NAOD_TAU/read_nanoaodsim_analysis.py
```

**Console Output:**

```
Loading file configuration...
✓ Configuration loaded
============================================================
FILE [1/3]: nanoaodsim_coffea_1
============================================================
Loading events from: /path/to/nanoaodsim_coffea_1.root
...
✓ Saved LHE histograms PNG files
✓ Saved combined ROOT: outputs/nanoaodsim_coffea_1/lhe_histograms.root
✓ Successfully analyzed: nanoaodsim_coffea_1
============================================================
FILE [2/3]: nanoaodsim_coffea_2
...
============================================================
BATCH ANALYSIS SUMMARY
============================================================
  Total files processed: 3
  ✓ Succeeded: 3
  ⚠ Skipped: 0
============================================================
✓ BATCH ANALYSIS COMPLETED
```

### Latest Enhancements (Current Release)

2. **Enhanced ROOT Output**
   - `save_lhe_histograms_root()` now handles both 1D and 2D
   - Automatic routing based on histogram tuple length (4-tuple vs 5-tuple)

3. **Single Combined ROOT File**
   - Replaced individual histogram ROOT files with one combined file
   - Cleaner output structure
   - Faster subsequent analysis

TODO this to be used as formula and to be written: https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004
