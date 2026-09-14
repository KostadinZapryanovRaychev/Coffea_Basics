#!/usr/bin/env python3

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from NAOD_TAU.helpers.io import load_events

TEST_ROOT_FILE = Path(__file__).resolve().parents[1] / "nanoaodsim_coffea_1.root"


def main():
    events = load_events(str(TEST_ROOT_FILE))
    print(len(events))
    print(events.fields)


if __name__ == "__main__":
    main()
