# Product Roadmap (Post-MVP → v1)

> Living document for air-engine product evolution after MVP.  
> **Update this file** at the start/end of each work session.  
> Reference: [Project Bible](../projectBilde.pdf) · [MVP Roadmap](MVP_ROADMAP.md) · [ADRs](adrs/) · [Architecture](architecture/)

**Last updated:** 2026-08-18  
**Current phase:** Sprint 7 — GitHub Action + Fixture CI  
**Product status:** 🟡 Post-MVP (v1 in progress)  
**MVP baseline:** 🟢 Complete — tag `mvp-v0.1.0` recommended before Sprint 6

---

## Product Vision (Project Bible alignment)

air-engine is **post-mortem verification infrastructure** for AI agent executions:

- Translate completed runs into immutable **AIR** causal graphs.
- Evaluate **deterministic contracts** (not LLM-as-judge, not exact string match).
- Produce reproducible **Diagnostics** suitable for CI gates and audit.

**What we are building toward (v1 product):**

> A developer installs air-engine, runs a agent (or replay fixture), and gets PASS/FAIL in CI — with user-defined policy YAML — **without paying for API calls during development.**

**What we are NOT building (identity guardrails):**

- Agent framework or prompt orchestrator
- Real-time observability dashboard (LangSmith-style)
- LLM-based verification
- Commercial SaaS (until v1 OSS path is proven)

---

## Operating Constraints

These constraints govern **all sprints below** until explicitly revoked:

| ID | Constraint | Implication |
|----|------------|-------------|
| C1 | **Zero API budget** | No sprint may *require* paid OpenAI/Anthropic/etc. calls |
| C2 | **Mock-first development** | Agents in repo are deterministic simulators or replay fixtures |
| C3 | **Live API optional** | Real API only behind explicit opt-in (`AIR_ENGINE_LIVE=1` + user key); never in CI |
| C4 | **Core purity** | `core/` and `analyzer/` remain stdlib-only; no framework imports |
| C5 | **Vertical slices** | Each sprint must demo end-to-end value, not isolated layers |
| C6 | **Immutable Trace** | Capture writes external logs; adapters produce AIR; verify never mutates |

---

## Version Map (README alignment)

| Version | Focus | Product outcome | Target |
|---------|-------|-----------------|--------|
| **MVP** | Core validation | Engine + CLI + reference adapters | ✅ Done |
| **v1** | Source agnosticism + CI | Capture, mock agent, GitHub Action, policy packs | Sprints 6–10 |
| **v1.5** | Team readiness | Diagnostic export (SARIF/JUnit), compare runs | Sprints 11–12 |
| **v2** | Normative expressiveness | Contract DSL compiler | Future |
| **v3** | Ergonomics | Local GUI / topology editor | Future |
| **v4** | Scalability | Distributed verification | Future |
| **v5** | Research | Predictive policies, early stopping | Future |

---

## v1 Definition

v1 is **product-ready open source**: another developer can adopt air-engine in CI using mocks/fixtures, custom policies, and clear docs — without contacting us and without API spend.

### Success Criteria (all required for v1 ✅)

- [ ] **Capture layer** records a deterministic agent run as a serializable event log
- [ ] **Mock agent demo** runs locally with zero network calls and produces a verify PASS
- [ ] **Replay fixtures** — golden captured runs checked into `examples/` and CI
- [ ] **GitHub Action** runs `validate` + `verify` on PRs using fixtures only
- [ ] **Policy packs** — user-selectable YAML templates (`strict`, `dev`) with documented params
- [ ] **Diagnostic artifact** — machine-readable export (JSON; SARIF or JUnit for CI parsers)
- [ ] **Expanded contract catalog** — at least 3 new business-oriented invariants
- [ ] **User docs** — 5-minute quickstart from install to first PASS/FAIL
- [ ] **Live API path documented** but optional; mock path is the default onboarding

### Hypotheses Under Test (post-MVP)

