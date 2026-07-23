from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.fr0 import LOCK_PATH, REGISTRY_DIR, generate_lock, load_json, sha256_hex, validate
from src.jcs import CanonicalizationError, canonicalize


class FR0Tests(unittest.TestCase):
    def test_v0_v8_pass(self):
        report = validate()
        self.assertEqual("PASS", report["result"], report)
        self.assertEqual({"V0": "PASS", "V1": "PASS", "V2": "PASS", "V3": "PASS", "V4": "PASS", "V5": "PASS", "V6": "PASS", "V7": "PASS", "V8": "PASS"}, report["stages"])

    def test_lock_is_deterministic(self):
        first = generate_lock()
        second = generate_lock()
        self.assertEqual(first, second)
        self.assertEqual(64, len(first["digest"]["baseline_digest"]))

    def test_key_order_uses_utf16(self):
        value = {"😀": 1, "\ue000": 2}
        encoded = canonicalize(value).decode("utf-8")
        self.assertTrue(encoded.startswith('{"😀"'), encoded)

    def test_floats_are_rejected(self):
        with self.assertRaises(CanonicalizationError):
            canonicalize({"value": 1.5})

    def test_registry_digest_changes_on_normative_change(self):
        doc = load_json(REGISTRY_DIR / "context-registry.v1.json")
        before = sha256_hex(doc)
        changed = copy.deepcopy(doc)
        changed["contexts"][0]["purpose"] += " changed"
        self.assertNotEqual(before, sha256_hex(changed))


    def test_every_invariant_is_traced(self):
        trace = load_json(REGISTRY_DIR / "traceability-registry.v1.json")
        inv = load_json(REGISTRY_DIR / "invariant-registry.v1.json")
        self.assertEqual({x["invariant_id"] for x in inv["invariants"]}, {x["invariant"] for x in trace["links"]})

    def test_non_waivable_controls_exist(self):
        exc = load_json(REGISTRY_DIR / "exception-registry.v1.json")
        enf = load_json(REGISTRY_DIR / "enforcement-registry.v1.json")
        controls = {x["control_id"] for x in enf["controls"]}
        self.assertTrue(set(exc["non_waivable_controls"]).issubset(controls))


if __name__ == "__main__":
    unittest.main()
