# Varly — Plan (post-feedback)

> **Active plan** after early validation (Aug 2026).  
> P0–P4 (engine + OSS foundation) are **done** — see [PRODUCT_DEV_ROADMAP](PRODUCT_DEV_ROADMAP.md).  
> This file drives **what to build next** to make Varly genuinely useful.

**Last updated:** 2026-08-31  
**Current phase:** **C4** — TFG memoria (C3 shipped in v1.2.0)  
**Evidence:** [FEEDBACK.md](FEEDBACK.md)

---

## Verdict

| Area | Score | Notes |
|------|-------|-------|
| Technical engine | Strong | AIR, policies, LangGraph capture, CI — solid |
| Perceived utility | Gap | Hard to try; golden path unclear; policies too coarse for some |
| Market fit | Niche | Problem is real; not everyone needs it yet |

**We are not off track.** The engine is right. The gap is **focus and adoption friction**, not a wrong problem.

---

## North star (updated)

> A **LangGraph + CI** team captures an agent run, verifies it against YAML contract gates, and gates PRs with `diff` — **without LLM-as-judge** — in under 30 minutes from `pip install`.

Secondary path: any Python agent via `RunRecorder` (manual hooks). Not the primary story until C2 is done.

---

## Who this is for (ICP)

**Primary:** Python team, agent in or near production, uses **LangGraph** (or LangChain callbacks), has **CI**, wants structural gates (tools, limits, shape) without flaky LLM evals.

**Not for (now):** Seniors happy with manual pre-prod + `pytest` mocks; teams with no agent in CI; people who need semantic output quality scoring.

---

## Product identity (do not drift)

| Varly **is** | Varly **is not** |
|--------------|------------------|
| **Contract gates in CI** for completed runs | Real-time observability (LangSmith) |
| Reproducible PASS/FAIL on **run shape** | “Same LLM output every time” |
| Post-mortem verification | LLM-as-judge evals |
| Complements pytest + manual QA | Replacement for all testing |
| Verification layer of a harness | Agent orchestration framework |

### Messaging (from feedback)

| Avoid | Use |
|-------|-----|
| “Deterministic agents” | “Contract gates in CI” |
| “Benchmark outputs” | “Verify run **behavior** (tools, limits, structure)” |
| “Replaces manual QA” | “Complements pytest and pre-prod review” |

---

## Phase map

| Phase | Focus | Outcome | Status |
|-------|--------|---------|--------|
| **P0–P4** | Engine + OSS foundation | PyPI, LangGraph, cookbook, team CI | ✅ Done |
| **C1** | Ship & first value | Anyone understands product in 5 min from pip | ✅ Code done (PyPI tag pending) |
| **C2** | LangGraph golden path | One flawless stack: capture → verify → CI | ✅ Docs + starter CI |
| **C3** | Richer policies (optional) | Tool args + parameter-level gates | ✅ Done |
| **C4** | TFG memoria | Document product + validation + limits | ⬜ Parallel |

**Paused:** SaaS, real-time hard stops, enterprise (P5), OpenAI auto-capture, contract DSL v2, topology editor.

---

## C1 — Ship & first value

**Goal:** Close the gap between `pip install` and “I understand what this does.”

**Problem today:** PyPI is `1.0.0`; cookbook requires clone; `--demo` alone feels like the whole product.

### Tasks

- [ ] Release **v1.1.0** on PyPI (P2–P4 + docs + viewer fix + CI fixes)
- [x] Add **`varly try`** — PASS + FAIL + `diff` regression without cloning repo
- [x] Bundle extra fixtures in wheel (`trace_valid_minimal`, `trace_invalid_missing_tool_return`)
- [x] Ship **`live` policy** in wheel (120s cap for real API captures)
- [x] Update [CHANGELOG](../CHANGELOG.md) for v1.1.0
- [x] [GETTING_STARTED.md](GETTING_STARTED.md) — pip-first path
- [x] [FEEDBACK.md](FEEDBACK.md) — validation log
- [x] README positioning — contract gates, not output determinism

**Done when:** Fresh machine → `pip install varly` → `varly try` → user sees PASS, FAIL, and regression in one command.

> **Code complete** — publish tag `v1.1.0` to PyPI when ready ([RELEASING.md](RELEASING.md)).

---

## C2 — LangGraph golden path

**Goal:** One stack done impeccably — not “any agent” at half quality.

**Golden path:**

