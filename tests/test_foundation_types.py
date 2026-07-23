from __future__ import annotations

import unittest

from src.foundation_types import (
    BaselineId,
    CanonicalIdentifier,
    ContextId,
    DecisionId,
    FactId,
    NormativeStatus,
    Priority,
    RegistryVersion,
    Severity,
    parse_enum,
)


class FoundationTypeTests(unittest.TestCase):
    def test_canonical_identifier_accepts_normative_format(self):
        identifier = CanonicalIdentifier("ARCH-VALIDATION-GRAPH")
        self.assertEqual(
            "ARCH-VALIDATION-GRAPH",
            str(identifier),
        )

    def test_canonical_identifier_rejects_lowercase(self):
        with self.assertRaises(ValueError):
            CanonicalIdentifier("ctx-org")

    def test_canonical_identifier_rejects_whitespace(self):
        with self.assertRaises(ValueError):
            CanonicalIdentifier("CTX ORG")

    def test_specialized_identifiers_require_correct_prefix(self):
        valid_cases = [
            (BaselineId, "AB-FR0-001"),
            (ContextId, "CTX-ORG"),
            (FactId, "FACT-ORGANIZATION-LIFECYCLE"),
            (DecisionId, "DEC-TENANT-BOUNDARY"),
        ]

        for identifier_type, value in valid_cases:
            with self.subTest(identifier_type=identifier_type):
                self.assertEqual(
                    value,
                    str(identifier_type(value)),
                )

    def test_specialized_identifiers_reject_wrong_prefix(self):
        with self.assertRaises(ValueError):
            ContextId("FACT-ORG")

        with self.assertRaises(ValueError):
            FactId("CTX-ORG")

    def test_registry_version_accepts_positive_integer(self):
        version = RegistryVersion(1)
        self.assertEqual(1, int(version))
        self.assertEqual("1", str(version))

    def test_registry_version_rejects_zero(self):
        with self.assertRaises(ValueError):
            RegistryVersion(0)

    def test_registry_version_rejects_boolean(self):
        with self.assertRaises(TypeError):
            RegistryVersion(True)

    def test_normative_status_values_are_stable(self):
        self.assertEqual("DRAFT", NormativeStatus.DRAFT.value)
        self.assertEqual(
            "APPROVED",
            NormativeStatus.APPROVED.value,
        )

    def test_priority_values_match_registry_contract(self):
        self.assertEqual(
            {
                "BLOCKER",
                "REQUIRED_BEFORE_IMPLEMENTATION",
                "REQUIRED_BEFORE_PRODUCTION",
            },
            {priority.value for priority in Priority},
        )

    def test_severity_values_are_stable(self):
        self.assertEqual(
            {"INFO", "WARNING", "ERROR"},
            {severity.value for severity in Severity},
        )

    def test_parse_enum_returns_typed_member(self):
        result = parse_enum(
            NormativeStatus,
            "APPROVED",
        )
        self.assertIs(
            NormativeStatus.APPROVED,
            result,
        )

    def test_parse_enum_rejects_unknown_value(self):
        with self.assertRaisesRegex(
            ValueError,
            "invalid NormativeStatus",
        ):
            parse_enum(
                NormativeStatus,
                "INVALID",
            )


if __name__ == "__main__":
    unittest.main()
