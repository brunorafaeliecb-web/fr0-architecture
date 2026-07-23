from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar


_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$"
)


class NormativeStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"


class Priority(str, Enum):
    BLOCKER = "BLOCKER"
    REQUIRED_BEFORE_IMPLEMENTATION = "REQUIRED_BEFORE_IMPLEMENTATION"
    REQUIRED_BEFORE_PRODUCTION = "REQUIRED_BEFORE_PRODUCTION"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True, order=True)
class RegistryVersion:
    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise TypeError("registry version must be an integer")

        if self.value < 1:
            raise ValueError("registry version must be positive")

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, order=True)
class CanonicalIdentifier:
    value: str

    expected_prefix: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("identifier must be a string")

        if not _IDENTIFIER_PATTERN.fullmatch(self.value):
            raise ValueError(
                f"invalid canonical identifier: {self.value!r}"
            )

        if (
            self.expected_prefix is not None
            and not self.value.startswith(
                f"{self.expected_prefix}-"
            )
        ):
            raise ValueError(
                f"identifier {self.value!r} must use "
                f"{self.expected_prefix!r} prefix"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, order=True)
class BaselineId(CanonicalIdentifier):
    expected_prefix: str | None = "AB"


@dataclass(frozen=True, order=True)
class ContextId(CanonicalIdentifier):
    expected_prefix: str | None = "CTX"


@dataclass(frozen=True, order=True)
class FactId(CanonicalIdentifier):
    expected_prefix: str | None = "FACT"


@dataclass(frozen=True, order=True)
class DecisionId(CanonicalIdentifier):
    expected_prefix: str | None = "DEC"


EnumType = TypeVar("EnumType", bound=Enum)


def parse_enum(enum_type: type[EnumType], value: str) -> EnumType:
    try:
        return enum_type(value)
    except ValueError as error:
        allowed = ", ".join(
            str(member.value) for member in enum_type
        )
        raise ValueError(
            f"invalid {enum_type.__name__}: {value!r}; "
            f"expected one of: {allowed}"
        ) from error
