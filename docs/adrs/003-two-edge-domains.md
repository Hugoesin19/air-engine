# ADR-003: Bipartition of the Relational Model (Control vs Information)

**Status:** Accepted  
**Date:** 2026-07-13

## Context

Executions involve both **control flow** (what runs before what) and **information flow** (what data is read, written, or referenced). A single edge set with uniform semantics cannot express both without contradictions.

Requiring the entire graph to be a DAG prevents modeling iterative reads over the same resource (information cycles). Treating all edges as causal would incorrectly impose execution order on passive data references.

## Alternatives

1. **Single edge set, all causal** — Simple model but cannot represent read/write cycles without false causal dependencies.
2. **Single edge set, all referential** — Loses execution order; state reconstruction becomes ill-defined.
3. **Bipartition into disjoint subgraphs** — `E = E_c ∪̇ E_r` with distinct semantics and invariants per subgraph.

## Decision

The edge set is divided into two **strictly disjoint** domains:

| Subgraph | Symbol | Role | Constraints |
|----------|--------|------|-------------|
| Control causality | `E_c` | Execution flow | Must form a DAG; sole source for state reconstruction |
| Information reference | `E_r` | Data access and provenance | May contain cycles; orthogonal to control order |

Semantic edge types for `E_c`: `causes`, `invokes`, `produces`, `contains`.  
Semantic edge types for `E_r`: `reads`, `writes`, `references`.

No edge in `E_r` may alter the partial order induced by `E_c`.

## Justification

Requiring global acyclicity would forbid modeling iterative reads of the same resource. Separating control from information guarantees mathematical acyclicity in execution flow while preserving data provenance, including cyclic information patterns.

State reconstruction uses only `E_c`. `E_r` influences semantic evaluation in Layer 3 but never topology.

## Consequences

- **Positive:** Rigorous state reconstruction via causal ancestors only.
- **Positive:** Rich information modeling without corrupting the execution DAG.
- **Negative:** Adapter authors must classify every edge correctly.
- **Negative:** Validation must enforce `E_c ∩ E_r = ∅` and DAG invariant on `E_c`.

## References

- Project Bible, Part VI — Section 6 (Relations and Subgraph Separation)
- Project Bible, Part VI — Axiom 7 (Referential Orthogonality)
