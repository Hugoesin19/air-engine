# Pilot runs (Step 2)

This folder holds **real-shaped agent pilots** — outside `examples/` toys and hand-written golden fixtures.

## Product model

air-engine does **not** run your agent in production. The commercial flow is:

```
Your agent runs (any LLM / framework)
        ↓
Capture produces a JSON event log
        ↓
air-engine verify → PASS / FAIL
```

The pilot reproduces that flow with a minimal **research assistant**: plan → `search` tool → answer.

## Gemini research assistant

Location: [`gemini_research_assistant/run.py`](gemini_research_assistant/run.py)

| Mode | When | API cost |
|------|------|----------|
| **Dry-run** (default) | No `PILOT_LIVE=1` or no API key | Zero |
| **Live** | `PILOT_LIVE=1` + `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) | ~2 Gemini calls per run |

Dry-run uses the same `RunRecorder` event sequence as live mode so CI and contributors never call paid APIs.  
For the strongest product story, run **live once**, review the capture, then commit the anonymized JSON under `artifacts/`.

### Where to put your API key (never commit it)

1. Copy the template in the repo root:
   ```powershell
   cd d:\tfg\air-engine
   copy .env.example .env
   ```
2. Open `.env` in the editor and replace `paste_your_gemini_api_key_here` with your real key.
3. Leave `PILOT_LIVE=1` in that file when you want live mode.

`.env` is listed in `.gitignore` — Git will **not** upload it to GitHub.  
Only `.env.example` (without secrets) is safe to commit.

The pilot script loads `.env` automatically when you run `run.py`.

### Setup (live mode only)

```bash
uv sync --group pilot
```

### Run (Windows PowerShell)

```powershell
cd d:\tfg\air-engine

# 1) Create .env once (see above) with PILOT_LIVE=1 and GOOGLE_API_KEY=...

# 2) Install pilot deps (google-genai) — once
uv sync --group pilot

# 3) Live run — reads .env automatically
uv run python pilot/gemini_research_assistant/run.py
# Should print: Pilot capture written (live): ...

# 4) Verify the capture (live runs: use pilot policy — real API latency exceeds mvp 10s cap)
uv run air-engine verify pilot/artifacts/research_run.json `
  --contract pilot/policies/live.yaml --source capture
```

### Run (bash / macOS / Linux)

```bash
uv sync --group pilot
# With .env in repo root, or:
PILOT_LIVE=1 GOOGLE_API_KEY=... uv run python pilot/gemini_research_assistant/run.py
```

### Run (dry-run, no API)

```bash
# Unset live in .env (PILOT_LIVE=0) or temporarily rename .env
uv run python pilot/gemini_research_assistant/run.py
```

### Verify

```bash
uv run air-engine verify pilot/artifacts/research_run.json \
  --contract pilot/policies/live.yaml \
  --source capture
```

### What makes this “real” enough

- Orchestration logic lives in the pilot script (not a one-line mock).
- Live mode calls **Gemini** for planning and synthesis; tokens come from the API response.
- Capture uses the same `RunRecorder` path a customer would instrument.
- Verification is deterministic on the saved log (no LLM-as-judge).

## Files

| Path | Purpose |
|------|---------|
| `gemini_research_assistant/run.py` | Agent + capture |
| `gemini_research_assistant/tools.py` | Deterministic `search` tool (no extra API) |
| `artifacts/research_run.json` | Committed capture (regenerate with live when ready) |
| `FRICTION.md` | What was hard or confusing (update after your live run) |

## Next (Step 3)

Frozen baseline: [`artifacts/baseline_research_run.json`](artifacts/baseline_research_run.json) (live Gemini capture, PASS).

```powershell
# Current run matches baseline → exit 0
uv run python pilot/scripts/verify_gate.py

# Or manually:
uv run air-engine diff pilot/artifacts/baseline_research_run.json `
  pilot/artifacts/research_run.json `
  --contract pilot/policies/live.yaml --source capture

# Intentional break demo → exit 1 (REGRESSION)
uv run air-engine diff pilot/artifacts/baseline_research_run.json `
  pilot/artifacts/broken_research_run.json `
  --contract pilot/policies/live.yaml --source capture
```

See [Baseline workflow](../docs/workflows/baseline.md).
