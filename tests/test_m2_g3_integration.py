from __future__ import annotations

import unittest

from src.baseline_workflow import (
    ArchitectureBaselineWorkflow,
    BaselineWorkflowState,
    EvidenceOutcome,
    EvidenceRecord,
    EvidenceType,
)
from src.fr0 import validate
from src.release_manifest import (
    DEFAULT_BASELINE_PATH,
    DEFAULT_LOCK_PATH,
    DEFAULT_REPORT_PATH,
    build_release_manifest,
    load_json,
    render_release_manifest,
)


class M2G3IntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = load_json(DEFAULT_BASELINE_PATH)
        self.lock = load_json(DEFAULT_LOCK_PATH)
        self.report = load_json(DEFAULT_REPORT_PATH)

    def test_validation_result_feeds_release_manifest(self) -> None:
        validation = validate()

        self.assertEqual("PASS", validation["result"])
        self.assertEqual(
            {f"V{stage}" for stage in range(9)},
            set(validation["stages"]),
        )
        self.assertTrue(
            all(
                result == "PASS"
                for result in validation["stages"].values()
            )
        )

        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            validation,
        )

        self.assertEqual(
            self.baseline["baseline_id"],
            manifest["baseline"]["baseline_id"],
        )
        self.assertEqual(
            self.baseline["target_release"],
            manifest["release"]["release_id"],
        )
        self.assertEqual("PASS", manifest["validation"]["result"])
        self.assertTrue(manifest["architecture_gate"]["required"])
        self.assertFalse(
            manifest["release"]["activation_authorized"]
        )
        self.assertTrue(
            manifest["release"]["publication_is_not_activation"]
        )

    def test_workflow_consumes_validation_and_gate_evidence(self) -> None:
        workflow = ArchitectureBaselineWorkflow(
            baseline_id=self.baseline["baseline_id"],
            accountable_identity="architecture-owner",
        )

        workflow.submit()

        workflow.record_evidence(
            EvidenceRecord(
                evidence_id="EVD-M2-G3-VALIDATION",
                baseline_id=self.baseline["baseline_id"],
                evidence_type=EvidenceType.VALIDATION_REPORT,
                outcome=EvidenceOutcome.PASS,
                recorded_by="architecture-gate",
                reference="reports/validation-v0-v8.json",
            )
        )

        workflow.mark_validated()

        workflow.record_evidence(
            EvidenceRecord(
                evidence_id="EVD-M2-G3-GATE",
                baseline_id=self.baseline["baseline_id"],
                evidence_type=EvidenceType.ARCHITECTURE_GATE,
                outcome=EvidenceOutcome.PASS,
                recorded_by="github-actions",
                reference=".github/workflows/architecture-gate.yml",
            )
        )

        workflow.record_evidence(
            EvidenceRecord(
                evidence_id="EVD-M2-G3-REVIEW",
                baseline_id=self.baseline["baseline_id"],
                evidence_type=EvidenceType.INDEPENDENT_REVIEW,
                outcome=EvidenceOutcome.APPROVED,
                recorded_by="independent-reviewer",
                reference="M2-G3 integration review",
            )
        )

        workflow.approve()

        self.assertEqual(
            BaselineWorkflowState.APPROVED,
            workflow.state,
        )
        self.assertNotEqual(
            BaselineWorkflowState.ACTIVE,
            workflow.state,
        )

        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        self.assertFalse(
            manifest["release"]["activation_authorized"]
        )

    def test_integrated_manifest_rendering_is_deterministic(self) -> None:
        first = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )
        second = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        self.assertEqual(
            render_release_manifest(first),
            render_release_manifest(second),
        )
        self.assertEqual(
            first["manifest_digest"],
            second["manifest_digest"],
        )


if __name__ == "__main__":
    unittest.main()
