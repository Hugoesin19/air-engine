# Product Development Roadmap

> **Historical phases P0–P4** (complete). **Active plan:** [PLAN.md](PLAN.md) (C1–C4, post-feedback).  
> Primary goal: a **shippable OSS product** for developers (and a foundation enterprises can adopt later).  
> The TFG is satisfied by documenting what exists; [PLAN.md](PLAN.md) drives **what to build next**.

**Last updated:** 2026-08-31  
**Current phase:** **P4 — Team readiness** ✅ → continue in [PLAN.md](PLAN.md) **C1**  
**North star:** A developer installs varly, captures a real agent run with minimal friction, and gets PASS/FAIL + regression gates in CI — without LLM-as-judge.

**Completed foundation:** Engine v1 (Sprints 0–12) · Adoption steps 1–6 · [Next Steps archive](NEXT_STEPS_ROADMAP.md)

---

## Product identity (do not drift)

| varly **is** | varly **is not** |
|-------------------|------------------------|
| Post-mortem **deterministic** verification | Real-time observability (LangSmith-style) |
| Contract / policy gates for agent **behavior** | LLM-as-judge evals |
| CI regression (`verify`, `diff`) | Agent orchestration framework |
| AIR causal graphs + YAML policies | Generic log search |

**Enterprise angle (later):** audit-friendly evidence, policy-as-code, self-host — not SaaS first.

---

## Phase map

| Phase | Focus | Outcome | Status |
|-------|--------|---------|--------|
| **P0** | Engine + adoption proof | v1 engine, pilot, CI, viewer, recipes | ✅ Done |
| **P1** | Distribution & release | `pip install`, stable tag, published Action | ✅ Done |
| **P2** | Automatic capture | LangGraph (or OpenAI) capture without manual `record_*` | ✅ Done |
| **P3** | Developer experience | Cookbook, viewer graph, policy packs by use case | ✅ Done |
| **P4** | Team readiness | Batch verify, baseline workflows, sharper reports | ✅ Done |
| **P5** | Enterprise foundations | Audit trail, OTel ingest, self-host guide | ⬜ Paused |

**Paused (not now):** commercialization (pricing, landing), contract DSL (v2), full topology editor (v3), multi-tenant cloud.

---

## P1 — Distribution & release ✅

**Goal:** Anyone can install a **versioned** package without cloning the repo.

- [x] Bump version to `1.0.0`
- [x] Publish to **PyPI** (`pip install varly`)
- [x] README install path: PyPI first, git second
- [x] Git tag + GitHub Release (`v1.0.0`)
- [x] Document **published** GitHub Action (`uses: …@v1.0.0`)
- [x] CI smoke: install from wheel in `package-smoke` job
- [x] GitHub repo renamed to `varly`

**Done when:** Fresh machine → `pip install varly` → `varly verify --demo` PASS. ✅

**Next:** P2

---

## P2 — Automatic capture (one framework, done well)

**Goal:** Fix the #1 friction from the pilot — **no manual `RunRecorder` hooks** for the chosen stack.

Pick **LangGraph** first (callback export already partially supported) **or** OpenAI Responses — not both at half quality.

- [x] One-page recipe: run agent → export JSON → `verify --source langgraph`
- [x] Example under `examples/langgraph_capture/` (mock graph, no API keys)
- [x] CI gate: `langgraph-capture-pipeline` job
- [x] Update [capture recipe](recipes/capture-run-recorder.md) with “when to use manual vs export”
- [x] Friction note updated in [pilot/FRICTION.md](../pilot/FRICTION.md)

**Done when:** You can verify a LangGraph run without writing `record_*` calls yourself. ✅ (LangGraph)

**Next:** OpenAI export slice (optional) or P3

---

## P3 — Developer experience ✅

**Goal:** Feels like a **product**, not only a library.

- [x] **Cookbook** — 3 end-to-end scenarios (tool agent, RAG-shaped run, regression break)
- [x] **Viewer** — ASCII causal graph in browser UI
- [x] **Policy packs** — `support-bot`, `rag`, `tool-heavy` (+ docs)
- [x] Error messages audit (wrong source hints, verify usage example)

**Done when:** A developer follows docs only through capture → verify → view → diff. ✅

**Next:** P4

---

## P4 — Team readiness ✅

**Goal:** Small teams can standardize on varly in CI.

- [x] Document team workflow: baseline per branch, `diff` on PR ([team-ci.md](workflows/team-ci.md))
- [x] Verify **multiple** traces in one command (`scripts/ci/verify_batch.py`)
- [x] Report artifacts (JUnit/SARIF) documented for GitHub/GitLab
- [x] `verify` / `diff` exit codes documented for wrappers
- [x] README **Team CI** section copy-paste ready

**Done when:** README has a “Team CI” section copy-paste ready. ✅

**Next:** P5 or user feedback

---

## P5 — Enterprise foundations (later)

Only after P1–P3 and **real usage signal** (even 1–2 external teams).

- [ ] Self-host / air-gapped runbook
- [ ] Policy versioning narrative
- [ ] OpenTelemetry or batch ingest spike
- [ ] Audit log design (who verified what, when)

**Not now:** SSO, billing, multi-tenant SaaS.

---

## Parallel tracks (background)

| Track | When | Notes |
|-------|------|--------|
| **TFG / memoria** | When your uni deadline requires it | Repo is the evidence; no feature sprint |
| **Commercialization** | After external users try P1–P3 | See archived Step 7 in [NEXT_STEPS_ROADMAP](NEXT_STEPS_ROADMAP.md) |
| **User interviews** | When you can | Adjust P3–P5 order from feedback |

---

## How to work

1. One **phase** at a time; finish “Done when” before the next.
2. Prefer **vertical slices** (docs + code + test + example).
3. Keep **mock-first CI** — no paid API in GitHub Actions.
4. Update this file’s **Current phase** and session log after each work session.

---

## Session log

| Date | Phase | Completed | Next |
|------|-------|-----------|------|
| 2026-08-31 | — | [PLAN.md](PLAN.md) — C1–C4 post-feedback roadmap | C1 — v1.1.0 + `varly try` |
| 2026-08-31 | — | Early feedback log ([FEEDBACK.md](FEEDBACK.md)); README positioning (contract gates) | PLAN.md |
| 2026-08-29 | P4 | Team CI guide, batch verify script, exit codes, README section | User feedback / P5 later |
| 2026-08-29 | P3 | Cookbook, viewer causal graph, policy packs, CLI hints | P4 — team readiness |
| 2026-08-29 | P2 | LangGraph auto-capture: collector, example, recipe, CI | P3 — developer experience |
| 2026-08-29 | P1 | v1.0.0, PyPI publish, GitHub Release, repo rename to `varly` | P2 — automatic capture |

---

## Related

- [Product Roadmap](PRODUCT_ROADMAP.md) — historical engine sprints
- [Next Steps Roadmap](NEXT_STEPS_ROADMAP.md) — adoption steps 1–6 (complete)
- [Team CI](workflows/team-ci.md) · [Baseline](workflows/baseline.md)
- [Install](INSTALL.md) · [Cookbook](cookbook/README.md) · [Viewer](VIEWER.md) · [Capture recipe](recipes/capture-run-recorder.md)
- [Pilot](../pilot/README.md)
