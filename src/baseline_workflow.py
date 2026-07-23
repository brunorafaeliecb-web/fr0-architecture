from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class BaselineWorkflowState(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"


class EvidenceType(str, Enum):
    VALIDATION_REPORT = "VALIDATION_REPORT"
    ARCHITECTURE_GATE = "ARCHITECTURE_GATE"
    INDEPENDENT_REVIEW = "INDEPENDENT_REVIEW"


class EvidenceOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    baseline_id: str
    evidence_type: EvidenceType
    outcome: EvidenceOutcome
    recorded_by: str
    reference: str

    def __post_init__(self) -> None:
        for name, value in (
            ("evidence_id", self.evidence_id),
            ("baseline_id", self.baseline_id),
            ("recorded_by", self.recorded_by),
            ("reference", self.reference),
        ):
            if not value or not value.strip():
                raise ValueError(f"{name} cannot be empty")


@dataclass
class ArchitectureBaselineWorkflow:
    baseline_id: str
    accountable_identity: str
    independent_review_required: bool = True
    _state: BaselineWorkflowState = field(
        default=BaselineWorkflowState.DRAFT,
        init=False,
    )
    _evidence: dict[EvidenceType, EvidenceRecord] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    _ALLOWED_TRANSITIONS = {
        BaselineWorkflowState.DRAFT: BaselineWorkflowState.SUBMITTED,
        BaselineWorkflowState.SUBMITTED: BaselineWorkflowState.VALIDATED,
        BaselineWorkflowState.VALIDATED: BaselineWorkflowState.APPROVED,
        BaselineWorkflowState.APPROVED: BaselineWorkflowState.ACTIVE,
    }

    def __post_init__(self) -> None:
        if not self.baseline_id or not self.baseline_id.strip():
            raise ValueError("baseline_id cannot be empty")

        if (
            not self.accountable_identity
            or not self.accountable_identity.strip()
        ):
            raise ValueError(
                "accountable_identity cannot be empty"
            )

    @property
    def state(self) -> BaselineWorkflowState:
        return self._state

    @property
    def evidence(
        self,
    ) -> Mapping[EvidenceType, EvidenceRecord]:
        return MappingProxyType(dict(self._evidence))

    def record_evidence(
        self,
        evidence: EvidenceRecord,
    ) -> None:
        if evidence.baseline_id != self.baseline_id:
            raise ValueError(
                "evidence baseline_id does not match workflow baseline"
            )

        if evidence.evidence_type in self._evidence:
            raise ValueError(
                f"evidence already recorded for "
                f"{evidence.evidence_type.value}"
            )

        self._evidence[evidence.evidence_type] = evidence

    def submit(self) -> None:
        self._transition_to(
            BaselineWorkflowState.SUBMITTED
        )

    def mark_validated(self) -> None:
        self._require_evidence(
            EvidenceType.VALIDATION_REPORT,
            EvidenceOutcome.PASS,
        )
        self._transition_to(
            BaselineWorkflowState.VALIDATED
        )

    def approve(self) -> None:
        self._require_evidence(
            EvidenceType.VALIDATION_REPORT,
            EvidenceOutcome.PASS,
        )
        self._require_evidence(
            EvidenceType.ARCHITECTURE_GATE,
            EvidenceOutcome.PASS,
        )

        if self.independent_review_required:
            review = self._require_evidence(
                EvidenceType.INDEPENDENT_REVIEW,
                EvidenceOutcome.APPROVED,
            )

            if (
                review.recorded_by.strip().casefold()
                == self.accountable_identity.strip().casefold()
            ):
                raise ValueError(
                    "independent reviewer must differ from "
                    "accountable identity"
                )

        self._transition_to(
            BaselineWorkflowState.APPROVED
        )

    def activate(self) -> None:
        self._transition_to(
            BaselineWorkflowState.ACTIVE
        )

    def snapshot(self) -> dict[str, object]:
        return {
            "baseline_id": self.baseline_id,
            "accountable_identity": self.accountable_identity,
            "independent_review_required": (
                self.independent_review_required
            ),
            "state": self.state.value,
            "evidence": {
                evidence_type.value: {
                    "evidence_id": evidence.evidence_id,
                    "outcome": evidence.outcome.value,
                    "recorded_by": evidence.recorded_by,
                    "reference": evidence.reference,
                }
                for evidence_type, evidence
                in sorted(
                    self._evidence.items(),
                    key=lambda item: item[0].value,
                )
            },
        }

    def _transition_to(
        self,
        target: BaselineWorkflowState,
    ) -> None:
        expected = self._ALLOWED_TRANSITIONS.get(
            self._state
        )

        if expected != target:
            raise ValueError(
                f"invalid baseline transition: "
                f"{self._state.value} -> {target.value}"
            )

        self._state = target

    def _require_evidence(
        self,
        evidence_type: EvidenceType,
        expected_outcome: EvidenceOutcome,
    ) -> EvidenceRecord:
        evidence = self._evidence.get(evidence_type)

        if evidence is None:
            raise ValueError(
                f"missing required evidence: "
                f"{evidence_type.value}"
            )

        if evidence.outcome != expected_outcome:
            raise ValueError(
                f"{evidence_type.value} evidence must be "
                f"{expected_outcome.value}, found "
                f"{evidence.outcome.value}"
            )

        return evidence
