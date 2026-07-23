from __future__ import annotations

import copy
import unittest

from jsonschema import Draft202012Validator

from src.fr0 import (
    BASELINE_PATH,
    REGISTRY_DIR,
    REGISTRY_FILES,
    SCHEMA_MAP,
    load_json,
)


class NormativeRegistrySchemaTests(unittest.TestCase):
    def _artifact_cases(self):
        for key, filename in REGISTRY_FILES.items():
            yield (
                key,
                load_json(REGISTRY_DIR / filename),
                load_json(SCHEMA_MAP[key]),
            )

        yield (
            "baseline",
            load_json(BASELINE_PATH),
            load_json(SCHEMA_MAP["baseline"]),
        )

    def test_all_normative_artifacts_satisfy_their_schemas(self):
        for key, document, schema in self._artifact_cases():
            with self.subTest(artifact=key):
                Draft202012Validator.check_schema(schema)
                errors = list(
                    Draft202012Validator(schema).iter_errors(document)
                )
                self.assertEqual([], errors)

    def test_all_schemas_have_canonical_identifiers(self):
        expected_keys = set(REGISTRY_FILES) | {"baseline"}

        for key in expected_keys:
            with self.subTest(schema=key):
                schema = load_json(SCHEMA_MAP[key])
                self.assertEqual(
                    f"urn:fr0:schema:{key.replace('_', '-')}:v1",
                    schema.get("$id"),
                )

    def test_unknown_root_properties_are_rejected(self):
        for key, document, schema in self._artifact_cases():
            with self.subTest(artifact=key):
                invalid = copy.deepcopy(document)
                invalid["unexpected_property"] = True

                errors = list(
                    Draft202012Validator(schema).iter_errors(invalid)
                )

                self.assertTrue(errors)
                self.assertTrue(
                    any(
                        error.validator == "additionalProperties"
                        for error in errors
                    ),
                    errors,
                )

    def test_missing_required_root_properties_are_rejected(self):
        for key, document, schema in self._artifact_cases():
            required = schema.get("required", [])

            for field in required:
                with self.subTest(artifact=key, missing=field):
                    invalid = copy.deepcopy(document)
                    invalid.pop(field, None)

                    errors = list(
                        Draft202012Validator(schema).iter_errors(invalid)
                    )

                    self.assertTrue(errors)
                    self.assertTrue(
                        any(error.validator == "required" for error in errors),
                        errors,
                    )


if __name__ == "__main__":
    unittest.main()
