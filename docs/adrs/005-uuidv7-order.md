# ADR-005: UUIDv7 as External Canonical Linearization (O_can)

**Status:** Accepted  
**Date:** 2026-07-13

## Context

State reconstruction over a DAG requires evaluating nodes in an order consistent with causal precedence. When multiple nodes are **concurrent** (no causal path between them), the reduction operator `⊕` needs a **deterministic tie-break** to serialize parallel branches.

Without a canonical order, the same trace could yield different states if reduction order varies. Requiring full commutativity of `⊕` for all domain operations is impractical in real systems.

## Alternatives

1. **Require commutative ⊕** — Mathematically elegant but unrealistic for ordered accumulators (lists, transcripts, token counts).
2. **Arbitrary insertion order** — Depends on capture adapter ordering; not reproducible across frameworks.
3. **External deterministic tie-break** — Fix a total order among concurrent nodes without adding causal edges. UUIDv7 timestamp component provides lexicographic ordering.

## Decision

The **physical time component of UUIDv7** is used exclusively as a **lexicographic tie-break** when establishing canonical linearization `O_can` among concurrent nodes in the causal DAG.

```
O_can : 2^V → V*
```

`O_can` is a deterministic linear extension of the partial order `≺_c` induced by `E_c`. When two nodes are concurrent, the UUIDv7 timestamp breaks the tie.

**Critical constraint:** The timestamp never introduces new causal relationships. It only resolves serialization among nodes already known to be concurrent.

## Justification

State reduction over a DAG requires strict topological order. Instead of demanding absolute commutativity from the domain algebra (often infeasible), UUIDv7 provides a universal, deterministic mechanism to serialize parallelism without altering true causal topology.

UUIDv7 also supports future distributed trace consolidation via time-ordered, globally unique identifiers.

## Consequences

- **Positive:** Reproducible state reconstruction across platforms and re-runs.
- **Positive:** Works for any adapter that assigns UUIDv7 node IDs at creation time.
- **Negative:** Incorrect ID assignment (non-v7 or clock skew) can affect tie-break order among concurrent nodes — not correctness of causality, but ordering of commutative-adjacent merges.
- **Negative:** Adapters must emit UUIDv7; other ID schemes need a documented mapping layer.

## References

- Project Bible, Part VI — Section 8 (Canonical Linear Extension)
- Project Bible, Part X — ADR-005 source rationale
