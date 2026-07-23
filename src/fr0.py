from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

from .jcs import canonicalize

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registries"
SCHEMA_DIR = ROOT / "schemas"
BASELINE_PATH = ROOT / "baseline" / "AB-FR0-001.json"
LOCK_PATH = ROOT / "baseline" / "AB-FR0-001.lock.json"
REPORT_PATH = ROOT / "reports" / "validation-v0-v8.json"

REGISTRY_FILES = {
    "context": "context-registry.v1.json",
    "ownership": "ownership-registry.v1.json",
    "invariant": "invariant-registry.v1.json",
    "enforcement": "enforcement-registry.v1.json",
    "contract": "contract-registry.v1.json",
    "capability": "capability-registry.v1.json",
    "test_catalog": "test-catalog.v1.json",
    "traceability": "traceability-registry.v1.json",
    "exception": "exception-registry.v1.json",
    "risk": "risk-registry.v1.json",
    "validation_graph": "validation-graph.v1.json",
    "work_package_catalog": "work-package-catalog.v1.json",
}

SCHEMA_MAP = {key: SCHEMA_DIR / f"{key}.schema.json" for key in REGISTRY_FILES}
SCHEMA_MAP["baseline"] = SCHEMA_DIR / "baseline.schema.json"


@dataclass
class Finding:
    stage: str
    code: str
    severity: str
    message: str
    artifact: str | None = None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonicalize(value)).hexdigest()


def _duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for value in values:
        if value in seen:
            dup.add(value)
        seen.add(value)
    return sorted(dup)


def discover() -> tuple[dict[str, Path], list[Finding]]:
    findings: list[Finding] = []
    artifacts: dict[str, Path] = {}
    for key, filename in REGISTRY_FILES.items():
        path = REGISTRY_DIR / filename
        if not path.is_file():
            findings.append(Finding("V0", "ARTIFACT_MISSING", "ERROR", f"Missing required registry: {filename}", filename))
        else:
            artifacts[key] = path
    if not BASELINE_PATH.is_file():
        findings.append(Finding("V0", "BASELINE_MISSING", "ERROR", "Missing AB-FR0-001.json", str(BASELINE_PATH)))
    else:
        artifacts["baseline"] = BASELINE_PATH
    extras = sorted(p.name for p in REGISTRY_DIR.glob("*.json") if p.name not in REGISTRY_FILES.values())
    for extra in extras:
        findings.append(Finding("V0", "UNDECLARED_REGISTRY", "ERROR", f"Undeclared registry artifact: {extra}", extra))
    return artifacts, findings


def validate_schemas(artifacts: dict[str, Path]) -> list[Finding]:
    findings: list[Finding] = []
    for key, path in artifacts.items():
        schema_path = SCHEMA_MAP[key]
        if not schema_path.is_file():
            findings.append(Finding("V1", "SCHEMA_MISSING", "ERROR", f"Schema missing for {key}", str(schema_path)))
            continue
        schema = load_json(schema_path)
        instance = load_json(path)
        validator = Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
            location = "$" + "".join(f"[{part!r}]" for part in error.absolute_path)
            findings.append(Finding("V1", "SCHEMA_INVALID", "ERROR", f"{location}: {error.message}", path.name))
    return findings


def validate_identity(artifacts: dict[str, Path]) -> list[Finding]:
    findings: list[Finding] = []
    if any(k not in artifacts for k in REGISTRY_FILES):
        return findings
    docs = {k: load_json(v) for k, v in artifacts.items() if k != "baseline"}
    registry_ids = [docs[k]["registry_id"] for k in REGISTRY_FILES]
    for duplicate in _duplicates(registry_ids):
        findings.append(Finding("V2", "DUPLICATE_REGISTRY_ID", "ERROR", f"Duplicate registry_id: {duplicate}"))

    collections = {
        "context_id": docs["context"]["contexts"],
        "fact_id": docs["ownership"]["facts"],
        "decision_id": docs["ownership"].get("decisions", []),
        "invariant_id": docs["invariant"]["invariants"],
        "control_id": docs["enforcement"]["controls"],
        "contract_id": docs["contract"]["contracts"],
        "capability_id": docs["capability"]["capabilities"],
        "test_id": docs["test_catalog"]["tests"],
        "risk_id": docs["risk"]["risks"],
        "work_package_id": docs["work_package_catalog"]["work_packages"],
        "stage_id": docs["validation_graph"]["stages"],
    }
    for id_field, items in collections.items():
        for duplicate in _duplicates(item[id_field] for item in items):
            findings.append(Finding("V2", "DUPLICATE_ID", "ERROR", f"Duplicate {id_field}: {duplicate}"))

    expected_counts = {
        "context_id": 32,
        "invariant_id": 33,
        "control_id": 14,
        "contract_id": 14,
        "work_package_id": 8,
        "stage_id": 12,
    }
    for id_field, expected in expected_counts.items():
        actual = len(collections[id_field])
        if actual != expected:
            findings.append(Finding("V2", "COUNT_MISMATCH", "ERROR", f"{id_field} count {actual}, expected {expected}"))
    return findings


