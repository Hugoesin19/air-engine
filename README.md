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

```bash
# Validate structure + metrics
uv run air-engine validate examples/trace_valid_minimal.json --show-dag

# Verify against the full MVP policy
uv run air-engine verify examples/trace_valid_minimal.json \
  --contract examples/policy_mvp.yaml --show-metrics

# Generate a deterministic mock agent run with zero API cost
uv run python examples/demo_agent/run.py

# LangGraph / OpenAI telemetry → same verification (via library)
uv run python -c "
from air_engine.interfaces.library import load_trace, verify
from pathlib import Path
p = Path('examples/policy_mvp.yaml')
for src, path in [
    ('langgraph', 'examples/langgraph_run_minimal.json'),
    ('openai', 'examples/openai_run_minimal.json'),
]:
    d = verify(path, p, source=src)
    print(src, 'PASS' if d.passed else 'FAIL')
"

# Capture log → AIR → verify
uv run python -c "
from pathlib import Path
from air_engine.interfaces.library import verify
policy = Path('examples/policies/mvp.yaml')
print(verify('examples/demo_agent/artifacts/mock_run.json', policy, source='capture').passed)
"
```

## Roadmap

| Phase | Focus | Outcome |
|-------|-------|---------|
| **MVP** | Core validation | ✅ AIR + contracts + adapters + CLI |
| **v1** | Source agnosticism + CI | Capture, mock agent, GitHub Action — [Product Roadmap](docs/PRODUCT_ROADMAP.md) |
| **v2** | Normative expressiveness | Formal contract DSL |
| **v3** | Ergonomics | Local GUI and topology editor |
| **v4** | Scalability | Distributed verification |
| **v5** | Research | Early stopping, policies, predictive analysis |

## Reference specification

- [MVP Roadmap](docs/MVP_ROADMAP.md) — Sprints 0–5 (complete)
- [Product Roadmap](docs/PRODUCT_ROADMAP.md) — post-MVP plan (Sprints 6+)
- [Architecture specs](docs/architecture/) — formal AIR schema and contract model
- [Architecture Decision Records](docs/adrs/) — foundational design decisions

## Policy packs

Ready-made contracts in `examples/policies/` — swap the YAML file only to change verification strictness:

| File | Use case |
|------|----------|
| `mvp.yaml` | Default CI gate (10 s / 10 000 tokens) |
| `strict.yaml` | Tight limits (500 ms / 100 tokens) |
| `dev.yaml` | Relaxed local runs |

```bash
uv run air-engine verify examples/trace_valid_minimal.json --contract examples/policies/strict.yaml
uv run air-engine verify examples/trace_valid_minimal.json --contract examples/policies/mvp.yaml --output diagnostic.json
```

See [docs/policies/README.md](docs/policies/README.md) and [Diagnostic JSON schema](docs/architecture/diagnostic-schema-1.0.0.md).

## CI integration

This repository runs three CI jobs on every push and pull request:

- `quality` — lint, typecheck, and pytest
- `golden-fixtures` — stable CLI exit codes on canonical pass/fail examples
- `mock-agent-pipeline` — deterministic mock agent → capture log → verify

Run the same fixture gate locally:

```bash
uv run python scripts/ci/verify_golden_fixtures.py
```

### Reuse in another repository

Copy `.github/actions/verify-trace/` into your project, then call it after your agent writes a trace or capture log:

```yaml
- uses: ./.github/actions/verify-trace
  with:
    trace-file: artifacts/run.json
    contract-file: policies/mvp.yaml
    source: capture
```

Requirements for consumer repos:

- Python 3.12+
- `uv` available in the workflow
- `pyproject.toml` with `air-engine` installed, or run from a checkout of this repo

For canonical AIR traces, keep `source: air` (default). The action will run `validate` before `verify`.

## Development

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run air-engine validate examples/trace_valid_minimal.json
uv run air-engine verify examples/trace_valid_minimal.json --contract examples/policy_mvp.yaml
```

## License

MIT — see [LICENSE](LICENSE).
