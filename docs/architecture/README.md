# Architecture Specification

Formal specifications for the varly verification infrastructure.

## Planned Documents

- **AIR Schema** — [`air-schema-1.0.0.md`](air-schema-1.0.0.md) (Sprint 0 ✅)
- **Contract Model** — Property and invariant definitions → Sprint 3–4 ✅
- **Verification Pipeline** — End-to-end flow from capture to diagnostic → Sprint 3 ✅; mock-agent capture path → Sprint 6 ✅
- **Capture Event Log** — [`capture-event-log-1.0.0.md`](capture-event-log-1.0.0.md) → Sprint 6 ✅
- **Diagnostic JSON** — [`diagnostic-schema-1.0.0.md`](diagnostic-schema-1.0.0.md) → Sprint 8 ✅
- **OpenAI run mapping** — [`openai-run-mapping.md`](openai-run-mapping.md) → Sprint 10 ✅
- **LangGraph run mapping** — [`langgraph-run-mapping.md`](langgraph-run-mapping.md) → Sprint 10 ✅
- **CI reports** — `verify --format json|junit|sarif` + GitHub Action artifacts → Sprint 11 ✅
- **Baseline workflow** — [`../workflows/baseline.md`](../workflows/baseline.md) → Sprint 12 ✅

See [MVP Roadmap](../MVP_ROADMAP.md) (complete) and [Product Roadmap](../PRODUCT_ROADMAP.md) (active).
