# ADR-004: Functional State Reconstruction Over Materialized Persistence

**Status:** Accepted  
**Date:** 2026-07-13

## Context

Verification often needs the **state at a node** — what was known when a tool was invoked, what context an LLM saw, etc. The engine must provide this without introducing a second mutable source of truth that can drift from the trace.

Materializing intermediate state in databases or mutable in-memory structures is a common pattern in debuggers and observability tools.

## Alternatives

1. **Materialized state store** — Persist state snapshots at each step. Fast lookup but risks desynchronization from the graph.
2. **Event sourcing with mutable aggregate** — Rebuild state once, then allow updates. Violates immutability principles.
3. **Pure functional reduction** — State at node `v` is computed by reducing over causal ancestors `Anc_{E_c}(v)` using a canonical topological order `O_can`.

## Decision

Execution **state is never stored** in persistent memory or databases. It is computed on demand via functional reduction:

```
state(v) = ⊕_{u ∈ O_can(Anc_{E_c}(v))} δ(u, S_0)
```

where `S_0` is the initial state, `⊕` is the reduction operator, and `O_can` is the canonical linear extension of the causal partial order.

State is a **derived, ephemeral** Layer 3 value. It is not part of the Trace.

## Justification

Storing intermediate state introduces a second source of truth that can desynchronize from the topological graph. State must be a pure, deterministic derivative of topology. If the trace is correct, state reconstruction is always reproducible.

This also keeps the MVP scope honest: no derived-state persistence (per Project Bible, Part VII).

## Consequences

- **Positive:** Single source of truth (the Trace); no sync bugs between graph and state store.
- **Positive:** Aligns with pure functional core; easy to test reduction in isolation.
- **Negative:** Repeated state queries recompute; caching is an optimization, not a correctness requirement.
- **Negative:** `⊕` must be associative; commutativity is not required because `O_can` fixes evaluation order.

## References

- Project Bible, Part VI — Section 7.1 (Reconstructed State)
- Project Bible, Part VII — MVP Scope Out (no derived-state persistence)
