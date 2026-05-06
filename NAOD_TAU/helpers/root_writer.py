import logging
from pathlib import Path
import numpy as np
import uproot


logger = logging.getLogger(__name__)


def build_root_histogram(name: str, title: str, counts, bin_edges):
    """Build a ROOT TH1 from counts and bin edges."""
    counts = np.asarray(counts, dtype=np.float64)
    bin_edges = np.asarray(bin_edges, dtype=np.float64)

    if len(counts) != len(bin_edges) - 1:
        raise ValueError(
            f"Bin count mismatch: {len(counts)} counts but {len(bin_edges) - 1} expected bins"
        )

    data = np.zeros(len(counts) + 2, dtype=np.float64)
    data[1:-1] = counts
    entries = float(counts.sum())
    centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    sumw = float(counts.sum())
    sumw2 = float(counts.sum())
    sumwx = float(np.sum(counts * centers))
    sumwx2 = float(np.sum(counts * centers * centers))
    sumw2_array = np.zeros(len(counts) + 2, dtype=np.float64)
    sumw2_array[1:-1] = counts

    xaxis = uproot.writing.identify.to_TAxis(
        "xaxis",
        "",
        len(counts),
        float(bin_edges[0]),
        float(bin_edges[-1]),
    )
    return uproot.writing.identify.to_TH1x(
        name,
        title,
        data,
        entries,
        sumw,
        sumw2,
        sumwx,
        sumwx2,
        sumw2_array,
        xaxis,
    )


def save_lhe_histograms_root(output_dir: Path, root_stem: str, histogram_specs):
    """Save multiple 1D histograms into a single ROOT file."""
    if not output_dir.exists():
        raise ValueError(f"Output directory does not exist: {output_dir}")
    if not output_dir.is_dir():
        raise ValueError(f"Output path is not a directory: {output_dir}")

    root_path = output_dir / f"{root_stem}.root"

    for old_root in output_dir.glob("*.root"):
        if old_root != root_path:
            old_root.unlink(missing_ok=True)

    with uproot.recreate(root_path) as root_file:
        for spec in histogram_specs:
            if len(spec) != 4:
                raise ValueError(f"Invalid histogram spec length: {len(spec)}, expected 4")
            histogram_name, title, counts, bin_edges = spec
            root_file[histogram_name] = build_root_histogram(histogram_name, title, counts, bin_edges)

    logger.debug("Saved combined ROOT: %s", root_path)
    return root_path
