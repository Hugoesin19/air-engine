"""Load contracts from YAML or JSON policy files."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from varly.contracts.errors import ContractLoadError
from varly.contracts.model import Contract, InvariantSpec, ParamScalar, ParamValue
from varly.core.types import AIR_SCHEMA_VERSION

_REQUIRED_FIELDS = ("air_schema_version", "invariants")


def load_policy_file(path: Path) -> Contract:
    """Load a contract from a YAML or JSON policy file."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"Unable to read contract file: {path}"
        raise ContractLoadError(msg) from exc

    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            payload = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            msg = f"Invalid YAML in contract file: {path}"
            raise ContractLoadError(msg) from exc
    elif suffix == ".json":
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            msg = f"Invalid JSON in contract file: {path}"
            raise ContractLoadError(msg) from exc
    else:
        msg = f"Unsupported contract file extension: {path.suffix}"
        raise ContractLoadError(msg)

    if not isinstance(payload, dict):
        msg = f"Contract file must contain a mapping at top level: {path}"
        raise ContractLoadError(msg)
    return parse_contract_payload(payload)


def parse_contract_payload(payload: Mapping[str, Any]) -> Contract:
    """Parse an in-memory policy payload into a Contract."""
    for field in _REQUIRED_FIELDS:
        if field not in payload:
            msg = f"Missing required contract field: {field}"
            raise ContractLoadError(msg)

    version = payload["air_schema_version"]
    if not isinstance(version, str) or not version:
        msg = "Field 'air_schema_version' must be a non-empty string"
        raise ContractLoadError(msg)
    if version != AIR_SCHEMA_VERSION:
        msg = (
            f"Unsupported air_schema_version: {version!r} "
            f"(expected {AIR_SCHEMA_VERSION!r})"
        )
        raise ContractLoadError(msg)

    invariants_raw = payload["invariants"]
    if not isinstance(invariants_raw, list):
        msg = "Field 'invariants' must be a list"
        raise ContractLoadError(msg)

    invariants = tuple(
        _parse_invariant(item, index) for index, item in enumerate(invariants_raw)
    )
    return Contract(air_schema_version=version, invariants=invariants)


def _parse_invariant(item: object, index: int) -> InvariantSpec:
    prefix = f"invariants[{index}]"
    if not isinstance(item, dict):
        msg = f"{prefix} must be an object"
        raise ContractLoadError(msg)

    invariant_id = item.get("id")
    if not isinstance(invariant_id, str) or not invariant_id:
        msg = f"{prefix}.id must be a non-empty string"
        raise ContractLoadError(msg)

    params_raw = item.get("params", {})
    if params_raw is None:
        params_raw = {}
    if not isinstance(params_raw, dict):
        msg = f"{prefix}.params must be an object when provided"
        raise ContractLoadError(msg)

    params: dict[str, ParamValue] = {}
    for key, value in params_raw.items():
        if not isinstance(key, str):
            msg = f"{prefix}.params keys must be strings"
            raise ContractLoadError(msg)
        params[key] = _materialize_param_value(value, f"{prefix}.params['{key}']")

    return InvariantSpec(id=invariant_id, params=params)


def _materialize_param_value(value: object, prefix: str) -> ParamValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        items: list[ParamScalar] = []
        for index, item in enumerate(value):
            if item is not None and not isinstance(item, (str, int, float, bool)):
                msg = f"{prefix}[{index}] must be a primitive JSON value"
                raise ContractLoadError(msg)
            items.append(item)
        return tuple(items)
    msg = f"{prefix} must be a primitive JSON value or a list of primitives"
    raise ContractLoadError(msg)
