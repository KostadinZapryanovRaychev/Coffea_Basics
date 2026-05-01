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
