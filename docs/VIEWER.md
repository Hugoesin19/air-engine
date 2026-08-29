# Local diagnostic viewer (Step 6)

Browser UI for PASS/FAIL and violations — no cloud, no terminal required to **read** results.

## Quick use

Verify a trace and open the viewer in one step:

```bash
uv run varly view \
  --trace examples/demo_agent/artifacts/mock_run.json \
  --contract examples/policies/mvp.yaml \
  --source capture
```

Or from an existing diagnostic JSON:

```bash
uv run varly verify examples/demo_agent/artifacts/mock_run.json \
  --contract examples/policies/mvp.yaml \
  --source capture \
  --output /tmp/report.json

uv run varly view /tmp/report.json
```

Your browser opens `http://127.0.0.1:8765/`. Press **Ctrl+C** in the terminal to stop the server.

## Without the CLI

Open `src/varly/interfaces/viewer/index.html` in a browser and drag-drop any diagnostic JSON from `verify --output`.

## Options

| Flag | Description |
|------|-------------|
| `--port 8765` | Change local port |
| `--no-open` | Start server without opening a tab |

## What it shows

- PASS / FAIL badge
- `trace_id`, violation count
- Table of invariant violations (id, node, message)

- Does **not** include: live agent runs, auth, billing, or DAG topology graph (later roadmap).
- **Does** include: run summary (steps, LLM/tool counts, duration, tokens) and a simple ordered timeline.
