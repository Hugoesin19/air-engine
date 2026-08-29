"""Unit tests for contract policy loading."""

from __future__ import annotations

import pytest

from varly.contracts import ContractLoadError, parse_contract_payload


def test_parse_contract_accepts_list_params() -> None:
    contract = parse_contract_payload(
        {
            "air_schema_version": "1.0.0",
            "invariants": [
                {
                    "id": "tool_name_allowlist",
                    "params": {"allowed": ["search", "calc"]},
                }
            ],
        }
    )
    assert contract.invariants[0].params["allowed"] == ("search", "calc")


def test_parse_contract_rejects_nested_object_params() -> None:
    with pytest.raises(ContractLoadError, match="primitive"):
        parse_contract_payload(
            {
                "air_schema_version": "1.0.0",
                "invariants": [
                    {
                        "id": "example",
                        "params": {"nested": {"a": 1}},
                    }
                ],
            }
        )
