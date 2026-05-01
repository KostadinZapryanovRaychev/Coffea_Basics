#!/usr/bin/env python3
"""NAOD_TAU tau-pair analysis entrypoint."""

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from NAOD_TAU.helpers.io import ROOT_FILE, HERE, load_events
from NAOD_TAU.helpers.plotting import make_tau_histogram
from NAOD_TAU.helpers.selection import load_tau_pairs


def main():
    events = load_events(ROOT_FILE)
    lhe_selected, gen_selected, _ = load_tau_pairs(events)
    output_dir = HERE / "outputs"
    make_tau_histogram(output_dir, lhe_selected, gen_selected=gen_selected)


if __name__ == "__main__":
    main()
