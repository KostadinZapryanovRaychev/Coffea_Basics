
import logging

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


logger = logging.getLogger(__name__)


def compute_histogram_data(values, bins , bin_edge_min=None, bin_edge_max=None):
    """
    Compute histogram bin edges and counts from values.
    
    Args:
        values: Array-like of numeric values
        bins: Number of bins or bin edges
        bin_edge_min: Minimum value for bin edges
        bin_edge_max: Maximum value for bin edges

    Returns:
        Tuple of (counts, bin_edges)
        
    Raises:
        ValueError: If values array is invalid or empty
        TypeError: If bins parameter is invalid
    """
    try:
        values = np.asarray(values, dtype=np.float64)
        
        if len(values) == 0:
            raise ValueError("Cannot compute histogram from empty values array")
        
        if np.all(np.isnan(values)):
            raise ValueError("All values are NaN")
        
        # Filter out NaN/Inf for valid min/max
        valid_values = values[np.isfinite(values)]
        if len(valid_values) == 0:
            raise ValueError("No valid (finite) values in input array")
        
        bin_edges = np.linspace(bin_edge_min, bin_edge_max, int(bins) + 1)
        counts, _ = np.histogram(values, bins=bin_edges)
        return counts, bin_edges
    except (ValueError, TypeError) as e:
        error_msg = (
            f"\n[ERROR] Failed to compute histogram data\n"
            f"  Values shape: {np.asarray(values).shape}\n"
            f"  Bins: {bins}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"\n[ERROR] Unexpected error computing histogram data\n"
            f"  Exception type: {type(e).__name__}\n"
            f"  Details: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_png(output_dir: Path, histogram_name: str, title: str, values, bin_edges, xlabel: str, ylabel: str):
    """
    Save a histogram as a PNG file.
    
    Args:
        output_dir: Directory to save the PNG file
        histogram_name: Base name for the histogram (without extension)
        title: Title of the histogram
        values: Array of values to histogram
        bin_edges: Edges of the histogram bins
        xlabel: Label for x-axis
        ylabel: Label for y-axis
    Raises:        RuntimeError: If saving the PNG file fails
    """
    try:
        plt.figure(figsize=(8, 6))
        plt.hist(values, bins=bin_edges, histtype='stepfilled', color='blue', alpha=0.7)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True, linestyle='--', alpha=0.5)
        png_path = output_dir / f"{histogram_name}.png"
        plt.savefig(png_path)
        plt.close()
        logger.debug(f"Saved PNG histogram: {png_path}")
    except Exception as e:
        error_msg = f"Failed to save PNG histogram '{histogram_name}': {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

