# Changelog

All notable changes to this project are documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (later in v0.2 cycle)
- **Optometry vertical** (5th vertical): VSP/Essilor adapter, 30-SKU catalog (contacts, lenses, frames, coatings, solutions, drops, diagnostics), sample export, uom_tables/optometry.yaml. End-to-end: 30 lines, $98.8K spend, $12.3K savings, 1 catalog gap.
- **Multi-supplier comparison** (`vpt compare`, `vpt/compare.py`): given the same vertical's purchase history from multiple distributors, finds the cheapest supplier per item and total potential savings — the cross-distributor value prop single-vendor clubs can't offer.
- **Benchmark script** (`scripts/benchmark.py`): honest per-vertical match-rate table across all bundled samples; surfaced in the README.
- **HVAC vertical** (closes #3): Ferguson adapter, 30-SKU HVAC catalog (refrigerant, capacitors, motors, ductwork, coils, ignition), sample export. End-to-end: 30 lines, $10.4K savings, 1 deliberate catalog gap.
- **Restaurant vertical** (closes #2): Sysco adapter (handles foodservice pack-size conventions like "6/#10 CAN", "5 GAL PAIL", quoted-comma totals), 30-SKU foodservice catalog, sample export. End-to-end: 30 lines, $8.2K savings.
- `vpt validate` CLI command — checks catalog for required columns, numeric prices, duplicate/blank SKUs; exits non-zero on problems
- `--vertical` CLI flag + automatic UOM-table loading per adapter (`ADAPTER_VERTICAL` map) — the matcher now loads the correct vertical vocabulary automatically
- `.pre-commit-config.yaml` — ruff + whitespace/EOF/yaml/large-file hooks
- Test suite expanded to 50 tests: new adapters, per-vertical end-to-end savings assertions, validate command, adapter→vertical mapping completeness

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
