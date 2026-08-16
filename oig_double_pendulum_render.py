#!/usr/bin/env python3
"""Dependency-free SVG rendering for a verified Tier-1 pendulum atlas report."""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path
from typing import Sequence

import numpy as np

from oig_double_pendulum_lab import verify_atlas_lab_report


_PALETTE = (
    "#440154",
    "#482878",
    "#3e4989",
    "#31688e",
    "#26828e",
    "#1f9e89",
    "#35b779",
    "#6ece58",
    "#b5de2b",
    "#fde725",
)


def _colour(value: float, lower: float, upper: float) -> str:
    if upper <= lower:
        return _PALETTE[len(_PALETTE) // 2]
    coordinate = min(1.0, max(0.0, (value - lower) / (upper - lower)))
    return _PALETTE[min(len(_PALETTE) - 1, int(coordinate * len(_PALETTE)))]


def render_atlas_svg(report: dict[str, object]) -> str:
    """Render the authoritative raw fields after internal report verification."""
    verification = verify_atlas_lab_report(report)
    if not verification["passed"]:
        raise ValueError(f"atlas report does not verify: {verification}")
    run = report["run"]
    raw = report["raw_fields"]
    side = int(run["side"])
    stretch = np.asarray(raw["grid_edge_log_stretch"], dtype=float)
    mask = np.asarray(
        raw["resolved_low_stretch_no_sampled_full_turn_mask"], dtype=bool
    )
    energy = np.asarray(raw["initial_energy"], dtype=float)
    turn_1 = np.asarray(raw["sampled_turn_excursion_arm_1"], dtype=int)
    turn_2 = np.asarray(raw["sampled_turn_excursion_arm_2"], dtype=int)
    labels = np.asarray(raw["connected_region_labels"], dtype=int)
    lower, upper = np.quantile(stretch, (0.05, 0.95))

    width, height = 760, 720
    left, top, plot = 86.0, 86.0, 520.0
    cell = plot / side
    fragments = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'role="img" aria-labelledby="atlas-title atlas-description">',
        '<title id="atlas-title">Double-pendulum finite-time operational atlas</title>',
        '<desc id="atlas-description">Cell-centred initial-angle torus coloured by grid-edge '
        'finite-time operational log-stretch. White circles mark the separately declared '
        'low-stretch, no-sampled-full-turn mask.</desc>',
        '<rect width="100%" height="100%" fill="#111318"/>',
        '<text x="86" y="34" fill="#f1f5f9" font-family="system-ui,sans-serif" '
        'font-size="22" font-weight="600">Double-pendulum operational atlas</text>',
        '<text x="86" y="60" fill="#aab4c3" font-family="system-ui,sans-serif" '
        'font-size="13">Grid-edge log-stretch; circles mark resolved cells with no sampled full turn</text>',
    ]
    angles = -np.pi + (np.arange(side) + 0.5) * (2.0 * np.pi / side)
    for row in range(side):
        for column in range(side):
            x = left + row * cell
            y = top + (side - 1 - column) * cell
            tooltip = html.escape(
                f"theta1={angles[row]:.6f}, theta2={angles[column]:.6f}; "
                f"log-stretch={stretch[row, column]:.6f}; "
                f"initial energy={energy[row, column]:.6f}; "
                f"sampled excursions=({turn_1[row, column]},{turn_2[row, column]}); "
                f"region={labels[row, column]}"
            )
            fragments.append(
                f'<g><title>{tooltip}</title><rect x="{x:.4f}" y="{y:.4f}" '
                f'width="{cell + 0.08:.4f}" height="{cell + 0.08:.4f}" '
                f'fill="{_colour(float(stretch[row, column]), float(lower), float(upper))}"/></g>'
            )
            if mask[row, column]:
                fragments.append(
                    f'<circle cx="{x + 0.5 * cell:.4f}" cy="{y + 0.5 * cell:.4f}" '
                    f'r="{0.18 * cell:.4f}" fill="none" stroke="#ffffff" '
                    'stroke-width="1.6"/>'
                )

    fragments.extend(
        [
            f'<rect x="{left}" y="{top}" width="{plot}" height="{plot}" '
            'fill="none" stroke="#d8dee9" stroke-width="1"/>',
            f'<text x="{left + 0.5 * plot}" y="{top + plot + 48}" '
            'fill="#d8dee9" font-family="system-ui,sans-serif" font-size="14" '
            'text-anchor="middle">initial θ₁ (radians)</text>',
            f'<text x="28" y="{top + 0.5 * plot}" fill="#d8dee9" '
            'font-family="system-ui,sans-serif" font-size="14" text-anchor="middle" '
            f'transform="rotate(-90 28 {top + 0.5 * plot})">initial θ₂ (radians)</text>',
        ]
    )
    for fraction, label in ((0.0, "−π"), (0.5, "0"), (1.0, "π")):
        x = left + fraction * plot
        y = top + (1.0 - fraction) * plot
        fragments.append(
            f'<text x="{x:.2f}" y="{top + plot + 23}" fill="#aab4c3" '
            f'font-family="system-ui,sans-serif" font-size="12" text-anchor="middle">{label}</text>'
        )
        fragments.append(
            f'<text x="{left - 14}" y="{y + 4:.2f}" fill="#aab4c3" '
            f'font-family="system-ui,sans-serif" font-size="12" text-anchor="end">{label}</text>'
        )

    legend_x, legend_y, legend_width = 635.0, 120.0, 24.0
    segment = 26.0
    for index, colour in enumerate(reversed(_PALETTE)):
        fragments.append(
            f'<rect x="{legend_x}" y="{legend_y + index * segment}" '
            f'width="{legend_width}" height="{segment + 0.2}" fill="{colour}"/>'
        )
    fragments.extend(
        [
            f'<text x="{legend_x - 1}" y="{legend_y - 14}" fill="#d8dee9" '
            'font-family="system-ui,sans-serif" font-size="12">log-stretch</text>',
            f'<text x="{legend_x + 32}" y="{legend_y + 6}" fill="#aab4c3" '
            f'font-family="system-ui,sans-serif" font-size="11">{upper:.3f}</text>',
            f'<text x="{legend_x + 32}" y="{legend_y + len(_PALETTE) * segment}" '
            f'fill="#aab4c3" font-family="system-ui,sans-serif" font-size="11">{lower:.3f}</text>',
            f'<circle cx="{legend_x + 10}" cy="{legend_y + 320}" r="5" fill="none" '
            'stroke="#ffffff" stroke-width="1.6"/>',
            f'<text x="{legend_x + 24}" y="{legend_y + 324}" fill="#d8dee9" '
            'font-family="system-ui,sans-serif" font-size="11">mask cell</text>',
            f'<text x="{left}" y="{height - 24}" fill="#8b96a6" '
            'font-family="system-ui,sans-serif" font-size="11">Tier 1 numerical portrait; '
            'raw report fields are authoritative, not colour or connectivity.</text>',
            '</svg>',
        ]
    )
    return "\n".join(fragments) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    report = json.loads(arguments.report.read_text(encoding="utf-8"))
    arguments.output.write_text(render_atlas_svg(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["render_atlas_svg"]
