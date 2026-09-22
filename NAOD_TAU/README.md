## Quick Setup

Project available on

/eos/user/k/kraychev/Coffea_Basics

ls -la /eos/cms/store/data/Run2024C/Tau/NANOAOD/2024CDEReprocessing-v1/140000/

```bash
cd ..
bash NAOD_TAU/setup_option_b_venv.sh
source .venv_local/bin/activate
python NAOD_TAU/reco_tau_mass.py
python NAOD_TAU/mc_reco_tau_mass.py
```

## Run

```bash
python NAOD_TAU/mc_tau_analysis.py
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

## coffea ProcessorABC version (data + MC in one run)

`processors/mass_processor.py` is the `reco_tau_mass.py` selection and
histograms rewritten as a `coffea.processor.ProcessorABC`, per
https://coffea-hep.readthedocs.io/en/latest/getting_started/index.html.
`run_mass_processor.py` builds a `fileset` with two dataset entries,
`"data"` (from `file_config.json`) and `"mc"` (from `file_config_mc.json`),
and runs both through `processor.Runner` with `IterativeExecutor` in one
call — no dask cluster, since our files are small enough for one process.

```bash
python NAOD_TAU/run_mass_processor.py
```

Each histogram carries a `dataset` axis (`"data"` / `"mc"`), so the same
run produces both sets of histograms; the script slices each dataset out
and writes it to `outputs/mass_processor.root` as
`reco_tau_<name>_data` / `reco_tau_<name>_mc`, matching the histogram
names `reco_tau_mass.root` / `mc_reco_tau_mass.root` already use.

This is a second implementation of the same analysis as
`reco_tau_mass.py` / `mc_reco_tau_mass.py`, kept side by side rather than
replacing them, since converting the rest of the scripts
(`reco_tau_dphi_pt.py`, `tau_mass_dphi_pz.py`, the GenPart/GenVisTau
scripts) to processors is a separate step.

## Batch Processing Multiple Mass Points

To process more mass points (250 GeV to 6000 GeV) at once with organized outputs:

```bash
source .venv_local/bin/activate
cp NAOD_TAU/file_config_batch_all_mass_points.json NAOD_TAU/file_config.json
python NAOD_TAU/generate_batch_config.py

# Run batch analysis (processes each mass point sequentially)
python NAOD_TAU/batch_runner.py

