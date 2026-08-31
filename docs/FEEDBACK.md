# Early feedback log

> External reactions while validating Varly (TFG + product direction).  
> **Last updated:** 2026-08-31

Use this for the thesis (market validation) and to decide what to build next.

---

## Summary

| Signal | Count | Implication |
|--------|-------|-------------|
| Problem validated (CI guardrails) | 2 | Positioning is right |
| Strong pain + feature ask | 1 | Priority follow-up (Reddit) |
| DIY / manual workflow sufficient | 2 | Not ICP today — document as alternative |
| Positioning confusion (“determinism”) | 1 | Clarify messaging (see [README](../README.md)) |
| Future vision (hard stops, observable state) | 1 | Roadmap note, not v1 scope |

**ICP (for now):** Python team with agents in CI, tired of LLM-as-judge, wants structural gates on runs (tools, limits, shape).

---

## Responses

### 1 — CI guardrails (Reddit)

> Seems like the kind of guardrail that should've been built into CI pipelines from day one, curious why it took this long for someone to package it up properly

| Field | Value |
|-------|--------|
| **Segment** | Problem validator |
| **Sentiment** | Positive |
| **Action** | Use quote in positioning; no direct follow-up required |

**Takeaway:** The “CI gate for agent runs” framing resonates.

---

### 2 — Build your own harness (Reddit)

> It's called "build your own harness". I routinely do those things with app-specific harnesses

| Field | Value |
|-------|--------|
| **Segment** | DIY senior |
| **Sentiment** | Neutral / skeptical |
| **Action** | Position Varly as the **verification layer** of a harness, not a replacement for app-specific orchestration |

**Takeaway:** Experienced devs roll their own. OSS-as-library may be the right relationship; hard sell for packaged product.

---

### 3 — Same headache + policy granularity (Reddit) 🔥

> bet. i've been dealing with this exact headache on my current project.
>
> the "no LLM as judge" angle is what actually interests me. so tired of using an LLM to babysit another LLM…
>
> quick question though, how specific can the policies get? like can i say "only allowed to call this api endpoint and only with these parameter shapes" or is it more coarse than that

| Field | Value |
|-------|--------|
| **Segment** | Early adopter candidate |
| **Sentiment** | Strong interest |
| **Action** | **Follow up** — did they try GETTING_STARTED? Allowlists enough or parameter-level a must-have? |
| **Feature signal** | Richer capture (tool args) + endpoint/parameter policies |

**Takeaway:** Best lead so far. Only explicit feature request: parameter shapes / API endpoints.

---

### 4 — Operational systems / hard stops (LinkedIn / YouTube)

> The no-LLM-as-judge distinction is important. Once an agent can act, deterministic gates can constrain the path, but teams still need observable state and a hard stop before an irreversible action.

| Field | Value |
|-------|--------|
| **Segment** | Advanced / thought leadership |
| **Sentiment** | Aligned, adds scope |
| **Action** | Note for long-term roadmap; **not** v1 — Varly is post-mortem today |

**Takeaway:** Broader “operational AI” narrative fits; real-time hard stops are out of scope for now.

---

### 5 — Skeptic / manual workflow (LinkedIn — Francisco)

> A ver así a priori encontrar determinismo en agente es imposible por como están concebidos. Entiendo que las pruebas son una especie de benchmark donde evalúes unas outputs en función de unas inputs que esas sí, deben ser deterministas.
>
> Por los años que llevo trabajando con agentes la validación al final lo hace el equipo ya sea manual (en preproducción) o tests simulados en python (en desarrollo).
>
> De todas formas… al ser un tfg entiendo que el alcance es meramente académico… usa herramientas ya existentes… openclaw o agent harness

| Field | Value |
|-------|--------|
| **Segment** | Skeptic senior |
| **Sentiment** | Constructive, not a fit |
| **Action** | Clarify: Varly checks **run shape**, not LLM output text; complements manual/pytest |
| **Misconception** | “Determinism” = same output per input (we mean reproducible PASS/FAIL on contracts) |

**Takeaway:** Common objection — document in thesis limitations. Harness tools (OpenClaw, etc.) are execution layer; Varly is verification layer.

---

## Messaging changes (from feedback)

| Avoid | Prefer |
|-------|--------|
| “Deterministic agents” | “Contract gates in CI” |
| “Benchmark outputs” | “Verify run **behavior** (tools, limits, structure)” |
| “Replaces manual QA” | “Complements pytest and manual pre-prod” |

---

## What to build next (feedback-driven)

| Priority | Item | Trigger |
|----------|------|---------|
| **P0** | Ship v1.1.0 + [GETTING_STARTED](GETTING_STARTED.md) | Enable self-serve trials |
| **P1** | Follow up Reddit lead (#3) | Only hot lead with stated pain |
| **P2** | Tool `args` capture + parameter policies | If #3 (or second person) confirms must-have |
| **Paused** | Real-time hard stops, SaaS, enterprise | No demand yet |

---

## Follow-up checklist

- [ ] Reddit #3 — replied? tried `pip install`? allowlists vs parameter enforcement?
- [ ] README positioning updated (contract gates, not output determinism)
- [ ] 2–3 more outreach messages to profiles like #3 (agents in prod, CI)

---

## Related

- [Active plan (C1–C4)](PLAN.md) · [Early feedback](FEEDBACK.md)
- [Getting started](GETTING_STARTED.md) · [Product dev roadmap (P0–P4)](PRODUCT_DEV_ROADMAP.md)
- [Pilot friction](../pilot/FRICTION.md)
