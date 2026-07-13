# ADR Index

Architecture Decision Records document foundational technical decisions for air-engine.

ADRs are **immutable**. To change a decision, publish a new ADR that explicitly supersedes the previous one.

## Active Records

| ADR | Title | Status |
|-----|-------|--------|
| [001](001-air-immutable.md) | Strict immutability of AIR | Accepted |
| [002](002-event-projection.md) | Structural node vs semantic event | Accepted |
| [003](003-two-edge-domains.md) | Bipartition of control and information edges | Accepted |
| [004](004-functional-state.md) | Functional state reconstruction | Accepted |
| [005](005-uuidv7-order.md) | UUIDv7 as canonical linearization | Accepted |

## Template

Each ADR must include: **Context**, **Alternatives**, **Decision**, **Justification**, and **Consequences**.
