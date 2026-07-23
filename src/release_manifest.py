from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BASELINE_PATH = (
    ROOT / "baseline" / "AB-FR0-001.json"
)
DEFAULT_LOCK_PATH = (
    ROOT / "baseline" / "AB-FR0-001.lock.json"
)
DEFAULT_REPORT_PATH = (
    ROOT / "reports" / "validation-v0-v8.json"
)
DEFAULT_OUTPUT_PATH = (
    ROOT / "release" / "FR-0.manifest.json"
)


class ReleaseManifestError(ValueError):
    """Raised when release manifest inputs are not eligible."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


def canonical_json_bytes(
    value: Mapping[str, Any],
) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        canonical_json_bytes(value)
    ).hexdigest()


def build_release_manifest(
    baseline: Mapping[str, Any],
    lock: Mapping[str, Any],
    report: Mapping[str, Any],
) -> dict[str, Any]:
    baseline_id = baseline.get("baseline_id")
    baseline_version = baseline.get("baseline_version")
    target_release = baseline.get("target_release")
    implementation_pack_id = baseline.get(
        "implementation_pack_id"
    )

    if lock.get("baseline_id") != baseline_id:
        raise ReleaseManifestError(
            "lock baseline_id does not match baseline"
        )

    if lock.get("baseline_version") != baseline_version:
        raise ReleaseManifestError(
            "lock baseline_version does not match baseline"
        )

    if report.get("baseline_id") != baseline_id:
        raise ReleaseManifestError(
            "validation report baseline_id does not match baseline"
        )

    if report.get("result") != "PASS":
        raise ReleaseManifestError(
            "release manifest requires validation result PASS"
        )

    stages = report.get("stages")

    if not isinstance(stages, Mapping) or not stages:
        raise ReleaseManifestError(
            "validation report must contain stage results"
        )

    failed_stages = sorted(
        stage_id
        for stage_id, result in stages.items()
        if result != "PASS"
    )

    if failed_stages:
        raise ReleaseManifestError(
            "release manifest requires every reported stage "
            f"to pass: {', '.join(failed_stages)}"
        )

    lock_validation = lock.get("validation", {})

    if lock_validation.get("result") != "PASS":
        raise ReleaseManifestError(
            "baseline lock validation result must be PASS"
        )

    baseline_digest = (
        lock.get("digest", {}).get("baseline_digest")
    )

    if not isinstance(baseline_digest, str) or not baseline_digest:
        raise ReleaseManifestError(
            "baseline lock must contain baseline_digest"
        )

    registries = lock.get("registries")

    if not isinstance(registries, Mapping) or not registries:
        raise ReleaseManifestError(
            "baseline lock must contain registries"
        )

    registry_entries: dict[str, dict[str, Any]] = {}

    for name in sorted(registries):
        entry = registries[name]

        version = entry.get("version")
        digest = entry.get("digest")
        registry_id = entry.get("registry_id")

        if not registry_id or not digest:
            raise ReleaseManifestError(
                f"registry {name} lacks identity or digest"
            )

        registry_entries[name] = {
            "registry_id": registry_id,
            "version": version,
            "digest": digest,
        }

    payload: dict[str, Any] = {
        "manifest_id": f"RM-{target_release}-001",
        "manifest_version": 1,
        "release": {
            "release_id": target_release,
            "implementation_pack_id": implementation_pack_id,
            "publication_state": "GENERATED",
            "activation_authorized": False,
            "publication_is_not_activation": True,
        },
        "baseline": {
            "baseline_id": baseline_id,
            "baseline_version": baseline_version,
            "declared_status": baseline.get("status"),
            "digest": baseline_digest,
        },
        "registries": registry_entries,
        "validation": {
            "validation_id": report.get("validation_id"),
            "validator_version": report.get(
                "validator_version"
            ),
            "result": report.get("result"),
            "stages": {
                stage_id: stages[stage_id]
                for stage_id in sorted(stages)
            },
            "finding_count": len(
                report.get("findings", [])
            ),
        },
        "architecture_gate": {
            "required": True,
            "required_result": "PASS",
            "evidence_source": (
                ".github/workflows/architecture-gate.yml"
            ),
        },
        "integrity": {
            "canonicalization_profile": (
                "JSON-SORTED-KEYS-UTF8"
            ),
            "digest_algorithm": "SHA-256",
        },
    }

    manifest_digest = sha256_hex(payload)

    return {
        **payload,
        "manifest_digest": manifest_digest,
    }


def render_release_manifest(
    manifest: Mapping[str, Any],
) -> str:
    return (
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def generate_release_manifest(
    baseline_path: Path = DEFAULT_BASELINE_PATH,
    lock_path: Path = DEFAULT_LOCK_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> dict[str, Any]:
    manifest = build_release_manifest(
        load_json(baseline_path),
        load_json(lock_path),
        load_json(report_path),
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        render_release_manifest(manifest),
        encoding="utf-8",
        newline="\n",
    )

    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the deterministic FR-0 release manifest."
        )
    )

    parser.add_argument(
        "command",
        choices=["generate"],
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE_PATH,
    )
    parser.add_argument(
        "--lock",
        type=Path,
        default=DEFAULT_LOCK_PATH,
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
    )

    args = parser.parse_args(argv)

    manifest = generate_release_manifest(
        baseline_path=args.baseline,
        lock_path=args.lock,
        report_path=args.report,
        output_path=args.output,
    )

    print(render_release_manifest(manifest), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
