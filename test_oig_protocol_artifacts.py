import json
from pathlib import Path
import unittest
from unittest.mock import patch

from oig_atlas_protocol_integration import verify_atlas_protocol_integration_report
from oig_neumann_matched_frame import verify_neumann_matched_frame_report
from oig_protocol_design_engine import verify_design_report
from oig_uniform_lattice_arb_cover import verify_cover_report


ROOT = Path(__file__).resolve().parent


class CommittedProtocolArtifactTests(unittest.TestCase):
    def _load(self, name: str) -> dict[str, object]:
        with (ROOT / "certificates" / name).open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_hidden_network_design_artifact_self_verifies(self) -> None:
        report = self._load("oig_hidden_protocol_design.json")
        self.assertTrue(verify_design_report(report)["passed"])

    def test_neumann_matched_frame_artifact_self_verifies(self) -> None:
        report = self._load("oig_neumann_matched_frame.json")
        self.assertTrue(verify_neumann_matched_frame_report(report)["passed"])

    def test_neumann_artifact_verification_uses_no_floating_eigensolver(self) -> None:
        report = self._load("oig_neumann_matched_frame.json")
        with patch(
            "oig_interval_protocol_design.eigh",
            side_effect=AssertionError("floating proposal path used"),
        ), patch(
            "oig_protocol_design_engine.eigh",
            side_effect=AssertionError("floating proposal path used"),
        ):
            verification = verify_neumann_matched_frame_report(report)
        self.assertTrue(verification["passed"], verification)

    def test_uniform_tau_cover_artifact_self_verifies(self) -> None:
        report = self._load("oig_uniform_lattice_arb_cover.json")
        self.assertTrue(verify_cover_report(report)["passed"])

    def test_atlas_protocol_integration_artifact_self_verifies(self) -> None:
        report = self._load("oig_atlas_protocol_integration.json")
        self.assertTrue(verify_atlas_protocol_integration_report(report)["passed"])


if __name__ == "__main__":
    unittest.main()
