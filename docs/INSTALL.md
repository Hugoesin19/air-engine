# Install varly

**Python 3.12+** required.

---

## Option A — PyPI (recommended)

```bash
pip install varly
varly verify --demo
```

Bundled inside the wheel: `mvp` / `strict` / `dev` / `live` policies and mock capture fixture.

Policies path when installed:

```python
from varly.resources import bundled_policy
print(bundled_policy("mvp"))
```

---

## Option B — uv from source (development)

```bash
git clone https://github.com/Hugoesin19/varly.git
cd varly
uv sync
uv run varly --help
```

Pilot live mode (optional Gemini):

```bash
uv sync --group pilot
```

---

## Option C — pip from Git tag

```bash
pip install "varly @ git+https://github.com/Hugoesin19/varly.git@v1.0.0"
varly verify --demo
```

---

## Verify installation

```bash
# PyPI smoke test
varly verify --demo

# Full bundled demo (PASS + FAIL + diff regression)
varly try

# Full local demo (requires git clone)
uv run python scripts/demo_60s.py
```

---

## GitHub Actions

Pin the composite action to a release tag:

```yaml
- uses: Hugoesin19/varly/.github/actions/verify-trace@v1.0.0
  with:
    trace-file: path/to/run.json
    contract-file: examples/policies/mvp.yaml
    source: capture
```

In-repo usage:

```yaml
- uses: ./.github/actions/verify-trace
```

See [Releasing](RELEASING.md) for maintainer release steps.

---

## Common errors

| Message | Likely cause | Fix |
|---------|--------------|-----|
| `looks like a capture trace, but --source 'air' was used` | Wrong adapter | Add `--source capture` |
| `verify requires trace_file and --contract` | Missing args | Pass both or use `--demo` |
| `Unable to read contract file` | Policy path wrong | Use `bundled_policy("mvp")` or clone repo for `examples/policies/` |

---

## Next steps

- **[Getting started](GETTING_STARTED.md)** — pip-only path: your agent, policies, viewer (beta testers start here)
- [Quick start](../README.md#quick-start-5-minutes)
- [Capture recipe](recipes/capture-run-recorder.md)
- [Viewer](VIEWER.md)
- [Getting started](GETTING_STARTED.md) · [Early feedback log](FEEDBACK.md) · [Product development roadmap](PRODUCT_DEV_ROADMAP.md)
