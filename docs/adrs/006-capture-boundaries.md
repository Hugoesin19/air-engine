# ADR-006: Capture Writes Event Logs, Not AIR or Diagnostics

**Status:** Accepted  
**Date:** 2026-08-18

## Context

Post-MVP development needs a path from a running agent to the verification
engine. A naive implementation could let runtime code emit AIR directly, or
even call verification logic while the run is still happening. That would blur
layer boundaries and couple capture to analysis concerns.

The Project Bible keeps capture, adaptation, and verification as distinct
responsibility domains. The product roadmap also requires a **zero-cost,
mock-first** path where recorded runs can be replayed offline in CI.

## Alternatives

1. **Capture writes AIR directly** — Fewer files, but runtime code becomes
   responsible for AIR semantics and structural correctness.
2. **Capture calls verifier directly** — Convenient for demos, but violates
   post-mortem separation and couples runtime instrumentation to contracts.
3. **Capture writes a neutral event log** — Runtime records facts only; an
   adapter later translates them into AIR.

## Decision

Capture produces a **framework-neutral event log** (`capture-event-log-1.0.0`)
and stops there.

- `capture/` may depend on stdlib only.
- `capture/` must not import `analyzer`, `contracts`, or framework SDKs.
- Adapters are responsible for translating capture logs into AIR.
- Verification remains strictly post-mortem over AIR traces.

## Justification

This preserves the Bible's architectural invariants:

- capture records what happened,
- adapters normalize external formats,
- AIR remains the single canonical analysis representation,
- verification remains deterministic and offline-replayable.

It also keeps development cheap: a mock agent can emit the same event log as a
future real runtime integration without any paid API calls.

## Consequences

- **Positive:** Clean separation between runtime instrumentation and analysis.
- **Positive:** Replay fixtures can be committed to git and verified in CI.
- **Positive:** Future SDK integrations only need to emit event logs, not
  understand AIR internals.
- **Negative:** One extra translation step exists before verification.
- **Negative:** Capture logs need their own small format specification.

## References

- Project Bible — capture / adapter / AIR / verification separation
- [Capture Event Log 1.0.0](../architecture/capture-event-log-1.0.0.md)
- [ADR-001](001-air-immutable.md)
