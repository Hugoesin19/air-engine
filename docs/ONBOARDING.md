# Onboarding checklist

Use this on a **fresh clone** or second machine. Goal: first PASS/FAIL in under 10 minutes using docs only.

## Checklist

- [ ] **1. Install** — follow [INSTALL.md](INSTALL.md) (`uv sync` or `pip install`)
- [ ] **2. Demo** — `uv run python scripts/demo_60s.py` (PASS + FAIL + REGRESSION)
- [ ] **3. Viewer** — [VIEWER.md](VIEWER.md) → `air-engine view --trace … --contract …`
- [ ] **4. Capture recipe** — [capture-run-recorder.md](recipes/capture-run-recorder.md) → your own `run.json`
- [ ] **5. Policy** — pick `examples/policies/mvp.yaml` (or `strict` / `dev`)
- [ ] **6. CI** — optional: wire [verify-trace action](../.github/actions/verify-trace/action.yml) in your repo

## Done when

You can run verify and interpret the result without asking the author:

```bash
uv run air-engine verify <file> --contract examples/policies/mvp.yaml --source <air|capture|langgraph|openai>
```

| Exit code | Meaning |
|-----------|---------|
| `0` | PASS — no violations |
| `1` | FAIL — violations listed, or diff REGRESSION |

## If stuck

1. Read the error — wrong `--source` hints are built in.
2. Check [INSTALL.md](INSTALL.md) troubleshooting table.
3. Compare your file shape to `examples/` fixtures.
