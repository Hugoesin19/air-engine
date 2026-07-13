# MVP Roadmap

> Living document for air-engine MVP execution.  
> **Update this file** at the start/end of each work session.  
> Reference: Project Bible (Part VII) · [ADRs](adrs/) · [Architecture](architecture/)

**Last updated:** 2026-07-13  
**Current phase:** Sprint 2 — Ordering + State Reconstruction  
**MVP status:** 🟡 In progress (Sprint 1 complete)

---

## MVP Definition

The MVP validates that the formal model, AIR representation, and verification engine produce **correct, deterministic, reproducible** results on real executions.

### Success Criteria (all required)

- [ ] Import a real async execution log (or static equivalent)
- [ ] Convert it to canonical AIR topology without losing causality
- [ ] Reconstruct intermediate state at any arbitrary node
- [ ] Run predefined contracts on the graph
- [ ] Produce a deterministic `Diagnostic` artifact
- [ ] Same diagnostic for the same trace regardless of execution platform

### Hypotheses Under Test

| ID | Hypothesis | Validated? | Evidence |
|----|------------|------------|----------|
| H1 | AIR models async execution without losing causality | 🟡 | Parser + examples + CLI validate |
| H2 | State reconstructs deterministically from topology only | ⬜ | |
| H3 | Contracts detect violations without false positives | ⬜ | |
| H4 | Model stays agnostic to origin framework | ⬜ | |

---

## Strategy

**Vertical slice** — one thin end-to-end path first, then widen.

```
JSON trace → Parser → Trace → Analyzer → Diagnostic → CLI
```

Do **not** build entire layers in isolation before the slice works.

---

## Implementation Phases

### Sprint 0 — Hello Trace ✅

**Goal:** Minimal valid `Trace` in memory + DAG validation.

- [x] `docs/architecture/air-schema-1.0.0.md` — minimal JSON schema spec
- [x] `examples/trace_valid_minimal.json`
- [x] `examples/trace_invalid_cycle.json`
- [x] `examples/trace_invalid_orphan.json`
- [x] `src/air_engine/core/types.py` — `NodeId`, edge kinds, semantic types
- [x] `src/air_engine/core/trace.py` — frozen `Trace`, `Node`, `Edge`
- [x] `src/air_engine/core/topology.py` — DAG check, reachability, root
- [x] `src/air_engine/core/errors.py` — typed domain errors
- [x] `tests/unit/core/test_topology.py`

**Done when:** valid trace passes validation; invalid traces fail with typed errors.

---

### Sprint 1 — Parser + Validate CLI ✅

**Goal:** `air-engine validate trace.json` works.

- [x] `src/air_engine/parser/json_loader.py`
- [x] `src/air_engine/parser/schema.py`
- [x] `src/air_engine/parser/builder.py`
- [x] `tests/integration/parser/` — fixture-driven
- [x] `src/air_engine/interfaces/cli/commands/validate.py`
- [x] CLI entry point in `pyproject.toml`
- [x] `examples/trace_valid_minimal.json` loads end-to-end

**Done when:** CLI exits 0 on valid trace, non-zero on invalid.

---

### Sprint 2 — Ordering + State Reconstruction

**Goal:** Deterministic state at any node (ADR-004, ADR-005).

- [ ] `src/air_engine/core/ordering.py` — `O_can` canonical linear extension
- [ ] `src/air_engine/core/state.py` — reduction `⊕` over causal ancestors
- [ ] `src/air_engine/core/labeling.py` — `λ_V`, `λ_E` projection
- [ ] `src/air_engine/analyzer/state_builder.py`
- [ ] `tests/unit/core/test_ordering.py`
- [ ] `tests/unit/core/test_state.py`

**Done when:** same trace → same state at node N, always.

---

### Sprint 3 — First Contract + Diagnostic

**Goal:** One invariant → structured diagnostic.

- [ ] `src/air_engine/contracts/model.py` — `Contract`, `Property`, `Invariant`
- [ ] `src/air_engine/contracts/loader.py` — YAML/JSON loader
- [ ] `src/air_engine/contracts/builtins/structural.py` — no cycles, reachability
- [ ] `src/air_engine/analyzer/diagnostic.py`
- [ ] `src/air_engine/analyzer/evaluator.py`
- [ ] `src/air_engine/analyzer/engine.py`
- [ ] `examples/policy_mvp.yaml`
- [ ] `tests/unit/analyzer/test_evaluator.py`

**Done when:** `verify` returns pass/fail + explanation for structural rules.

---

### Sprint 4 — Full Contract Catalog (MVP)

**Goal:** All MVP invariants from Project Bible Part VII §2.3.

- [ ] Structural: no causal cycles, root reachability, no orphans
- [ ] Semantic: `ToolCall` → reachable `ToolReturn` in `E_c`
- [ ] Metrics: max trace duration, token budget
- [ ] `src/air_engine/contracts/builtins/semantic.py`
- [ ] `src/air_engine/contracts/builtins/metrics.py`
- [ ] `src/air_engine/interfaces/cli/commands/verify.py`
- [ ] `tests/e2e/test_mvp_flow.py` — full pipeline fixtures

**Done when:** all success criteria checkboxes above are ✅.

---

### Sprint 5 — Adapters + Polish

**Goal:** Reference adapter + CLI output polish.

- [ ] `src/air_engine/adapters/json/` — static JSON adapter
- [ ] `src/air_engine/adapters/langgraph/` — reference implementation
- [ ] `src/air_engine/adapters/openai/` — reference implementation (optional for MVP)
- [ ] CLI: DAG ASCII render, metrics summary, error listing
- [ ] `src/air_engine/interfaces/library/` — programmatic API
- [ ] `tests/integration/adapters/`
- [ ] CI: canonical trace fixtures validation (future step)

**Done when:** real framework telemetry → same diagnostic as manual JSON.

---

## Explicitly Out of Scope (MVP)

Do **not** implement until post-MVP:

- Derived state persistence
- LLM-based verification
- Auto-fix / code rewriting
- Distributed execution
- Streaming / real-time analysis
- Web dashboard or visual editor
- Full contract DSL compiler
- Jaeger / Grafana / OpenTelemetry integration

---

## Module Dependency Rules

```
adapters → parser → core ← analyzer ← contracts
                         ↑
                    interfaces (cli, library)
```

- `core/` and `analyzer/` — **pure functions only**, zero third-party deps
- `parser/` may depend on `core/` only
- `adapters/` may depend on `parser/` and `core/`, never on `analyzer/`
- `analyzer/` must **not** import from `adapters/` or capture code

---

## Session Log

| Date | Session | Completed | Next |
|------|---------|-----------|------|
| 2026-07-13 | Bootstrap | Repo structure, tooling, CI, ADRs 001–005 | Sprint 0 |
| 2026-07-13 | Sprint 0 | AIR core model, topology validation, schema spec, examples, 9 unit tests | Sprint 1 parser + CLI |
| 2026-07-13 | Sprint 1 | JSON parser, `air-engine validate`, 10 new integration/CLI tests | Sprint 2 state reconstruction |

---

## Blockers / Open Questions

| ID | Question | Decision | ADR needed? |
|----|----------|----------|-------------|
| — | — | — | — |

---

## Related Documents

- [ADR Index](adrs/README.md)
- [Architecture specs](architecture/README.md) — add `air-schema-1.0.0.md` in Sprint 0
- [README](../README.md) — user-facing overview
