"""Exact selection certificates for a declared finite library of query designs.

This module composes the sealed reports produced by
``oig_query_protocol_design``.  It does not optimize over a continuum of
protocols.  Instead, it proves what can be concluded from a finite, explicitly
embedded candidate list:

* every finite candidate is independently identifiable and has a certified
  rational interval ``[lower_i, upper_i]`` for its squared minimax query
  amplification;
* the best value in the declared library lies in
  ``[min_i lower_i, min_i upper_i]``;
* the selected candidate has the smallest certified upper bound (with a
  deterministic declaration-order tie break); and
* uniqueness is asserted only when the selected upper bound is strictly below
  every other identifiable candidate's lower bound.

Unidentifiable candidates have infinite minimax loss under the unbounded-source
model used by the child theorem and are excluded from the finite minima.  Every
report embeds the complete child certificates, so the public verifier can
reconstruct the selection without access to the original Python objects.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from oig_protocol_design_engine import ExactScalar
from oig_query_protocol_design import (
    QueryProtocol,
    certify_query_independent_nuisance_mixture,
    certify_query_model,
    certify_query_protocol_mixture,
    verify_query_protocol_report,
)


Q = Fraction


_SCHEMA = "oig-query-candidate-library-certificate-v1"
_STATUS = "exact finite query-candidate-library certificate"
_OBJECTIVE = "minimize squared minimax query amplification over the declared finite library"
_SCOPE = (
    "The comparison is exactly over the embedded finite candidate list under one "
    "exact common source/query/noise-radius contract; no unlisted protocol, budget "
    "mixture, or continuous design family is optimized or excluded."
)
_PROOF_BOUNDARY = (
    "This certificate composes exact finite-dimensional rational child certificates. "
    "It proves a minimax bracket and, when separated, a unique winner only within the "
    "declared finite library and its embedded common comparison contract. It makes no "
    "continuous-design global-optimality, cross-query comparison, or external physical-"
    "model enclosure claim."
)
_DATA_NOISE_RADIUS_CONVENTION = (
    "For every candidate i, the same numerical epsilon bounds ||eta_i|| in that "
    "candidate's declared output metric W_i; query error is measured in the common "
    "declared query metric. Candidate-specific W_i is part of the calibrated design."
)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _strict_json_equal(left: object, right: object) -> bool:
    """Compare JSON-like objects without treating booleans as integers."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _strict_json_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _strict_json_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def _candidate_name(value: object) -> str:
    if type(value) is not str or not value or value.strip() != value:
        raise ValueError("candidate names must be nonempty, trimmed JSON strings")
    return value


@dataclass(frozen=True)
class QueryCandidate:
    """One named, sealed query certificate offered to the finite selector.

    The class methods are convenience constructors for the three child-model
    semantics.  ``from_report`` also permits a previously generated sealed
    child certificate to participate without recomputing it.
    """

    name: str
    query_certificate: dict[str, object]

    @classmethod
    def from_report(
        cls, name: str, query_certificate: dict[str, object]
    ) -> "QueryCandidate":
        return cls(_candidate_name(name), deepcopy(query_certificate))

    @classmethod
    def single_model(
        cls,
        name: str,
        observation: Sequence[Sequence[ExactScalar]],
        nuisance_response: Sequence[Sequence[ExactScalar]] | None,
        source_metric: Sequence[Sequence[ExactScalar]],
        output_metric: Sequence[Sequence[ExactScalar]],
        query: Sequence[Sequence[ExactScalar]],
        query_metric: Sequence[Sequence[ExactScalar]],
        *,
        amplification_vector_scale: int = 10**8,
    ) -> "QueryCandidate":
        return cls.from_report(
            name,
            certify_query_model(
                observation,
                nuisance_response,
                source_metric,
                output_metric,
                query,
                query_metric,
                amplification_vector_scale=amplification_vector_scale,
            ),
        )

    @classmethod
    def shared_mixture(
        cls,
        name: str,
        protocols: Sequence[QueryProtocol],
        budget_shares: Sequence[ExactScalar],
        source_metric: Sequence[Sequence[ExactScalar]],
        query: Sequence[Sequence[ExactScalar]],
        query_metric: Sequence[Sequence[ExactScalar]],
        *,
        amplification_vector_scale: int = 10**8,
    ) -> "QueryCandidate":
        return cls.from_report(
            name,
            certify_query_protocol_mixture(
                protocols,
                budget_shares,
                source_metric,
                query,
                query_metric,
                amplification_vector_scale=amplification_vector_scale,
            ),
        )

    @classmethod
    def independent_mixture(
        cls,
        name: str,
        protocols: Sequence[QueryProtocol],
        budget_shares: Sequence[ExactScalar],
        source_metric: Sequence[Sequence[ExactScalar]],
        query: Sequence[Sequence[ExactScalar]],
        query_metric: Sequence[Sequence[ExactScalar]],
        *,
        amplification_vector_scale: int = 10**8,
    ) -> "QueryCandidate":
        return cls.from_report(
            name,
            certify_query_independent_nuisance_mixture(
                protocols,
                budget_shares,
                source_metric,
                query,
                query_metric,
                amplification_vector_scale=amplification_vector_scale,
            ),
        )


