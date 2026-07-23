from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping

from .foundation_types import (
    BaselineId,
    CanonicalIdentifier,
    ContextId,
    NormativeStatus,
    RegistryVersion,
    parse_enum,
)
from .jcs import canonicalize


class InteractionType(str, Enum):
    QUERY = "QUERY"
    COMMAND = "COMMAND"
    EVENT = "EVENT"
    DECISION = "DECISION"


_CONTRACT_PREFIX = {
    InteractionType.QUERY: "QRY",
    InteractionType.COMMAND: "CMD",
    InteractionType.EVENT: "EVT",
    InteractionType.DECISION: "DEC",
}


@dataclass(frozen=True)
class ContractDefinition:
    contract_id: CanonicalIdentifier
    canonical_name: str
    interaction_type: InteractionType
    semantic_owner: ContextId
    producer_contexts: tuple[ContextId, ...]
    authorized_consumers: tuple[ContextId, ...]
    contract_version: RegistryVersion
    status: NormativeStatus

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
    ) -> "ContractDefinition":
        interaction_type = parse_enum(
            InteractionType,
            value["interaction_type"],
        )

        contract_id = CanonicalIdentifier(value["contract_id"])
        expected_prefix = _CONTRACT_PREFIX[interaction_type]

        if not contract_id.value.startswith(
            f"{expected_prefix}-"
        ):
            raise ValueError(
                f"contract {contract_id} must use "
                f"{expected_prefix} prefix for "
                f"{interaction_type.value}"
            )

        canonical_name = value["canonical_name"]

        if (
            not isinstance(canonical_name, str)
            or not canonical_name.strip()
        ):
            raise ValueError(
                "canonical_name must be a non-empty string"
            )

        producers = tuple(
            ContextId(context_id)
            for context_id in value["producer_contexts"]
        )
        consumers = tuple(
            ContextId(context_id)
            for context_id in value["authorized_consumers"]
        )

        if not producers:
            raise ValueError(
                "contract must declare at least one producer"
            )

        if not consumers:
            raise ValueError(
                "contract must declare at least one consumer"
            )

        return cls(
            contract_id=contract_id,
            canonical_name=canonical_name,
            interaction_type=interaction_type,
            semantic_owner=ContextId(
                value["semantic_owner"]
            ),
            producer_contexts=producers,
            authorized_consumers=consumers,
            contract_version=RegistryVersion(
                value["contract_version"]
            ),
            status=parse_enum(
                NormativeStatus,
                value["status"],
            ),
        )


def _require_utc_timestamp(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "occurred_at must be an ISO-8601 string"
        )

    normalized = value.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ValueError(
            "occurred_at must be a valid ISO-8601 timestamp"
        ) from error

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
        or parsed.utcoffset().total_seconds() != 0
    ):
        raise ValueError(
            "occurred_at must use UTC"
        )

    return parsed.isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ContractEnvelope:
    envelope_version: RegistryVersion
    message_id: CanonicalIdentifier
    contract: ContractDefinition
    architecture_baseline_id: BaselineId
    producer_context: ContextId
    consumer_context: ContextId
    occurred_at: str
    correlation_id: CanonicalIdentifier
    causation_id: CanonicalIdentifier | None
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.message_id.value.startswith("MSG-"):
            raise ValueError(
                "message_id must use MSG prefix"
            )

        if not self.correlation_id.value.startswith("CORR-"):
            raise ValueError(
                "correlation_id must use CORR prefix"
            )

        if (
            self.causation_id is not None
            and not self.causation_id.value.startswith("MSG-")
        ):
            raise ValueError(
                "causation_id must use MSG prefix"
            )

        if self.causation_id == self.message_id:
            raise ValueError(
                "causation_id cannot equal message_id"
            )

        if self.producer_context not in (
            self.contract.producer_contexts
        ):
            raise ValueError(
                f"{self.producer_context} is not an authorized "
                f"producer for {self.contract.contract_id}"
            )

        if self.consumer_context not in (
            self.contract.authorized_consumers
        ):
            raise ValueError(
                f"{self.consumer_context} is not an authorized "
                f"consumer for {self.contract.contract_id}"
            )

        object.__setattr__(
            self,
            "occurred_at",
            _require_utc_timestamp(self.occurred_at),
        )

        if not isinstance(self.payload, Mapping):
            raise TypeError(
                "payload must be a mapping"
            )

        payload_copy = copy.deepcopy(dict(self.payload))

        # Prova que o payload é compatível com a representação
        # canônica do FR-0. Floats e tipos não suportados falham aqui.
        canonicalize(payload_copy)

        object.__setattr__(
            self,
            "payload",
            payload_copy,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": {
                "envelope_version": int(
                    self.envelope_version
                ),
                "message_id": str(self.message_id),
                "contract_id": str(
                    self.contract.contract_id
                ),
                "contract_version": int(
                    self.contract.contract_version
                ),
                "interaction_type": (
                    self.contract.interaction_type.value
                ),
                "architecture_baseline_id": str(
                    self.architecture_baseline_id
                ),
                "producer_context": str(
                    self.producer_context
                ),
                "consumer_context": str(
                    self.consumer_context
                ),
                "occurred_at": self.occurred_at,
                "correlation_id": str(
                    self.correlation_id
                ),
                "causation_id": (
                    str(self.causation_id)
                    if self.causation_id is not None
                    else None
                ),
            },
            "payload": copy.deepcopy(
                dict(self.payload)
            ),
        }

    def canonical_bytes(self) -> bytes:
        return canonicalize(self.to_dict())
