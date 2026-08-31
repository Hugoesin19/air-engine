# Varly

> Contract gates in CI for AI agent runs — without LLM-as-judge.

Varly verifies **completed** agent runs against YAML policies (tool allowlists, invocation caps, structure, limits) and returns reproducible PASS/FAIL. Same trace + same policy → same result every time. It does **not** assert that the LLM output text is identical run-to-run.

AIR (Analysis Intermediate Representation) is the internal trace format.

## What is it?

varly is **post-mortem contract verification** for agent runs: after your agent finishes, you check whether the run respected the rules you defined in YAML.

It does not execute your agents. It reads a trace of what happened (tools used, call counts, tokens, event order) and evaluates **structural and behavioral invariants** — not whether the answer “sounds right.”

**Complements** manual pre-prod review and `pytest`; **does not replace** them. **Differs from** LLM-as-judge evals (no second model scoring outputs).

Typical use: gate PRs in CI — `verify` on a captured run, `diff` against a baseline when behavior regresses.

## Quick start (5 minutes)

Prerequisites: **Python 3.12+**.

**→ [Getting started](docs/GETTING_STARTED.md)** — full guide: capture paths, policies, tool args, CI, viewer, diff.

```bash
pip install varly
varly verify --demo    # smoke test (PASS only)
varly try              # PASS + FAIL + regression demo (~1 min)
```

Expect `PASS` on `--demo`. `try` walks through PASS, FAIL, and `diff` REGRESSION using bundled fixtures.

> **LangGraph teams:** [LangGraph quickstart](docs/LANGGRAPH_QUICKSTART.md) · **Install options:** [INSTALL.md](docs/INSTALL.md)

### LangGraph in 3 commands (from clone)

```bash
pip install "varly[langgraph]"
git clone https://github.com/Hugoesin19/varly.git && cd varly
uv sync --group langgraph && uv run python examples/langgraph_capture/run.py
uv run varly verify examples/langgraph_capture/artifacts/run.json \
  --contract examples/policies/mvp.yaml --source langgraph
```

Expect **PASS**. CI template: [`examples/starter-ci/`](examples/starter-ci/README.md).

### Develop from source

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Hugoesin19/varly.git
cd varly
uv sync

# 1) Generate a deterministic mock agent run (no API keys)
uv run python examples/demo_agent/run.py

# 2) Verify against the default policy → expect PASS (exit code 0)
uv run varly verify examples/demo_agent/artifacts/mock_run.json \
  --contract examples/policies/mvp.yaml \
  --source capture
```

You should see `PASS` and `violations: 0`. Run the full test suite with `uv run pytest`.

**Install options:** [docs/INSTALL.md](docs/INSTALL.md) · **[Getting started](docs/GETTING_STARTED.md)** · **60s demo:** `uv run python scripts/demo_60s.py` · **Viewer:** `varly view --trace … --contract … --source capture`

More examples (canonical AIR traces, LangGraph/OpenAI fixtures, CI reports, `diff`) are below.

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

## More examples

```bash
# Validate structure + metrics
uv run varly validate examples/trace_valid_minimal.json --show-dag

# Verify against the full MVP policy
uv run varly verify examples/trace_valid_minimal.json \
  --contract examples/policy_mvp.yaml --show-metrics

# Generate a deterministic mock agent run with zero API cost
uv run python examples/demo_agent/run.py

# LangGraph / OpenAI telemetry → same verification (via library)
uv run python -c "
from varly.interfaces.library import load_trace, verify
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
from varly.interfaces.library import verify
policy = Path('examples/policies/mvp.yaml')
print(verify('examples/demo_agent/artifacts/mock_run.json', policy, source='capture').passed)
"

