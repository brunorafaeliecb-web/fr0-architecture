from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Protocol


class FindingLike(Protocol):
    stage: str
    severity: str


StageRunner = Callable[
    [dict[str, Any]],
    Iterable[FindingLike],
]


@dataclass(frozen=True)
class StageDefinition:
    stage_id: str
    canonical_name: str
    runner: StageRunner
    depends_on: tuple[str, ...] = ()
    required: bool = True

    def __post_init__(self) -> None:
        if not self.stage_id:
            raise ValueError("stage_id cannot be empty")

        if not self.canonical_name:
            raise ValueError(
                "canonical_name cannot be empty"
            )

        if self.stage_id in self.depends_on:
            raise ValueError(
                f"{self.stage_id} cannot depend on itself"
            )


class ArchitectureTestEngine:
    def __init__(
        self,
        stages: Iterable[StageDefinition],
    ) -> None:
        self._stages = tuple(stages)

        stage_ids = [
            stage.stage_id
            for stage in self._stages
        ]

        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError(
                "stage identifiers must be unique"
            )

        known = set(stage_ids)

        for stage in self._stages:
            unknown = set(stage.depends_on) - known

            if unknown:
                raise ValueError(
                    f"{stage.stage_id} has unknown "
                    f"dependencies: {sorted(unknown)}"
                )

    @property
    def stages(self) -> tuple[StageDefinition, ...]:
        return self._stages

    def run(
        self,
        *,
        validation_id: str,
        baseline_id: str,
        validator_version: str,
        context: Mapping[str, Any] | None = None,
        finding_serializer: Callable[
            [FindingLike],
            dict[str, Any],
        ],
    ) -> dict[str, Any]:
        execution_context = dict(context or {})
        findings: list[FindingLike] = []
        stage_results: dict[str, str] = {}
        stage_details: list[dict[str, Any]] = []

        for stage in self._stages:
            blocked_by = [
                dependency
                for dependency in stage.depends_on
                if stage_results.get(dependency)
                != "PASS"
            ]

            if blocked_by:
                stage_results[stage.stage_id] = "SKIP"
                stage_details.append(
                    {
                        "stage_id": stage.stage_id,
                        "canonical_name": (
                            stage.canonical_name
                        ),
                        "required": stage.required,
                        "result": "SKIP",
                        "blocked_by": blocked_by,
                        "finding_count": 0,
                    }
                )
                continue

            produced = list(
                stage.runner(execution_context)
            )
            findings.extend(produced)

            errors = [
                finding
                for finding in produced
                if finding.severity == "ERROR"
            ]

            result = "FAIL" if errors else "PASS"
            stage_results[stage.stage_id] = result

            stage_details.append(
                {
                    "stage_id": stage.stage_id,
                    "canonical_name": (
                        stage.canonical_name
                    ),
                    "required": stage.required,
                    "result": result,
                    "blocked_by": [],
                    "finding_count": len(produced),
                }
            )

        required_results = [
            stage_results[stage.stage_id]
            for stage in self._stages
            if stage.required
        ]

        result = (
            "PASS"
            if required_results
            and all(
                stage_result == "PASS"
                for stage_result in required_results
            )
            else "FAIL"
        )

        return {
            "validation_id": validation_id,
            "baseline_id": baseline_id,
            "validator_version": validator_version,
            "stages": stage_results,
            "stage_details": stage_details,
            "result": result,
            "findings": [
                finding_serializer(finding)
                for finding in findings
            ],
        }
