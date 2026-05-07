import numpy as np
import matplotlib.pyplot as plt
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def check_zprime_candidates(mass_values, output_dir: Path = None, mass_threshold_range=(100, 5000)):
    """
    Analyze invariant mass distribution to identify Z' (hypothetical mother particle) candidates.
    Creates a visualization of the mass distribution with Z' mass window highlighted.
    
    The simplest check: find the mass distribution peak and report statistics.
    A clear peak in the mass distribution indicates potential Z' decay events.
    
    Args:
        mass_values: Array of di-tau invariant mass values
        output_dir: Optional output directory to save Z' candidate plot (PNG)
        mass_threshold_range: Mass window (min, max) in GeV for Z' hypothesis. Default (100, 5000) GeV.
        
    Returns:
        Dictionary with Z' candidate analysis:
        {
            'total_events': int,
            'events_in_window': int,
            'window_percentage': float,
            'mass_mean': float,
            'mass_median': float,
            'mass_std': float,
            'mass_mode_bin': float (bin center with most events),
            'is_zprime_candidate': bool (True if >10% events in mass window)
        }
    """
    try:
        mass_array = np.asarray(mass_values, dtype=np.float64)
        mass_array = mass_array[np.isfinite(mass_array)]
        
        total = len(mass_array)
        if total == 0:
            return {
                'total_events': 0,
                'events_in_window': 0,
                'window_percentage': 0.0,
                'mass_mean': np.nan,
                'mass_median': np.nan,
                'mass_std': np.nan,
                'mass_mode_bin': np.nan,
                'is_zprime_candidate': False,
            }
        
        # Count events in mass window
        in_window = np.sum((mass_array >= mass_threshold_range[0]) & (mass_array <= mass_threshold_range[1]))
        window_pct = 100.0 * in_window / total if total > 0 else 0.0
        
        # Find mode (bin with most counts)
        counts, bin_edges = np.histogram(mass_array, bins=100)
        mode_bin_idx = np.argmax(counts)
        mode_mass = (bin_edges[mode_bin_idx] + bin_edges[mode_bin_idx + 1]) / 2.0
        
        result = {
            'total_events': int(total),
            'events_in_window': int(in_window),
            'window_percentage': float(window_pct),
            'mass_mean': float(np.mean(mass_array)),
            'mass_median': float(np.median(mass_array)),
            'mass_std': float(np.std(mass_array)),
            'mass_mode_bin': float(mode_mass),
            'is_zprime_candidate': bool(window_pct > 10.0),  # Heuristic: >10% in mass window suggests Z' signal
        }
        
        logger.info(
            f"\n[Z' CANDIDATE ANALYSIS]\n"
            f"  Total events: {result['total_events']}\n"
            f"  Events in window [{mass_threshold_range[0]}, {mass_threshold_range[1]}] GeV: {result['events_in_window']} ({result['window_percentage']:.1f}%)\n"
            f"  Mass mean: {result['mass_mean']:.1f} GeV | median: {result['mass_median']:.1f} GeV | std: {result['mass_std']:.1f} GeV\n"
            f"  Mass mode (peak): {result['mass_mode_bin']:.1f} GeV\n"
            f"  ✓ Z' CANDIDATE: {result['is_zprime_candidate']} (>10% signal in mass window)\n"
        )
        
        # Create Z' candidate visualization if output_dir provided
        if output_dir is not None:
            try:
                _plot_zprime_candidates(output_dir, mass_array, result, mass_threshold_range)
            except Exception as e:
                logger.warning(f"Could not create Z' candidate plot: {str(e)}")
        
        return result
    except Exception as e:
        logger.error(f"Error in check_zprime_candidates: {str(e)}")
        return {'is_zprime_candidate': False, 'error': str(e)}


def _plot_zprime_candidates(output_dir: Path, mass_array, result, mass_threshold_range):
    """
    Create a visualization of the invariant mass distribution for Z' candidates.
    Highlights the Z' mass window and shows peak/mean markers.
    
    Args:
        output_dir: Output directory to save the plot
        mass_array: Array of mass values
        result: Dictionary with analysis results from check_zprime_candidates
        mass_threshold_range: Mass window tuple (min, max) in GeV
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Create histogram
        counts, bin_edges, patches = ax.hist(
            mass_array, 
            bins=150, 
            histtype='stepfilled', 
            color='steelblue', 
            alpha=0.7,
            edgecolor='navy',
            linewidth=1.5,
            label='All events'
        )
        
        # Highlight Z' mass window
        for i, patch in enumerate(patches):
            bin_center = (bin_edges[i] + bin_edges[i+1]) / 2.0
            if mass_threshold_range[0] <= bin_center <= mass_threshold_range[1]:
                patch.set_facecolor('orangered')
                patch.set_alpha(0.8)
        
        # Add vertical lines for peak and mean
        ax.axvline(result['mass_mode_bin'], color='red', linestyle='--', linewidth=2.5, 
                   label=f"Peak: {result['mass_mode_bin']:.1f} GeV")
        ax.axvline(result['mass_mean'], color='green', linestyle='--', linewidth=2.5, 
                   label=f"Mean: {result['mass_mean']:.1f} GeV")
        
        # Shade the Z' window region
        ax.axvspan(mass_threshold_range[0], mass_threshold_range[1], alpha=0.15, color='orange', 
                   label=f"Z' window [{mass_threshold_range[0]}, {mass_threshold_range[1]}] GeV")
        
        # Add statistics text box
        zprime_status = "✓ Z' CANDIDATE" if result['is_zprime_candidate'] else "✗ No Z' signal"
        stats_text = (
            f"Z' Candidate Analysis\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Total events: {result['total_events']:,}\n"
            f"Events in window: {result['events_in_window']:,} ({result['window_percentage']:.1f}%)\n"
            f"Mean: {result['mass_mean']:.1f} ± {result['mass_std']:.1f} GeV\n"
            f"Median: {result['mass_median']:.1f} GeV\n"
            f"Mode: {result['mass_mode_bin']:.1f} GeV\n"
            f"\n{zprime_status}\n"
            f"(>10% in window)"
        )
        
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                family='monospace')
        
        # Formatting
        ax.set_xlabel(r"$m(\tau^{-}\tau^{+})$ [GeV]", fontsize=12, fontweight='bold')
        ax.set_ylabel("Events", fontsize=12, fontweight='bold')
        ax.set_title("Z' Candidate Analysis: Di-tau Invariant Mass Distribution", 
                     fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='upper left', fontsize=10, framealpha=0.95)
        ax.grid(True, linestyle='--', alpha=0.4)
        
        # Save figure
        zprime_plot_path = output_dir / "zprime_candidate_analysis.png"
        plt.tight_layout()
        plt.savefig(zprime_plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✓ Saved Z' candidate plot: {zprime_plot_path}")
        
    except Exception as e:
        logger.error(f"Error creating Z' candidate plot: {str(e)}")
        raise RuntimeError(f"Failed to create Z' candidate plot: {str(e)}") from e

