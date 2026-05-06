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
│   ├── lhe_mass.root
│   ├── lhe_delta_r.png
│   ├── lhe_delta_r.root
│   └── ...
└── nanoaodsim_coffea_2/
    ├── lhe_mass.png
    ├── lhe_mass.root
    └── ...
```

## Outputs

Histograms are written to `NAOD_TAU/outputs/` in per-file directories:

- **PNG files** for quick visual inspection (matplotlib)
- **ROOT files** for detailed analysis (ROOT/TBrowser)

Each enabled file in `file_config.json` gets its own output directory:

```
outputs/
  file1_name/
    lhe_mass.png
    lhe_mass.root
    lhe_delta_r.png
    lhe_delta_r.root
    lhe_delta_phi.png
    lhe_delta_phi.root
    lhe_delta_eta.png
    lhe_delta_eta.root
  file2_name/
    (same histograms for file 2)
```

**LHE-Only Analysis (Current):**

The current analysis plots LHE particles (parton-level, before shower):

- `lhe_mass` — Di-tau invariant mass distribution
- `lhe_delta_r` — ΔR between tau- and tau+
- `lhe_delta_phi` — Azimuthal angle difference (signed, range [-π, π])
- `lhe_delta_eta` — Pseudorapidity difference (signed)

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

TODO this to be used as formula and to be written: https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004
