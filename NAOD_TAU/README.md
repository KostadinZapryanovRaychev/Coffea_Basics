# NAOD_TAU

This folder contains the tau-pair NanoAOD analysis in a small package layout.

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

## load_events -- what we load in load events actually ? in essence

COLLISION EVENT CHAIN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
