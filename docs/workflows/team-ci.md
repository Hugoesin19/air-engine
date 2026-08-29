# Team CI with varly

Standard workflow for small teams: **verify** every run on PR, **diff** against a golden baseline, upload **JUnit/SARIF** for the CI UI.

Copy-paste ready. No cloud SaaS required.

---

## Exit codes (stable for wrappers)

| Command | Code | Meaning |
|---------|------|---------|
| `varly verify` | `0` | PASS — no violations |
| `varly verify` | `1` | FAIL — violations or load/adapter error |
| `varly verify` | `2` | Usage error (missing args) |
| `varly diff` | `0` | No regression (current ⊆ baseline violations) |
| `varly diff` | `1` | Regression — new violations vs baseline |
| `varly validate` | `0` | Structural OK |
| `varly validate` | `1` | Structural error |

Machine-readable stdout: use `--format json|junit|sarif` with `verify`.

---

## 1. Verify on every PR (single trace)

After your agent writes a capture file:

```yaml
# .github/workflows/varly.yml
name: varly

on:
  pull_request:
  push:
    branches: [main]

jobs:
  verify-agent-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install varly
        run: pip install varly

      - name: Run your agent (example)
        run: python your_agent/run.py --output artifacts/run.json

      - uses: Hugoesin19/varly/.github/actions/verify-trace@v1.0.0
        with:
          trace-file: artifacts/run.json
          contract-file: policies/mvp.yaml
          source: capture
          report-format: sarif
          report-file: varly-report.sarif
```

In-repo (development):

```yaml
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - uses: ./.github/actions/verify-trace
        with:
          trace-file: examples/demo_agent/artifacts/mock_run.json
          contract-file: examples/policies/mvp.yaml
          source: capture
```

---

## 2. Regression gate (`diff` on PR)

Keep a golden trace in git. Fail when the current run introduces **new** violations.

```yaml
      - name: Regression diff vs baseline
        run: |
          varly diff \
            fixtures/baseline_run.json \
            artifacts/run.json \
            --contract policies/mvp.yaml \
            --source capture
```

See [baseline.md](baseline.md) for semantics.

---

## 3. Batch verify (multiple fixtures)

Verify every trace in a folder with one command:

```bash
uv run python scripts/ci/verify_batch.py \
  examples/fixtures/recorded/*.json \
  --contract examples/policies/mvp.yaml \
  --source openai
```

GitHub Actions:

```yaml
      - name: Verify all golden fixtures
        run: |
          python scripts/ci/verify_batch.py \
            fixtures/*.json \
            --contract policies/mvp.yaml \
            --source capture
```

Exit `0` only if **all** traces pass.

---

## 4. Report artifacts

### JUnit (GitHub / GitLab test UI)

```bash
varly verify run.json \
  --contract policies/mvp.yaml \
  --source capture \
  --format junit \
  --output varly-report.xml
```

**GitHub Actions** — publish as check:

```yaml
      - name: Upload JUnit
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: varly-junit
          path: varly-report.xml
```

**GitLab CI** — `reports: junit: varly-report.xml` in your job.

### SARIF (GitHub Code Scanning)

```bash
varly verify run.json \
  --contract policies/mvp.yaml \
  --format sarif \
  --output varly-report.sarif
```

The composite action `verify-trace` uploads SARIF when `report-format: sarif` (requires `security-events: write`).

### JSON (custom dashboards)

```bash
varly verify run.json --contract policies/mvp.yaml --format json > diagnostic.json
```

Schema: [diagnostic-schema-1.0.0.md](../architecture/diagnostic-schema-1.0.0.md).

---

## 5. Recommended team workflow

1. **Policy in repo** — `policies/mvp.yaml` (or `rag.yaml`, `support-bot.yaml` — see [policy packs](../policies/README.md)).
2. **Golden baseline** — commit `fixtures/baseline_run.json` from a known-good agent run.
3. **PR pipeline** — generate `artifacts/run.json` → `verify` → `diff` vs baseline.
4. **Update baseline** only when the team accepts a deliberate behavior change (review + commit).
5. **Branch policies** — stricter pack on `main`, relaxed `dev.yaml` on feature branches (optional).

---

## Related

- [Baseline regression](baseline.md)
- [Install](../INSTALL.md)
- [Cookbook](../cookbook/README.md)
- [Product development roadmap](../PRODUCT_DEV_ROADMAP.md) — P4