CandidateInput = QueryCandidate | tuple[str, dict[str, object]]


def _normalize_candidates(
    candidates: Sequence[CandidateInput],
) -> tuple[tuple[str, dict[str, object]], ...]:
    if not candidates:
        raise ValueError("the declared candidate library must be nonempty")
    normalized: list[tuple[str, dict[str, object]]] = []
    names: set[str] = set()
    for candidate in candidates:
        if isinstance(candidate, QueryCandidate):
            name = _candidate_name(candidate.name)
            child = candidate.query_certificate
        elif type(candidate) is tuple and len(candidate) == 2:
            name = _candidate_name(candidate[0])
            child = candidate[1]
        else:
            raise TypeError(
                "each candidate must be QueryCandidate or a (name, sealed_report) tuple"
            )
        if name in names:
            raise ValueError(f"duplicate candidate name: {name}")
        if type(child) is not dict:
            raise TypeError("each query certificate must be a JSON object")
        names.add(name)
        normalized.append((name, deepcopy(child)))
    return tuple(normalized)


def _child_interval(
    child: dict[str, object],
) -> tuple[str, Fraction | None, Fraction | None, dict[str, object]]:
    verification = verify_query_protocol_report(child)
    if verification.get("passed") is not True:
        raise ValueError(f"a child query certificate failed verification: {verification}")

    identifiability = child.get("identifiability")
    factorization = child.get("factorization_and_minimax")
    if type(identifiability) is not dict or type(factorization) is not dict:
        raise ValueError("a child query certificate is missing theorem blocks")
    identifiable = identifiability.get("query_identifiable_exact")
    if type(identifiable) is not bool:
        raise ValueError("a child identifiability decision is not Boolean")
    if not identifiable:
        if factorization.get("kind") != "unidentifiable-unbounded-source":
            raise ValueError("an unidentifiable child has inconsistent minimax semantics")
        return "unidentifiable-infinite-loss", None, None, verification

    lower_raw = factorization.get("minimax_amplification_squared_lower_exact")
    upper_raw = factorization.get("minimax_amplification_squared_upper_exact")
    if type(lower_raw) is not str or type(upper_raw) is not str:
        raise ValueError("an identifiable child is missing exact rational bounds")
    lower = Q(lower_raw)
    upper = Q(upper_raw)
    if lower < 0 or lower > upper:
        raise ValueError("a child minimax interval is not ordered and nonnegative")
    if lower_raw != _fraction_text(lower) or upper_raw != _fraction_text(upper):
        raise ValueError("a child minimax bound is not canonically serialized")
    classification = (
        "identifiable-zero-query" if upper == 0 else "identifiable-finite-loss"
    )
    return classification, lower, upper, verification


def _comparison_contract(child: dict[str, object]) -> dict[str, object]:
    """Extract the exact scientific contract that must be common to the library."""
    source_dimension = child.get("source_dimension")
    query_dimension = child.get("query_dimension")
    if type(source_dimension) is not int or type(query_dimension) is not int:
        raise ValueError("a child certificate has malformed source/query dimensions")
    source_metric = child.get("declared_source_metric_exact")
    query = child.get("declared_query_exact")
    query_metric = child.get("declared_query_metric_exact")
    if type(source_metric) is not list or type(query) is not list or type(query_metric) is not list:
        raise ValueError("a child certificate is missing exact source/query declarations")
    return {
        "source_dimension": source_dimension,
        "declared_source_metric_exact": deepcopy(source_metric),
        "query_dimension": query_dimension,
        "declared_query_exact": deepcopy(query),
        "declared_query_metric_exact": deepcopy(query_metric),
        "data_noise_radius_convention": _DATA_NOISE_RADIUS_CONVENTION,
        "same_numerical_epsilon_across_candidates": True,
        "candidate_output_metrics_are_calibrated_design_declarations": True,
        "common_contract_verified_exact": True,
    }


