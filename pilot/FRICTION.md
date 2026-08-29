# Pilot friction notes (Step 2)

Update this file after your first **live** Gemini run. Dry-run findings below are from scaffolding.

## Dry-run (scaffolding)

- **Instrumentation is manual for generic agents** — each LLM/tool step needs an explicit `record_*` call unless you use LangGraph callbacks.  
  → LangGraph: [capture-langgraph-export recipe](../docs/recipes/capture-langgraph-export.md)  
  → Generic: [capture recipe](../docs/recipes/capture-run-recorder.md) + [examples/capture_recipe/](../examples/capture_recipe/).
- **No `--source gemini`** — captures use `RunRecorder` (`--source capture`), not a native Gemini export adapter.
- **Tool is local/canned** — `search` does not call the web; only the LLM steps hit Gemini in live mode (by design for cost control).
- **Policy coupling** — `mvp.yaml` allowlists tool name `search`; renaming the tool requires policy edits.

## Live run

- [x] Ran live successfully (Gemini `gemini-3.6-flash`, ~48s wall-clock, 292+264 tokens)
- [x] `verify` → PASS with `pilot/policies/live.yaml` (mvp 10s cap is too tight for real API latency)
- [x] Committed anonymized `artifacts/research_run.json` when ready

- **Policy mismatch on first verify** — `examples/policies/mvp.yaml` caps duration at 10s; two Gemini calls took ~48s. Use `pilot/policies/live.yaml` (120s) for live captures, or tune SLA per environment.
- **Model deprecation** — default had to move from `gemini-2.0-flash` to `gemini-3.6-flash` (404 from API).
