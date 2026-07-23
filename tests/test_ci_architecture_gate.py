from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

WORKFLOW_PATH = (
    ROOT
    / ".github"
    / "workflows"
    / "architecture-gate.yml"
)

REQUIREMENTS_PATH = ROOT / "requirements-ci.txt"


class CIArchitectureGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW_PATH.read_text(
            encoding="utf-8-sig"
        )
        cls.requirements = REQUIREMENTS_PATH.read_text(
            encoding="utf-8-sig"
        )

    def test_gate_uses_minimum_permissions(self):
        self.assertIn(
            "permissions:\n  contents: read",
            self.workflow,
        )
        self.assertIn(
            "persist-credentials: false",
            self.workflow,
        )

    def test_gate_cancels_superseded_runs(self):
        self.assertIn(
            "concurrency:",
            self.workflow,
        )
        self.assertIn(
            "cancel-in-progress: true",
            self.workflow,
        )

    def test_gate_has_execution_timeout(self):
        self.assertIn(
            "timeout-minutes: 10",
            self.workflow,
        )

    def test_gate_compiles_before_validation(self):
        compile_position = self.workflow.index(
            "Compile Python sources"
        )
        validation_position = self.workflow.index(
            "Validate architecture V0-V8"
        )
        tests_position = self.workflow.index(
            "Run automated tests"
        )

        self.assertLess(
            compile_position,
            validation_position,
        )
        self.assertLess(
            validation_position,
            tests_position,
        )

    def test_gate_uses_pinned_ci_dependencies(self):
        self.assertEqual(
            "jsonschema==4.23.0",
            self.requirements.strip(),
        )
        self.assertIn(
            "-r requirements-ci.txt",
            self.workflow,
        )
        self.assertIn(
            "cache-dependency-path: requirements-ci.txt",
            self.workflow,
        )

    def test_gate_publishes_validation_evidence(self):
        self.assertIn(
            "actions/upload-artifact@v4",
            self.workflow,
        )
        self.assertIn(
            "if: always()",
            self.workflow,
        )
        self.assertIn(
            "reports/validation-v0-v8.json",
            self.workflow,
        )
        self.assertIn(
            "if-no-files-found: error",
            self.workflow,
        )


if __name__ == "__main__":
    unittest.main()
