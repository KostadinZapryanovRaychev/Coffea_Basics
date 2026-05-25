# NAOD_TAU

Tau-pair NanoAOD analysis framework for LHE-level tau-pair kinematics and correlation studies.

## Quick Setup

**Option A: CERN LCG** (if available)

```bash
source setup.sh
python mc_tau_analysis.py
```

**Option B1: Local Python venv** (recommended)

```bash
cd ..
bash NAOD_TAU/setup_option_b_venv.sh
source .venv_local/bin/activate
python NAOD_TAU/read_nanoaodsim_analysis.py
```

**Option B2: Conda** (if conda installed)

```bash
cd ..
bash NAOD_TAU/setup_option_b_conda.sh
conda activate naod-tau
python NAOD_TAU/read_nanoaodsim_analysis.py
```

👉 **See [SETUP_OPTIONS.md](SETUP_OPTIONS.md) for detailed setup instructions**

## Structure

- `read_nanoaodsim_analysis.py` — Main batch processor for LHE tau-pair analysis
- `helpers/io.py` — Loads NanoEvents from ROOT files
- `helpers/selection.py` — Selects LHE tau pairs
- `helpers/plotting.py` — Generates histograms (PNG + ROOT)

## Run

```bash
python NAOD_TAU/read_nanoaodsim_analysis.py
```

## Configuration

Edit **`NAOD_TAU/file_config.json`** to specify ROOT files to process:

```json
{
  "root_files": [
    {
      "name": "nanoaodsim_coffea_1",
      "path": "nanoaodsim_coffea_1.root",
      "tree": "Events",
      "enabled": true
    }
  ]
}
```

**Fields:** `name` (output directory), `path` (file path, relative to project root), `tree` (ROOT tree name), `enabled` (process or skip)

## Output

Histograms saved to `NAOD_TAU/outputs/{file_name}/`:

**1D Histograms (PNG + ROOT):**

- `lhe_mass.png` — Di-tau invariant mass
- `lhe_pt.png` — Di-tau transverse momentum
- `lhe_delta_r.png` — ΔR between tau- and tau+
- `lhe_delta_phi.png` — Azimuthal angle difference
- `lhe_cos_delta_eta.png` — Pseudorapidity difference

**2D Correlation Heatmaps (PNG + ROOT):**

- `lhe_delta_phi_vs_mass.png` — Δφ vs mass
- `lhe_delta_r_vs_mass.png` — ΔR vs mass
- `lhe_delta_eta_vs_mass.png` — Δη vs mass

**Combined ROOT File:**

- `lhe_histograms.root` — All 8 histograms (5× TH1 + 3× TH2)

## Analysis Pipeline

1. **Load**: Read NanoAOD ROOT file (uproot + coffea)
2. **Select**: Filter LHE tau pairs (pdgId=15, status=1)
3. **Compute**: Calculate kinematics (pT, η, φ, m) and angular separations (ΔR, Δφ, Δη)
4. **Generate**: Create 5 individual histograms + 3 correlation plots
5. **Combine**: Write all histograms to single ROOT file

## Functions

**Main Entry Point:**

| Function                | Role                                 |
| ----------------------- | ------------------------------------ |
| `load_config()`         | Read and validate `file_config.json` |
| `analyze_single_file()` | Process one ROOT file                |
| `main()`                | Orchestrate batch processing         |

**Plotting Module** (`helpers/plotting.py`):

| Function                         | Role                                 |
| -------------------------------- | ------------------------------------ |
| `create_output_directory()`      | Setup output directory               |
| `validate_lhe_events()`          | Validate event selection             |
| `build_lhe_tau_vectors()`        | Create Lorentz vectors               |
| `compute_lhe_ditau_kinematics()` | Calculate mass, pT, η, φ             |
| `compute_lhe_delta_angles()`     | Calculate ΔR, Δφ, Δη                 |
| `save_lhe_*_histogram()`         | Save individual 1D histograms        |
| `make_tau_histogram_lhe()`       | Orchestrate all histogram generation |

**Design**: Single-responsibility functions for better modularity, testability, and maintainability.

## Physics

**LHE Level**: Parton-level tau pairs before parton shower

- Pure generator-level information from MadGraph5 + Pythia8
- Ideal for resonance searches and model comparisons

**Plot Interpretation**:

- `m(τ⁻τ⁺)` — Invariant mass reveals mother particle (e.g., Z boson)
- Angular separations (ΔR, Δφ, Δη) — Tau-pair spatial configuration
- Signed angles — Preserve directional asymmetries

## References

Methodology: [PhysRevD.111.112004](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004)