def _contract_mismatches(
    reference: dict[str, object], candidate: dict[str, object]
) -> list[str]:
    return [
        key
        for key in reference
        if not _strict_json_equal(reference[key], candidate.get(key))
    ]


def _build_core(
    named_children: Sequence[tuple[str, dict[str, object]]],
) -> dict[str, object]:
    if not named_children:
        raise ValueError("the declared candidate library must be nonempty")

    rows: list[dict[str, object]] = []
    finite: list[tuple[int, str, Fraction, Fraction]] = []
    seen: set[str] = set()
    common_contract: dict[str, object] | None = None
    for index, (raw_name, raw_child) in enumerate(named_children):
        name = _candidate_name(raw_name)
        if name in seen:
            raise ValueError(f"duplicate candidate name: {name}")
        if type(raw_child) is not dict:
            raise TypeError("each embedded query certificate must be a JSON object")
        seen.add(name)
        child = deepcopy(raw_child)
        classification, lower, upper, child_verification = _child_interval(child)
        candidate_contract = _comparison_contract(child)
        if common_contract is None:
            common_contract = candidate_contract
        else:
            mismatches = _contract_mismatches(common_contract, candidate_contract)
            if mismatches:
                raise ValueError(
                    f"candidate {name!r} violates the exact common comparison contract: "
                    + ", ".join(mismatches)
                )
        eligible = lower is not None and upper is not None
        if eligible:
            finite.append((index, name, lower, upper))  # type: ignore[arg-type]
        rows.append(
            {
                "index": index,
                "name": name,
                "query_certificate": child,
                "child_exact_verification": child_verification,
                "classification": classification,
                "finite_minimax_eligible": eligible,
                "kappa_squared_lower_exact": (
                    None if lower is None else _fraction_text(lower)
                ),
                "kappa_squared_upper_exact": (
                    None if upper is None else _fraction_text(upper)
                ),
            }
        )

    if common_contract is None:
        raise AssertionError("a nonempty library lost its common comparison contract")

    if not finite:
        selection: dict[str, object] = {
            "outcome": "no-identifiable-candidate",
            "selected_candidate_index": None,
            "selected_candidate_name": None,
            "selection_rule": "smallest certified upper bound, declaration-order tie break",
            "library_optimum_kappa_squared_lower_exact": None,
            "library_optimum_kappa_squared_upper_exact": None,
            "unique_winner_certified": False,
            "unique_winner_basis": "no finite candidate exists",
            "competitor_checks": [],
        }
    else:
        selected = min(finite, key=lambda item: (item[3], item[0]))
        selected_index, selected_name, _, selected_upper = selected
        library_lower = min(item[2] for item in finite)
        library_upper = min(item[3] for item in finite)
        if library_upper != selected_upper:
            raise AssertionError("selection and finite-library upper bound disagree")
        checks = [
            {
                "competitor_index": index,
                "competitor_name": name,
                "competitor_lower_exact": _fraction_text(lower),
                "selected_upper_exact": _fraction_text(selected_upper),
                "selected_upper_strictly_below_competitor_lower": (
                    selected_upper < lower
                ),
            }
            for index, name, lower, _ in finite
            if index != selected_index
        ]
        unique = all(
            check["selected_upper_strictly_below_competitor_lower"] is True
            for check in checks
        )
        if not checks:
            unique_basis = "only identifiable candidate in the declared library"
        elif unique:
            unique_basis = "selected upper is strictly below every other identifiable lower"
        else:
            unique_basis = "certified intervals overlap or touch for at least one competitor"
        selection = {
            "outcome": "finite-candidate-selected",
            "selected_candidate_index": selected_index,
            "selected_candidate_name": selected_name,
            "selection_rule": "smallest certified upper bound, declaration-order tie break",
            "library_optimum_kappa_squared_lower_exact": _fraction_text(library_lower),
            "library_optimum_kappa_squared_upper_exact": _fraction_text(library_upper),
            "unique_winner_certified": unique,
            "unique_winner_basis": unique_basis,
            "competitor_checks": checks,
        }

    return {
        "schema_version": _SCHEMA,
        "status": _STATUS,
        "objective": _OBJECTIVE,
        "comparison_scope": _SCOPE,
        "comparison_contract": common_contract,
        "continuous_design_optimality_claimed": False,
        "candidate_count": len(rows),
        "identifiable_candidate_count": len(finite),
        "candidates": rows,
        "selection": selection,
        "finite_library_theorem": (
            "For identifiable candidates i with true squared losses kappa_i^2 in "
            "[lower_i, upper_i], min_i kappa_i^2 lies in "
            "[min_i lower_i, min_i upper_i]. Unidentifiable candidates have infinite "
            "loss in the child unbounded-source model."
        ),
        "proof_boundary": _PROOF_BOUNDARY,
        "report_valid": True,
    }