| ID | Hypothesis | Validated? | Evidence |
|----|------------|------------|----------|
| H5 | Capture → adapter → verify works without live LLM calls | ✅ | mock agent + capture adapter + e2e PASS |
| H6 | Users can tailor policies (YAML) per project without code changes | ⬜ | |
| H7 | CI integration catches regressions on fixture traces | ⬜ | |
| H8 | Mock-first path is sufficient to demo commercial value | ⬜ | |

---

## Strategy

Continue **vertical slice** from MVP:

```
Mock Agent → Capture → Event Log → Adapter → AIR → Verify → Diagnostic → CI
```

**Do not** build dashboard, DSL, or cloud before the mock-agent slice is green.

Priority order when unsure:

1. Does it complete the slice above?
2. Does it work with **zero API cost**?
3. Does it preserve Bible architecture boundaries?

---

## Implementation Phases

### Sprint 6 — Capture + Mock Agent Pipeline ✅

**Goal:** First end-to-end run that is *not* hand-written JSON — still zero API cost.

- [x] `docs/architecture/capture-event-log-1.0.0.md` — capture event log format
- [x] `src/air_engine/capture/` — `RunRecorder`, event types, flush to disk
- [x] `examples/demo_agent/` — deterministic mock agent (tool call + return, timestamps, tokens)
- [x] Native capture log (`capture-event-log-1.0.0`) → capture adapter → AIR
- [x] `tests/e2e/test_mock_agent_pipeline.py` — run mock → verify PASS
- [x] `examples/policies/` — duplicate MVP policy template
- [x] ADR-006: Capture layer boundaries (capture must not import `analyzer`)

**Done when:** `uv run python examples/demo_agent/run.py` produces a log that verifies PASS against `examples/policies/mvp.yaml` with no network.

---

### Sprint 7 — GitHub Action + Fixture CI

**Goal:** PR gate using air-engine; CI never calls external APIs.

- [ ] `.github/actions/verify-trace/` — composite action (validate + verify)
- [ ] Workflow: verify golden fixtures on every PR
- [ ] Workflow: mock agent e2e job (generate log → verify)
- [ ] Document fork usage in README (copy action into consumer repos)
- [ ] Exit codes and output stable for CI parsers

**Done when:** PR fails if a deliberately broken fixture is committed; passes on main.

---

### Sprint 8 — Policy Packs + Diagnostic Export

**Goal:** Users pick policies per case; CI consumes structured output.

- [ ] `examples/policies/strict.yaml` — tight duration/token limits
- [ ] `examples/policies/dev.yaml` — relaxed limits for local runs
- [ ] `docs/policies/README.md` — param reference for each invariant
- [ ] `air-engine verify --output diagnostic.json` (or library export)
- [ ] Diagnostic JSON schema doc in `docs/architecture/`
- [ ] Tests: same trace + different policies → different PASS/FAIL as expected

**Done when:** user can swap policy file only (no code) and change verification outcome.

---

### Sprint 9 — Expanded Contract Catalog (business rules)

**Goal:** More real-world invariants; still deterministic builtins (not DSL yet).

Candidates (pick ≥3 for v1):

- [ ] `max_llm_invocations` — cap count of `llm_invoke` nodes
- [ ] `tool_name_allowlist` — param `allowed: [search, calc]`
- [ ] `required_event_sequence` — param ordered event types subset
- [ ] `max_tool_calls` — cap tool_call nodes
- [ ] `forbidden_referential_edges` — restrict E_r patterns (optional)

- [ ] `src/air_engine/contracts/builtins/` — new modules per category
- [ ] Update `examples/policies/*.yaml` with new rules
- [ ] Unit tests per invariant + false-positive checks on valid trace

**Done when:** at least 3 new invariants ship with tests and policy examples.

---

### Sprint 10 — Real Adapter Formats (still fixture-driven)

**Goal:** Adapters match *real* export shapes; validation uses recorded files, not live SDK.

