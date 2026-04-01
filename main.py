#!/usr/bin/env python3
"""Run a compact, non-interactive reproduction of the Coffea NanoEvents tutorial.

Saves example plots into an output directory. Intended to be executed as:

    python main.py            # run the demo using a tiny example NanoAOD (downloaded)
    python main.py --sample /path/to/my.root --outdir results

The script is defensive: it prints a clear `pip install` line when required packages are missing.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import platform
import urllib.request
from pathlib import Path
from typing import Optional

# --- dependency check (fail fast with an actionable message) ---
REQUIRED_PIP = "coffea[uproot] uproot awkward vector matplotlib pandas"


def ensure_imports():
    """Try to import required packages and return them. On failure, print a helpful pip command and exit."""
    try:
        import numpy as np
        import awkward as ak
        import vector
        import matplotlib
        matplotlib.use("Agg")  # safe backend for script (no DISPLAY needed)
        import matplotlib.pyplot as plt
        import uproot
        from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
        # coffea.processor used only in the optional example
        from coffea import processor, hist
    except Exception as exc:  # pragma: no cover - actionable runtime message
        pip_cmd = f"{sys.executable} -m pip install --user {REQUIRED_PIP}"
        venv_cmd = (
            f"{sys.executable} -m venv .venv && .venv/bin/python -m pip install --upgrade pip setuptools wheel "
            f"&& .venv/bin/python -m pip install --prefer-binary {REQUIRED_PIP}"
        )
        conda_cmd = "conda install -c conda-forge coffea uproot awkward vector matplotlib pandas"
        apple_note = ""
        try:
            if platform.system() == "Darwin" and platform.machine().lower().startswith("arm"):
                apple_note = "On Apple Silicon (M1/M2) prefer conda-forge (mambaforge) to avoid build issues."
        except Exception:
            apple_note = ""
        print(
            "Missing required packages for the NanoEvents demo:\n  ",
            exc,
            "\nInstall with pip:\n  ",
            pip_cmd,
            "\nOr with conda (recommended for prebuilt binaries):\n  ",
            conda_cmd,
            (f"\n{apple_note}" if apple_note else ""),
            "\nOr create an isolated venv (recommended):\n  ",
            venv_cmd,
            file=sys.stderr,
        )
        sys.exit(1)
    # attach vector behavior to awkward so .mass/.delta_r are available
    ak.behavior.update(vector.behavior)
    return {
        "np": np,
        "ak": ak,
        "vector": vector,
        "plt": plt,
        "uproot": uproot,
        "NanoEventsFactory": NanoEventsFactory,
        "NanoAODSchema": NanoAODSchema,
        "processor": processor,
        "hist": hist,
    }


# --- utilities ---

def get_sample_file(dest: Optional[str] = None, url: Optional[str] = None) -> str:
    """Download a tiny NanoAOD sample (if not present) and return the absolute path.

    By default the sample is placed next to this script (so other helper modules like
    `nano.py` can find it reliably). If `dest` is provided it is respected (expanded).
    """
    HERE = Path(__file__).resolve().parent
    # default: place beside the script so other modules can locate it
    if dest is None:
        dest_path = HERE / "nano_dy.root"
    else:
        dest_path = Path(dest).expanduser()
        if not dest_path.is_absolute():
            dest_path = Path.cwd() / dest_path

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest = str(dest_path)

    if url is None:
        url = (
            "https://raw.githubusercontent.com/CoffeaTeam/coffea/main/tests/samples/nano_dy.root"
        )

    if dest_path.exists():
        return dest

    print("downloading example NanoAOD to:", dest)
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as exc:  # pragma: no cover - network I/O
        raise RuntimeError(f"could not download sample from {url}: {exc}")
    return dest


def inspect_with_uproot(uproot, fn: str, ak):
    print("\n--- uproot inspection ---")
    with uproot.open(fn) as f:
        keys = list(f.keys())
        print("top-level keys:", keys)
        if "Events" not in f:
            raise RuntimeError("no 'Events' tree found in file")
        tree = f["Events"]
        print("number of entries:", tree.num_entries)
        sample_branches = [k for k in tree.keys() if k.startswith("Muon_")][:40]
        print("example Muon branches:", sample_branches)
        small = tree.arrays(["Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass"], entry_stop=5, library="ak")
        print("shapes (first 5 events):", {k: v.shape for k, v in small.items()})
        print("sample Muon_pt (first 5 events):\n", small["Muon_pt"])


# --- core demonstrations (keeps memory small and saves plots) ---

def demo_nanoevents(NanoEventsFactory, NanoAODSchema, fn: str, outdir: str, ak, plt, np):
    print("\n--- creating NanoEvents (convenience) ---")
    events = NanoEventsFactory.from_root(fn, schemaclass=NanoAODSchema).events()
    print("top-level fields (sample):", events.fields[:40])

    # defensive: ensure Muon exists
    if "Muon" not in events.fields:
        raise RuntimeError("Muon collection not found in NanoEvents fields")

    muons = events.Muon
    print("nMuon per event (first 10):", ak.num(muons)[:10])

    # selection: 'tight' muons (example)
    tight = muons[(muons.pt > 25) & (abs(muons.eta) < 2.4)]
    print("nTight per event (first 10):", ak.num(tight)[:10])
    frac_with_tight = float((ak.num(tight) > 0).mean())
    print(f"fraction of events with >=1 tight muon: {frac_with_tight:.3f}")

    # leading tight muon pT (per-event reduction)
    leading_pt = ak.max(tight.pt, axis=1)
    mask = ak.num(tight) > 0
    leading_vals = ak.to_numpy(leading_pt[mask])
    pthist_path = os.path.join(outdir, "leading_tight_mu_pt.png")
    plt.figure(figsize=(6, 4))
    plt.hist(leading_vals, bins=50, range=(0, 200), histtype="stepfilled", alpha=0.8)
    plt.xlabel("leading tight muon pt [GeV]")
    plt.ylabel("events")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(pthist_path, dpi=150)
    plt.close()
    print("wrote", pthist_path)

    # four-vectors and dimuon (leading two tight muons)
    mu_p4 = ak.zip(
        {"pt": tight.pt, "eta": tight.eta, "phi": tight.phi, "mass": tight.mass},
        with_name="LorentzVector",
    )
    pairs = ak.topk(mu_p4, 2, "pt")
    has_two = ak.num(pairs) == 2
    dimu_mass = (pairs[has_two][:, 0] + pairs[has_two][:, 1]).mass
    dimu_vals = ak.to_numpy(dimu_mass)
    dimu_path = os.path.join(outdir, "dimuon_mass_leading2.png")
    plt.figure(figsize=(6, 4))
    plt.hist(dimu_vals, bins=80, range=(0, 200))
    plt.xlabel("dimuon mass [GeV]")
    plt.ylabel("events")
    plt.axvspan(80, 100, color="C1", alpha=0.2, label="Z window")
    plt.legend()
    plt.tight_layout()
    plt.savefig(dimu_path, dpi=150)
    plt.close()
    print("wrote", dimu_path)
    print("fraction in 80--100 GeV window:", float(((dimu_mass > 80) & (dimu_mass < 100)).mean()))

    return events


def demo_opposite_sign(events, outdir: str, ak, plt):
    print("\n--- opposite-sign (OS) dimuon combinations ---")
    mu = events.Muon
    tight = mu[(mu.pt > 25) & (abs(mu.eta) < 2.4)]
    mu_p4 = ak.zip(
        {
            "pt": tight.pt,
            "eta": tight.eta,
            "phi": tight.phi,
            "mass": tight.mass,
            "charge": tight.charge,
        },
        with_name="LorentzVector",
    )
    pairs = ak.combinations(mu_p4, 2)
    os_pairs = pairs[(pairs["0"].charge != pairs["1"].charge)]
    masses = ak.flatten((os_pairs["0"] + os_pairs["1"]).mass)
    masses_np = ak.to_numpy(masses)
    out_path = os.path.join(outdir, "os_dimuon_mass_allpairs.png")
    plt.figure(figsize=(6, 4))
    plt.hist(masses_np, bins=80, range=(0, 200), histtype="stepfilled", alpha=0.8)
    plt.xlabel("opposite-sign dimuon mass [GeV]")
    plt.ylabel("pairs")
    plt.axvspan(80, 100, color="C1", alpha=0.2, label="Z window")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print("wrote", out_path)

    has_z = ak.sum(((os_pairs["0"] + os_pairs["1"]).mass > 80) & ((os_pairs["0"] + os_pairs["1"]).mass < 100), axis=1) > 0
    print("fraction of events with an OS dimuon in 80-100 GeV:", float(has_z.mean()))


def demo_chunked(uproot, fn: str, outdir: str, ak, np, plt):
    print("\n--- chunked processing with uproot.iterate (keeps memory small) ---")
    branches = ["Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass"]
    bins = np.linspace(0, 200, 101)
    acc = np.zeros(len(bins) - 1, dtype=np.int64)
    for arrays in uproot.iterate(fn, "Events", branches, step_size=100_000, library="ak"):
        mu = ak.zip({
            "pt": arrays["Muon_pt"],
            "eta": arrays["Muon_eta"],
            "phi": arrays["Muon_phi"],
            "mass": arrays["Muon_mass"],
        }, depth_limit=1)
        tight_mu = mu[(mu.pt > 25) & (abs(mu.eta) < 2.4)]
        lead = ak.max(tight_mu.pt, axis=1)
        lead_vals = ak.to_numpy(lead[ak.num(tight_mu) > 0])
        h, _ = np.histogram(lead_vals, bins=bins)
        acc += h
    out_path = os.path.join(outdir, "chunked_leading_tight_mu_pt.png")
    plt.figure(figsize=(6, 4))
    plt.step((bins[:-1] + bins[1:]) / 2, acc, where="mid")
    plt.yscale("log")
    plt.xlabel("leading tight muon pt [GeV]")
    plt.ylabel("counts")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print("wrote", out_path)


def demo_processor_example(processor, hist, NanoAODSchema, fn: str, ak):
    """Minimal coffea.processor example — useful to scale this logic to many files/executors."""
    print("\n--- coffea.processor minimal example (runs on the single sample) ---")

    class DimuonProcessor(processor.ProcessorABC):
        def __init__(self):
            self._accumulator = processor.dict_accumulator({
                "lead_mu_pt": hist.Hist("Events", hist.Bin("pt", "leading mu pt [GeV]", 50, 0, 200)),
                "dimu_mass": hist.Hist("Events", hist.Bin("mass", "dimu mass [GeV]", 80, 0, 200)),
            })

        @property
        def accumulator(self):
            return self._accumulator

        def process(self, events):
            out = self.accumulator.copy()
            mu = events.Muon
            tight = mu[(mu.pt > 25) & (abs(mu.eta) < 2.4)]
            lead = ak.max(tight.pt, axis=1)
            out["lead_mu_pt"].fill(pt=ak.to_numpy(ak.fill_none(lead, 0)))

            mu_p4 = ak.zip({
                "pt": tight.pt,
                "eta": tight.eta,
                "phi": tight.phi,
                "mass": tight.mass,
                "charge": tight.charge,
            }, with_name="LorentzVector")
            pairs = ak.combinations(mu_p4, 2)
            os_pairs = pairs[(pairs["0"].charge != pairs["1"].charge)]
            masses = ak.flatten((os_pairs["0"] + os_pairs["1"]).mass)
            out["dimu_mass"].fill(mass=ak.to_numpy(masses))
            return out

        def postprocess(self, accumulator):
            return accumulator

    fileset = {"sample": [fn]}
    result = processor.run_uproot_job(
        fileset,
        "Events",
        DimuonProcessor(),
        processor.futures_executor,
        {"schema": NanoAODSchema, "workers": 1},
        chunksize=100_000,
    )
    print("processor output keys:", list(result.keys()))
    return result


# --- CLI and orchestration ---

def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(description="Coffea NanoEvents tutorial - runnable demo")
    p.add_argument("--sample", help="path to a NanoAOD ROOT file (if omitted a tiny sample will be downloaded)")
    p.add_argument("--outdir", default="./outputs", help="where to save plots and outputs")
    p.add_argument("--no-plots", action="store_true", help="run calculations but do not save plots")
    p.add_argument("--skip-processor", action="store_true", help="do not run the coffea.processor example")
    args = p.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)

    deps = ensure_imports()
    np = deps["np"]
    ak = deps["ak"]
    plt = deps["plt"]
    uproot = deps["uproot"]
    NanoEventsFactory = deps["NanoEventsFactory"]
    NanoAODSchema = deps["NanoAODSchema"]

    sample = args.sample or get_sample_file()
    print("using sample:", sample)

    inspect_with_uproot(uproot, sample, ak)

    events = demo_nanoevents(NanoEventsFactory, NanoAODSchema, sample, args.outdir, ak, plt, np)

    if not args.no_plots:
        demo_opposite_sign(events, args.outdir, ak, plt)
        demo_chunked(uproot, sample, args.outdir, ak, np, plt)
    else:
        print("--no-plots: skipping plot generation")

    if not args.skip_processor:
        result = demo_processor_example(deps["processor"], deps["hist"], NanoAODSchema, sample, ak)
        # (user can inspect `result` programmatically)
    else:
        print("--skip-processor: skipped coffea.processor example")

    print("\nDemo complete — outputs saved to:", os.path.abspath(args.outdir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
