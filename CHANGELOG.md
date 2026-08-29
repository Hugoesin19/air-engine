# Changelog

All notable changes to varly are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning aims at [SemVer](https://semver.org/).

## [1.0.0] — 2026-08-29

First **PyPI** release. Product phases P0–P6 complete; distribution (P1) ships here.

### Added

- **`pip install varly`** — bundled policies (`mvp`, `strict`, `dev`) and mock fixture
- **`varly verify --demo`** — smoke test without cloning the repo
- **`varly view`** — local browser diagnostic viewer with run summary and timeline
- Pilot Gemini capture, regression `diff` gate, capture recipe, source hints, `demo_60s` script
- Publish workflow (`.github/workflows/publish.yml`) for tags `v*`

### Changed

- **Product name:** `air-engine` → **Varly** (`pip install varly`, CLI `varly`)
- Version `1.0.0` (from `0.1.0` / `v1.0.0-beta` tag)
- Development status: Beta

[1.0.0]: https://github.com/Hugoesin19/varly/compare/v1.0.0-beta...v1.0.0

## [1.0.0-beta] — 2026-08-29

First tagged baseline after the v1 engine (MVP + post-MVP sprints 6–12).

### Added

- **AIR core** — immutable causal graphs, structural validation, state reconstruction
- **Contracts** — YAML policies; structural, semantic, metric, and business-rule invariants
- **CLI** — `validate`, `verify`, `diff`
- **Adapters** — canonical AIR JSON, capture logs, LangGraph, OpenAI (including recorded Responses shape)
- **Capture** — `RunRecorder` and deterministic mock agent (`examples/demo_agent/`)
- **CI** — GitHub Action, golden fixtures, mock-agent pipeline; reports as JSON / JUnit / SARIF
- **Policy packs** — `mvp`, `strict`, `dev` under `examples/policies/`
- **Regression gate** — `diff` compares violation sets against a baseline trace
- **Docs** — architecture specs, policy reference, baseline workflow, product and next-steps roadmaps

### Does not include (yet)

- Published PyPI package (install from source with `uv`)
- One-click capture for every framework (recipes are partial; see `docs/architecture/`)
- Web UI or hosted SaaS
- Contract DSL (v2 roadmap)
- Live API calls in CI (mock-first by design)

### Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) recommended

[1.0.0-beta]: https://github.com/Hugoesin19/varly/compare/mvp-v0.1.0...v1.0.0-beta
