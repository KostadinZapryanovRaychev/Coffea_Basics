
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

def save_png(output_dir: Path, histogram_name: str, title: str, values, bin_edges, xlabel: str, ylabel: str, num_events: int = None, num_particles: int = None):
    """
    Save a histogram as a PNG file with optional statistics.
    
    Args:
        output_dir: Directory to save the PNG file
        histogram_name: Base name for the histogram (without extension)
        title: Title of the histogram
        values: Array of values to histogram
        bin_edges: Edges of the histogram bins
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        num_events: Number of events analyzed (optional)
        num_particles: Number of particles analyzed (optional)
    Raises:        RuntimeError: If saving the PNG file fails
    """
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Count actual particles from values array
        values_array = np.asarray(values)
        actual_particles = len(values_array[np.isfinite(values_array)])
        
        fig, ax = plt.subplots(figsize=(11, 8))
        ax.hist(values, bins=bin_edges, histtype='stepfilled', color='blue', alpha=0.7, edgecolor='darkblue', linewidth=1.5)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Build statistics text
        stats_text = ""
        if num_events is not None:
            stats_text += f"Events analyzed: {num_events:,}\n"
        if num_particles is not None:
            stats_text += f"Particles analyzed: {num_particles:,}\n"
        stats_text += f"Particles in histogram: {actual_particles:,}"
        
        # Add statistics text box with better positioning
        if stats_text:
            ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
                    fontsize=11, verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round,pad=0.7', facecolor='wheat', edgecolor='black', linewidth=1.5, alpha=0.9))
        
        # Add extra padding to prevent text cutoff
        plt.tight_layout(pad=0.5)
        
        png_path = output_dir / f"{histogram_name}.png"
        plt.savefig(png_path, dpi=100, bbox_inches='tight', pad_inches=0.3)
        plt.close()
        logger.debug(f"Saved PNG histogram: {png_path}")
    except Exception as e:
        error_msg = f"Failed to save PNG histogram '{histogram_name}': {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def save_2d_histogram_png(output_dir: Path, histogram_name: str, title: str, x_values, y_values, 
                          x_bins: int, y_bins: int, x_min: float, x_max: float, y_min: float, y_max: float,
                          xlabel: str, ylabel: str, num_events: int = None, num_particles: int = None):
    """
    Save a 2D histogram as a PNG heatmap with optional statistics.
    
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
        num_events: Number of events analyzed (optional)
        num_particles: Number of particles analyzed (optional)
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
        
        # Count actual particles (both dimensions must be finite)
        valid_mask = np.isfinite(x_values) & np.isfinite(y_values)
        actual_particles = np.sum(valid_mask)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create 2D histogram
        h = ax.hist2d(x_values, y_values, 
                      bins=[x_bins, y_bins],
                      range=[[x_min, x_max], [y_min, y_max]],
                      cmap='YlOrRd', cmin=1)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        cbar = plt.colorbar(h[3], ax=ax, label='Counts')
        cbar.ax.tick_params(labelsize=10)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Build statistics text
        stats_text = ""
        if num_events is not None:
            stats_text += f"Events analyzed: {num_events:,}\n"
        if num_particles is not None:
            stats_text += f"Particles analyzed: {num_particles:,}\n"
        stats_text += f"Data points in histogram: {int(actual_particles):,}"
        
        # Add statistics text box with better positioning
        if stats_text:
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                    fontsize=11, verticalalignment='top', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.7', facecolor='wheat', edgecolor='black', linewidth=1.5, alpha=0.9))
        
        # Add extra padding
        plt.tight_layout(pad=0.5)
        
        png_path = output_dir / f"{histogram_name}.png"
        plt.savefig(png_path, dpi=100, bbox_inches='tight', pad_inches=0.3)
        plt.close()
        logger.debug(f"Saved 2D PNG histogram: {png_path}")
    except Exception as e:
        error_msg = f"Failed to save 2D PNG histogram '{histogram_name}': {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e



def save_tau_multiplicity_histogram(
    output_dir: Path,
    tau_info: dict,
    mass_point: str = "unknown",
    num_events: int = None,
):
    """
    Save histogram of number of reconstructed taus per event.

    Args:
        output_dir: Directory where PNG is saved.
        tau_info: Dictionary returned by get_number_of_taus_per_event().
                  Expected key: "n_taus_per_event"
        mass_point: Mass point label.
        num_events: Number of analyzed events.

    Returns:
        None
    """

    try:
        n_taus_values = tau_info.get("n_taus_per_event", tau_info.get("n_taus"))
        if n_taus_values is None:
            raise KeyError("n_taus_per_event")

        n_taus = np.asarray(n_taus_values, dtype=np.float64)

        if len(n_taus) == 0:
            raise ValueError("No tau multiplicity values found")

        # Create integer-centered bins:
        # Example:
        # 0 taus -> bin [-0.5,0.5]
        # 1 tau  -> bin [0.5,1.5]
        # 2 taus -> bin [1.5,2.5]
        max_taus = int(np.max(n_taus))

        bin_edges = np.arange(
            -0.5,
            max_taus + 1.5,
            1
        )

        title = (
            f"Reconstructed Tau Multiplicity per Event "
            f"(M={mass_point} GeV)"
        )

        save_png(
            output_dir=output_dir,
            histogram_name="tau_multiplicity",
            title=title,
            values=n_taus,
            bin_edges=bin_edges,
            xlabel="Number of reconstructed taus",
            ylabel="Events",
            num_events=num_events,
            num_particles=len(n_taus),
        )

    except Exception as e:
        error_msg = (
            f"\n[ERROR] Failed to save tau multiplicity histogram\n"
            f"  Exception: {type(e).__name__}: {str(e)}\n"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e