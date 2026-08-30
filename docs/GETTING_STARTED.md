# Getting started with Varly

**For beta testers** — use this guide after `pip install varly`. No need to clone the repo unless you want the full cookbook examples.

**Python 3.12+** required.

---

## What Varly does 

Varly checks a **finished agent run** against a **YAML policy** (tool allowlists, token limits, event order, etc.) and returns **PASS or FAIL** — deterministically, without another LLM judging the output.

Typical flow:

```
Your agent runs → you save a trace JSON → varly verify → PASS/FAIL
```

Useful when you want CI-style gates: “this PR must not introduce new contract violations.”

---

## Step 1 — Install and smoke test

```bash
pip install varly
varly verify --demo
```

Expect `PASS` and `violations: 0`. This only proves the install works.

**`--demo` is not the product.** It is a bundled mock trace + policy. Everything below is the real usage.

---

## Step 2 — Verify any trace file you already have

If you have a JSON trace (from LangGraph export, OpenAI Responses, or Varly capture):

```bash
varly verify path/to/run.json --contract path/to/policy.yaml --source capture
```

| `--source` | When to use |
|------------|-------------|
| `capture` | Varly `RunRecorder` output (most common for custom agents) |
| `langgraph` | LangGraph / LangChain callback export |
| `openai` | OpenAI Responses-shaped JSON |
| `air` | Canonical AIR JSON (advanced) |

Wrong source? The CLI prints a hint (e.g. “looks like capture, try `--source capture`”).

### Bundled policies (no repo clone needed)

Three policies ship inside the wheel:

```bash
python -c "from varly.resources import bundled_policy; print(bundled_policy('mvp'))"
```

| Name | Use |
|------|-----|
| `mvp` | Default CI gate |
| `strict` | Tighter production limits |
| `dev` | Relaxed for local debugging |

Example:

```bash
varly verify my_run.json \
  --contract "$(python -c "from varly.resources import bundled_policy; print(bundled_policy('mvp'))")" \
  --source capture
```

---

## Step 3 — Try it with your own Python agent

You do **not** need to clone the repo. `RunRecorder` is included in `pip install varly`.

Minimal script (`my_agent.py`):

```python
from pathlib import Path
import time

from varly.capture import RunRecorder

recorder = RunRecorder(run_id="my-run-001")
clock = time.perf_counter()

def ts() -> float:
    return round((time.perf_counter() - clock) * 1000, 3)

# --- your agent logic here ---
recorder.record_run_start(step_id="step-001", timestamp_ms=ts())

# after each LLM call
recorder.record_llm_call(step_id="step-002", timestamp_ms=ts(), total_tokens=150)

# before / after each tool call
recorder.record_tool_call(step_id="step-003", timestamp_ms=ts(), tool_name="search")
recorder.record_tool_output(step_id="step-004", timestamp_ms=ts(), tool_name="search")

recorder.record_run_end(step_id="step-005", timestamp_ms=ts())
# --- end agent logic ---

out = Path("my_run.json")
recorder.write_json(out)
print(f"Wrote {out}")
```

Then verify:

```bash
python my_agent.py
varly verify my_run.json \
  --contract "$(python -c "from varly.resources import bundled_policy; print(bundled_policy('mvp'))")" \
  --source capture
```

**Important:** `mvp` allowlists tool name `search`. If your tools have other names, copy `mvp.yaml` from the [repo examples](https://github.com/Hugoesin19/varly/tree/main/examples/policies) and edit the allowlist.

Full hook reference: [capture recipe](recipes/capture-run-recorder.md) (examples live in the GitHub repo).

---

## Step 4 — LangGraph users

```bash
pip install "varly[langgraph]"
```

Wire `LangGraphCallbackCollector` around your graph, export JSON, then:

```bash
varly verify run.json --contract policy.yaml --source langgraph
```

Recipe with copy-paste code: [capture-langgraph-export.md](recipes/capture-langgraph-export.md).

---

## Step 5 — View results in the browser

```bash
varly view --trace my_run.json \
  --contract "$(python -c "from varly.resources import bundled_policy; print(bundled_policy('mvp'))")" \
  --source capture
```

Opens a local page with timeline and causal graph.

---

## Step 6 — Regression gate (`diff`)

Compare a **baseline** run (good) vs **current** run (new). Fails if the current run has violations the baseline did not:

```bash
varly diff baseline.json current.json --contract policy.yaml --source capture
```

Exit `0` = no regression. Exit `1` = new violations.

---

## What needs the GitHub repo?

| Task | `pip install` only | Clone repo |
|------|-------------------|------------|
| Smoke test (`--demo`) | ✅ | ✅ |
| Verify your own traces | ✅ | ✅ |
| `RunRecorder` in your project | ✅ | ✅ |
| LangGraph capture | ✅ with `[langgraph]` extra | ✅ |
| Viewer | ✅ | ✅ |
| Cookbook fixtures + examples | ❌ | ✅ |
| GitHub Action CI template | ❌ | ✅ (or copy from docs) |

Clone when you want ready-made examples: [cookbook](cookbook/README.md).

---

## Common errors

| Problem | Fix |
|---------|-----|
| `looks like capture, but --source 'air'` | Add `--source capture` |
| Tool not in allowlist | Edit policy `allowed_tools` |
| Duration violation on live API | Increase `max_duration_ms` in policy |
| `verify requires trace_file and --contract` | Pass both paths, or use `--demo` |

More: [INSTALL.md](INSTALL.md).

---

## Give feedback

If someone asked you to try Varly: run Steps 1–3 (or 4 if you use LangGraph), then reply with:

1. Did you get PASS/FAIL? What broke?
2. Would this help in your real project? Why / why not?
3. What felt confusing or too much work?

No form — a short message or a 15-minute call is enough.

---

## Related

- [Install](INSTALL.md) · [Cookbook](cookbook/README.md) · [Viewer](VIEWER.md)
- [Policy reference](policies/README.md) · [Team CI](workflows/team-ci.md)
