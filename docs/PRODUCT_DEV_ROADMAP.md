# Product Development Roadmap

> **Active roadmap** — primary goal is a **shippable OSS product** for developers (and a foundation enterprises can adopt later).  
> The TFG is satisfied by documenting what exists; this file drives **what to build next**.

**Last updated:** 2026-08-29  
**Current phase:** **P1 — Distribution & release** (tag `v1.0.0` + PyPI publish pending)  
**North star:** A developer installs air-engine, captures a real agent run with minimal friction, and gets PASS/FAIL + regression gates in CI — without LLM-as-judge.

**Completed foundation:** Engine v1 (Sprints 0–12) · Adoption steps 1–6 · [Next Steps archive](NEXT_STEPS_ROADMAP.md)

---

## Product identity (do not drift)

| air-engine **is** | air-engine **is not** |
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
| **P1** | Distribution & release | `pip install`, stable tag, published Action | ⬜ **Current** (push tag) |
| **P2** | Automatic capture | LangGraph (or OpenAI) capture without manual `record_*` | ⬜ |
| **P3** | Developer experience | Cookbook, viewer graph, policy packs by use case | ⬜ |
| **P4** | Team readiness | Batch verify, baseline workflows, sharper reports | ⬜ |
| **P5** | Enterprise foundations | Audit trail, OTel ingest, self-host guide | ⬜ Paused |

**Paused (not now):** commercialization (pricing, landing), contract DSL (v2), full topology editor (v3), multi-tenant cloud.

---

## P1 — Distribution & release

**Goal:** Anyone can install a **versioned** package without cloning the repo.

- [x] Bump version to `1.0.0` (or `0.2.0` if you prefer cautious semver)
- [ ] Publish to **PyPI** (`pip install air-engine`) — workflow ready; **push tag `v1.0.0`** to trigger
- [x] README install path: PyPI first, git second
- [ ] Git tag + GitHub Release notes — after PyPI trusted publishing is configured
- [x] Document **published** GitHub Action (`uses: …@v1.0.0`)
- [x] CI smoke: install from wheel in `package-smoke` job

**Done when:** Fresh machine → `pip install air-engine` → `demo_60s` equivalent PASS.

**Next:** P2

---

## P2 — Automatic capture (one framework, done well)

**Goal:** Fix the #1 friction from the pilot — **no manual `RunRecorder` hooks** for the chosen stack.

Pick **LangGraph** first (callback export already partially supported) **or** OpenAI Responses — not both at half quality.

- [ ] One-page recipe: run agent → export JSON → `verify --source langgraph|openai`
- [ ] Example under `examples/` that produces a capture file (mock or recorded fixture)
- [ ] Golden fixture + CI gate for the new path
- [ ] Update [capture recipe](recipes/capture-run-recorder.md) with “when to use manual vs export”
- [ ] Friction note closed or updated in [pilot/FRICTION.md](../pilot/FRICTION.md)

**Done when:** You can verify a run without writing `record_*` calls yourself.

**Next:** P3

---

## P3 — Developer experience

**Goal:** Feels like a **product**, not only a library.

- [ ] **Cookbook** — 3 end-to-end scenarios (e.g. tool agent, RAG-shaped run, regression break)
- [ ] **Viewer** — minimal causal graph or ASCII-in-UI (not full v3 editor)
- [ ] **Policy packs** — `support-bot`, `rag`, `tool-heavy` (or document mapping from `mvp`/`strict`/`dev`)
- [ ] Error messages audit (wrong source, bad policy, missing fields)

**Done when:** A developer follows docs only through capture → verify → view → diff.

**Next:** P4

---

## P4 — Team readiness

**Goal:** Small teams can standardize on air-engine in CI.

- [ ] Document team workflow: baseline per branch, `diff` on PR
- [ ] Verify **multiple** traces in one command or script
- [ ] Report artifacts (JUnit/SARIF) documented for GitHub/GitLab
- [ ] Optional: `air-engine verify` exit codes + JSON stable for wrappers

**Done when:** README has a “Team CI” section copy-paste ready.

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
| 2026-08-29 | P1 | v1.0.0, bundled resources, `verify --demo`, publish workflow, package-smoke CI | Push `v1.0.0` tag → PyPI |

---

## Related

- [Product Roadmap](PRODUCT_ROADMAP.md) — historical engine sprints
- [Next Steps Roadmap](NEXT_STEPS_ROADMAP.md) — adoption steps 1–6 (complete)
- [Install](INSTALL.md) · [Viewer](VIEWER.md) · [Capture recipe](recipes/capture-run-recorder.md)
- [Pilot](../pilot/README.md)
