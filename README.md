# air-engine

> Deterministic runtime verification engine for AI agents.

AIR (Analysis Intermediate Representation) transforms agent executions into immutable causal graphs to mathematically enforce structural and semantic contracts — without relying on LLMs for evaluation.

## What is it?

air-engine is a **post-mortem verification infrastructure** for software systems with non-deterministic components (LLMs, multi-agent workflows).

It does not execute your agents. It observes completed executions, translates them into a provider-agnostic intermediate representation (AIR), and evaluates **properties and invariants** defined in contracts — not exact string matches.

The goal is to bring CI-style regression detection to probabilistic systems: deterministic, reproducible diagnostics that can gate merges before production.

## Architecture

Seven responsibility domains, unidirectional data flow:

```
Capture → Adapters → AIR → Verification ← Contracts
                              ↓
                        Persistence
```

| Domain | Responsibility |
|--------|----------------|
| **Capture** | Obtain execution telemetry with minimal overhead |
| **Adapters** | Translate external formats into the internal model |
| **AIR** | Immutable, provider-agnostic intermediate representation |
| **Contracts** | Load and validate user-defined properties and invariants |
| **Verification** | Evaluate contracts against the AIR |
| **Persistence** | I/O for traces and diagnostics (no semantic knowledge) |
| **Orchestration** | CLI, policies, and lifecycle coordination |

The core (`core`, `analyzer`) has **zero external dependencies** and knows only about events and graphs — never about OpenAI, LangGraph, or any specific framework.

## Quick example

_Coming soon — MVP in progress._

```bash
uv run air-engine validate examples/trace_valid_minimal.json
```

## Roadmap

| Phase | Focus | Outcome |
|-------|-------|---------|
| **MVP** | Core validation | Basic capture + AIR + static contracts |
| **v1** | Source agnosticism | Multiple adapters and external frameworks |
| **v2** | Normative expressiveness | Formal contract DSL |
| **v3** | Ergonomics | Local GUI and topology editor |
| **v4** | Scalability | Distributed verification |
| **v5** | Research | Early stopping, policies, predictive analysis |

## Reference specification

- [MVP Roadmap](docs/MVP_ROADMAP.md) — implementation plan and progress tracker
- [Architecture specs](docs/architecture/) — formal AIR schema and contract model (in progress)
- [Architecture Decision Records](docs/adrs/) — foundational design decisions

## Development

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run air-engine validate examples/trace_valid_minimal.json
```

## License

MIT — see [LICENSE](LICENSE).
