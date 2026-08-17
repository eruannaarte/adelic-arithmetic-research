import unittest

from double_pendulum_dynamics import DoublePendulumParameters, IntegrationConfig
from oig_double_pendulum_lab import AtlasRunConfig, run_atlas_lab
from oig_double_pendulum_render import render_atlas_svg


class DoublePendulumAtlasRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, _ = run_atlas_lab(
            AtlasRunConfig(
                side=3,
                duration=0.2,
                observation_count=9,
                feature_sample_count=3,
                log_stretch_threshold=2.0,
            ),
            DoublePendulumParameters(),
            IntegrationConfig(
                rtol=1e-8,
                atol=1e-10,
                max_step=0.04,
                energy_drift_tolerance=1e-7,
            ),
        )

    def test_svg_contains_one_tooltip_cell_per_initial_condition(self):
        svg = render_atlas_svg(self.report)
        self.assertTrue(svg.startswith("<svg"))
        self.assertEqual(svg.count("theta1="), 9)
        self.assertIn("initial θ₁ (radians)", svg)
        self.assertIn("raw report fields are authoritative", svg)

    def test_renderer_rejects_tampered_report(self):
        self.report["atlas_summary"]["cell_count"] = 8
        try:
            with self.assertRaises(ValueError):
                render_atlas_svg(self.report)
        finally:
            self.report["atlas_summary"]["cell_count"] = 9


if __name__ == "__main__":
    unittest.main()
