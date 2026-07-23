from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.release_manifest import (
    DEFAULT_BASELINE_PATH,
    DEFAULT_LOCK_PATH,
    DEFAULT_REPORT_PATH,
    ReleaseManifestError,
    build_release_manifest,
    generate_release_manifest,
    load_json,
    render_release_manifest,
    sha256_hex,
)


class ReleaseManifestGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = load_json(
            DEFAULT_BASELINE_PATH
        )
        self.lock = load_json(DEFAULT_LOCK_PATH)
        self.report = load_json(DEFAULT_REPORT_PATH)

    def test_manifest_is_linked_to_baseline(self):
        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        self.assertEqual(
            "AB-FR0-001",
            manifest["baseline"]["baseline_id"],
        )
        self.assertEqual(
            self.lock["digest"]["baseline_digest"],
            manifest["baseline"]["digest"],
        )

    def test_manifest_contains_release_identity(self):
        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        self.assertEqual(
            "FR-0",
            manifest["release"]["release_id"],
        )
        self.assertEqual(
            "FR0-IP-001",
            manifest["release"][
                "implementation_pack_id"
            ],
        )

    def test_manifest_contains_registry_versions_and_digests(
        self,
    ):
        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        self.assertEqual(
            set(self.lock["registries"]),
            set(manifest["registries"]),
        )

        for name, entry in manifest[
            "registries"
        ].items():
            self.assertEqual(
                self.lock["registries"][name]["version"],
                entry["version"],
            )
            self.assertEqual(
                self.lock["registries"][name]["digest"],
                entry["digest"],
            )

    def test_manifest_requires_validation_pass(self):
        report = copy.deepcopy(self.report)
        report["result"] = "FAIL"

        with self.assertRaisesRegex(
            ReleaseManifestError,
            "requires validation result PASS",
        ):
            build_release_manifest(
                self.baseline,
                self.lock,
                report,
            )

    def test_manifest_rejects_failed_stage(self):
        report = copy.deepcopy(self.report)
        report["stages"]["V8"] = "FAIL"

        with self.assertRaisesRegex(
            ReleaseManifestError,
            "every reported stage to pass",
        ):
            build_release_manifest(
                self.baseline,
                self.lock,
                report,
            )

    def test_manifest_rejects_foreign_lock(self):
        lock = copy.deepcopy(self.lock)
        lock["baseline_id"] = "AB-OTHER-001"

        with self.assertRaisesRegex(
            ReleaseManifestError,
            "lock baseline_id does not match",
        ):
            build_release_manifest(
                self.baseline,
                lock,
                self.report,
            )

    def test_manifest_publication_does_not_activate_release(
        self,
    ):
        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        self.assertFalse(
            manifest["release"][
                "activation_authorized"
            ]
        )
        self.assertTrue(
            manifest["release"][
                "publication_is_not_activation"
            ]
        )

    def test_architecture_gate_is_required(self):
        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        self.assertEqual(
            {
                "required": True,
                "required_result": "PASS",
                "evidence_source": (
                    ".github/workflows/"
                    "architecture-gate.yml"
                ),
            },
            manifest["architecture_gate"],
        )

    def test_manifest_digest_matches_payload(self):
        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        digest = manifest.pop("manifest_digest")

        self.assertEqual(
            sha256_hex(manifest),
            digest,
        )

    def test_reexecution_produces_identical_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.json"
            second = root / "second.json"

            generate_release_manifest(
                output_path=first
            )
            generate_release_manifest(
                output_path=second
            )

            self.assertEqual(
                first.read_bytes(),
                second.read_bytes(),
            )

    def test_rendered_manifest_is_valid_json(self):
        manifest = build_release_manifest(
            self.baseline,
            self.lock,
            self.report,
        )

        rendered = render_release_manifest(manifest)

        self.assertEqual(
            manifest,
            json.loads(rendered),
        )


if __name__ == "__main__":
    unittest.main()