# Recorded OpenAI Responses shape (no live API)
uv run varly verify examples/fixtures/recorded/openai_responses_search.json \
  --contract examples/policies/mvp.yaml --source openai
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
- [Product Development Roadmap](docs/PRODUCT_DEV_ROADMAP.md) — product phases P0–P4 (complete)
- [**Active plan**](docs/PLAN.md) — **C1–C4** (post-feedback, what to build next)
- [Next Steps Roadmap](docs/NEXT_STEPS_ROADMAP.md) — adoption steps 1–6 (complete)
- [Install guide](docs/INSTALL.md) — `uv`, `pip`, GitHub Action
- [Onboarding checklist](docs/ONBOARDING.md) — first PASS/FAIL on a fresh machine
- [Diagnostic viewer](docs/VIEWER.md) — `varly view` in the browser
- [Cookbook](docs/cookbook/README.md) — 3 end-to-end scenarios (tool agent, RAG, regression)
- [Capture recipe](docs/recipes/capture-run-recorder.md) — instrument any agent with `RunRecorder`
- [LangGraph capture](docs/recipes/capture-langgraph-export.md) — automatic callbacks, no `record_*`
- [Changelog](CHANGELOG.md)
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
uv run varly verify examples/trace_valid_minimal.json --contract examples/policies/strict.yaml
uv run varly verify examples/trace_valid_minimal.json --contract examples/policies/mvp.yaml --output diagnostic.json
```

See [docs/policies/README.md](docs/policies/README.md) and [Diagnostic JSON schema](docs/architecture/diagnostic-schema-1.0.0.md).

## CI integration

This repository runs three CI jobs on every push and pull request:

- `quality` — lint, typecheck, and pytest
- `golden-fixtures` — stable CLI exit codes on canonical pass/fail examples
- `mock-agent-pipeline` — deterministic mock agent → capture log → verify (uploads SARIF)

Machine-readable reports:

```bash
uv run varly verify examples/trace_valid_minimal.json \
  --contract examples/policies/mvp.yaml --format json

uv run varly verify examples/trace_valid_minimal.json \
  --contract examples/policies/strict.yaml --format junit --output report.xml

uv run varly verify examples/trace_valid_minimal.json \
  --contract examples/policies/mvp.yaml --format sarif --output report.sarif
```

On GitHub Actions, failed verifies also emit `::error` annotations. The composite action uploads the report as an artifact (and SARIF when `report-format: sarif`).

### Baseline regression gate

Fail CI when a new run introduces violations the golden baseline did not have:

```bash
uv run varly diff \
  examples/trace_valid_minimal.json \
  examples/trace_invalid_missing_tool_return.json \
  --contract examples/policies/mvp.yaml
```

See [docs/workflows/baseline.md](docs/workflows/baseline.md).

## Team CI

Copy-paste workflow for PR gates: verify, regression `diff`, JUnit/SARIF reports, and batch verify.

**Full guide:** [docs/workflows/team-ci.md](docs/workflows/team-ci.md)

```yaml
# .github/workflows/varly.yml — minimal PR gate
name: varly
on: [pull_request, push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install varly
      - run: python your_agent/run.py --output artifacts/run.json
      - uses: Hugoesin19/varly/.github/actions/verify-trace@v1.2.0
        with:
          trace-file: artifacts/run.json
          contract-file: policies/mvp.yaml
          source: capture
          report-format: sarif
      - run: |
          varly diff fixtures/baseline_run.json artifacts/run.json \
            --contract policies/mvp.yaml --source capture
```

Batch verify multiple fixtures locally:

```bash
uv run python scripts/ci/verify_batch.py \
  examples/demo_agent/artifacts/mock_run.json \
  examples/capture_recipe/artifacts/run.json \
  --contract examples/policies/mvp.yaml --source capture
```

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
    report-format: junit
    report-file: varly-report.xml
```

Requirements for consumer repos:

- Python 3.12+
- `uv` available in the workflow
- `pyproject.toml` with `varly` installed, or run from a checkout of this repo

For canonical AIR traces, keep `source: air` (default). The action will run `validate` before `verify`.

## Development

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run varly validate examples/trace_valid_minimal.json
uv run varly verify examples/trace_valid_minimal.json --contract examples/policy_mvp.yaml
```

## Product status

varly is an **open-source product under active development**, started as a Final Year Project and evolving toward a production-ready verification tool for AI-agent workflows.

- **MVP:** complete (AIR core, contracts, adapters, CLI)
- **v1:** complete (capture, CI, policy packs, reports, `diff`, viewer)
- **Now:** [Active plan](docs/PLAN.md) (C1–C4) — v1.2.0 shipped (tool args policies); next: TFG memoria (C4)
- **Later:** contract DSL, enterprise ingest, scalable verification

This repository is the source of truth for design and implementation. Contributions and feedback are welcome under the license below.

## Authorship

Designed and implemented by **Hugo** ([@Hugoesin19](https://github.com/Hugoesin19)).

Copyright (c) 2026 Hugoesin19. All rights reserved under the MIT License terms.

If you reference this work academically or commercially, please keep attribution to the repository: [github.com/Hugoesin19/varly](https://github.com/Hugoesin19/varly).

## License

Released under the **MIT License** — see [LICENSE](LICENSE).

You may use, modify, and redistribute the software, including in commercial products, provided the copyright notice and license text are retained. The software is provided as-is, without warranty.
