# ADR-002: Ontological Separation Between Structural Node and Semantic Event

**Status:** Accepted  
**Date:** 2026-07-13

## Context

Executions are modeled as decorated graphs. The system must separate mathematical topology (Layer 1) from operational meaning (Layer 2). Domain concepts such as `ToolCall`, `LLMResponse`, or `AgentHandoff` are tempting to model as first-class node types in the structural layer.

If structure and domain are fused, the core graph algebra must know business rules, breaking orthogonality and complicating schema evolution.

## Alternatives

1. **Typed node hierarchy** — Each event type is a distinct structural node class (e.g. `ToolCallNode`, `MessageNode`). Simple for readers but couples Layer 1 to Layer 2.
2. **Event as topological primitive** — Events are vertices with intrinsic meaning. Collapses structure and semantics.
3. **Structural node + semantic projection** — Vertices are meaningless carriers; an Event is the pair `(v, λ_V(v))` where `λ_V` is the semantic labeling function.

## Decision

The topological vertex `V` has **no intrinsic meaning**. An **Event** is not a primitive; it is formally defined as:

```
Event(v) = (v, λ_V(v))
```

where `v ∈ V` is a structural node and `λ_V` is the semantic labeling function.

Agents, tools, and resources have no topological identity — they appear only as attributes or references in the semantic projection of the corresponding node.

## Justification

Merging structure with domain (e.g. making `ToolCall` a structural node class) forces Layer 1 mathematics to know Layer 2 business rules. That breaks orthogonality and makes every new semantic type a structural schema change.

Separating node from projection allows the graph algebra to remain stable while the semantic type system evolves additively.

## Consequences

- **Positive:** Clean three-layer model; schema evolution is additive on `Σ_V` and `Σ_E`.
- **Positive:** Multiple frameworks can map to the same topology with different labelings.
- **Negative:** Less intuitive for developers expecting OOP-style event classes.
- **Negative:** Queries must always go through `λ_V`; raw nodes are not self-describing.

## References

- Project Bible, Part VI — Ontological Commitment
- Project Bible, Part V — Glossary (Event, AIR)