def validate_references(artifacts: dict[str, Path]) -> list[Finding]:
    findings: list[Finding] = []
    required = set(REGISTRY_FILES) | {"baseline"}
    if not required.issubset(artifacts):
        return findings
    docs = {k: load_json(v) for k, v in artifacts.items()}
    contexts = {x["context_id"] for x in docs["context"]["contexts"]}
    facts = {x["fact_id"] for x in docs["ownership"]["facts"]}
    invariants = {x["invariant_id"] for x in docs["invariant"]["invariants"]}
    controls = {x["control_id"] for x in docs["enforcement"]["controls"]}
    contracts = {x["contract_id"] for x in docs["contract"]["contracts"]}
    capabilities = {x["capability_id"] for x in docs["capability"]["capabilities"]}
    tests = {x["test_id"] for x in docs["test_catalog"]["tests"]}
    wps = {x["work_package_id"] for x in docs["work_package_catalog"]["work_packages"]}

    def require(stage_code: str, ref: str, allowed: set[str], source: str) -> None:
        if ref not in allowed:
            findings.append(Finding("V3", stage_code, "ERROR", f"Unknown reference {ref} from {source}"))

    for fact in docs["ownership"]["facts"]:
        require("UNKNOWN_CONTEXT", fact["semantic_owner"], contexts, fact["fact_id"])
        require("UNKNOWN_CONTEXT", fact["transition_owner"], contexts, fact["fact_id"])
    for decision in docs["ownership"].get("decisions", []):
        require("UNKNOWN_CONTEXT", decision["decision_owner"], contexts, decision["decision_id"])
        for ref in decision.get("inputs", []):
            require("UNKNOWN_FACT", ref, facts, decision["decision_id"])
    for invariant in docs["invariant"]["invariants"]:
        require("UNKNOWN_CONTEXT", invariant["semantic_owner"], contexts, invariant["invariant_id"])
        for ref in invariant["enforcement_references"]:
            require("UNKNOWN_CONTROL", ref, controls, invariant["invariant_id"])
        for ref in invariant["verification_tests"]:
            require("UNKNOWN_TEST", ref, tests, invariant["invariant_id"])
    for control in docs["enforcement"]["controls"]:
        require("UNKNOWN_CONTEXT", control["semantic_owner"], contexts, control["control_id"])
        for ref in control["invariants"]:
            require("UNKNOWN_INVARIANT", ref, invariants, control["control_id"])
    for contract in docs["contract"]["contracts"]:
        require("UNKNOWN_CONTEXT", contract["semantic_owner"], contexts, contract["contract_id"])
        for ref in contract["producer_contexts"] + contract["authorized_consumers"]:
            require("UNKNOWN_CONTEXT", ref, contexts, contract["contract_id"])
    for capability in docs["capability"]["capabilities"]:
        require("UNKNOWN_CONTEXT", capability["semantic_owner"], contexts, capability["capability_id"])
    for link in docs["traceability"]["links"]:
        require("UNKNOWN_INVARIANT", link["invariant"], invariants, "traceability")
        require("UNKNOWN_CONTROL", link["control"], controls, "traceability")
        require("UNKNOWN_TEST", link["test"], tests, "traceability")
        require("UNKNOWN_WORK_PACKAGE", link["work_package"], wps, "traceability")
    for name, ref in docs["baseline"]["normative_registries"].items():
        if name not in REGISTRY_FILES:
            findings.append(Finding("V3", "UNKNOWN_REGISTRY_REFERENCE", "ERROR", f"Baseline references unknown registry key: {name}"))
        elif ref["version"] != docs[name]["registry_version"]:
            findings.append(Finding("V3", "REGISTRY_VERSION_MISMATCH", "ERROR", f"Baseline expects {name} v{ref['version']}, found v{docs[name]['registry_version']}"))
    # Ensure every blocker invariant has at least one control and one test reference.
    for invariant in docs["invariant"]["invariants"]:
        if invariant["priority"] == "BLOCKER" and (not invariant["enforcement_references"] or not invariant["verification_tests"]):
            findings.append(Finding("V3", "BLOCKER_TRACEABILITY_INCOMPLETE", "ERROR", invariant["invariant_id"]))
    # Exact contract count/type distribution.
    distribution: dict[str, int] = {}
    for contract in docs["contract"]["contracts"]:
        distribution[contract["interaction_type"]] = distribution.get(contract["interaction_type"], 0) + 1
    expected = {"QUERY": 1, "COMMAND": 6, "EVENT": 6, "DECISION": 1}
    if distribution != expected:
        findings.append(Finding("V3", "CONTRACT_DISTRIBUTION_MISMATCH", "ERROR", f"Actual {distribution}, expected {expected}"))
    return findings



