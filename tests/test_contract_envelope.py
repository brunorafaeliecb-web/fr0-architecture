from __future__ import annotations

import unittest

from src.contract_envelope import (
    ContractDefinition,
    ContractEnvelope,
    InteractionType,
)
from src.foundation_types import (
    BaselineId,
    CanonicalIdentifier,
    ContextId,
    RegistryVersion,
)
from src.fr0 import REGISTRY_DIR, load_json
from src.jcs import CanonicalizationError


class CanonicalContractEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        registry = load_json(
            REGISTRY_DIR / "contract-registry.v1.json"
        )
        cls.contract_documents = registry["contracts"]
        cls.contracts = [
            ContractDefinition.from_mapping(document)
            for document in cls.contract_documents
        ]

    def _command_contract(self):
        return next(
            contract
            for contract in self.contracts
            if contract.interaction_type
            is InteractionType.COMMAND
        )

    def _envelope(self, **changes):
        contract = changes.pop(
            "contract",
            self._command_contract(),
        )

        values = {
            "envelope_version": RegistryVersion(1),
            "message_id": CanonicalIdentifier(
                "MSG-000001"
            ),
            "contract": contract,
            "architecture_baseline_id": BaselineId(
                "AB-FR0-001"
            ),
            "producer_context": (
                contract.producer_contexts[0]
            ),
            "consumer_context": (
                contract.authorized_consumers[0]
            ),
            "occurred_at": "2026-07-23T17:30:00Z",
            "correlation_id": CanonicalIdentifier(
                "CORR-000001"
            ),
            "causation_id": None,
            "payload": {
                "baseline_id": "AB-FR0-001",
                "attempt": 1,
            },
        }

        values.update(changes)
        return ContractEnvelope(**values)

    def test_all_registry_contracts_are_valid_definitions(self):
        self.assertEqual(
            len(self.contract_documents),
            len(self.contracts),
        )

    def test_contract_prefix_matches_interaction_type(self):
        prefixes = {
            InteractionType.QUERY: "QRY-",
            InteractionType.COMMAND: "CMD-",
            InteractionType.EVENT: "EVT-",
            InteractionType.DECISION: "DEC-",
        }

        for contract in self.contracts:
            with self.subTest(
                contract=str(contract.contract_id)
            ):
                self.assertTrue(
                    str(contract.contract_id).startswith(
                        prefixes[contract.interaction_type]
                    )
                )

    def test_envelope_serializes_deterministically(self):
        envelope = self._envelope()

        self.assertEqual(
            envelope.canonical_bytes(),
            envelope.canonical_bytes(),
        )

    def test_envelope_contains_normative_metadata(self):
        document = self._envelope().to_dict()
        metadata = document["metadata"]

        self.assertEqual(
            "AB-FR0-001",
            metadata["architecture_baseline_id"],
        )
        self.assertEqual(
            1,
            metadata["contract_version"],
        )
        self.assertEqual(
            "COMMAND",
            metadata["interaction_type"],
        )

    def test_payload_is_defensively_copied(self):
        payload = {"attempt": 1}
        envelope = self._envelope(payload=payload)

        payload["attempt"] = 2

        self.assertEqual(
            1,
            envelope.to_dict()["payload"]["attempt"],
        )

    def test_float_payload_is_rejected(self):
        with self.assertRaises(
            CanonicalizationError
        ):
            self._envelope(
                payload={"confidence": 0.5}
            )

    def test_non_utc_timestamp_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "must use UTC",
        ):
            self._envelope(
                occurred_at="2026-07-23T14:30:00-03:00"
            )

    def test_invalid_message_prefix_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "MSG prefix",
        ):
            self._envelope(
                message_id=CanonicalIdentifier(
                    "EVENT-000001"
                )
            )

    def test_invalid_correlation_prefix_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "CORR prefix",
        ):
            self._envelope(
                correlation_id=CanonicalIdentifier(
                    "MSG-000002"
                )
            )

    def test_causation_cannot_equal_message_id(self):
        identifier = CanonicalIdentifier(
            "MSG-000001"
        )

        with self.assertRaisesRegex(
            ValueError,
            "cannot equal",
        ):
            self._envelope(
                message_id=identifier,
                causation_id=identifier,
            )

    def test_unauthorized_producer_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "not an authorized producer",
        ):
            self._envelope(
                producer_context=ContextId(
                    "CTX-VOICE"
                )
            )

    def test_unauthorized_consumer_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "not an authorized consumer",
        ):
            self._envelope(
                consumer_context=ContextId(
                    "CTX-VOICE"
                )
            )


if __name__ == "__main__":
    unittest.main()