- [ ] Document mapping: OpenAI Responses / tool-call shapes → `openai.run.v1`
- [ ] Document mapping: LangGraph callback events → `langgraph.run.v1`
- [ ] `examples/fixtures/recorded/` — anonymized real-shaped captures (manual or exported once)
- [ ] Adapter regression tests: fixture → same event sequence as golden AIR
- [ ] Optional: `AIR_ENGINE_LIVE=1` script stub for user-owned API key (not CI)

**Done when:** a recorded OpenAI-shaped fixture verifies PASS without calling OpenAI in tests.

---

### Sprint 11 — CI Report Formats

**Goal:** air-engine plugs into existing CI UX.

- [ ] JUnit XML output mode (for GitHub/GitLab test summary)
- [ ] or SARIF output mode (for security/code scanning tabs)
- [ ] `verify --format junit|json|sarif|text`
- [ ] GitHub Action uploads report artifact

**Done when:** failed verify shows as a check annotation or test failure in GitHub UI.

---

### Sprint 12 — Trace Comparison + Regression

**Goal:** Detect when a new run is *worse* than baseline (product differentiation).

- [ ] `air-engine diff baseline.json current.json --contract policy.yaml`
- [ ] Compare violation sets deterministically
- [ ] Fail if new violations appear (regression gate)
- [ ] Docs: “baseline trace” workflow for teams

**Done when:** introducing a broken fixture increases violations vs golden baseline.

---

## v1.5+ Backlog (not scheduled — do not start before v1 ✅)

| Item | Version | Notes |
|------|---------|-------|
| Contract DSL compiler | v2 | Bible Part roadmap; needs v1 catalog stable |
| Local web UI | v3 | Topology viewer; not verification core |
| Hosted SaaS / API keys | Commercial | After OSS adoption signal |
| LangGraph SDK live capture | v1+ | Optional; mock path remains default |
| OpenTelemetry / Jaeger | Out | Bible explicit out-of-scope for MVP |
| LLM-as-judge eval | Out | Violates deterministic identity |

---

## Explicitly Out of Scope (v1)

Do **not** implement during v1:

- Derived state persistence databases
- LLM-based verification or auto-fix
- Multi-tenant cloud, billing, auth
- Full contract DSL (v2)
- Web dashboard (v3)
- Distributed verification (v4)
- Spending project budget on API calls for CI or dev defaults

---

## Module Dependency Rules (extended)

```
capture → (event log file)
event log → adapters → parser → core ← analyzer ← contracts
                                    ↑
                               interfaces (cli, library)
```

- `capture/` may depend on **stdlib only** (same purity as `core/`)
- `capture/` must **not** import `analyzer`, `contracts`, or framework SDKs
- `adapters/` translate event logs → AIR; never call `verify`
- `interfaces/` orchestrates; no business logic in CLI handlers

---

## Session Log

| Date | Session | Completed | Next |
|------|---------|-----------|------|
| 2026-08-17 | Roadmap | PRODUCT_ROADMAP.md created; Sprint 6 defined | Sprint 6 capture + mock agent |
| 2026-08-18 | Sprint 6 | Capture spec, ADR-006, RunRecorder, capture adapter, mock agent, e2e PASS | Sprint 7 GitHub Action + fixture CI |

---

## Blockers / Open Questions

| ID | Question | Decision | ADR needed? |
|----|----------|----------|-------------|
| B1 | No API budget for dev/CI | Mock-first; live API opt-in only | No |
| B2 | Capture emits openai.run.v1 vs native format | Native capture log + adapter | Yes → ADR-006 |
| B3 | JUnit vs SARIF for CI reports | Decide in Sprint 11 | Maybe ADR-007 |

---

## Related Documents

- [MVP Roadmap](MVP_ROADMAP.md) — Sprints 0–5 (complete)
- [ADR Index](adrs/README.md)
- [AIR Schema 1.0.0](architecture/air-schema-1.0.0.md)
- [README](../README.md) — version map (MVP → v5)
