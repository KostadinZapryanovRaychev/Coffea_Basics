
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
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
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

def save_2d_histogram_png(output_dir: Path, histogram_name: str, title: str, x_values, y_values, 
                          x_bins: int, y_bins: int, x_min: float, x_max: float, y_min: float, y_max: float,
                          xlabel: str, ylabel: str):
    """
    Save a 2D histogram as a PNG heatmap.
    
    Args:
        output_dir: Directory to save the PNG file
        histogram_name: Base name for the histogram (without extension)
        title: Title of the histogram
        x_values: Array of x-values
        y_values: Array of y-values
        x_bins: Number of bins for x-axis
        y_bins: Number of bins for y-axis
        x_min: Minimum value for x-axis
        x_max: Maximum value for x-axis
        y_min: Minimum value for y-axis
        y_max: Maximum value for y-axis
        xlabel: Label for x-axis
        ylabel: Label for y-axis
    Raises:
        RuntimeError: If saving the PNG file fails
    """
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        x_values = np.asarray(x_values, dtype=np.float64)
        y_values = np.asarray(y_values, dtype=np.float64)
        
        if len(x_values) == 0 or len(y_values) == 0:
            raise ValueError("Cannot create 2D histogram from empty arrays")
        
        if len(x_values) != len(y_values):
            raise ValueError("x_values and y_values must have the same length")
        
        plt.figure(figsize=(10, 8))
        
        # Create 2D histogram
        h = plt.hist2d(x_values, y_values, 
                       bins=[x_bins, y_bins],
                       range=[[x_min, x_max], [y_min, y_max]],
                       cmap='YlOrRd', cmin=1)
        
        plt.title(title, fontsize=14)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.colorbar(h[3], label='Counts')
        plt.grid(True, linestyle='--', alpha=0.3)
        
        png_path = output_dir / f"{histogram_name}.png"
        plt.savefig(png_path, dpi=100, bbox_inches='tight')
        plt.close()
        logger.debug(f"Saved 2D PNG histogram: {png_path}")
    except Exception as e:
        error_msg = f"Failed to save 2D PNG histogram '{histogram_name}': {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

