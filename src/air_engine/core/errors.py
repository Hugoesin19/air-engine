"""Typed domain errors for the AIR verification engine."""

from __future__ import annotations


class AirEngineError(Exception):
    """Base error for all air-engine domain failures."""


class StructuralValidationError(AirEngineError):
    """Raised when a trace violates structural axioms."""


class DuplicateIdError(StructuralValidationError):
    """Raised when node or edge identifiers are not unique."""


class UnknownNodeReferenceError(StructuralValidationError):
    """Raised when an edge references a node that does not exist."""


class InvalidRootError(StructuralValidationError):
    """Raised when root_id is missing or violates root invariants."""


class CycleDetectedError(StructuralValidationError):
    """Raised when control edges form a cycle."""


class UnreachableNodeError(StructuralValidationError):
    """Raised when a node is not reachable from the root via control edges."""


class OverlappingEdgeIdError(StructuralValidationError):
    """Raised when control and referential edges share an identifier."""