def _verification_payload(core: dict[str, object]) -> dict[str, object]:
    selection = core["selection"]
    if type(selection) is not dict:
        raise AssertionError("internally reconstructed selection is malformed")
    return {
        "passed": True,
        "method": (
            "standalone exact reconstruction of every sealed child certificate, rational "
            "common source/query/noise-radius contract, candidate interval, finite-library "
            "optimum bracket, deterministic selection, and strict uniqueness comparison"
        ),
        "candidate_certificates_verified": core["candidate_count"],
        "identifiable_candidates": core["identifiable_candidate_count"],
        "common_comparison_contract_verified_exactly": True,
        "selection_reconstructed_exactly": True,
        "library_bracket_reconstructed_exactly": True,
        "unique_winner_test_reconstructed_exactly": True,
        "outcome": selection["outcome"],
    }


def _verify_library_report(
    report: dict[str, object], *, require_embedded: bool
) -> dict[str, object]:
    try:
        if type(report) is not dict:
            raise TypeError("candidate-library report must be a JSON object")
        expected_keys = {
            "schema_version",
            "status",
            "objective",
            "comparison_scope",
            "comparison_contract",
            "continuous_design_optimality_claimed",
            "candidate_count",
            "identifiable_candidate_count",
            "candidates",
            "selection",
            "finite_library_theorem",
            "proof_boundary",
            "report_valid",
        }
        embedded_present = "independent_exact_verification" in report
        if embedded_present:
            expected_keys.add("independent_exact_verification")
        if require_embedded and not embedded_present:
            raise ValueError("independent exact verification block is missing")
        if set(report) != expected_keys:
            raise ValueError("candidate-library report has missing or unexpected fields")
        if report.get("schema_version") != _SCHEMA:
            raise ValueError("unknown candidate-library schema")

        raw_rows = report.get("candidates")
        if type(raw_rows) is not list or not raw_rows:
            raise ValueError("embedded candidate rows must be a nonempty JSON list")
        named_children: list[tuple[str, dict[str, object]]] = []
        for row in raw_rows:
            if type(row) is not dict:
                raise ValueError("an embedded candidate row is malformed")
            name = row.get("name")
            child = row.get("query_certificate")
            if type(child) is not dict:
                raise ValueError("an embedded child query certificate is malformed")
            named_children.append((_candidate_name(name), child))

        core = _build_core(tuple(named_children))
        reported_core = {
            key: value
            for key, value in report.items()
            if key != "independent_exact_verification"
        }
        if not _strict_json_equal(reported_core, core):
            raise ValueError(
                "candidate-library theorem fields do not match exact reconstruction"
            )
        verification = _verification_payload(core)
        if embedded_present and not _strict_json_equal(
            report["independent_exact_verification"], verification
        ):
            raise ValueError("embedded independent exact verification is inconsistent")
        return verification
    except (ArithmeticError, KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        return {"passed": False, "reason": str(error)}


def certify_query_candidate_library(
    candidates: Sequence[CandidateInput],
) -> dict[str, object]:
    """Certify selection over exactly the supplied finite candidate library."""
    normalized = _normalize_candidates(candidates)
    report = _build_core(normalized)
    verification = _verify_library_report(report, require_embedded=False)
    if verification.get("passed") is not True:
        raise AssertionError(
            f"candidate-library self-verification failed: {verification}"
        )
    report["independent_exact_verification"] = verification
    sealed = verify_query_candidate_library_report(report)
    if sealed.get("passed") is not True:
        raise AssertionError(f"sealed candidate-library verification failed: {sealed}")
    return report


def verify_query_candidate_library_report(
    report: dict[str, object],
) -> dict[str, object]:
    """Reconstruct a sealed finite-library certificate from its embedded inputs."""
    return _verify_library_report(report, require_embedded=True)


__all__ = [
    "CandidateInput",
    "QueryCandidate",
    "certify_query_candidate_library",
    "verify_query_candidate_library_report",
]