def validate_ownership_consistency(artifacts: dict[str, Path]) -> list[Finding]:
    findings: list[Finding] = []
    required = {"context", "ownership"}
    if not required.issubset(artifacts):
        return findings
    ownership = load_json(artifacts["ownership"])
    facts = ownership["facts"]
    # One record per authoritative fact and one owner per ownership dimension.
    for duplicate in _duplicates(f["fact_id"] for f in facts):
        findings.append(Finding("V4", "DUPLICATE_AUTHORITATIVE_FACT", "ERROR", f"Duplicate fact record: {duplicate}"))
    for fact in facts:
        if not fact.get("semantic_owner"):
            findings.append(Finding("V4", "SEMANTIC_OWNER_MISSING", "ERROR", fact["fact_id"]))
        if not fact.get("transition_owner"):
            findings.append(Finding("V4", "TRANSITION_OWNER_MISSING", "ERROR", fact["fact_id"]))
    allowed_relations = {"OWNS", "REFERENCES", "PROJECTS", "DECIDES"}
    for rel in ownership.get("relationships", []):
        relation = rel.get("relation")
        if relation not in allowed_relations:
            findings.append(Finding("V4", "UNKNOWN_OWNERSHIP_RELATION", "ERROR", f"Unknown relation: {relation}"))
        if relation == "OWNS":
            findings.append(Finding("V4", "SECONDARY_OWNERSHIP_DECLARATION", "ERROR", "Relationships cannot create a second authoritative owner"))
    return findings


def validate_dependency_consistency(artifacts: dict[str, Path]) -> list[Finding]:
    findings: list[Finding] = []
    if "ownership" not in artifacts:
        return findings
    ownership = load_json(artifacts["ownership"])
    forbidden_projection_consumers = {"CTX-SYNC"}
    for rel in ownership.get("relationships", []):
        source = rel.get("source_fact", "")
        consumer = rel.get("consumer_context", "")
        relation = rel.get("relation", "")
        if relation == "PROJECTS" and consumer in forbidden_projection_consumers:
            findings.append(Finding("V5", "SYNC_PROJECTION_AUTHORITY_RISK", "ERROR", f"{consumer} cannot gain authority by projecting {source}"))
        if relation in {"REFERENCES", "PROJECTS"} and not source:
            findings.append(Finding("V5", "DEPENDENCY_SOURCE_MISSING", "ERROR", f"Missing source_fact for {consumer}"))
    return findings


def validate_contract_compatibility(artifacts: dict[str, Path]) -> list[Finding]:
    findings: list[Finding] = []
    if "contract" not in artifacts:
        return findings
    contracts = load_json(artifacts["contract"])["contracts"]
    names = [c["canonical_name"] for c in contracts]
    for duplicate in _duplicates(names):
        findings.append(Finding("V6", "DUPLICATE_CONTRACT_NAME", "ERROR", duplicate))
    for contract in contracts:
        if contract["contract_version"] < 1:
            findings.append(Finding("V6", "INVALID_CONTRACT_VERSION", "ERROR", contract["contract_id"]))
        if not contract.get("producer_contexts") or not contract.get("authorized_consumers"):
            findings.append(Finding("V6", "CONTRACT_ENDPOINTS_MISSING", "ERROR", contract["contract_id"]))
    return findings


def validate_invariant_coverage(artifacts: dict[str, Path]) -> list[Finding]:
    findings: list[Finding] = []
    required = {"invariant", "enforcement", "test_catalog", "traceability", "work_package_catalog"}
    if not required.issubset(artifacts):
        return findings
    inv_doc = load_json(artifacts["invariant"])
    trace = load_json(artifacts["traceability"])["links"]
    links_by_inv: dict[str, list[dict[str, Any]]] = {}
    for link in trace:
        links_by_inv.setdefault(link["invariant"], []).append(link)
    for inv in inv_doc["invariants"]:
        links = links_by_inv.get(inv["invariant_id"], [])
        if not links:
            findings.append(Finding("V7", "INVARIANT_NOT_TRACED", "ERROR", inv["invariant_id"]))
            continue
        for link in links:
            if not link.get("evidence"):
                findings.append(Finding("V7", "EVIDENCE_REFERENCE_MISSING", "ERROR", inv["invariant_id"]))
    blocker_controls = {c["control_id"] for c in load_json(artifacts["enforcement"])["controls"] if c["priority"] == "BLOCKER"}
    traced_controls = {l["control"] for l in trace}
    for control in sorted(blocker_controls - traced_controls):
        findings.append(Finding("V7", "BLOCKER_CONTROL_NOT_TRACED", "ERROR", control))
    return findings


