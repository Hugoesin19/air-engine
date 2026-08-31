# Install varly

**Python 3.12+** required.

**New here?** Read **[Getting started](GETTING_STARTED.md)** first — it covers everything Varly can do after install.

---

## Option A — PyPI (recommended)

```bash
pip install varly
varly verify --demo
varly try
```

Bundled in the wheel:

| Resource | Names |
|----------|-------|
| Policies | `mvp`, `strict`, `dev`, `live` |
| Fixtures | `mock_run`, `trace_valid_minimal`, `trace_invalid_missing_tool_return` |

```python
from varly.resources import bundled_policy, bundled_fixture
print(bundled_policy("mvp"))
print(bundled_fixture("mock_run"))
```

LangGraph capture:

```bash
pip install "varly[langgraph]"
```

More policy packs (`rag`, `api-guard`, …) live in the repo under `examples/policies/`.

---

## Option B — uv from source (development)

```bash
git clone https://github.com/Hugoesin19/varly.git
cd varly
uv sync
uv run varly --help
```

Cookbook + LangGraph examples:

```bash
uv sync --group langgraph
```

Pilot live mode (optional Gemini):

```bash
uv sync --group pilot
```

---

## Option C — pip from Git tag

```bash
pip install "varly @ git+https://github.com/Hugoesin19/varly.git@v1.2.0"
varly verify --demo
```

---

## Verify installation

```bash
varly verify --demo          # smoke test (PASS)
varly try                    # PASS + FAIL + diff regression
```

From a clone:

```bash
uv run python scripts/demo_60s.py
```

---

## GitHub Actions

Pin the composite action to a release tag:

```yaml
- uses: Hugoesin19/varly/.github/actions/verify-trace@v1.2.0
  with:
    trace-file: path/to/run.json
    contract-file: examples/policies/mvp.yaml
    source: capture
```

In-repo usage:

```yaml
- uses: ./.github/actions/verify-trace
```

Full CI guide: [workflows/team-ci.md](workflows/team-ci.md) · Maintainer releases: [RELEASING.md](RELEASING.md)

---

## Common errors

| Message | Likely cause | Fix |
|---------|--------------|-----|
| `looks like a capture trace, but --source 'air' was used` | Wrong adapter | Add `--source capture` |
| `verify requires trace_file and --contract` | Missing args | Pass both or use `--demo` |
| `Unable to read contract file` | Policy path wrong | Use `bundled_policy("mvp")` or clone repo for `examples/policies/` |
| `Unknown bundled policy` | Pack not in wheel | Copy from `examples/policies/` (e.g. `api-guard.yaml`) |

---

## Next steps

- **[Getting started](GETTING_STARTED.md)** — full product guide (start here)
- [LangGraph quickstart](LANGGRAPH_QUICKSTART.md)
- [Policy reference](policies/README.md)
- [Cookbook](cookbook/README.md)
- [Viewer](VIEWER.md)
