from __future__ import annotations

import unittest
from dataclasses import asdict, dataclass

from src.architecture_test_engine import (
    ArchitectureTestEngine,
    StageDefinition,
)
from src.fr0 import validate


@dataclass(frozen=True)
class FakeFinding:
    stage: str
    code: str
    severity: str
    message: str


class ArchitectureTestEngineTests(unittest.TestCase):
    def test_executes_stages_in_declared_order(self):
        executed = []

        def runner(stage_id):
            def execute(_context):
                executed.append(stage_id)
                return []

            return execute

        engine = ArchitectureTestEngine(
            [
                StageDefinition(
                    "V0",
                    "Discovery",
                    runner("V0"),
                ),
                StageDefinition(
                    "V1",
                    "Schema",
                    runner("V1"),
                    depends_on=("V0",),
                ),
            ]
        )

        engine.run(
            validation_id="VAL-TEST",
            baseline_id="AB-TEST-001",
            validator_version="test",
            finding_serializer=asdict,
        )

        self.assertEqual(
            ["V0", "V1"],
            executed,
        )

    def test_failed_stage_marks_report_as_failed(self):
        engine = ArchitectureTestEngine(
            [
                StageDefinition(
                    "V0",
                    "Discovery",
                    lambda _context: [
                        FakeFinding(
                            "V0",
                            "FAILURE",
                            "ERROR",
                            "failure",
                        )
                    ],
                )
            ]
        )

        report = engine.run(
            validation_id="VAL-TEST",
            baseline_id="AB-TEST-001",
            validator_version="test",
            finding_serializer=asdict,
        )

        self.assertEqual("FAIL", report["result"])
        self.assertEqual(
            "FAIL",
            report["stages"]["V0"],
        )

    def test_dependency_failure_skips_downstream_stage(self):
        executed = []

        engine = ArchitectureTestEngine(
            [
                StageDefinition(
                    "V0",
                    "Discovery",
                    lambda _context: [
                        FakeFinding(
                            "V0",
                            "FAILURE",
                            "ERROR",
                            "failure",
                        )
                    ],
                ),
                StageDefinition(
                    "V1",
                    "Schema",
                    lambda _context: (
                        executed.append("V1") or []
                    ),
                    depends_on=("V0",),
                ),
            ]
        )

        report = engine.run(
            validation_id="VAL-TEST",
            baseline_id="AB-TEST-001",
            validator_version="test",
            finding_serializer=asdict,
        )

        self.assertEqual([], executed)
        self.assertEqual(
            "SKIP",
            report["stages"]["V1"],
        )

    def test_warning_does_not_fail_stage(self):
        engine = ArchitectureTestEngine(
            [
                StageDefinition(
                    "V0",
                    "Discovery",
                    lambda _context: [
                        FakeFinding(
                            "V0",
                            "WARNING",
                            "WARNING",
                            "warning",
                        )
                    ],
                )
            ]
        )

        report = engine.run(
            validation_id="VAL-TEST",
            baseline_id="AB-TEST-001",
            validator_version="test",
            finding_serializer=asdict,
        )

        self.assertEqual("PASS", report["result"])
        self.assertEqual(
            "PASS",
            report["stages"]["V0"],
        )

    def test_duplicate_stage_ids_are_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "must be unique",
        ):
            ArchitectureTestEngine(
                [
                    StageDefinition(
                        "V0",
                        "One",
                        lambda _context: [],
                    ),
                    StageDefinition(
                        "V0",
                        "Two",
                        lambda _context: [],
                    ),
                ]
            )

    def test_unknown_dependencies_are_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "unknown dependencies",
        ):
            ArchitectureTestEngine(
                [
                    StageDefinition(
                        "V1",
                        "Schema",
                        lambda _context: [],
                        depends_on=("V0",),
                    )
                ]
            )

    def test_report_contains_machine_readable_details(self):
        engine = ArchitectureTestEngine(
            [
                StageDefinition(
                    "V0",
                    "Discovery",
                    lambda _context: [],
                )
            ]
        )

        report = engine.run(
            validation_id="VAL-TEST",
            baseline_id="AB-TEST-001",
            validator_version="test",
            finding_serializer=asdict,
        )

        detail = report["stage_details"][0]

        self.assertEqual("V0", detail["stage_id"])
        self.assertEqual("PASS", detail["result"])
        self.assertEqual(0, detail["finding_count"])
        self.assertEqual([], detail["blocked_by"])

    def test_production_engine_preserves_v0_v8_contract(self):
        report = validate()

        self.assertEqual("PASS", report["result"])
        self.assertEqual(
            {
                "V0": "PASS",
                "V1": "PASS",
                "V2": "PASS",
                "V3": "PASS",
                "V4": "PASS",
                "V5": "PASS",
                "V6": "PASS",
                "V7": "PASS",
                "V8": "PASS",
            },
            report["stages"],
        )
        self.assertEqual(
            9,
            len(report["stage_details"]),
        )


if __name__ == "__main__":
    unittest.main()
