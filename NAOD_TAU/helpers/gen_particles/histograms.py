from pathlib import Path
import logging

from ..image_processing import compute_histogram_data, save_png, save_2d_histogram_png
from ..root_writer import save_lhe_histograms_root


logger = logging.getLogger(__name__)

bin_size = 120


def _get_histogram_ranges(mass_point: str) -> dict:
    try:
        if mass_point == "unknown":
            mass_value = 500.0
        else:
            mass_value = float(mass_point)
    except ValueError:
        logger.warning("Could not parse mass point '%s', using default 500 GeV", mass_point)
        mass_value = 500.0

    return {
        "invariant_mass_max": 2.0 * mass_value,
        "pt_max": 0.6 * mass_value,
        "pz_max": 1.5 * mass_value,
        "delta_r_max": 6.0,
    }


def get_gen_mass_his(output_dir: Path, mass, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        ranges = _get_histogram_ranges(mass_point)
        counts, bin_edges = compute_histogram_data(
            mass,
            bins=250,
            bin_edge_min=0,
            bin_edge_max=ranges["invariant_mass_max"],
        )
        title = f"GenPart Tau Pair Invariant Mass (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_mass",
            title,
            mass,
            bin_edges,
            r"$m(\tau^{-}\tau^{+})$ [GeV]",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_mass", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart mass histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_tau_pt_his(output_dir: Path, pt, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        ranges = _get_histogram_ranges(mass_point)
        counts, bin_edges = compute_histogram_data(
            pt,
            bins=bin_size,
            bin_edge_min=0,
            bin_edge_max=ranges["pt_max"],
        )
        title = f"GenPart τ⁻ Transverse Momentum Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_tau_pt",
            title,
            pt,
            bin_edges,
            r"$p_{T}(\tau^{-})$ [GeV]",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_tau_pt", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart tau pT histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_anti_tau_pt_his(output_dir: Path, pt, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        ranges = _get_histogram_ranges(mass_point)
        counts, bin_edges = compute_histogram_data(
            pt,
            bins=bin_size,
            bin_edge_min=0,
            bin_edge_max=ranges["pt_max"],
        )
        title = f"GenPart τ⁺ Transverse Momentum Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_antitau_pt",
            title,
            pt,
            bin_edges,
            r"$p_{T}(\tau^{+})$ [GeV]",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_antitau_pt", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart anti-tau pT histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_tau_pz_his(output_dir: Path, pz, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        ranges = _get_histogram_ranges(mass_point)
        pz_max = ranges["pz_max"]
        counts, bin_edges = compute_histogram_data(
            pz,
            bins=bin_size,
            bin_edge_min=-pz_max,
            bin_edge_max=pz_max,
        )
        title = f"GenPart τ⁻ Longitudinal Momentum Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_tau_pz",
            title,
            pz,
            bin_edges,
            r"$p_{z}(\tau^{-})$ [GeV]",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_tau_pz", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart tau pz histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_anti_tau_pz_his(output_dir: Path, pz, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        ranges = _get_histogram_ranges(mass_point)
        pz_max = ranges["pz_max"]
        counts, bin_edges = compute_histogram_data(
            pz,
            bins=bin_size,
            bin_edge_min=-pz_max,
            bin_edge_max=pz_max,
        )
        title = f"GenPart τ⁺ Longitudinal Momentum Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_antitau_pz",
            title,
            pz,
            bin_edges,
            r"$p_{z}(\tau^{+})$ [GeV]",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_antitau_pz", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart anti-tau pz histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_tau_eta_his(output_dir: Path, eta, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        counts, bin_edges = compute_histogram_data(eta, bins=bin_size, bin_edge_min=-3, bin_edge_max=3)
        title = f"GenPart τ⁻ Pseudorapidity Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_tau_eta",
            title,
            eta,
            bin_edges,
            r"$\eta(\tau^{-})$",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_tau_eta", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart tau eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_anti_tau_eta_his(output_dir: Path, eta, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        counts, bin_edges = compute_histogram_data(eta, bins=bin_size, bin_edge_min=-3, bin_edge_max=3)
        title = f"GenPart τ⁺ Pseudorapidity Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_antitau_eta",
            title,
            eta,
            bin_edges,
            r"$\eta(\tau^{+})$",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_antitau_eta", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart anti-tau eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_tau_phi_his(output_dir: Path, phi, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        counts, bin_edges = compute_histogram_data(phi, bins=bin_size, bin_edge_min=-3.2, bin_edge_max=3.2)
        title = f"GenPart τ⁻ Azimuthal Angle Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_tau_phi",
            title,
            phi,
            bin_edges,
            r"$\phi(\tau^{-})$",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_tau_phi", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart tau phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_anti_tau_phi_his(output_dir: Path, phi, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        counts, bin_edges = compute_histogram_data(phi, bins=bin_size, bin_edge_min=-3.2, bin_edge_max=3.2)
        title = f"GenPart τ⁺ Azimuthal Angle Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_antitau_phi",
            title,
            phi,
            bin_edges,
            r"$\phi(\tau^{+})$",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_antitau_phi", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart anti-tau phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_delta_phi_his(output_dir: Path, delta_phi, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        counts, bin_edges = compute_histogram_data(delta_phi, bins=bin_size, bin_edge_min=-6.4, bin_edge_max=6.4)
        title = f"GenPart Tau-Pair $\Delta\phi$ Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_delta_phi",
            title,
            delta_phi,
            bin_edges,
            r"$\Delta\phi(\tau^{-},\tau^{+})$",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_delta_phi", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart delta phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_delta_eta_his(output_dir: Path, tau_minus_lv, tau_plus_lv, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        delta_eta = tau_minus_lv.eta - tau_plus_lv.eta
        counts, bin_edges = compute_histogram_data(delta_eta, bins=bin_size, bin_edge_min=-7.5, bin_edge_max=7.5)
        title = f"GenPart Tau-Pair $\Delta\eta$ Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_delta_eta",
            title,
            delta_eta,
            bin_edges,
            r"$\Delta\eta(\tau^{-},\tau^{+})$",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_delta_eta", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart delta eta histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_delta_r_his(output_dir: Path, tau_minus_lv, tau_plus_lv, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        delta_r = tau_minus_lv.delta_r(tau_plus_lv)
        ranges = _get_histogram_ranges(mass_point)
        counts, bin_edges = compute_histogram_data(delta_r, bins=bin_size, bin_edge_min=0, bin_edge_max=ranges["delta_r_max"])
        title = f"GenPart Tau-Pair $\Delta R$ Distribution (M={mass_point} GeV)"
        save_png(
            output_dir,
            "gen_delta_r",
            title,
            delta_r,
            bin_edges,
            r"$\Delta R(\tau^{-},\tau^{+})$",
            "Events",
            num_events=num_events,
            num_particles=num_particles,
        )
        return "gen_delta_r", title, counts, bin_edges
    except Exception as e:
        error_msg = f"Failed to save GenPart delta R histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_gen_delta_r_vs_delta_phi_2d_his(output_dir: Path, tau_minus_lv, tau_plus_lv, mass_point: str = "unknown", num_events: int = None, num_particles: int = None):
    try:
        delta_r = tau_minus_lv.delta_r(tau_plus_lv)
        delta_phi = tau_minus_lv.phi - tau_plus_lv.phi
        ranges = _get_histogram_ranges(mass_point)
        save_2d_histogram_png(
            output_dir,
            "gen_delta_r_vs_delta_phi",
            f"GenPart Tau-Pair $\Delta R$ vs $\Delta\phi$ (M={mass_point} GeV)",
            delta_r,
            delta_phi,
            x_bins=bin_size,
            y_bins=bin_size,
            x_min=0,
            x_max=ranges["delta_r_max"],
            y_min=-6.4,
            y_max=6.4,
            xlabel=r"$\Delta R(\tau^{-},\tau^{+})$",
            ylabel=r"$\Delta\phi(\tau^{-},\tau^{+})$",
            num_events=num_events,
            num_particles=num_particles,
        )
        return None
    except Exception as e:
        error_msg = f"Failed to save GenPart delta R vs delta phi histogram: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def make_gen_ditau_histograms(output_dir: Path, gen_selected, mass_point: str = "unknown"):
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        from ..validation import validate_lhe_events
        from ..vector_builder import build_tau_vectors

        validate_lhe_events(gen_selected)

        gen_minus_lv, gen_plus_lv = build_tau_vectors(
            gen_selected.GenPart,
            gen_selected.GenPart.pdgId == 15,
            gen_selected.GenPart.pdgId == -15,
        )

        num_events = len(gen_selected)
        num_tau_minus = len(gen_minus_lv)
        num_tau_plus = len(gen_plus_lv)
        num_tau_pairs = min(num_tau_minus, num_tau_plus)

        histogram_specs = []
        histogram_specs.append(get_gen_mass_his(output_dir, (gen_minus_lv + gen_plus_lv).mass, mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_gen_tau_pt_his(output_dir, gen_minus_lv.pt, mass_point, num_events=num_events, num_particles=num_tau_minus))
        histogram_specs.append(get_gen_anti_tau_pt_his(output_dir, gen_plus_lv.pt, mass_point, num_events=num_events, num_particles=num_tau_plus))
        histogram_specs.append(get_gen_tau_pz_his(output_dir, gen_minus_lv.pz, mass_point, num_events=num_events, num_particles=num_tau_minus))
        histogram_specs.append(get_gen_anti_tau_pz_his(output_dir, gen_plus_lv.pz, mass_point, num_events=num_events, num_particles=num_tau_plus))
        histogram_specs.append(get_gen_tau_eta_his(output_dir, gen_minus_lv.eta, mass_point, num_events=num_events, num_particles=num_tau_minus))
        histogram_specs.append(get_gen_anti_tau_eta_his(output_dir, gen_plus_lv.eta, mass_point, num_events=num_events, num_particles=num_tau_plus))
        histogram_specs.append(get_gen_tau_phi_his(output_dir, gen_minus_lv.phi, mass_point, num_events=num_events, num_particles=num_tau_minus))
        histogram_specs.append(get_gen_anti_tau_phi_his(output_dir, gen_plus_lv.phi, mass_point, num_events=num_events, num_particles=num_tau_plus))
        histogram_specs.append(get_gen_delta_phi_his(output_dir, (gen_minus_lv.phi - gen_plus_lv.phi), mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_gen_delta_eta_his(output_dir, gen_minus_lv, gen_plus_lv, mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_gen_delta_r_his(output_dir, gen_minus_lv, gen_plus_lv, mass_point, num_events=num_events, num_particles=num_tau_pairs))
        histogram_specs.append(get_gen_delta_r_vs_delta_phi_2d_his(output_dir, gen_minus_lv, gen_plus_lv, mass_point, num_events=num_events, num_particles=num_tau_pairs))

        save_lhe_histograms_root(output_dir, "gen_tau_pair_histograms", histogram_specs)
    except Exception as e:
        error_msg = f"Unexpected error in make_gen_ditau_histograms: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