# in progress
( python NAOD_TAU/batch_compare_results.py --all )
```

Results will be organized in:

```
outputs/M-250/   → histograms for M-250 GeV
outputs/M-500/   → histograms for M-500 GeV
outputs/M-750/   → histograms for M-750 GeV
... (and so on for all mass points)
```

Methodology: [PhysRevD.111.112004](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004)

The Plan 17.07.26

1. To understand the structure of NANOAOD data and how they are related to real physics
2. To start using Root and Python and to compare the results from both
3. To Figure out what we have and what we can do with this
4. To save all the results in root files ( C files )

/Tau/Run2024D-MINIv6NANOv15-v1/NANOAOD

"/eos/cms/store/data/Run2018A/Tau/NANOAOD/Nano25Oct2019-v1/230000/02785FC8-0354-A04D-8996-3AD8D18DCF7A.root"

simple analysis for check

{
"root_files": [
{
"name": "Tau_Run2024D_real_data",
"paths": [
"root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/0019cbeb-f99c-4a57-a911-5f72f5d9de28.root",
],
"tree": "Events",
"description": "Real Tau primary dataset, Run2024D, via CMS global xrootd redirector",
"enabled": true
}
],
"notes": "✓ ACTIVE CONFIG - Remote xrootd files. Each entry's 'paths' is a list of ROOT files processed and combined together. Set 'enabled': true/false to include/exclude an entry."
}

[kraychev@lxplus924 store]$ dasgoclient -query="file dataset=/Tau/Run2024D-MINIv6NANOv15-v1/NANOAOD" | grep '/120000/'

/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/e8393d52-174a-4cde-bb15-0f98571d0b33.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/d0e3a051-2fc4-49f1-b6e7-25fd936e0101.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/77bd2cd8-3ea1-48b5-b280-981000b45879.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/55ce73ea-16ce-4869-81b0-a22dc67d93ed.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/9076e542-19a7-478c-af9b-843dbcf7620d.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/5213f2f4-68ec-4738-9cf9-88b5d7474a3e.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/e727db27-b76b-4183-8b35-a6fe52a4cd86.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/008ca5f3-4b34-4e83-a897-fc34bb87343e.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/639c0075-3dce-41c7-843f-0c948d77d07c.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/c3be4954-8bbb-40a3-8a2b-6c5ca249b5d3.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/b203470e-65a4-408c-ad56-b33bd78da615.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/ce7c3bd1-8426-45ae-8e41-e287be9d306f.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/7a4a144f-efb6-4d06-8ccf-014c9dde3c35.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/b064c16b-2b75-45b5-ab56-982074f0cf87.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/db16f8c4-da36-499e-92cb-1dc63df8f99c.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/8cd8fe52-2b8d-4914-b08c-d2809313687d.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/6da3a189-910e-4810-9a40-84cde5ced5c4.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/372b8298-7c6e-4f2c-8f0b-8b1c5d3e0445.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/06e27c51-bd3a-482f-9933-889a454e03fe.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/4029594a-fe25-498a-b67b-961bf6c830fa.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/6b9ce373-8d81-4236-a473-1b16d8ff3cb9.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/3c9cd887-453b-4610-a27b-799d30393af3.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/232998a3-e6ae-48a6-a9d8-f85e21e0e0f8.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/4e33a138-0f1e-4b37-b830-ce155616ff97.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/5db80087-a1f8-44ab-80e9-07aa66c8b31c.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/225d069a-3f6f-4c07-a063-4a547aed20cc.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/fca85820-ec7c-47f5-ac0c-fe10c36ceb4b.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/3d9a88bf-6c26-49f4-a99f-8a90306ccd24.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/1b62f6a3-7479-46ad-a03e-5f253c505666.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/246b69a4-e4a5-43f7-bcf4-44980a2fbd5c.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/179455b3-0e99-46ec-820a-ee459fd92a4c.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/ec0b8891-960b-4fcf-8457-0cbe47f00e93.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/fcc1ed71-7505-4878-8504-6511ef646505.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/b9881b4b-ac7c-44ea-8b41-ddebf7763a5c.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/858431e5-2c3f-4550-919f-6b05c66c962a.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/e3c95d01-59e6-4b0c-a490-e975581a4a64.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/3fc6b439-5aba-4223-959d-35f367b8ac0c.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/85a75b9d-e7cf-432a-8b88-089f36eca845.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/a0cede5b-1d6b-4f0a-896c-43cd4cd7b7f6.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/a6860b04-39b6-47d0-a840-5a220deea206.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/84b616f0-0ef5-453b-9939-4ca3e9c65fec.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/bd30ca45-6a76-4762-9161-1ae5d2b66765.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/93a2aef6-6ca9-41b2-afa6-f133033cbb89.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/91360ec3-338d-410e-a0d9-931265420326.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/7c9625a5-2703-49bd-821b-2c8a7e13ebcc.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/fea9cb8a-dc5a-4eed-b679-70a50e3757b7.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/6d093332-f256-4c51-a70c-b74b273e3462.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/cebd697a-93e9-44fc-aa77-4341e06fd818.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/0fac4495-aedc-4352-8d51-e63c30df57c2.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/873737d7-47eb-4463-a878-eb1be19991ef.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/40fd4f68-40be-49d5-bafd-6afd7d871f02.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/d1d8adc5-0d71-4352-a6fd-09237ba20940.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/f2724d44-d212-4573-a89b-b58af07da313.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/96a28fdb-28fd-4803-8830-af3080c6dc3b.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/cefe0cd0-2cb4-4e57-856a-96b73120ad42.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/15b9ecc2-541e-4a82-9651-6bbf973c7f11.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/0019cbeb-f99c-4a57-a911-5f72f5d9de28.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/17bbd269-64d3-450f-ac60-98bc1eb9efe3.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/8aba0f8c-1304-4f17-bfab-cdbd05f6d465.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/870a8b9c-853e-4f80-b289-e869a82a02ef.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/10132535-1c6c-44b8-ae7b-4233289e6e88.root
/store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/cec64127-dbc0-4332-b6b2-d5d9635154fd.root

pz — longitudinal momentum of the τ⁻τ⁺ system, role: sanity/bias check, not a discriminator

pz = pz(τ) + pz(τ̄). Physically: inside each proton, the two colliding partons (quarks/gluons) each carry some fraction of the proton's momentum (x₁, x₂), and these fractions are essentially never equal. Whatever momentum imbalance exists gets inherited by the resonance, so the τ⁻τ⁺ system is usually boosted along the beam (z) axis by some amount — that boost is pz.

What role does it play in our analysis specifically? It's not something we cut on or search in — it's a consistency/bias check:

It should come out symmetric around 0 in a proton-proton collider (LHC collides identical beams head-on, so there's no preferred direction — as much chance of boost toward +z as −z). Our result showed exactly that (mean ≈ −3.6, essentially zero within the spread) — that tells us there's no accidental left-right bias baked into our event selection, reading, or reconstruction.
If it came out skewed (e.g. consistently positive), that would be a red flag — either a real physics effect worth investigating, or more likely a bug (e.g. accidentally always labeling the same detector-side tau as "tau" vs "antitau").
It's also potentially useful later for more advanced techniques (e.g. some neutrino-recovery methods used for tau decays boost into the ditau rest frame using this quantity), but we're not using it that way yet — right now it's purely a validation plot.

Δr — combined angular separation, role: confirms we're in the "resolved pair" regime

Δr = √(Δη² + Δφ²). It tells us how far apart, in a boost-invariant angular sense, the two taus land in the detector. A large Δr (which is what we saw — peaked near π ≈ 3.14) means the two taus are well-separated, reconstructible as two distinct objects with standard techniques — exactly the assumption our whole pipeline (select_leading_tau_pair, separate pt/eta cuts on each) relies on. If Δr were small (collimated pair), that would mean the resonance is highly boosted and the taus start to merge — a completely different (harder) reconstruction problem we're not handling. So its role here: confirms the resolved-pair assumption underlying this analysis is valid for the events we kept.
