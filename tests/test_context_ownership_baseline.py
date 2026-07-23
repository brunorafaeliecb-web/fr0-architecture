from __future__ import annotations

import unittest

from src.fr0 import REGISTRY_DIR, load_json


class ContextAndOwnershipBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context_registry = load_json(
            REGISTRY_DIR / "context-registry.v1.json"
        )
        cls.ownership_registry = load_json(
            REGISTRY_DIR / "ownership-registry.v1.json"
        )

        cls.contexts = cls.context_registry["contexts"]
        cls.facts = cls.ownership_registry["facts"]
        cls.decisions = cls.ownership_registry.get("decisions", [])
        cls.relationships = cls.ownership_registry.get("relationships", [])

        cls.context_ids = {
            context["context_id"] for context in cls.contexts
        }
        cls.fact_ids = {
            fact["fact_id"] for fact in cls.facts
        }

    def test_context_ids_are_unique(self):
        ids = [context["context_id"] for context in self.contexts]
        self.assertEqual(len(ids), len(set(ids)))

    def test_context_canonical_names_are_unique(self):
        names = [
            context["canonical_name"] for context in self.contexts
        ]
        self.assertEqual(len(names), len(set(names)))

    def test_context_purposes_are_not_placeholders(self):
        for context in self.contexts:
            with self.subTest(context=context["context_id"]):
                purpose = context["purpose"].strip()
                self.assertGreaterEqual(len(purpose), 20)
                self.assertNotIn("TODO", purpose.upper())
                self.assertNotIn("TBD", purpose.upper())

    def test_fact_ids_are_unique(self):
        ids = [fact["fact_id"] for fact in self.facts]
        self.assertEqual(len(ids), len(set(ids)))

    def test_fact_canonical_names_are_unique(self):
        names = [fact["canonical_name"] for fact in self.facts]
        self.assertEqual(len(names), len(set(names)))

    def test_every_fact_has_valid_semantic_owner(self):
        for fact in self.facts:
            with self.subTest(fact=fact["fact_id"]):
                self.assertIn(
                    fact["semantic_owner"],
                    self.context_ids,
                )

    def test_every_fact_has_valid_transition_owner(self):
        for fact in self.facts:
            with self.subTest(fact=fact["fact_id"]):
                self.assertIn(
                    fact["transition_owner"],
                    self.context_ids,
                )

    def test_fact_priorities_are_normative(self):
        allowed = {
            "BLOCKER",
            "REQUIRED_BEFORE_IMPLEMENTATION",
            "REQUIRED_BEFORE_PRODUCTION",
        }

        for fact in self.facts:
            with self.subTest(fact=fact["fact_id"]):
                self.assertIn(fact["priority"], allowed)

    def test_decision_ids_are_unique(self):
        ids = [
            decision["decision_id"]
            for decision in self.decisions
        ]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_decision_has_valid_owner(self):
        for decision in self.decisions:
            with self.subTest(decision=decision["decision_id"]):
                self.assertIn(
                    decision["decision_owner"],
                    self.context_ids,
                )

    def test_every_decision_input_references_an_existing_fact(self):
        for decision in self.decisions:
            for input_fact in decision["inputs"]:
                with self.subTest(
                    decision=decision["decision_id"],
                    input=input_fact,
                ):
                    self.assertIn(input_fact, self.fact_ids)

    def test_decisions_have_at_least_one_input(self):
        for decision in self.decisions:
            with self.subTest(decision=decision["decision_id"]):
                self.assertTrue(decision["inputs"])

    def test_relationships_reference_known_contexts_when_present(self):
        owner_fields = {
            "source_context",
            "target_context",
            "upstream_context",
            "downstream_context",
        }

        for index, relationship in enumerate(self.relationships):
            for field in owner_fields & relationship.keys():
                with self.subTest(
                    relationship=index,
                    field=field,
                ):
                    self.assertIn(
                        relationship[field],
                        self.context_ids,
                    )

    def test_all_ownership_references_are_unambiguous(self):
        references = []

        for fact in self.facts:
            references.extend(
                [
                    fact["semantic_owner"],
                    fact["transition_owner"],
                ]
            )

        for decision in self.decisions:
            references.append(decision["decision_owner"])

        unknown = sorted(set(references) - self.context_ids)
        self.assertEqual([], unknown)


if __name__ == "__main__":
    unittest.main()
