# Getting started with Varly

**Start here.** This guide shows everything Varly can do today — install, capture, policies, CI, and debugging — after `pip install varly`. Clone the [repo](https://github.com/Hugoesin19/varly) only when you want cookbook fixtures or copy-paste CI templates.

**Python 3.12+** required · Install details: [INSTALL.md](INSTALL.md)

---

## Table of contents

1. [What Varly is](#what-varly-is)
2. [What you can do (at a glance)](#what-you-can-do-at-a-glance)
3. [Install and try it](#install-and-try-it)
4. [CLI commands](#cli-commands)
5. [Get a trace (capture paths)](#get-a-trace-capture-paths)
6. [Policies — what you can enforce](#policies--what-you-can-enforce)
7. [Policy packs](#policy-packs)
8. [Tool argument gates](#tool-argument-gates)
9. [Verify, view, and diff](#verify-view-and-diff)
10. [CI and reports](#ci-and-reports)
11. [Python library API](#python-library-api)
12. [pip only vs clone repo](#pip-only-vs-clone-repo)
13. [Common errors](#common-errors)
14. [Documentation map](#documentation-map)

---

## What Varly is

Varly is **post-mortem contract verification** for AI agent runs. After your agent finishes, you check whether the run respected rules you defined in YAML — tool names, call counts, token budgets, event order, tool argument keys/values — and get a reproducible **PASS or FAIL** without another LLM judging the output.

```
Your agent runs → save trace JSON → varly verify → PASS/FAIL
                                      varly diff   → regression gate
                                      varly view   → browser timeline
```

| Varly **is** | Varly **is not** |
|--------------|------------------|
| Contract gates in **CI** for completed runs | Real-time observability (LangSmith, etc.) |
| Reproducible PASS/FAIL on **run shape** | “Same LLM text every time” |
| Structural + behavioral rules (tools, limits, args) | LLM-as-judge evals |
| Complements `pytest` and manual QA | Replacement for all testing |
| Verification layer you add to a harness | Agent orchestration framework |

---

## What you can do (at a glance)

| Capability | How | Needs clone? |
|------------|-----|--------------|
| Smoke test install | `varly verify --demo` | No |
| Full product demo (PASS + FAIL + regression) | `varly try` | No |
| Verify any trace file | `varly verify run.json --contract policy.yaml --source …` | No |
| Gate PR regressions | `varly diff baseline.json current.json …` | No |
| Browse results locally | `varly view --trace … --contract …` | No |
| Capture from **LangGraph** | `LangGraphCallbackCollector` + `--source langgraph` | No (`pip install "varly[langgraph]"`) |
| Capture from **any Python agent** | `RunRecorder` + `--source capture` | No |
| Import **OpenAI Responses** JSON | `--source openai` | No |
| Enforce tool **names** | `tool_name_allowlist` | No |
| Enforce tool **argument keys/values** | `tool_args_keys_allowlist`, `tool_arg_equals` | No |
| CI on GitHub Actions | `verify-trace` action + JUnit/SARIF | Copy template from repo |
| Cookbook scenarios (4 paths) | LangGraph, RAG, diff, api-guard | Yes |
| Ready-made policy packs | `mvp`, `rag`, `api-guard`, … | Bundled: `mvp`/`strict`/`dev`/`live`; rest in repo |

---

## Install and try it

```bash
pip install varly
varly verify --demo          # PASS — proves install works
varly try                    # PASS + FAIL + REGRESSION (~1 min)
```

**`--demo` is not the product.** It only checks the wheel installed correctly. **`varly try`** shows what Varly actually does: verify a good run, catch a broken run, and detect regressions with `diff`.

LangGraph users:

```bash
pip install "varly[langgraph]"
```

---

## CLI commands

| Command | Purpose |
|---------|---------|
| `varly verify` | Check one trace against a policy → PASS/FAIL |
| `varly diff` | Compare baseline vs current → fail on **new** violations |
| `varly view` | Open local browser UI (timeline + causal graph) |
| `varly try` | Bundled demo: PASS, FAIL, regression (no files needed) |
| `varly validate` | Structural AIR check only (no policy) |

### `verify` essentials

```bash
varly verify run.json \
  --contract policy.yaml \
  --source capture          # capture | langgraph | openai | air
```

| Flag | Use |
|------|-----|
| `--demo` | Smoke test without files |
| `--source` | Trace format adapter (see [capture paths](#get-a-trace-capture-paths)) |
| `--format json\|junit\|sarif` | Machine-readable stdout for CI parsers |
| `--output report.json` | Write diagnostic JSON to file |
| `--show-dag` | Print ASCII causal graph in terminal |
| `--show-metrics` | Print duration and token totals |

Exit codes: `0` = PASS, `1` = FAIL, `2` = usage error.

---

## Get a trace (capture paths)

Varly never runs your agent. You (or your CI) produce a JSON trace, then verify it.

| Path | Best for | `--source` | Setup |
|------|----------|------------|-------|
| **LangGraph** | LangGraph / LangChain callbacks | `langgraph` | `pip install "varly[langgraph]"` — [quickstart](LANGGRAPH_QUICKSTART.md) |
| **RunRecorder** | Any Python agent (manual hooks) | `capture` | `pip install varly` — see [below](#path-b--runrecorder-any-python-agent) |
| **OpenAI Responses** | Exported Responses API JSON | `openai` | [OpenAI mapping](architecture/openai-run-mapping.md) |
| **Canonical AIR** | Advanced / pre-normalized traces | `air` | [AIR schema](architecture/air-schema-1.0.0.md) |

Wrong `--source`? The CLI suggests the correct one (e.g. “looks like capture, try `--source capture`”).

### Path A — LangGraph (recommended)

Automatic capture — no manual `record_*` hooks.

```python
from varly.capture.langgraph_callbacks import LangGraphCallbackCollector

collector = LangGraphCallbackCollector(run_id="my-run-001")
graph.invoke({"query": "..."}, config={"callbacks": [collector]})
collector.write_json("run.json")
```

```bash
varly verify run.json --contract policies/mvp.yaml --source langgraph
```

Full walkthrough: **[LangGraph quickstart](LANGGRAPH_QUICKSTART.md)** · CI template: [`examples/starter-ci/`](../examples/starter-ci/README.md)

Runnable mock example (requires repo clone):

```bash
git clone https://github.com/Hugoesin19/varly.git && cd varly
uv sync --group langgraph
uv run python examples/langgraph_capture/run.py
uv run varly verify examples/langgraph_capture/artifacts/run.json \
  --contract examples/policies/mvp.yaml --source langgraph
```

### Path B — RunRecorder (any Python agent)

Included in `pip install varly`. Call hooks around your agent logic:

```python
from pathlib import Path
import time
from varly.capture import RunRecorder

recorder = RunRecorder(run_id="my-run-001")
clock = time.perf_counter()
ts = lambda: round((time.perf_counter() - clock) * 1000, 3)

recorder.record_run_start(step_id="s1", timestamp_ms=ts())
recorder.record_llm_call(step_id="s2", timestamp_ms=ts(), total_tokens=150)
recorder.record_tool_call(
    step_id="s3", timestamp_ms=ts(), name="search",
    args={"query": "capital of France", "endpoint": "https://api.example.com/search"},
)
recorder.record_tool_output(step_id="s4", timestamp_ms=ts(), tool_name="search")
recorder.record_run_end(step_id="s5", timestamp_ms=ts())

recorder.write_json(Path("my_run.json"))
```

```bash
python my_agent.py
varly verify my_run.json \
  --contract "$(python -c "from varly.resources import bundled_policy; print(bundled_policy('mvp'))")" \
  --source capture
```

Hook reference: [capture recipe](recipes/capture-run-recorder.md)

### Path C — File you already have

```bash
varly verify path/to/run.json --contract path/to/policy.yaml --source capture
```

---

## Policies — what you can enforce

Policies are YAML files listing **invariants**. All listed invariants must pass.

### Structural (always safe to include)

| Invariant | Checks |
|-----------|--------|
| `no_causal_cycles` | Control-flow graph has no cycles |
| `root_reachability` / `no_orphans` | Every step reachable from run start |
| `tool_call_has_return` | Each tool call has a matching tool return |

### Metrics (budgets)

| Invariant | Param | Checks |
|-----------|-------|--------|
| `max_trace_duration` | `max_ms` | Wall-clock span of the run |
| `token_budget` | `max_tokens` | Sum of tokens on LLM calls |

### Business rules (behavior)

| Invariant | Param | Checks |
|-----------|-------|--------|
| `max_llm_invocations` | `max` | Cap on LLM call count |
| `max_tool_calls` | `max` | Cap on tool call count |
| `tool_name_allowlist` | `allowed` | Only these tool names |
| `tool_args_keys_allowlist` | `allowed` | Only these argument keys on tool calls |
| `tool_arg_equals` | `key`, `value` | Argument must equal exact value |
| `required_event_sequence` | `sequence` | Events appear in order (e.g. `run_start → llm_invoke → run_end`) |

Full reference with examples: [Policy packs](policies/README.md)

Minimal policy:

```yaml
air_schema_version: "1.0.0"
invariants:
  - id: tool_call_has_return
  - id: tool_name_allowlist
    params:
      allowed: [search]
  - id: max_tool_calls
    params:
      max: 5
```

---

## Policy packs

Ready-made policies for common agent shapes. Swap the file — no code changes.

| Pack | Use case | In wheel? |
|------|----------|-----------|
| `mvp` | Default CI / PR gate | ✅ `bundled_policy("mvp")` |
| `live` | Real API captures (120s cap) | ✅ `bundled_policy("live")` |
| `strict` | Tight production limits | ✅ `bundled_policy("strict")` |
| `dev` | Local debugging (relaxed) | ✅ `bundled_policy("dev")` |
| `support-bot` | FAQ / support agents | Repo: `examples/policies/` |
| `rag` | RAG / retrieval workflows | Repo |
| `tool-heavy` | Multi-tool orchestrators | Repo |
| `api-guard` | Tool arg keys + endpoint value | Repo |

```bash
python -c "from varly.resources import bundled_policy; print(bundled_policy('mvp'))"
```

---

## Tool argument gates

**New in v1.2.0** — enforce *which parameters* a tool was called with, not just the tool name.

Requires capture with args: `record_tool_call(..., args={...})` or LangGraph auto-capture.

Example policy ([`api-guard.yaml`](../examples/policies/api-guard.yaml)):

```yaml
invariants:
  - id: tool_name_allowlist
    params:
      allowed: [search]
  - id: tool_args_keys_allowlist
    params:
      allowed: [query, endpoint]
  - id: tool_arg_equals
    params:
      key: endpoint
      value: "https://api.example.com/search"
```

Try it from a clone:

```bash
uv run varly verify examples/cookbook/artifacts/tool_args_valid.json \
  --contract examples/policies/api-guard.yaml --source capture   # PASS

uv run varly verify examples/cookbook/artifacts/tool_args_invalid.json \
  --contract examples/policies/api-guard.yaml --source capture   # FAIL
```

**Supported today:** allowlisted arg keys, exact key=value checks.  
**Not yet:** full JSON Schema per tool, arbitrary URL pattern matching.

Cookbook scenario: [cookbook §4](cookbook/README.md#scenario-4--tool-argument-gates-api-guard)

---

## Verify, view, and diff

### Verify

```bash
varly verify my_run.json --contract policy.yaml --source capture
```

### View (browser)

```bash
varly view --trace my_run.json --contract policy.yaml --source capture
```

Opens `http://127.0.0.1:8765/` with PASS/FAIL, violations, timeline, and causal graph. Details: [VIEWER.md](VIEWER.md)

### Diff (regression gate)

Fails when the **current** run has violations the **baseline** did not:

```bash
varly diff baseline.json current.json --contract policy.yaml --source capture
```

Exit `0` = no regression · Exit `1` = new violations.  
`varly try` demonstrates this with bundled fixtures.

Workflow guide: [baseline workflow](workflows/baseline.md)

---

## CI and reports

### GitHub Actions

Pin to a release tag:

```yaml
- uses: Hugoesin19/varly/.github/actions/verify-trace@v1.2.0
  with:
    trace-file: artifacts/run.json
    contract-file: policies/mvp.yaml
    source: langgraph
    report-format: sarif
    report-file: varly-report.sarif
```

Copy full workflow: [`examples/starter-ci/`](../examples/starter-ci/README.md) · [Team CI guide](workflows/team-ci.md)

### Report formats

```bash
varly verify run.json --contract policy.yaml --source capture --format junit
varly verify run.json --contract policy.yaml --source capture --format sarif --output report.sarif
```

GitHub Actions can ingest SARIF for inline annotations. JUnit works with most CI dashboards.

---

## Python library API

Same engine as the CLI — use in tests or custom pipelines:

```python
from pathlib import Path
from varly.interfaces.library import verify, load_trace

diagnostic = verify("run.json", "policy.yaml", source="capture")
print(diagnostic.passed, len(diagnostic.violations))

trace = load_trace("run.json", source="langgraph")
```

---

## pip only vs clone repo

| Task | `pip install` only | Clone repo |
|------|-------------------|------------|
| `verify --demo` / `varly try` | ✅ | ✅ |
| Verify your own traces | ✅ | ✅ |
| `RunRecorder` in your project | ✅ | ✅ |
| LangGraph capture | ✅ with `[langgraph]` | ✅ |
| Viewer | ✅ | ✅ |
| Bundled policies (`mvp`, `strict`, `dev`, `live`) | ✅ | ✅ |
| Policy packs (`rag`, `api-guard`, …) | Copy from repo | ✅ |
| Cookbook fixtures (4 scenarios) | ❌ | ✅ |
| CI workflow template | Copy from repo | ✅ |
| Contribute / run tests | ❌ | ✅ |

Clone for hands-on examples: [Cookbook](cookbook/README.md)

---

## Common errors

| Problem | Fix |
|---------|-----|
| `looks like capture, but --source 'air'` | Use `--source capture` |
| `tool_name_allowlist` violation | Rename tool or edit policy `allowed` list |
| `tool_args_keys_allowlist` violation | Remove extra arg keys or update policy |
| `tool_arg_equals` violation | Fix arg value or policy `key`/`value` |
| Duration violation on live API | Use `bundled_policy("live")` or raise `max_ms` |
| `verify requires trace_file and --contract` | Pass both paths, or use `--demo` |
| LangGraph `ImportError` | `pip install "varly[langgraph]"` |
| Empty LangGraph events | Pass `config={"callbacks": [collector]}` on `invoke` |

More: [INSTALL.md](INSTALL.md)

---

## Documentation map

| Doc | When to read |
|-----|--------------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | You are here — full product overview |
| [LANGGRAPH_QUICKSTART.md](LANGGRAPH_QUICKSTART.md) | LangGraph capture → CI in one flow |
| [INSTALL.md](INSTALL.md) | Install options, troubleshooting |
| [policies/README.md](policies/README.md) | Every invariant + policy pack details |
| [cookbook/README.md](cookbook/README.md) | Four runnable end-to-end scenarios |
| [workflows/team-ci.md](workflows/team-ci.md) | PR gates, diff, SARIF/JUnit |
| [VIEWER.md](VIEWER.md) | Local browser diagnostics |
| [recipes/capture-run-recorder.md](recipes/capture-run-recorder.md) | RunRecorder hook reference |
| [recipes/capture-langgraph-export.md](recipes/capture-langgraph-export.md) | LangGraph export details |
| [architecture/](architecture/README.md) | AIR schema, adapters, diagnostic format |

---

## Give feedback

Trying Varly as a beta tester? After Steps 1–2 (or LangGraph / RunRecorder if relevant), reply with:

1. Did you get PASS/FAIL? What broke?
2. Would this help in your real project? Why / why not?
3. What felt confusing or too much work?

No form — a short message is enough. We log signals in [FEEDBACK.md](FEEDBACK.md).
