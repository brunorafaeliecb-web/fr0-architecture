from __future__ import annotations

import unittest

from src.baseline_workflow import (
    ArchitectureBaselineWorkflow,
    BaselineWorkflowState,
    EvidenceOutcome,
    EvidenceRecord,
    EvidenceType,
)


BASELINE_ID = "AB-FR0-001"


def evidence(
    evidence_type: EvidenceType,
    outcome: EvidenceOutcome,
    *,
    recorded_by: str = "Independent Reviewer",
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=f"EVD-{evidence_type.value}",
        baseline_id=BASELINE_ID,
        evidence_type=evidence_type,
        outcome=outcome,
        recorded_by=recorded_by,
        reference=f"urn:fr0:evidence:{evidence_type.value.lower()}",
    )


class ArchitectureBaselineWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = ArchitectureBaselineWorkflow(
            baseline_id=BASELINE_ID,
            accountable_identity="Rafael",
            independent_review_required=True,
        )

    def test_workflow_starts_in_draft(self):
        self.assertEqual(
            BaselineWorkflowState.DRAFT,
            self.workflow.state,
        )

    def test_submit_moves_draft_to_submitted(self):
        self.workflow.submit()

        self.assertEqual(
            BaselineWorkflowState.SUBMITTED,
            self.workflow.state,
        )

    def test_invalid_transition_is_blocked(self):
        with self.assertRaisesRegex(
            ValueError,
            "invalid baseline transition",
        ):
            self.workflow.activate()

    def test_validation_requires_validation_evidence(self):
        self.workflow.submit()

        with self.assertRaisesRegex(
            ValueError,
            "missing required evidence: VALIDATION_REPORT",
        ):
            self.workflow.mark_validated()

    def test_failed_validation_evidence_is_rejected(self):
        self.workflow.submit()
        self.workflow.record_evidence(
            evidence(
                EvidenceType.VALIDATION_REPORT,
                EvidenceOutcome.FAIL,
            )
        )

        with self.assertRaisesRegex(
            ValueError,
            "must be PASS",
        ):
            self.workflow.mark_validated()

    def test_approval_requires_architecture_gate(self):
        self.workflow.submit()
        self.workflow.record_evidence(
            evidence(
                EvidenceType.VALIDATION_REPORT,
                EvidenceOutcome.PASS,
            )
        )
        self.workflow.mark_validated()

        with self.assertRaisesRegex(
            ValueError,
            "missing required evidence: ARCHITECTURE_GATE",
        ):
            self.workflow.approve()

    def test_approval_requires_independent_review(self):
        self.workflow.submit()
        self.workflow.record_evidence(
            evidence(
                EvidenceType.VALIDATION_REPORT,
                EvidenceOutcome.PASS,
            )
        )
        self.workflow.record_evidence(
            evidence(
                EvidenceType.ARCHITECTURE_GATE,
                EvidenceOutcome.PASS,
            )
        )
        self.workflow.mark_validated()

        with self.assertRaisesRegex(
            ValueError,
            "missing required evidence: INDEPENDENT_REVIEW",
        ):
            self.workflow.approve()

    def test_accountable_identity_cannot_review_itself(self):
        self.workflow.submit()
        self.workflow.record_evidence(
            evidence(
                EvidenceType.VALIDATION_REPORT,
                EvidenceOutcome.PASS,
            )
        )
        self.workflow.record_evidence(
            evidence(
                EvidenceType.ARCHITECTURE_GATE,
                EvidenceOutcome.PASS,
            )
        )
        self.workflow.record_evidence(
            evidence(
                EvidenceType.INDEPENDENT_REVIEW,
                EvidenceOutcome.APPROVED,
                recorded_by="Rafael",
            )
        )
        self.workflow.mark_validated()

        with self.assertRaisesRegex(
            ValueError,
            "reviewer must differ",
        ):
            self.workflow.approve()

    def test_rejected_review_cannot_promote_baseline(self):
        self.workflow.submit()
        self.workflow.record_evidence(
            evidence(
                EvidenceType.VALIDATION_REPORT,
                EvidenceOutcome.PASS,
            )
        )
        self.workflow.record_evidence(
            evidence(
                EvidenceType.ARCHITECTURE_GATE,
                EvidenceOutcome.PASS,
            )
        )
        self.workflow.record_evidence(
            evidence(
                EvidenceType.INDEPENDENT_REVIEW,
                EvidenceOutcome.REJECTED,
            )
        )
        self.workflow.mark_validated()

        with self.assertRaisesRegex(
            ValueError,
            "must be APPROVED",
        ):
            self.workflow.approve()

    def test_evidence_for_another_baseline_is_rejected(self):
        foreign = EvidenceRecord(
            evidence_id="EVD-FOREIGN",
            baseline_id="AB-OTHER-001",
            evidence_type=EvidenceType.VALIDATION_REPORT,
            outcome=EvidenceOutcome.PASS,
            recorded_by="Validator",
            reference="urn:foreign",
        )

        with self.assertRaisesRegex(
            ValueError,
            "does not match",
        ):
            self.workflow.record_evidence(foreign)

    def test_duplicate_evidence_type_is_rejected(self):
        record = evidence(
            EvidenceType.VALIDATION_REPORT,
            EvidenceOutcome.PASS,
        )
        self.workflow.record_evidence(record)

        with self.assertRaisesRegex(
            ValueError,
            "already recorded",
        ):
            self.workflow.record_evidence(record)

    def test_complete_workflow_reaches_active(self):
        self.workflow.submit()

        self.workflow.record_evidence(
            evidence(
                EvidenceType.VALIDATION_REPORT,
                EvidenceOutcome.PASS,
                recorded_by="FR0 Validator",
            )
        )
        self.workflow.mark_validated()

        self.workflow.record_evidence(
            evidence(
                EvidenceType.ARCHITECTURE_GATE,
                EvidenceOutcome.PASS,
                recorded_by="GitHub Actions",
            )
        )
        self.workflow.record_evidence(
            evidence(
                EvidenceType.INDEPENDENT_REVIEW,
                EvidenceOutcome.APPROVED,
                recorded_by="Independent Reviewer",
            )
        )

        self.workflow.approve()
        self.workflow.activate()

        self.assertEqual(
            BaselineWorkflowState.ACTIVE,
            self.workflow.state,
        )

        snapshot = self.workflow.snapshot()

        self.assertEqual("AB-FR0-001", snapshot["baseline_id"])
        self.assertEqual("ACTIVE", snapshot["state"])
        self.assertEqual(
            {
                "ARCHITECTURE_GATE",
                "INDEPENDENT_REVIEW",
                "VALIDATION_REPORT",
            },
            set(snapshot["evidence"]),
        )


if __name__ == "__main__":
    unittest.main()
