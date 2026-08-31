# Starter CI template

Copy this into **your** LangGraph project to gate agent runs in GitHub Actions.

## Setup

1. Copy [`workflow.yml`](workflow.yml) → `.github/workflows/varly.yml` in your repo.
2. Ensure your CI step produces a trace JSON (see [LangGraph quickstart](../../docs/LANGGRAPH_QUICKSTART.md)).
3. Adjust `trace-file`, `contract-file`, and `source` in the workflow.
4. Commit a **baseline** trace on `main`; use `diff` on PRs (see [team-ci.md](../../docs/workflows/team-ci.md)).

## What the workflow does

```
generate trace (your script) → varly verify → PASS/FAIL in CI
```

This template uses `pip install` — no need to clone the varly repo.

## Example trace generation step

Add before the verify step in `workflow.yml`:

```yaml
- name: Generate agent trace
  run: python scripts/export_langgraph_run.py --output artifacts/run.json
```

Your script should use `LangGraphCallbackCollector` and `write_json()` — see [capture-langgraph-export.md](../../docs/recipes/capture-langgraph-export.md).

## Policy files

Copy a pack from [`examples/policies/`](../../examples/policies/) or use bundled policies:

```yaml
- run: |
    python -c "from varly.resources import bundled_policy; import shutil; shutil.copy(bundled_policy('mvp'), policies/mvp.yaml)"
```

## In this repo

The golden path is already exercised in CI job `langgraph-capture-pipeline` (`.github/workflows/ci.yml`).