def validate_exceptions(artifacts: dict[str, Path]) -> list[Finding]:
    findings: list[Finding] = []
    required = {"exception", "enforcement"}
    if not required.issubset(artifacts):
        return findings
    doc = load_json(artifacts["exception"])
    controls = {c["control_id"] for c in load_json(artifacts["enforcement"])["controls"]}
    non_waivable = set(doc.get("non_waivable_controls", []))
    for unknown in sorted(non_waivable - controls):
        findings.append(Finding("V8", "UNKNOWN_NON_WAIVABLE_CONTROL", "ERROR", unknown))
    seen = set()
    for exc in doc.get("exceptions", []):
        eid = exc.get("exception_id")
        if not eid or eid in seen:
            findings.append(Finding("V8", "INVALID_EXCEPTION_ID", "ERROR", str(eid)))
        seen.add(eid)
        control = exc.get("control_id")
        if control in non_waivable:
            findings.append(Finding("V8", "NON_WAIVABLE_EXCEPTION", "ERROR", f"{eid}: {control}"))
        if control not in controls:
            findings.append(Finding("V8", "UNKNOWN_EXCEPTION_CONTROL", "ERROR", f"{eid}: {control}"))
        if not exc.get("expires_at") or not exc.get("remediation_package"):
            findings.append(Finding("V8", "EXCEPTION_GOVERNANCE_INCOMPLETE", "ERROR", str(eid)))
    return findings

def validate() -> dict[str, Any]:
    artifacts, findings = discover()
    findings += validate_schemas(artifacts)
    if not any(f.stage in {"V0", "V1"} and f.severity == "ERROR" for f in findings):
        findings += validate_identity(artifacts)
        findings += validate_references(artifacts)
        findings += validate_ownership_consistency(artifacts)
        findings += validate_dependency_consistency(artifacts)
        findings += validate_contract_compatibility(artifacts)
        findings += validate_invariant_coverage(artifacts)
        findings += validate_exceptions(artifacts)
    stage_results = {}
    for stage in ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8"]:
        errors = [f for f in findings if f.stage == stage and f.severity == "ERROR"]
        stage_results[stage] = "FAIL" if errors else "PASS"
    result = "PASS" if all(v == "PASS" for v in stage_results.values()) else "FAIL"
    report = {
        "validation_id": "VAL-AB-FR0-001-V0-V8",
        "baseline_id": "AB-FR0-001",
        "validator_version": "1.1.0",
        "stages": stage_results,
        "result": result,
        "findings": [asdict(f) for f in findings],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return report


def generate_lock() -> dict[str, Any]:
    report = validate()
    if report["result"] != "PASS":
        raise RuntimeError("V0–V8 validation failed; lock generation refused")
    baseline = load_json(BASELINE_PATH)
    registries = {}
    for key, filename in REGISTRY_FILES.items():
        doc = load_json(REGISTRY_DIR / filename)
        registries[key] = {
            "registry_id": doc["registry_id"],
            "version": doc["registry_version"],
            "digest": sha256_hex(doc),
        }
    lock = {
        "baseline_id": baseline["baseline_id"],
        "baseline_version": baseline["baseline_version"],
        "canonicalization": {
            "specification": "RFC-8785",
            "profile": "FR0-INTEGER-ONLY",
            "encoding": "UTF-8",
        },
        "digest": {"algorithm": "SHA-256", "baseline_digest": ""},
        "registries": registries,
        "validation": {
            "validation_id": report["validation_id"],
            "validator_version": report["validator_version"],
            "stages": report["stages"],
            "result": report["result"],
        },
    }
    material = copy.deepcopy(lock)
    material["digest"]["baseline_digest"] = None
    lock["digest"]["baseline_digest"] = sha256_hex(material)
    LOCK_PATH.write_text(json.dumps(lock, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return lock


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "lock"])
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            output = validate()
        else:
            output = generate_lock()
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0 if output.get("result", output.get("validation", {}).get("result")) == "PASS" else 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
