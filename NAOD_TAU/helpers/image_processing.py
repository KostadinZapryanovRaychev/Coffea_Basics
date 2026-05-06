
import logging

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


logger = logging.getLogger(__name__)

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

