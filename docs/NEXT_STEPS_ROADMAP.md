# Next Steps Roadmap (Adoption → Product)

> Living document for what comes **after** the v1 engine (Sprints 0–12).  
> Ordered by **steps**, not by calendar. Advance only when the step’s “Done when” is true.  
> Update checkboxes as you complete work.

**Last updated:** 2026-08-29  
**Current step:** Step 2 — One real pilot run  
**Related:** [Product Roadmap](PRODUCT_ROADMAP.md) (engine sprints) · [Baseline workflow](workflows/baseline.md)

---

## How to use this file

1. Work **one step at a time**.
2. Do not start the next step until the current “Done when” is met.
3. Skip UI / commercialize until Steps 1–4 prove real value.
4. After each session: tick boxes and move “Current step” at the top.

**Guiding questions (in order):**

1. Does someone get a useful PASS/FAIL? → Steps 1–3  
2. Can they do it without you sitting next to them? → Steps 4–5  
3. Would they depend on it or pay for help? → Steps 6–7  

---

## Principles

| Do | Don’t (yet) |
|----|-------------|
| Prove value on a real run | Build a big web UI |
| Lower install / capture friction | Add a contract DSL |
| Learn from 1–2 real users | Price, SaaS, billing |
| Polish errors and docs | Ten new invariants “just in case” |

---

## Step 1 — Ship & freeze the v1 baseline

**Goal:** Main is clean, tagged, and anyone can reproduce a PASS from the README.

- [x] All pending work committed and pushed to `main`
- [ ] CI green on GitHub (`quality`, `golden-fixtures`, `mock-agent-pipeline`)
- [x] Git tag for this baseline (e.g. `v0.2.0` or `v1.0.0-beta`)
- [x] README has **one** 5-minute path: install → mock agent → `verify` → PASS
- [x] Short CHANGELOG (what this release does / does not do)

**Done when:** A clean clone + the README path yields PASS without asking you questions.

**Next:** Step 2

---

## Step 2 — One real pilot run

**Goal:** Prove the engine outside hand-written `examples/` fixtures.

- [ ] Choose one small real agent (yours or a friend’s)
- [ ] Capture **one** completed run as JSON (anonymize secrets / PII)
- [ ] Store it under `examples/fixtures/` or a `pilot/` folder
- [ ] `verify` against an existing or lightly tuned policy → PASS or FAIL that makes sense
- [ ] Write a short friction note (5–10 lines): what broke, what was confusing

**Done when:** You have one non-toy run + a verify result you trust + a friction list.

**Next:** Step 3

---

## Step 3 — Make that pilot useful as a gate

**Goal:** The product protects against regressions, not only “passes once”.

- [ ] Keep the good pilot (or golden) run as **baseline**
- [ ] Break something on purpose (missing tool return, stricter policy, etc.)
- [ ] `air-engine diff baseline current --contract …` exits **1** (REGRESSION)
- [ ] Fix the intentional break; `diff` exits **0** again
- [ ] Optionally wire `diff` into a local script / CI job for the pilot

**Done when:** Introducing a broken run reliably fails the gate vs baseline.

**Docs:** [Baseline workflow](workflows/baseline.md)

**Next:** Step 4

---

## Step 4 — Easy capture (one framework only)

**Goal:** Someone else can produce a verifiable log without reverse-engineering `RunRecorder`.

Pick **one** stack first (LangGraph **or** OpenAI), not both.

- [ ] One-page recipe: paste snippet → write `run.json` → `verify --source …`
- [ ] Example script or callback under `examples/` that writes the log
- [ ] Recipe tested on a clean machine / fresh clone
- [ ] Friction from Step 2 either fixed or documented as known limitation

**Done when:** A technical friend follows the recipe alone and gets PASS/FAIL.

**Next:** Step 5

---

## Step 5 — Easy install & onboarding

**Goal:** “Works on my machine” becomes “works on yours”.

- [ ] Install path documented (`uv` and/or `pip` when published)
- [ ] Errors from bad files / wrong `--source` are readable
- [ ] Optional: publish a pre-release to PyPI (`0.2.0a1` is fine)
- [ ] Optional: versioned GitHub Action reference in docs
- [ ] 60-second demo script (mock or pilot → PASS; break → FAIL / REGRESSION)

**Done when:** A stranger (or you on a second PC) reaches first PASS/FAIL with the docs only.

**Next:** Step 6

---

## Step 6 — Light UX (only if Step 5 is done)

**Goal:** Reduce friction for people who hate the terminal — **without** becoming LangSmith.

Start tiny. Prefer one of:

- [ ] Local report viewer (open JSON/JUnit diagnostic in a simple page), **or**
- [ ] Minimal local UI: upload/select trace + policy → show PASS/FAIL + violations

Explicitly **out** of this step:

- Multi-user cloud
- Auth / billing
- Live agent orchestration
- Full topology editor (that is later / v3)

**Done when:** A non-CLI-preferring user can see a diagnostic without asking you to run commands for them.

**Next:** Step 7

---

## Step 7 — Prepare to commercialize (last)

**Goal:** Decide *how* to offer value — after real usage signal.

- [ ] 2–3 conversations with people who tried Steps 4–6 (what they needed)
- [ ] Choose a first offer (examples: OSS + paid setup help; hosted verify later; team CI pack)
- [ ] Pricing sketch (even rough) and what is free vs paid
- [ ] Legal basics if charging (license clarity, invoices, no secrets in public repos)
- [ ] Only then: landing page / waitlist / paid pilot

**Done when:** You can explain in one paragraph who pays, for what, and why air-engine beats “just LangSmith / just pytest”.

---

## Step status board

| Step | Name | Status |
|------|------|--------|
| 1 | Ship & freeze v1 baseline | ✅ |
| 2 | One real pilot run | ⬜ Current |
| 3 | Pilot as regression gate | ⬜ |
| 4 | Easy capture (one framework) | ⬜ |
| 5 | Easy install & onboarding | ⬜ |
| 6 | Light UX | ⬜ Locked until Step 5 |
| 7 | Prepare to commercialize | ⬜ Locked until usage signal |

---

## Session log

| Date | Step | Completed | Next |
|------|------|-----------|------|
| 2026-08-24 | — | Document created; engine v1 (sprints 6–12) treated as done | Step 1 ship & freeze |
| 2026-08-29 | 1 | README quick start, CHANGELOG, tag `v1.0.0-beta` | Step 2 pilot run |

---

## Related documents

- [Product Roadmap](PRODUCT_ROADMAP.md) — engine sprints 6–12
- [MVP Roadmap](MVP_ROADMAP.md) — sprints 0–5
- [Baseline workflow](workflows/baseline.md)
- [Policy packs](policies/README.md)
- [README](../README.md)
