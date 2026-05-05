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

## Outputs

Each histogram is written twice into `NAOD_TAU/outputs/`:

- `.png` for quick visual inspection
- `.root` for ROOT/TBrowser inspection

The current analysis now also writes invariant-mass histograms for the LHE, GenPart parent, and GenPart child tau-pair levels. The GenPart selection is constrained to tau pairs whose mother is a Z boson (`pdgId = 23`) so the plotted sample is consistent with `Z \to \tau^+\tau^-` rather than an arbitrary tau pair.

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
4. PARTON SHOWER (QCD radiation)
   Particles emit additional gluons/photons as they move
   Like an explosion of extra particles

Provided to Pythia8 (file.lhe) for further hadranization and processing ( those are GenPart)

5. HADRONIZATION (Confinement)
   Quarks/Gluons CANNOT exist alone in nature
   They group into COLORLESS hadrons:
   - Quarks → Pions, Kaons, protons, etc.
   - Taus → Still taus (leptons don't hadronize)

   ← THIS IS GenPart (GENERATOR LEVEL)

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

- `m(\tau^-\tau^+)` is the invariant mass of the tau pair, built from the Lorentz-vector sum of the two taus at each level.
- `p_T`, `p_z`, `\eta`, `\phi`, `\Delta R`, `\Delta\phi`, `\Delta\eta`, and `\Delta\theta` describe the pair kinematics and angular separation.
- Signed `\Delta\phi`, `\Delta\eta`, and `\Delta\theta` keep the asymmetry information that was previously lost when absolute values were used.
