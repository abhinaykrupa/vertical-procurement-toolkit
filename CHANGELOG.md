# Changelog

All notable changes to this project are documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `vpt/` Python package — clean public API: `from vpt import match_invoice, load_catalog, get_adapter`
- CLI: `vpt analyze`, `vpt adapters`, `vpt detect`, `vpt --version` (via `python -m vpt.cli` or installed entrypoint)
- Generic CSV adapter (`vpt.generic_adapter`) — handles any CSV given a column mapping; auto-computes `annual_spend` when missing; suggests column mappings heuristically
- Real LLM-backed Stage 3 judge (`vpt.llm_judge`) — Anthropic Claude + OpenAI providers behind `LLM_JUDGE_PROVIDER` env flag; falls back to mock when no credentials
- Per-vertical UOM tables in YAML (`uom_tables/dental.yaml`, `vet.yaml`, `hvac.yaml`, `restaurant.yaml`) and loader (`vpt.uom`)
- Vetcove adapter for veterinary vertical (closes part of issue #1)
- Vet vertical example: `sample_data/vet_catalog.csv` (~30 SKUs) + `sample_clinic_vetcove.csv` (30-line multi-distributor order history)
- Pytest test suite — 40 tests across adapters, matcher, generic adapter, UOM loader, and CLI
- GitHub Actions CI — runs on Python 3.10/3.11/3.12, includes CLI smoke tests
- `pyproject.toml` — pip-installable package, optional `[streamlit]`, `[llm]`, `[dev]` extras
- `CHANGELOG.md`

### Changed
- `app/main.py` page title generalized: "SourceClub Ops POC" → "Vertical Procurement Toolkit"
- `app/main.py` docstring rewritten to point readers at `ADAPTING.md`
- Adapter registry now includes `Vetcove`

## [0.1.0] — 2026-06-01

### Added
- Initial extraction from the SourceClub case-study deliverable
- 3-stage matching engine (deterministic → semantic → LLM judge)
- UOM/pack-size normalizer with regex + alias table
- 5 dental supplier adapters: Benco, Henry Schein, Darby, Base86, Patterson
- Streamlit reference app with leadership dashboard + savings analysis tabs
- Mock Stripe ↔ HubSpot multi-location billing sync engine
- `README.md`, `ADAPTING.md`, `CONTRIBUTING.md`, `LICENSE` (MIT), `PRODUCTION_ARCHITECTURE.md`, `SECURITY_REVIEW.md`
- Original SourceClub case-study deliverables preserved under `case-study/`
- 8 "good first issue" GitHub issues for community contributors

[Unreleased]: https://github.com/abhinaykrupa/vertical-procurement-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/abhinaykrupa/vertical-procurement-toolkit/releases/tag/v0.1.0