```
LangGraph agent → LangGraphCallbackCollector → run.json
       → varly verify --source langgraph
       → varly diff on PR (GitHub Action)
```

### Tasks

- [x] LangGraph recipe as **primary** entry in README / GETTING_STARTED (not buried)
- [x] **Starter CI** template — [`examples/starter-ci/`](../examples/starter-ci/README.md)
- [x] Link policy packs to scenarios (`rag`, `support-bot`, `tool-heavy`) from golden-path docs
- [x] Document “what Varly does / does not do” table in GETTING_STARTED (expectations)
- [x] Pin GitHub Action examples to `v1.2.0` after PyPI tag is published

**Done when:** Someone with LangGraph follows docs only and has a green CI gate in one session.

---

## C3 — Richer policies (one vertical slice)

**Goal:** Address the only explicit feature ask from validation — parameter-level enforcement.

**Trigger:** Build after C2, or sooner if clearly blocking adoption. Feedback signal: tool allowlists are “too coarse”; need endpoint / parameter shapes.

### Scope (minimal)

- [x] `record_tool_call(..., args=...)` in `RunRecorder` (+ LangGraph capture if feasible)
- [x] One new invariant (e.g. `tool_args_keys_allowlist` or JSON-schema hook per tool name)
- [x] Cookbook example + test
- [x] Docs: what is captured, what policies can check

**Out of scope for C3:** Full JSON Schema engine, arbitrary endpoint URL matching, real-time enforcement.

**Done when:** Policy can fail a run because a tool was called with disallowed argument keys/shapes.

---

## C4 — TFG memoria (parallel)

**Goal:** Thesis documents product + market validation, not only code.

### Suggested structure

1. Problem — lack of structural CI gates for agent runs  
2. Solution — Varly architecture (post-mortem, AIR, YAML policies)  
3. Implementation — repo as evidence (P0–P4)  
4. Validation — [FEEDBACK.md](FEEDBACK.md) (enthusiasts, skeptics, feature ask)  
5. Limitations — coarse policies, manual capture for non-LangGraph, niche adoption  
6. Future work — C3, operational hard stops (long-term), enterprise  

**Done when:** Memoria draft explains what Varly is, who it’s for, and honest limits.

---

## Explicitly not building (now)

| Item | Why |
|------|-----|
| Multi-tenant SaaS | No demand; huge effort |
| Real-time hard stops before irreversible actions | Vision only; post-mortem is the wedge |
| Native Gemini / Anthropic adapters | `RunRecorder` suffices until users exist |
| Contract DSL v2 | v1 policies not yet adopted |
| “Any framework” capture at half quality | LangGraph first |
| Commercial landing / pricing page | After C2 proves self-serve usefulness |

---

## Success metrics (no more outreach required)

| Metric | Target |
|--------|--------|
| `pip install` → understand product | `varly try` works, no clone |
| Golden path documented | LangGraph → CI in one doc flow |
| Thesis evidence | FEEDBACK + PLAN + working repo |
| Optional product proof | C3 invariant if coarse policies block the use case |

We are **not** waiting for N more survey responses to execute C1–C2.

---

## How to work

1. **C1 before C2** — ship v1.1.0 and `varly try` before more features.  
2. **One vertical slice** — code + test + docs + example per task.  
3. **Mock-first CI** — no paid API keys in GitHub Actions.  
4. Update **session log** below after each work session.

---

## Session log

| Date | Phase | Completed | Next |
|------|-------|-----------|------|
| 2026-08-31 | C3 | Tool args capture, `tool_args_keys_allowlist`, `tool_arg_equals`, v1.2.0 bump | Publish `v1.2.0` → C4 |
| 2026-08-31 | C2 | LangGraph quickstart, starter-ci template, GETTING_STARTED reorder | Publish `v1.1.0` → C3/C4 |
| 2026-08-31 | C1 | `varly try`, bundled fixtures, `live` policy, v1.1.0 bump | C2 |
| 2026-08-29 | P4 | Team CI, batch verify, cookbook, LangGraph capture | Validation → this plan |

---

## Related

- [Early feedback](FEEDBACK.md) · [Getting started](GETTING_STARTED.md) · [Product dev roadmap (P0–P4)](PRODUCT_DEV_ROADMAP.md)
- [Install](INSTALL.md) · [Cookbook](cookbook/README.md) · [LangGraph recipe](recipes/capture-langgraph-export.md)
- [Team CI](workflows/team-ci.md) · [Pilot friction](../pilot/FRICTION.md) · [Releasing](RELEASING.md)
