# Onboarding checklist

Goal: first PASS/FAIL in under 10 minutes.

**PyPI users:** follow **[Getting started](GETTING_STARTED.md)** — no clone required for `varly try`, `RunRecorder`, or LangGraph capture.

**Contributors / cookbook:** use this checklist on a fresh clone.

---

## Checklist

- [ ] **1. Install** — [INSTALL.md](INSTALL.md) (`pip install varly` or `uv sync`)
- [ ] **2. Demo** — `varly try` (pip) or `uv run python scripts/demo_60s.py` (clone)
- [ ] **3. Pick a capture path** — [LangGraph quickstart](LANGGRAPH_QUICKSTART.md) or [RunRecorder recipe](recipes/capture-run-recorder.md)
- [ ] **4. Verify** — `varly verify <file> --contract <policy> --source <capture|langgraph|openai>`
- [ ] **5. Policy** — `bundled_policy("mvp")` or `examples/policies/api-guard.yaml` for tool args
- [ ] **6. Viewer** — [VIEWER.md](VIEWER.md) → `varly view --trace … --contract …`
- [ ] **7. CI** (optional) — [starter-ci](../examples/starter-ci/README.md) or [team CI](workflows/team-ci.md)

---

## Done when

You can run verify and interpret the result without asking the author:

```bash
varly verify <file> --contract <policy.yaml> --source <capture|langgraph|openai|air>
```

| Exit code | Meaning |
|-----------|---------|
| `0` | PASS — no violations |
| `1` | FAIL — violations listed, or diff REGRESSION |

---

## If stuck

1. Read the error — wrong `--source` hints are built in.
2. [Getting started — common errors](GETTING_STARTED.md#common-errors)
3. [INSTALL.md](INSTALL.md) troubleshooting table
4. Compare your file shape to `examples/` fixtures or run the [cookbook](cookbook/README.md)
