# Good First Issues — paste into GitHub after pushing

These are entry-point issues for new contributors. After the repo is pushed to GitHub, paste each one as a separate issue and tag with `good first issue` + `help wanted` + the relevant `vertical:*` label.

---

## Issue 1 — Add a Vetcove adapter (veterinary vertical)

**Vertical:** Veterinary
**Difficulty:** Medium
**Estimated time:** 4-6 hours

Vetcove is the dominant procurement platform in US veterinary (15K+ clinics). It exposes per-clinic order history that's an obvious target for savings analysis against a vet GPO catalog.

**What to build:**
- `app/engine/adapters/vetcove.py` parser
- Sample Vetcove export under `sample_data/sample_clinic_vetcove.csv` (anonymized or fabricated)
- Sample vet GPO catalog under `sample_data/vet_catalog.csv` (~30-40 items: vaccines, anesthetics, surgical consumables)
- Update `auto_detect.py` and `main.py` dispatch
- UOM additions for vet vocabulary: "ml", "L", "dose", "vial", "100-tab bottle"

**Reference:** see `app/engine/adapters/benco.py` for the adapter template, ADAPTING.md for the walkthrough.

**Labels:** `good first issue`, `vertical:vet`, `help wanted`

---

## Issue 2 — Add a Sysco adapter (restaurant vertical)

**Vertical:** Independent restaurants
**Difficulty:** Medium-Hard (Sysco exports are notoriously inconsistent)
**Estimated time:** 6-8 hours

Sysco is the largest US foodservice distributor. Independent restaurants face a known information asymmetry against Sysco's pricing — buyer-side intelligence has clear demand.

**What to build:**
- `app/engine/adapters/sysco.py` parser (handle their quirky export format)
- Sample Sysco export
- Sample restaurant catalog (~40 items spanning produce, proteins, dry goods)
- UOM additions: "case", "#10 can", "5-gal pail", "lb", "oz", "each", "bushel"
- Pack-size regex updates for foodservice conventions

**Bonus:** add a second adapter for US Foods or PFG to demonstrate multi-supplier comparison.

**Labels:** `good first issue`, `vertical:restaurant`, `help wanted`

---

## Issue 3 — Add an HVAC supplier adapter (Ferguson, Carrier, or Trane)

**Vertical:** HVAC contractors
**Difficulty:** Medium
**Estimated time:** 4-6 hours

HVAC is the most under-served vertical for procurement tooling (~120K US establishments, top-5 only ~35% share, no Vetcove-equivalent identified). This is the highest-leverage vertical to add — if this toolkit becomes useful in HVAC, it has a real path to community adoption.

**What to build:**
- Adapter for Ferguson HVAC, Carrier, Trane, Lennox, or R.E. Michel
- Sample export
- Sample HVAC catalog (~30 items: refrigerant, fittings, ductwork, controls)
- UOM additions: "lb" (refrigerant), "gallon", "drum", "pallet", "linear ft"

**Labels:** `good first issue`, `vertical:hvac`, `help wanted`

---

## Issue 4 — Generic CSV adapter for unknown suppliers

**Difficulty:** Medium
**Estimated time:** 4-6 hours

Right now, if a user uploads a CSV from a supplier we don't have an adapter for, the auto-detect falls back to "Unknown" and the pipeline fails. A generic adapter that asks the user to map columns interactively (or uses an LLM to infer the mapping) would unlock arbitrary CSVs without writing adapter code.

**What to build:**
- `app/engine/adapters/generic.py` parser that accepts a user-provided column mapping
- UI in `main.py`: when adapter = "Unknown", show a column-mapping form before parsing
- (Optional) LLM-assisted column inference behind a feature flag

**Labels:** `good first issue`, `enhancement`, `help wanted`

---

## Issue 5 — Improve UOM normalizer with industry vocabulary table

**Difficulty:** Easy-Medium
**Estimated time:** 2-4 hours

Today the UOM normalizer in `app/engine/matcher.py` has dental-flavored vocabulary hardcoded. Extract this to a YAML/JSON table per vertical (`uom_tables/dental.yaml`, `uom_tables/vet.yaml`, etc.) and let the matcher load the appropriate table.

**What to build:**
- `uom_tables/` directory with one YAML per supported vertical
- Update matcher to load the relevant table at init
- Document how to add a new UOM table in ADAPTING.md

**Labels:** `good first issue`, `enhancement`, `help wanted`

---

## Issue 6 — Wire in a real LLM call for Stage 3 (behind feature flag)

**Difficulty:** Medium
**Estimated time:** 4-6 hours

Stage 3 (LLM Judge) is currently a rule-based mock. Wire in a real LLM call (Anthropic Claude Haiku or OpenAI GPT-4o-mini) behind an env-var feature flag, so users with API keys get real reasoning without breaking the offline demo for everyone else.

**What to build:**
- `app/engine/llm_judge.py` with real Anthropic/OpenAI call
- Use the production prompt sketch already in `app/engine/matcher.py` docstring
- Feature flag: `LLM_JUDGE_ENABLED=true` env var + API key
- Fallback to mock when key is absent
- Update README "Tech choices" section

**Labels:** `good first issue`, `enhancement`, `ai`, `help wanted`

---

## Issue 7 — Add unit tests for adapters

**Difficulty:** Easy
**Estimated time:** 2-4 hours

There are no automated tests today. Add a `tests/` directory with pytest cases for each adapter:

- `tests/test_benco.py` — parse the sample file, assert row count + key columns
- Same for each other adapter
- GitHub Action workflow to run tests on PR

**Labels:** `good first issue`, `testing`, `help wanted`

---

## Issue 8 — CLI wrapper for headless usage

**Difficulty:** Medium
**Estimated time:** 4 hours

A simple CLI (`python -m vpt analyze <supplier_file> <catalog_file>`) that runs the same pipeline without Streamlit and outputs JSON. Unlocks scripting, batch processing, and integration into other tools.

**What to build:**
- `app/cli.py` argparse entry point
- Reuse `engine.matcher` directly
- Output: JSON to stdout with matched/review/no-match buckets
- Document in README

**Labels:** `good first issue`, `enhancement`, `help wanted`
