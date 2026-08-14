#!/usr/bin/env python3
"""Stage V scaling laboratory for Operational Information Geometry.

This module keeps three limits separate:

* fixed-domain refinement, with cell width ``h=1/n`` and generator ``h^-2 L``;
* an expanding-domain limit at fixed lattice spacing; and
* the propagation envelope obtained before and after diffusive rescaling.

The response calculation uses a modal reduction and never forms the dense
``n^2 by n^2`` generator.  Sparse matrices are used only for the propagation
audit.  The reference continuum convention is the cell-centred finite-volume
Neumann path, whose low eigenvalues converge quadratically.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Literal, Sequence

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import brentq
from scipy.sparse import csr_matrix, diags, eye, kron
from scipy.sparse.linalg import expm_multiply
from scipy.stats import poisson

from operational_information_geometry_ii import mixture_tangent_basis


BackgroundKind = Literal["delta", "centered_delta", "smooth_cosine", "uniform"]


def path_graph_laplacian(side_length: int, spacing: float | None = None) -> np.ndarray:
    """Return the path graph Laplacian, optionally divided by ``spacing**2``."""
    if side_length < 2:
        raise ValueError("side_length must be at least two")
    diagonal = np.r_[1.0, np.full(side_length - 2, 2.0), 1.0]
    laplacian = np.diag(diagonal)
    indices = np.arange(side_length - 1)
    laplacian[indices, indices + 1] = -1.0
    laplacian[indices + 1, indices] = -1.0
    if spacing is not None:
        if spacing <= 0.0:
            raise ValueError("spacing must be positive")
        laplacian /= spacing**2
    return laplacian


def cell_centres(side_length: int) -> np.ndarray:
    """Cell-centred coordinates on the unit interval."""
    if side_length < 2:
        raise ValueError("side_length must be at least two")
    return (np.arange(side_length, dtype=float) + 0.5) / side_length


def exact_path_eigenvalues(side_length: int, spacing: float = 1.0) -> np.ndarray:
    """Exact spectrum ``4 h^-2 sin^2(k pi/(2n))`` of the Neumann path."""
    if side_length < 2 or spacing <= 0.0:
        raise ValueError("invalid side length or spacing")
    modes = np.arange(side_length, dtype=float)
    return 4.0 / spacing**2 * np.sin(np.pi * modes / (2.0 * side_length)) ** 2


def target_background(
    side_length: int,
    kind: BackgroundKind,
    cosine_amplitude: float = 0.5,
) -> np.ndarray:
    """Return a probability background for the target factor."""
    if not 0.0 <= cosine_amplitude < 1.0:
        raise ValueError("cosine_amplitude must lie in [0,1)")
    if kind == "delta":
        result = np.zeros(side_length)
        result[side_length // 2] = 1.0
    elif kind == "centered_delta":
        result = np.zeros(side_length)
        if side_length % 2 == 0:
            result[side_length // 2 - 1 : side_length // 2 + 1] = 0.5
        else:
            result[side_length // 2] = 1.0
    elif kind == "smooth_cosine":
        result = (
            1.0 + cosine_amplitude * np.cos(np.pi * cell_centres(side_length))
        ) / side_length
    elif kind == "uniform":
        result = np.ones(side_length) / side_length
    else:
        raise ValueError(f"unknown background kind: {kind}")
    return result


def directed_cell_generator_sparse(
    side_length: int, interaction_strength: float = 0.8
) -> csr_matrix:
    """Sparse fixed-domain directed generator on the unit square."""
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    n = side_length
    h = 1.0 / n
    one = np.ones(n - 1)
    base = diags(
        [-one, np.r_[1.0, np.full(n - 2, 2.0), 1.0], -one],
        offsets=[-1, 0, 1],
        format="csr",
    ) / h**2
    identity = eye(n, format="csr")
    modulation = diags(cell_centres(n), format="csr")
    return (
        kron(base, identity, format="csr")
        + kron(identity, base, format="csr")
        + interaction_strength * kron(modulation, base, format="csr")
    )


def reduced_response_singular_values(
    side_length: int,
    observation_times: Sequence[float],
    background: BackgroundKind = "smooth_cosine",
    interaction_strength: float = 0.8,
    source_mode_count: int | None = 4,
) -> np.ndarray:
    """Compute directed response singular values by separation in B modes.

    If ``v_l`` is a B eigenvector with eigenvalue ``mu_l``, the response row
    in that mode is

    ``<v_l,q> 1^T exp[-t(L_A+mu_l(I+gD))] H``.

    Thus only ``n`` eigendecompositions of size ``n`` are required.  A fixed
    number of low A modes gives a dimensionally comparable continuum audit.
    ``source_mode_count=None`` instead uses the entire simplex tangent.
    """
    n = side_length
    times = np.asarray(observation_times, dtype=float)
    if times.ndim != 1 or len(times) == 0 or np.any(times < 0.0):
        raise ValueError("observation_times must be nonempty and nonnegative")
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    laplacian = path_graph_laplacian(n, spacing=1.0 / n)
    eigenvalues, eigenvectors = eigh(laplacian)
    if source_mode_count is None:
        source = mixture_tangent_basis(n)
    else:
        if not 1 <= source_mode_count <= n - 1:
            raise ValueError("source_mode_count must lie between one and n-1")
        source = eigenvectors[:, 1 : source_mode_count + 1]
    q = target_background(n, background)
    modulation = np.diag(cell_centres(n))
    identity = np.eye(n)
    ones = np.ones(n)
    gram = np.zeros((source.shape[1], source.shape[1]))

    for mode, mu in enumerate(eigenvalues):
        target_coefficient = float(eigenvectors[:, mode] @ q)
        if abs(target_coefficient) <= 32.0 * np.finfo(float).eps:
            continue
        reduced_generator = laplacian + mu * (
            identity + interaction_strength * modulation
        )
        values, vectors = eigh(reduced_generator)
        spectral_rows = (ones @ vectors)[:, None] * (vectors.T @ source)
        for time in times:
            row = target_coefficient * (
                np.exp(-float(time) * values) @ spectral_rows
            )
            gram += np.outer(row, row)

    singular_squared = np.linalg.eigvalsh(gram)[::-1]
    return np.sqrt(np.maximum(singular_squared, 0.0))


def first_causal_jet_norm(
    side_length: int,
    background: BackgroundKind,
    interaction_strength: float = 0.8,
) -> float:
    """Return the exact Frobenius norm of ``M_B G J_A``.

    For ``J_A=H_A tensor q`` the first coefficient is the rank-one matrix

    ``g (L_B q) (1^T D H_A)``.
    """
    n = side_length
    laplacian = path_graph_laplacian(n, spacing=1.0 / n)
    tangent = mixture_tangent_basis(n)
    q = target_background(n, background)
    modulation_row = np.ones(n) @ np.diag(cell_centres(n)) @ tangent
    return float(
        interaction_strength
        * np.linalg.norm(laplacian @ q)
        * np.linalg.norm(modulation_row)
    )


def closed_form_first_jet_norm(
    side_length: int,
    background: Literal["delta", "smooth_cosine"],
    interaction_strength: float = 0.8,
    cosine_amplitude: float = 0.5,
) -> float:
    """Closed forms for the two Stage V reference backgrounds."""
    n = side_length
    if background == "delta":
        # The selected cell is interior for n >= 3, so ||L e_j||=sqrt(6)n^2.
        if n < 3:
            raise ValueError("the delta formula requires n at least three")
        return float(
            interaction_strength
            * n**2
            * math.sqrt((n**2 - 1.0) / (2.0 * n))
        )
    if background == "smooth_cosine":
        lambda_one = exact_path_eigenvalues(n, spacing=1.0 / n)[1]
        return float(
            interaction_strength
            * cosine_amplitude
            * lambda_one
            * math.sqrt(n**2 - 1.0)
            / (math.sqrt(24.0) * n)
        )
    raise ValueError("unsupported closed-form background")


def causal_jet_rank_upper_bound(
    side_length: int, maximum_order: int, nonstationary_target_modes: int
) -> int:
    """Upper-bound the cumulative response-jet rank through a given order.

    At derivative order k, modal response rows evaluate a vector-valued
    polynomial in the target eigenvalue.  Its constant coefficient vanishes
    and its degree is at most k.  Hence that order adds at most
    ``min(k, target modal support)`` dimensions.
    """
    if side_length < 2 or maximum_order < 0 or nonstationary_target_modes < 0:
        raise ValueError("invalid causal-jet parameters")
    return min(
        side_length - 1,
        sum(
            min(order, nonstationary_target_modes)
            for order in range(1, maximum_order + 1)
        ),
    )


def path_spectrum_audit(
    side_lengths: Sequence[int] = (6, 8, 12, 16, 24, 32, 48, 64)
) -> dict[str, object]:
    """Compare cell-centred and endpoint-labelled low-mode scalings."""
    rows = []
    for n in side_lengths:
        raw_lambda = exact_path_eigenvalues(n)[1]
        cell_value = n**2 * raw_lambda
        endpoint_value = (n - 1) ** 2 * raw_lambda
        rows.append(
            {
                "side_length": int(n),
                "cell_centered_first_eigenvalue": float(cell_value),
                "cell_centered_relative_error": float(cell_value / np.pi**2 - 1.0),
                "endpoint_scaled_first_eigenvalue": float(endpoint_value),
                "endpoint_scaled_relative_error": float(
                    endpoint_value / np.pi**2 - 1.0
                ),
            }
        )
    return {
        "continuum_first_neumann_eigenvalue": float(np.pi**2),
        "rows": rows,
        "exact_formula": "4 h^-2 sin^2(k pi/(2n))",
        "conclusion": (
            "h=1/n is the cell-centred Neumann convention and has O(n^-2) "
            "low-mode error; assigning the same endpoint stencil h=1/(n-1) "
            "introduces an O(n^-1) effective-boundary shift"
        ),
    }


def response_scaling_audit(
    side_lengths: Sequence[int] = (6, 8, 12, 16, 24, 32, 48, 64),
    observation_times: Sequence[float] | None = None,
    interaction_strength: float = 0.8,
    source_mode_count: int = 4,
    microscopic_time_constant: float = 0.1,
) -> dict[str, object]:
    """Track fixed-time spectra and the singular initial layer as n grows."""
    if observation_times is None:
        times = np.geomspace(0.01, 2.0, 20)
    else:
        times = np.asarray(observation_times, dtype=float)
    rows = []
    for n in side_lengths:
        modes = min(source_mode_count, n - 1)
        fixed_delta = reduced_response_singular_values(
            n, times, "delta", interaction_strength, modes
        )
        fixed_smooth = reduced_response_singular_values(
            n, times, "smooth_cosine", interaction_strength, modes
        )
        microscopic_time = microscopic_time_constant / n**2
        micro_delta = reduced_response_singular_values(
            n,
            [microscopic_time],
            "delta",
            interaction_strength,
            source_mode_count=None,
        )[0]
        micro_smooth = reduced_response_singular_values(
            n,
            [microscopic_time],
            "smooth_cosine",
            interaction_strength,
            source_mode_count=None,
        )[0]
        delta_jet = first_causal_jet_norm(n, "delta", interaction_strength)
        smooth_jet = first_causal_jet_norm(
            n, "smooth_cosine", interaction_strength
        )
        rows.append(
            {
                "side_length": int(n),
                "fixed_protocol_delta_singular_values": fixed_delta.tolist(),
                "fixed_protocol_smooth_singular_values": fixed_smooth.tolist(),
                "delta_first_jet_norm": delta_jet,
                "delta_first_jet_over_n_to_5_over_2": float(delta_jet / n**2.5),
                "smooth_first_jet_norm": smooth_jet,
                "microscopic_time": float(microscopic_time),
                "delta_microscopic_leading_singular_value": float(micro_delta),
                "delta_microscopic_leading_over_sqrt_n": float(
                    micro_delta / math.sqrt(n)
                ),
                "smooth_microscopic_leading_singular_value": float(micro_smooth),
                "smooth_microscopic_leading_times_n_squared": float(
                    micro_smooth * n**2
                ),
            }
        )
    smooth_jet_limit = (
        interaction_strength * 0.5 * np.pi**2 / math.sqrt(24.0)
    )
    return {
        "source_mode_count_for_fixed_protocol": source_mode_count,
        "fixed_observation_times": times.tolist(),
        "microscopic_time_constant": microscopic_time_constant,
        "rows": rows,
        "closed_form_limits": {
            "delta_first_jet_over_n_to_5_over_2": float(
                interaction_strength / math.sqrt(2.0)
            ),
            "smooth_first_jet_norm": float(smooth_jet_limit),
        },
        "interpretation": (
            "fixed positive times smooth both delta and smooth backgrounds and "
            "the first fixed low-mode response spectrum stabilizes; at the "
            "initial layer t=c/n^2 the delta response grows as sqrt(n), while "
            "the smooth response decays as n^-2"
        ),
    }


def uniformization_rate(side_length: int, interaction_strength: float = 0.8) -> float:
    """Return the exact maximum exit rate by scanning the separable diagonal."""
    n = side_length
    path_degrees = np.r_[1.0, np.full(n - 2, 2.0), 1.0]
    coordinates = cell_centres(n)
    diagonal = n**2 * (
        path_degrees[:, None]
        + (1.0 + interaction_strength * coordinates[:, None])
        * path_degrees[None, :]
    )
    return float(np.max(diagonal))


def davies_bennett_rate(
    physical_radius: float,
    time: float,
    spacing: float,
    combined_rate_bound: float,
) -> float:
    """Finite-lattice Chernoff rate for signed nearest-neighbour displacement."""
    if physical_radius < 0.0 or time <= 0.0 or spacing <= 0.0:
        raise ValueError("invalid radius, time, or spacing")
    if combined_rate_bound <= 0.0:
        raise ValueError("combined_rate_bound must be positive")
    if physical_radius == 0.0:
        return 0.0
    ratio = physical_radius * spacing / (2.0 * combined_rate_bound * time)
    return float(
        physical_radius / spacing * np.arcsinh(ratio)
        - 2.0
        * combined_rate_bound
        * time
        / spacing**2
        * (math.sqrt(1.0 + ratio**2) - 1.0)
    )


def diffusive_l1_tail_bound(
    physical_radius: float,
    time: float,
    spacing: float,
    interaction_strength: float = 0.8,
) -> float:
    """Four-orthant exponential-martingale bound for physical L1 leakage."""
    rate = davies_bennett_rate(
        physical_radius, time, spacing, 2.0 + interaction_strength
    )
    return float(min(1.0, 4.0 * math.exp(-rate)))


def diffusive_l1_radius(
    time: float,
    spacing: float,
    leakage_tolerance: float = 0.01,
    interaction_strength: float = 0.8,
) -> float:
    """Invert the finite-h martingale leakage bound."""
    if not 0.0 < leakage_tolerance < 1.0:
        raise ValueError("leakage_tolerance must lie in (0,1)")
    target = math.log(4.0 / leakage_tolerance)
    combined = 2.0 + interaction_strength

    def residual(radius: float) -> float:
        return davies_bennett_rate(radius, time, spacing, combined) - target

    upper = math.sqrt(4.0 * combined * time * target) + spacing
    while residual(upper) < 0.0:
        upper *= 2.0
    return float(brentq(residual, 0.0, upper))


def propagation_scaling_audit(
    side_lengths: Sequence[int] = (8, 12, 16, 24, 32, 48, 64),
    time: float = 0.005,
    leakage_tolerance: float = 0.01,
    interaction_strength: float = 0.8,
) -> dict[str, object]:
    """Compare actual, Poisson, and diffusive physical leakage radii."""
    rows = []
    maximum_poisson_violation = 0.0
    maximum_diffusive_violation = 0.0
    for n in side_lengths:
        generator = directed_cell_generator_sparse(n, interaction_strength)
        source_left = n // 2
        source_right = n // 2
        source = source_left * n + source_right
        initial = np.zeros(n * n)
        initial[source] = 1.0
        distribution = expm_multiply(-time * generator, initial)
        left_indices = np.arange(n)[:, None]
        right_indices = np.arange(n)[None, :]
        distances = (
            np.abs(left_indices - source_left)
            + np.abs(right_indices - source_right)
        ).ravel()
        eccentricity = int(np.max(distances))
        actual_radius = eccentricity
        for radius in range(eccentricity + 1):
            if float(np.sum(distribution[distances > radius])) <= leakage_tolerance:
                actual_radius = radius
                break

        rate = uniformization_rate(n, interaction_strength)
        mean = rate * time
        poisson_radius = int(poisson.ppf(1.0 - leakage_tolerance, mean))
        while poisson.sf(poisson_radius, mean) > leakage_tolerance:
            poisson_radius += 1
        while poisson_radius > 0 and poisson.sf(poisson_radius - 1, mean) <= leakage_tolerance:
            poisson_radius -= 1
        spacing = 1.0 / n
        bennett_radius = diffusive_l1_radius(
            time, spacing, leakage_tolerance, interaction_strength
        )

        for threshold in range(1, eccentricity + 1):
            actual_tail = float(np.sum(distribution[distances >= threshold]))
            poisson_bound = float(poisson.sf(threshold - 1, mean))
            diffusive_bound = diffusive_l1_tail_bound(
                threshold * spacing, time, spacing, interaction_strength
            )
            maximum_poisson_violation = max(
                maximum_poisson_violation, actual_tail - poisson_bound
            )
            maximum_diffusive_violation = max(
                maximum_diffusive_violation, actual_tail - diffusive_bound
            )

        rows.append(
            {
                "side_length": int(n),
                "spacing": spacing,
                "uniformization_rate": rate,
                "uniformization_rate_over_n_squared": float(rate / n**2),
                "poisson_mean": mean,
                "actual_graph_radius": actual_radius,
                "actual_physical_radius": float(actual_radius * spacing),
                "poisson_graph_radius": poisson_radius,
                "poisson_uncapped_physical_radius": float(
                    poisson_radius * spacing
                ),
                "poisson_graph_capped_physical_radius": float(
                    min(poisson_radius, eccentricity) * spacing
                ),
                "diffusive_bennett_physical_radius": bennett_radius,
                "source_physical_eccentricity": float(eccentricity * spacing),
            }
        )

    continuum_bennett_radius = math.sqrt(
        4.0
        * (2.0 + interaction_strength)
        * time
        * math.log(4.0 / leakage_tolerance)
    )
    return {
        "time": time,
        "leakage_tolerance": leakage_tolerance,
        "rows": rows,
        "continuum_bennett_radius": float(continuum_bennett_radius),
        "maximum_poisson_bound_violation": float(maximum_poisson_violation),
        "maximum_diffusive_bound_violation": float(maximum_diffusive_violation),
        "conclusion": (
            "under diffusive scaling Lambda is Theta(n^2), so the uncapped "
            "Poisson jump-count radius grows linearly in physical units and "
            "the capped bound becomes the whole domain; the signed-jump "
            "martingale radius has a finite Gaussian continuum limit"
        ),
    }


def thermodynamic_flattening_audit(
    side_lengths: Sequence[int] = (8, 12, 16, 24, 32, 48, 64),
    interaction_strength: float = 0.8,
) -> dict[str, object]:
    """Show that stretching ``D_i=d(i/n)`` kills a localized fixed-h arrow."""
    rows = []
    for n in side_lengths:
        laplacian = path_graph_laplacian(n)
        q = target_background(n, "delta")
        coordinates = cell_centres(n)
        left = n // 2 - 1
        right = n // 2
        local_contrast = np.zeros(n)
        local_contrast[left] = 1.0 / math.sqrt(2.0)
        local_contrast[right] = -1.0 / math.sqrt(2.0)
        modulation_factor = abs(coordinates @ local_contrast)
        jet_norm = (
            interaction_strength
            * modulation_factor
            * np.linalg.norm(laplacian @ q)
        )
        rows.append(
            {
                "side_length": int(n),
                "localized_first_jet_norm": float(jet_norm),
                "n_times_localized_first_jet_norm": float(n * jet_norm),
            }
        )
    return {
        "fixed_lattice_spacing": 1.0,
        "stretched_profile": "D_i=(i+1/2)/n",
        "rows": rows,
        "exact_n_times_limit": float(
            interaction_strength * math.sqrt(3.0)
        ),
        "conclusion": (
            "in an expanding domain the normalized profile becomes locally "
            "constant and a nearest-neighbour A contrast has arrow strength "
            "g sqrt(3)/n; a nontrivial infinite-volume arrow requires a "
            "fixed-physical-scale bounded modulation profile"
        ),
    }


def run_scaling_experiment(
    maximum_side_length: int = 64,
    interaction_strength: float = 0.8,
) -> dict[str, object]:
    """Run the complete fixed-domain and expanding-domain scaling audit."""
    candidates = (6, 8, 12, 16, 24, 32, 48, 64)
    sizes = tuple(n for n in candidates if n <= maximum_side_length)
    if len(sizes) < 2:
        raise ValueError("maximum_side_length must include at least two audit sizes")
    propagation_sizes = tuple(n for n in sizes if n >= 8)
    return {
        "model": "OIG Stage V fixed-domain continuum and scale-flow audit",
        "scope": (
            "cell-centred Neumann finite-volume paths; fixed bounded modulation "
            "D(x)=x; finite linear Markov toy model"
        ),
        "continuum_operator": (
            "partial_t p = partial_a^2 p + (1+g a) partial_b^2 p, "
            "with reflecting boundaries"
        ),
        "parameters": {
            "side_lengths": list(sizes),
            "interaction_strength": interaction_strength,
        },
        "path_spectrum": path_spectrum_audit(sizes),
        "directed_response_scaling": response_scaling_audit(
            sizes, interaction_strength=interaction_strength
        ),
        "causal_jet_rank_theorem": {
            "bound": (
                "rank J_<=r <= min(n-1, sum_{k=1}^r min(k,s)), where s "
                "is the number of nonstationary target modes"
            ),
            "single_mode_bounds_orders_1_to_6": [
                causal_jet_rank_upper_bound(64, order, 1)
                for order in range(1, 7)
            ],
            "broadband_bounds_orders_1_to_6": [
                causal_jet_rank_upper_bound(64, order, 63)
                for order in range(1, 7)
            ],
        },
        "propagation_scale_flow": propagation_scaling_audit(
            propagation_sizes, interaction_strength=interaction_strength
        ),
        "expanding_domain_control": thermodynamic_flattening_audit(
            propagation_sizes, interaction_strength
        ),
        "limit_separation": {
            "fixed_domain_refinement": (
                "h=1/n, domain length one, h^-2 L_n, fixed physical times"
            ),
            "infinite_volume": (
                "h fixed and n to infinity; the spectral gap closes and the "
                "modulation profile must be specified in physical coordinates"
            ),
            "joint_limit": (
                "h_n to zero and n h_n to infinity; neither preceding result "
                "transfers without uniform profile and localization assumptions"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maximum-side-length", type=int, default=64)
    parser.add_argument("--interaction-strength", type=float, default=0.8)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            run_scaling_experiment(
                arguments.maximum_side_length, arguments.interaction_strength
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
