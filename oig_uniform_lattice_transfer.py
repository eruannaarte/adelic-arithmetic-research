#!/usr/bin/env python3
"""Descriptive general-tau laboratory for OIG finite lattice transfer.

This module extends the Stage XII K=2 noncommuting cell-centred Neumann
benchmark away from the single point ``tau=1``.  It intentionally uses
binary64 SciPy calculations: its scans and fitted rates are evidence and
certificate-design diagnostics, not outward-rounded proofs.

The compared objects are

    G(tau)   = sqrt(1+tau) int_0^1 F(tau*omega(xi)) F(...)^T dxi,

and the complete finite response Gram formed with

    exp[-tau (L_n + omega_{n,l} V_n)].

The finite calculation retains all diffusion--modulation words.  Odd grids
place a one-cell target exactly at x=1/2, making its odd target-mode
coefficients exactly zero.  Even-grid one-cell targets are deliberately
treated as a different, displaced experiment.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Literal

import numpy as np
from scipy.integrate import quad_vec
from scipy.linalg import eigh_tridiagonal
from scipy.sparse import diags
from scipy.sparse.linalg import expm_multiply


INTERACTION_STRENGTH = 4.0 / 5.0
SOURCE_MODES = (1, 2)
Metric = Literal["L2", "declared_H1", "natural_discrete_H1"]


def phase_profile(mode: int, s: np.ndarray | float) -> np.ndarray | float:
    """Return the affine-ramp continuum response F_k(s).

    The closed form avoids a nested spatial quadrature:

      F_k(s) = sqrt(2) exp(-s) a[1-(-1)^k exp(-a)]/(a^2+(k*pi)^2),
      a = (4/5)s.
    """
    if mode < 1:
        raise ValueError("mode must be positive")
    values = np.asarray(s, dtype=float)
    a = INTERACTION_STRENGTH * values
    parity = -1.0 if mode % 2 else 1.0
    answer = (
        math.sqrt(2.0)
        * np.exp(-values)
        * a
        * (1.0 - parity * np.exp(-a))
        / (a * a + (mode * math.pi) ** 2)
    )
    if values.ndim == 0:
        return float(answer)
    return answer


def _packed_outer(vector: np.ndarray) -> np.ndarray:
    return np.array(
        [vector[0] * vector[0], vector[0] * vector[1], vector[1] * vector[1]],
        dtype=float,
    )


def _unpack_symmetric(packed: np.ndarray) -> np.ndarray:
    return np.array(
        [[packed[0], packed[1]], [packed[1], packed[2]]], dtype=float
    )


def continuum_gram(
    tau: float,
    *,
    epsabs: float = 2.0e-13,
    epsrel: float = 2.0e-13,
) -> np.ndarray:
    """Compute the normalized K=2 continuum lattice Gram descriptively."""
    if not math.isfinite(tau) or tau <= 0.0:
        raise ValueError("tau must be finite and positive")

    def integrand(xi: float) -> np.ndarray:
        omega = 4.0 * math.sin(0.5 * math.pi * xi) ** 2
        response = np.array(
            [phase_profile(mode, tau * omega) for mode in SOURCE_MODES]
        )
        return _packed_outer(response)

    packed, _ = quad_vec(
        integrand, 0.0, 1.0, epsabs=epsabs, epsrel=epsrel, limit=500
    )
    return math.sqrt(1.0 + tau) * _unpack_symmetric(packed)


def response_correction(mode: int, tau: float, omega: float) -> float:
    """Candidate n^-2 coefficient for the general-tau modal response.

    This is the direct fixed-tau extension of the proved Stage XII formula.
    Put s=tau*omega.  Midpoint quadrature contributes ``s*g*B/24``;
    the first weak Duhamel insertion is multiplied by tau.  Uniform control
    of the remainder when tau grows with n is a theorem target, not a result
    asserted by this binary64 laboratory.
    """
    if mode < 1:
        raise ValueError("mode must be positive")
    if tau <= 0.0 or omega < 0.0:
        raise ValueError("tau must be positive and omega nonnegative")
    s = tau * omega
    boundary = math.sqrt(2.0) * (
        ((-1.0) ** mode) * math.exp(-(1.0 + INTERACTION_STRENGTH) * s)
        - math.exp(-s)
    )
    profile = float(phase_profile(mode, s))
    midpoint = s * INTERACTION_STRENGTH * boundary / 24.0
    dynamical = tau * (
        s * INTERACTION_STRENGTH * boundary / 2.0
        + s * s * INTERACTION_STRENGTH**2 * profile / 3.0
    )
    return midpoint + dynamical


def leading_error_matrix(
    tau: float,
    *,
    epsabs: float = 2.0e-13,
    epsrel: float = 2.0e-13,
) -> np.ndarray:
    """Candidate E(tau) in G_n-G=E(tau)/n^2+o(n^-2), fixed tau."""
    if not math.isfinite(tau) or tau <= 0.0:
        raise ValueError("tau must be finite and positive")

    def integrand(xi: float) -> np.ndarray:
        omega = 4.0 * math.sin(0.5 * math.pi * xi) ** 2
        response = np.array(
            [phase_profile(mode, tau * omega) for mode in SOURCE_MODES]
        )
        correction = np.array(
            [response_correction(mode, tau, omega) for mode in SOURCE_MODES]
        )
        matrix = np.outer(response, correction) + np.outer(correction, response)
        return np.array([matrix[0, 0], matrix[0, 1], matrix[1, 1]])

    packed, _ = quad_vec(
        integrand, 0.0, 1.0, epsabs=epsabs, epsrel=epsrel, limit=500
    )
    return math.sqrt(1.0 + tau) * _unpack_symmetric(packed)


def atomic_tail_gram(
    *, epsabs: float = 2.0e-13, epsrel: float = 2.0e-13
) -> np.ndarray:
    """Compute the tau->infinity normalized atomic-tail Gram.

    With y=sqrt(tau) xi and tau*omega(xi)->pi^2 y^2, the limit is

      H = int_0^infinity F(pi^2 y^2) F(pi^2 y^2)^T dy.
    """

    def integrand(y: float) -> np.ndarray:
        s = (math.pi * y) ** 2
        response = np.array([phase_profile(mode, s) for mode in SOURCE_MODES])
        return _packed_outer(response)

    packed, _ = quad_vec(
        integrand, 0.0, np.inf, epsabs=epsabs, epsrel=epsrel, limit=500
    )
    return _unpack_symmetric(packed)


def source_ports(side_length: int) -> np.ndarray:
    """Return the two orthonormal cell-centred DCT source columns."""
    if side_length <= max(SOURCE_MODES):
        raise ValueError("side_length must exceed both source modes")
    cells = (np.arange(side_length, dtype=float) + 0.5) / side_length
    return math.sqrt(2.0 / side_length) * np.column_stack(
        [np.cos(mode * math.pi * cells) for mode in SOURCE_MODES]
    )


def target_coefficients(
    side_length: int, carrier_cell: int | None = None
) -> np.ndarray:
    """Return DCT coefficients of a one-cell atomic target.

    The default is the central cell for odd n and the left-central cell for
    even n.  Thus only odd n represents an exactly centred one-cell target.
    """
    if side_length < 1:
        raise ValueError("side_length must be positive")
    if carrier_cell is None:
        carrier_cell = (side_length - 1) // 2
    if not 0 <= carrier_cell < side_length:
        raise ValueError("carrier_cell is outside the grid")
    modes = np.arange(side_length, dtype=float)
    coefficients = np.empty(side_length, dtype=float)
    coefficients[0] = 1.0 / math.sqrt(side_length)
    coefficients[1:] = math.sqrt(2.0 / side_length) * np.cos(
        math.pi
        * modes[1:]
        * (carrier_cell + 0.5)
        / side_length
    )
    return coefficients


def _response_for_target_mode(
    side_length: int,
    target_mode: int,
    tau: float,
    sources: np.ndarray,
    *,
    method: Literal["auto", "krylov", "low_spectrum"] = "auto",
    spectral_cutoff: float = 36.0,
) -> np.ndarray:
    """Evaluate both normalized source responses for one target mode."""
    n = side_length
    omega = 4.0 * math.sin(math.pi * target_mode / (2.0 * n)) ** 2
    x = (np.arange(n, dtype=float) + 0.5) / n
    laplacian_diagonal = np.full(n, 2.0)
    laplacian_diagonal[[0, -1]] = 1.0
    diagonal = laplacian_diagonal + omega * (
        1.0 + INTERACTION_STRENGTH * x
    )
    if method == "auto":
        method = "low_spectrum" if tau >= 12.0 else "krylov"
    if method == "krylov":
        generator = diags(
            (-np.ones(n - 1), diagonal, -np.ones(n - 1)),
            offsets=(-1, 0, 1),
            format="csc",
        )
        evolved = expm_multiply(
            -tau * generator,
            sources,
            traceA=-tau * float(diagonal.sum()),
        )
        return np.asarray(evolved.sum(axis=0), dtype=float) / math.sqrt(n)
    if method != "low_spectrum":
        raise ValueError("method must be auto, krylov, or low_spectrum")

    # Every omitted eigencomponent is attenuated by at least exp(-cutoff).
    # This truncation is excellent descriptive numerics, but is not used as
    # an outward-rounded bound in this laboratory.
    eigenvalues, eigenvectors = eigh_tridiagonal(
        diagonal,
        -np.ones(n - 1),
        select="v",
        select_range=(-1.0e-12, spectral_cutoff / tau),
        check_finite=False,
        lapack_driver="stebz",
    )
    if eigenvalues.size == 0:
        return np.zeros(2)
    uniform_projection = eigenvectors.sum(axis=0) / math.sqrt(n)
    source_projection = eigenvectors.T @ sources
    return (uniform_projection * np.exp(-tau * eigenvalues)) @ source_projection


def finite_neumann_gram(
    side_length: int,
    tau: float,
    *,
    carrier_cell: int | None = None,
    exploit_exact_centre: bool = True,
    method: Literal["auto", "krylov", "low_spectrum"] = "auto",
    spectral_cutoff: float = 36.0,
) -> np.ndarray:
    """Compute the complete finite noncommuting K=2 response Gram.

    This is a binary64 diagnostic.  ``expm_multiply`` applies the exponential
    of the actual tridiagonal sum; it is not the multiplication-phase model.
    """
    if side_length <= max(SOURCE_MODES):
        raise ValueError("side_length must exceed both source modes")
    if not math.isfinite(tau) or tau <= 0.0:
        raise ValueError("tau must be finite and positive")
    n = side_length
    if carrier_cell is None:
        carrier_cell = (n - 1) // 2
    coefficients = target_coefficients(n, carrier_cell)
    sources = source_ports(n)
    result = np.zeros((2, 2), dtype=float)

    exact_centre = n % 2 == 1 and carrier_cell == (n - 1) // 2
    target_modes: Iterable[int]
    if exploit_exact_centre and exact_centre:
        target_modes = range(2, n, 2)
    else:
        target_modes = range(1, n)

    for target_mode in target_modes:
        omega = 4.0 * math.sin(math.pi * target_mode / (2.0 * n)) ** 2
        if method != "krylov" and tau >= 12.0 and tau * omega > spectral_cutoff:
            # A >= omega I.  The omitted normalized response is therefore at
            # most exp(-spectral_cutoff) in magnitude.
            continue
        response = _response_for_target_mode(
            n,
            target_mode,
            tau,
            sources,
            method=method,
            spectral_cutoff=spectral_cutoff,
        )
        result += coefficients[target_mode] ** 2 * np.outer(response, response)
    return math.sqrt(1.0 + tau) * result


def continuum_cost_diagonal() -> np.ndarray:
    return np.array([1.0 + (mode * math.pi) ** 2 for mode in SOURCE_MODES])


def natural_discrete_cost_diagonal(side_length: int) -> np.ndarray:
    if side_length <= max(SOURCE_MODES):
        raise ValueError("side_length must exceed both source modes")
    n = side_length
    return np.array(
        [
            1.0
            + n
            * n
            * 4.0
            * math.sin(math.pi * mode / (2.0 * n)) ** 2
            for mode in SOURCE_MODES
        ]
    )


def whitened_gram(gram: np.ndarray, cost_diagonal: np.ndarray) -> np.ndarray:
    inverse_sqrt = 1.0 / np.sqrt(np.asarray(cost_diagonal, dtype=float))
    return inverse_sqrt[:, None] * gram * inverse_sqrt[None, :]


def transfer_error(
    finite: np.ndarray,
    continuum: np.ndarray,
    *,
    metric: Metric,
    side_length: int,
) -> float:
    """Return the descriptive operator-norm transfer error."""
    if metric == "L2":
        error = finite - continuum
    elif metric == "declared_H1":
        cost = continuum_cost_diagonal()
        error = whitened_gram(finite, cost) - whitened_gram(continuum, cost)
    elif metric == "natural_discrete_H1":
        error = whitened_gram(
            finite, natural_discrete_cost_diagonal(side_length)
        ) - whitened_gram(continuum, continuum_cost_diagonal())
    else:
        raise ValueError("unknown metric")
    return float(np.linalg.norm(error, ord=2))


def spectral_floor(gram: np.ndarray, cost_diagonal: np.ndarray) -> float:
    """Smallest eigenvalue after source-cost whitening."""
    return float(np.linalg.eigvalsh(whitened_gram(gram, cost_diagonal))[0])


@dataclass(frozen=True)
class ScanRow:
    tau: float
    side_length: int
    ratio_n_over_sqrt_tau: float
    l2_error: float
    declared_h1_error: float
    natural_discrete_h1_error: float
    continuum_l2_floor: float
    continuum_h1_floor: float


def comparison_row(tau: float, side_length: int) -> ScanRow:
    continuum = continuum_gram(tau)
    finite = finite_neumann_gram(side_length, tau)
    return ScanRow(
        tau=tau,
        side_length=side_length,
        ratio_n_over_sqrt_tau=side_length / math.sqrt(tau),
        l2_error=transfer_error(
            finite, continuum, metric="L2", side_length=side_length
        ),
        declared_h1_error=transfer_error(
            finite,
            continuum,
            metric="declared_H1",
            side_length=side_length,
        ),
        natural_discrete_h1_error=transfer_error(
            finite,
            continuum,
            metric="natural_discrete_H1",
            side_length=side_length,
        ),
        continuum_l2_floor=spectral_floor(continuum, np.ones(2)),
        continuum_h1_floor=spectral_floor(
            continuum, continuum_cost_diagonal()
        ),
    )


def make_odd(value: int) -> int:
    value = max(value, 3)
    return value if value % 2 else value + 1


def empirical_order(errors: list[float], resolutions: list[float]) -> float:
    if len(errors) != len(resolutions) or len(errors) < 2:
        raise ValueError("at least two paired samples are required")
    slope = np.polyfit(np.log(resolutions), np.log(errors), 1)[0]
    return float(-slope)


def conservative_tau_lipschitz_bound(
    tau_lower: float, *, metric: Metric = "L2"
) -> float:
    """Evaluate an analytically justified coarse envelope for cover planning.

    It uses only contraction and ||L_n+omega V_n|| <= 56/5.  The same
    estimate with ||omega V|| <= 36/5 applies to the continuum object.
    Whitening can only reduce it for the three declared diagonal metrics.
    The displayed formula is a valid real-arithmetic bound, but this function
    evaluates it in binary64 and is therefore not an outward certificate.
    A practical proof should use exact rationals or interval-enclosed local
    derivatives.
    """
    if tau_lower <= 0.0:
        raise ValueError("tau_lower must be positive")
    if metric not in ("L2", "declared_H1", "natural_discrete_H1"):
        raise ValueError("unknown metric")
    normalization = math.sqrt(1.0 + tau_lower)
    normalization_derivative = 0.5 / normalization
    finite_bound = normalization_derivative + 2.0 * normalization * (56.0 / 5.0)
    continuum_bound = normalization_derivative + 2.0 * normalization * (36.0 / 5.0)
    # A symmetric 2x2 matrix has spectral norm at most twice its largest
    # entry magnitude.  Apply that safe conversion after summing the finite
    # and continuum entrywise derivative envelopes.
    return 2.0 * (finite_bound + continuum_bound)


def default_experiment() -> dict[str, object]:
    """Run a compact, fixed-n-tail, and joint-scaling diagnostic suite."""
    compact_taus = (1.0, 2.0, 4.0, 8.0)
    compact_ns = (41, 81)
    compact = [
        comparison_row(tau, n)
        for tau in compact_taus
        for n in compact_ns
    ]

    fixed_n_taus = (16.0, 64.0, 256.0, 1024.0)
    fixed_n = 31
    fixed_rows = [comparison_row(tau, fixed_n) for tau in fixed_n_taus]

    # n ~ tau^(3/4) makes n/sqrt(tau)=tau^(1/4)->infinity.  A generous
    # prefactor exposes the asymptotic regime at computationally modest tau.
    joint_taus = (4.0, 16.0, 64.0, 256.0)
    joint_rows = [
        comparison_row(tau, make_odd(math.ceil(12.0 * tau ** 0.75)))
        for tau in joint_taus
    ]

    tail = atomic_tail_gram()
    continuum_tail_rows = []
    for tau in fixed_n_taus:
        continuum = continuum_gram(tau)
        continuum_tail_rows.append(
            {
                "tau": tau,
                "continuum_to_tail_l2": float(
                    np.linalg.norm(continuum - tail, ord=2)
                ),
            }
        )

    compact_rates: list[dict[str, float]] = []
    for tau in compact_taus:
        selected = [row for row in compact if row.tau == tau]
        coefficient = leading_error_matrix(tau)
        compact_rates.append(
            {
                "tau": tau,
                "l2_order_from_n41_n81": empirical_order(
                    [row.l2_error for row in selected],
                    [row.side_length for row in selected],
                ),
                "candidate_E_spectral_norm": float(
                    np.linalg.norm(coefficient, ord=2)
                ),
                "n81_scaled_matrix_residual": float(
                    np.linalg.norm(
                        81.0**2
                        * (
                            finite_neumann_gram(81, tau)
                            - continuum_gram(tau)
                        )
                        - coefficient,
                        ord=2,
                    )
                ),
            }
        )

    tail_coefficient = leading_error_matrix(1024.0) / 1024.0

    return {
        "schema_version": "oig-uniform-lattice-transfer-lab-v1",
        "status": "descriptive binary64 evidence; not a proof certificate",
        "model": {
            "source_modes": list(SOURCE_MODES),
            "interaction_strength": INTERACTION_STRENGTH,
            "target": "one central cell on odd grids",
            "normalization": "sqrt(1+tau)",
            "finite_generator": "L_n + omega_(n,l) V_n (noncommuting)",
        },
        "atomic_tail_gram": tail.tolist(),
        "compact_scan": [asdict(row) for row in compact],
        "compact_empirical_orders": compact_rates,
        "fixed_n_tail_control": [asdict(row) for row in fixed_rows],
        "continuum_tail_check": continuum_tail_rows,
        "joint_n_over_sqrt_tau_scan": [asdict(row) for row in joint_rows],
        "large_tau_candidate_E_over_tau_at_tau1024": tail_coefficient.tolist(),
        "cover_planning": {
            "coarse_l2_tau_derivative_bound_at_tau_1": conservative_tau_lipschitz_bound(1.0),
            "recommendation": (
                "enclose Gram values and local tau derivatives with Arb Taylor "
                "models; subdivide until value margin exceeds derivative radius"
            ),
        },
        "scope": (
            "All reported transfer errors and empirical orders are binary64 "
            "diagnostics. They suggest resolution and cover laws but prove none."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="optional JSON output path")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="print one inexpensive tau=1,n=21 comparison instead of the full suite",
    )
    args = parser.parse_args()
    if args.quick:
        result: object = {
            "status": "descriptive binary64 evidence; not a proof certificate",
            "row": asdict(comparison_row(1.0, 21)),
        }
    else:
        result = default_experiment()
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(payload + "\n")
    print(payload)


if __name__ == "__main__":
    main()
