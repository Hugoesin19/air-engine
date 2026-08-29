"""Contract domain model."""

from __future__ import annotations

from dataclasses import dataclass

from varly.core.types import AIR_SCHEMA_VERSION

ParamScalar = str | int | float | bool | None
ParamValue = ParamScalar | tuple[ParamScalar, ...]


@dataclass(frozen=True, slots=True)
class InvariantSpec:
    """A single verifiable invariant declared in a contract."""

    id: str
    params: dict[str, ParamValue]


@dataclass(frozen=True, slots=True)
class Contract:
    """Versioned collection of invariants that define expected behavior."""

    air_schema_version: str
    invariants: tuple[InvariantSpec, ...]

    @classmethod
    def with_defaults(cls, invariants: tuple[InvariantSpec, ...]) -> Contract:
        return cls(
            air_schema_version=AIR_SCHEMA_VERSION,
            invariants=invariants,
        )
