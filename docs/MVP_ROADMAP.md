# MVP Roadmap

> Living document for varly MVP execution.  
> **Update this file** at the start/end of each work session.  
> Reference: Project Bible (Part VII) · [ADRs](adrs/) · [Architecture](architecture/)

**Last updated:** 2026-08-17  
**Current phase:** MVP complete — see [Product Roadmap](PRODUCT_ROADMAP.md) for Sprints 6+  
**MVP status:** 🟢 Complete

---

## MVP Definition

The MVP validates that the formal model, AIR representation, and verification engine produce **correct, deterministic, reproducible** results on real executions.

### Success Criteria (all required)

- [x] Import a real async execution log (or static equivalent)
- [x] Convert it to canonical AIR topology without losing causality
- [x] Reconstruct intermediate state at any arbitrary node
- [x] Run predefined contracts on the graph
- [x] Produce a deterministic `Diagnostic` artifact
- [x] Same diagnostic for the same trace regardless of execution platform

### Hypotheses Under Test

| ID | Hypothesis | Validated? | Evidence |
|----|------------|------------|----------|
| H1 | AIR models async execution without losing causality | 🟡 | Parser + examples + CLI validate |
| H2 | State reconstructs deterministically from topology only | ✅ | `ordering.py`, `state.py`, e2e state test |
| H3 | Contracts detect violations without false positives | ✅ | full MVP catalog + semantic/metrics tests |
| H4 | Model stays agnostic to origin framework | ✅ | langgraph + openai adapters → same diagnostic |

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
- [x] `src/varly/core/types.py` — `NodeId`, edge kinds, semantic types
- [x] `src/varly/core/trace.py` — frozen `Trace`, `Node`, `Edge`
- [x] `src/varly/core/topology.py` — DAG check, reachability, root
- [x] `src/varly/core/errors.py` — typed domain errors
- [x] `tests/unit/core/test_topology.py`

**Done when:** valid trace passes validation; invalid traces fail with typed errors.

---

### Sprint 1 — Parser + Validate CLI ✅

**Goal:** `varly validate trace.json` works.

- [x] `src/varly/parser/json_loader.py`
- [x] `src/varly/parser/schema.py`
- [x] `src/varly/parser/builder.py`
- [x] `tests/integration/parser/` — fixture-driven
- [x] `src/varly/interfaces/cli/commands/validate.py`
- [x] CLI entry point in `pyproject.toml`
- [x] `examples/trace_valid_minimal.json` loads end-to-end

**Done when:** CLI exits 0 on valid trace, non-zero on invalid.

---

### Sprint 2 — Ordering + State Reconstruction ✅

**Goal:** Deterministic state at any node (ADR-004, ADR-005).

- [x] `src/varly/core/ordering.py` — `O_can` canonical linear extension
- [x] `src/varly/core/state.py` — reduction `⊕` over causal ancestors
- [x] `src/varly/core/labeling.py` — `λ_V`, `λ_E` projection
- [x] `src/varly/analyzer/state_builder.py`
- [x] `tests/unit/core/test_ordering.py`
- [x] `tests/unit/core/test_state.py`

**Done when:** same trace → same state at node N, always.

---

### Sprint 3 — First Contract + Diagnostic ✅

**Goal:** One invariant → structured diagnostic.

- [x] `src/varly/contracts/model.py` — `Contract`, `Property`, `Invariant`
- [x] `src/varly/contracts/loader.py` — YAML/JSON loader
- [x] `src/varly/contracts/builtins/structural.py` — no cycles, reachability
- [x] `src/varly/analyzer/diagnostic.py`
- [x] `src/varly/analyzer/evaluator.py`
- [x] `src/varly/analyzer/engine.py`
- [x] `examples/policy_mvp.yaml`
- [x] `tests/unit/analyzer/test_evaluator.py`
- [x] `src/varly/interfaces/cli/commands/verify.py` — verify CLI

**Done when:** `verify` returns pass/fail + explanation for structural rules.

---

### Sprint 4 — Full Contract Catalog (MVP) ✅

**Goal:** All MVP invariants from Project Bible Part VII §2.3.

- [x] Structural: no causal cycles, root reachability, no orphans
- [x] Semantic: `ToolCall` → reachable `ToolReturn` in `E_c`
- [x] Metrics: max trace duration, token budget
- [x] `src/varly/contracts/builtins/semantic.py`
- [x] `src/varly/contracts/builtins/metrics.py`
- [x] `examples/policy_mvp.yaml` — full catalog
- [x] `examples/trace_invalid_missing_tool_return.json`
- [x] `tests/e2e/test_mvp_flow.py` — full pipeline fixtures

**Done when:** all success criteria checkboxes above are ✅ (except cross-platform, deferred to Sprint 5).

---

### Sprint 5 — Adapters + Polish ✅

**Goal:** Reference adapter + CLI output polish.

- [x] `src/varly/adapters/json/` — static JSON adapter
- [x] `src/varly/adapters/langgraph/` — reference implementation
- [x] `src/varly/adapters/openai/` — reference implementation
- [x] CLI: DAG ASCII render, metrics summary, error listing
- [x] `src/varly/interfaces/library/` — programmatic API
- [x] `tests/integration/adapters/`
- [x] CI: canonical trace fixtures validation

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
| 2026-07-13 | Sprint 1 | JSON parser, `varly validate`, 10 new integration/CLI tests | Sprint 2 state reconstruction |
| 2026-08-17 | Sprint 2 | Canonical ordering, state reconstruction, labeling, 9 new unit tests | Sprint 3 contracts + diagnostic |
| 2026-08-17 | Sprint 3 | Contracts, evaluator, diagnostic, verify CLI, policy_mvp.yaml, 8 new tests | Sprint 4 full contract catalog |
| 2026-08-17 | Sprint 4 | Semantic + metrics invariants, full policy, e2e pipeline, 13 new tests | Sprint 5 adapters + polish |
| 2026-08-17 | Sprint 5 | Adapters, library API, CLI render, adapter tests, CI fixtures | Post-MVP (v1 adapters) |

---

## Blockers / Open Questions

| ID | Question | Decision | ADR needed? |
|----|----------|----------|-------------|
| — | — | — | — |

---

## Related Documents

- [Product Roadmap](PRODUCT_ROADMAP.md) — post-MVP sprints (v1 → commercial path)
- [ADR Index](adrs/README.md)
- [Architecture specs](architecture/README.md) — add `air-schema-1.0.0.md` in Sprint 0
- [README](../README.md) — user-facing overview
