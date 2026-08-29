# Install air-engine

**Python 3.12+** required.

---

## Option A — uv (recommended for development)

```bash
git clone https://github.com/Hugoesin19/air-engine.git
cd air-engine
uv sync
uv run air-engine --help
```

Run commands with `uv run air-engine …` or activate the venv (`.venv`).

Pilot live mode (optional Gemini):

```bash
uv sync --group pilot
```

---

## Option B — pip from Git tag

Install a released tag without cloning the full dev tree:

```bash
pip install "air-engine @ git+https://github.com/Hugoesin19/air-engine.git@v1.0.0-beta"
air-engine --help
```

Replace `v1.0.0-beta` with the [latest tag](https://github.com/Hugoesin19/air-engine/tags).

---

## Option C — pip editable (local clone)

```bash
git clone https://github.com/Hugoesin19/air-engine.git
cd air-engine
pip install -e .
air-engine --help
```

---

## PyPI

Not published yet. Track [releases](https://github.com/Hugoesin19/air-engine/releases) for updates.  
Pre-release target: `0.2.0a1` on PyPI (optional roadmap item).

---

## Verify installation

```bash
# 60-second demo: mock agent → PASS → FAIL → REGRESSION
uv run python scripts/demo_60s.py
```

Or manually:

```bash
uv run python examples/demo_agent/run.py
uv run air-engine verify examples/demo_agent/artifacts/mock_run.json \
  --contract examples/policies/mvp.yaml --source capture
```

Expect `PASS`.

---

## GitHub Actions

Pin the composite action to a release tag:

```yaml
- uses: Hugoesin19/air-engine/.github/actions/verify-trace@v1.0.0-beta
  with:
    trace-file: examples/demo_agent/artifacts/mock_run.json
    contract-file: examples/policies/mvp.yaml
    source: capture
```

The job must checkout `air-engine` (or vendor the action). For in-repo usage, reference the local path:

```yaml
- uses: ./.github/actions/verify-trace
  with:
    trace-file: path/to/run.json
    contract-file: examples/policies/mvp.yaml
    source: capture
```

---

## Common errors

| Message | Likely cause | Fix |
|---------|--------------|-----|
| `looks like a capture trace, but --source 'air' was used` | Wrong adapter | Add `--source capture` |
| `looks like a openai trace` | OpenAI JSON with wrong source | `--source openai` |
| `Unable to read trace file` | Path typo | Check file exists |
| `Unable to read contract file` | Policy path wrong | Point to `.yaml` under `examples/policies/` |
| `max_trace_duration` on live runs | API latency | Use relaxed policy (see `pilot/policies/live.yaml`) |

---

## Next steps

- [Quick start](../README.md#quick-start-5-minutes)
- [Capture recipe](recipes/capture-run-recorder.md)
- [Onboarding checklist](ONBOARDING.md)
