# Vertical Procurement Toolkit

**An open-source reference architecture for automating supplier-invoice savings analysis in fragmented-supplier industries.**

Small businesses in dental, veterinary, optometry, HVAC, auto repair, independent restaurants, and similar verticals all face the same problem: they buy from 3–7 different distributors, every distributor uses different SKUs, different descriptions, different pack sizes, different units of measure — and nobody has time to compare line-by-line whether they're overpaying.

This repo is the engine that does that comparison automatically. It was originally built as a case study for a dental Group Purchasing Organization, but the architecture is vertical-agnostic — swap the catalog and add a supplier adapter, and the same engine works for veterinary, HVAC, or any fragmented-supplier vertical.

**Live demo (dental example):** https://sourceclub-poc.streamlit.app/

---

## What's inside

```
app/
  main.py                       Streamlit UI — four tabs
  engine/
    matcher.py                  3-stage matching engine + UOM/pack-size normalizer
    adapters/
      benco.py                  Per-supplier parser (dental example)
      henry_schein.py
      darby.py
      base86.py
      patterson.py              Handles messy real-world export
      auto_detect.py            Supplier auto-detection
  sync/                         Mock Stripe ↔ HubSpot billing rollup (multi-location example)
sample_data/
  *_catalog.csv                 Reference catalog (negotiated prices)
  *_<supplier>.csv              Sample supplier exports
ADAPTING.md                     ← Read this to adapt to your vertical
CONTRIBUTING.md                 How to contribute (new adapters, verticals, fixes)
case-study/                     Original SourceClub case-study deliverables
```

## The architecture

```
Upload → Auto-detect supplier → Adapter (per-supplier parser) → Canonical schema
   ↓
3-Stage Matching Engine (per line item):
   Stage 1: Deterministic   — exact SKU / manufacturer SKU lookup
   Stage 2: Semantic         — fuzzy description + token-overlap retrieval
   Stage 3: LLM Judge        — adjudicates candidates, generates rationale
   Cross-cut: UOM / Pack-size normalizer — "box vs case" detection
   ↓
Confidence router:
   ≥ 0.85 → Auto-accept   → Savings report
   0.60-0.85 → Review queue (human approval)
   UOM mismatch → Force review
   < 0.60 → No-match bucket (catalog gap)
```

The **3 stages exist because the failure modes are different.** Stage 1 catches the easy 30–40% (clean SKU matches) at zero LLM cost. Stage 2 narrows the candidate space. Stage 3 is where reasoning happens (UOM normalization, manufacturer disambiguation).

The **UOM / pack-size normalizer** is the actual hard problem. "Box of 100" vs "case of 10 boxes" matters more than fuzzy description scoring — the unit-economics math breaks otherwise. This is its own concern in the architecture and runs cross-cut to the 3 stages.

---

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/abhinaykrupa/vertical-procurement-toolkit.git
cd vertical-procurement-toolkit
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app/main.py
```

Opens at `http://localhost:8501`. Pick any sample file from the dropdown to see the pipeline run end-to-end.

---

## Adapt it to your vertical

The bundled example is dental supply (Benco, Henry Schein, Darby, Base86, Patterson). To run it against vet supply (Patterson Vet, Covetrus, MWI), HVAC (Ferguson, Carrier, Trane), restaurant supply (Sysco, US Foods, PFG), or any other vertical:

**Read [ADAPTING.md](./ADAPTING.md).** It's a ~10-minute walkthrough covering:

1. Swap the catalog CSV
2. Add a supplier adapter (template provided — look at [`app/engine/adapters/benco.py`](./app/engine/adapters/benco.py))
3. Tweak the UOM regex table for your industry's vocabulary
4. Register the new adapter in `auto_detect.py`

That's it. Same engine, new vertical.

---

## Tech choices and why

| Choice | Why |
|---|---|
| **Streamlit** | Fastest path to a runnable demo. Pure Python. Anyone can install and run in 2 minutes. |
| **Plotly** | Looks like a real product. Works inside Streamlit with zero config. |
| **reportlab** | Pure Python, no system deps. Generates real branded PDFs. |
| **Pandas only for matching** | No vector DB needed for the POC. Deterministic + fuzzy + token-overlap gets 70–85% match rate on representative data. |
| **Mocked LLM** | Demo runs offline, zero setup. Architecture is API-ready — swap one function. Production prompt sketch is in the code. |
| **MIT License** | Build on it freely. Fork it. Ship it. |

---

## Production-readiness gaps (intentionally out of POC scope)

The repo is a runnable reference architecture, not production code. For a production deployment, you'd need:

- Real vector store (pgvector + sentence-transformers) replacing fuzzy matching in Stage 2
- Real LLM API calls (Claude Haiku / GPT-4o-mini) for Stage 3
- Authentication, multi-tenant isolation, audit log per matching decision
- Background job queue for batch ingestion
- Persistent review queue with state (POC buttons are illustrative)
- Catalog versioning so historical reports remain reproducible

[PRODUCTION_ARCHITECTURE.md](./PRODUCTION_ARCHITECTURE.md) covers the full production stack — vendor picks, cost model, build path.

---

## Contributing

This repo is meant to grow. The fastest contributions:

- **Add a supplier adapter** for your vertical (vet, HVAC, restaurant, auto, etc.)
- **Add a sample export file** + catalog for a new vertical
- **Improve the UOM normalizer** for your industry's pack-size vocabulary
- **Wire in a real LLM call** for Stage 3 behind a feature flag

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the process. Open issues are tagged `good first issue` if you want a starter task.

---

## Original context

This repo started as a case-study deliverable for the Head of AI Powered Operations role at **SourceClub** (a dental GPO). The original case-study docs are preserved in [`case-study/`](./case-study/) — they're a useful read if you want to see how the architecture was justified to a business audience:

- [`case-study/SUBMISSION.md`](./case-study/SUBMISSION.md) — full written deliverable
- [`case-study/STRATEGIC_ADDENDUM.md`](./case-study/STRATEGIC_ADDENDUM.md) — six-quarter growth thesis
- [`case-study/VIDEO_SCRIPT.md`](./case-study/VIDEO_SCRIPT.md) — 3–5 min demo walkthrough script
- [`case-study/SUBMISSION_EMAIL.md`](./case-study/SUBMISSION_EMAIL.md) — recruiter email
- [`case-study/assignments.md`](./case-study/assignments.md) — original case-study brief

---

## License

[MIT](./LICENSE) — build on it freely.
