# ADR-001: Strict Immutability of the Analysis Intermediate Representation (AIR)

**Status:** Accepted  
**Date:** 2026-07-13

## Context

The verification engine operates on completed executions. Developers need reproducible diagnostics: the same trace and contracts must always yield the same evaluation results. If the intermediate representation could be mutated during analysis, verification would depend on evaluation order and side effects, destroying reproducibility.

The system must act as an auditor of past facts, not as an interactive debugger that rewrites history.

## Alternatives

1. **Mutable trace with copy-on-write** — Allow in-place updates but fork before verification. Adds complexity and risks accidental mutation before the fork point.
2. **Lazy/mutable views over the trace** — Projections that can be updated during evaluation. Breaks the guarantee that the trace is a closed universe for verification.
3. **Strict immutability** — The Trace is a static, read-only artifact once constructed. All derived data (state, diagnostics) lives outside the Trace.

## Decision

The Trace is defined as a **static, read-only artifact**. Once emitted, no structural or semantic element of the AIR may be modified, deleted, or replaced. Layer 3 (derived) computations never write back into the Trace.

## Justification

Allowing mutation of events or relations during verification would destroy reproducibility. Two evaluations of the same contract set could observe different traces. Immutability makes the Trace a single source of truth for what happened; all analysis is a pure function over that artifact.

This aligns with the ontological commitment: topology is persistent; semantics and behavior are obtained via external pure functions.

## Consequences

- **Positive:** Deterministic verification; safe concurrent reads; clear audit boundary.
- **Positive:** Simpler reasoning about correctness — no hidden state in the representation.
- **Negative:** Corrections to captured data require re-ingestion, not in-place fixes.
- **Negative:** Large traces cannot be incrementally patched; a new Trace must be emitted.

## References

- Project Bible, Part VI — Axiom 3 (Immutability)
- Project Bible, Part VIII — Architectural invariants in code
