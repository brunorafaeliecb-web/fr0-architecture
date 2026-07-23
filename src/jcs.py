"""Restricted RFC 8785 JSON Canonicalization Scheme implementation.

FR-0 normative artifacts intentionally prohibit floating-point values. With that
profile restriction, this module implements deterministic RFC 8785-compatible
serialization: UTF-16 property ordering, JSON escaping, UTF-8 output, and no
insignificant whitespace.
"""
from __future__ import annotations

import json
from typing import Any


class CanonicalizationError(ValueError):
    pass


def _reject_invalid(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise CanonicalizationError(f"floating-point value prohibited at {path}")
    if isinstance(value, str):
        for ch in value:
            cp = ord(ch)
            if 0xD800 <= cp <= 0xDFFF:
                raise CanonicalizationError(f"unpaired surrogate prohibited at {path}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _reject_invalid(item, f"{path}[{i}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"non-string object key at {path}")
            _reject_invalid(key, f"{path}.<key>")
            _reject_invalid(item, f"{path}.{key}")
    elif value is None or isinstance(value, (bool, int)):
        return
    else:
        raise CanonicalizationError(f"unsupported JSON value {type(value).__name__} at {path}")


def _utf16_sort_key(text: str) -> bytes:
    return text.encode("utf-16-be")


def _serialize(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(_serialize(item) for item in value) + "]"
    if isinstance(value, dict):
        parts = []
        for key in sorted(value, key=_utf16_sort_key):
            parts.append(_serialize(key) + ":" + _serialize(value[key]))
        return "{" + ",".join(parts) + "}"
    raise CanonicalizationError(f"unsupported JSON value {type(value).__name__}")


def canonicalize(value: Any) -> bytes:
    _reject_invalid(value)
    return _serialize(value).encode("utf-8")
