---
title: I built a supplier invoice matching engine for a job interview. They passed. So I open-sourced it — and it now works for 5 industries.
published: false
description: An open-source 3-stage matching pipeline (deterministic → semantic → LLM judge) that catches overcharges in supplier invoices across dental, vet, HVAC, restaurant, and optometry verticals.
tags: opensource, python, ai, procurement
cover_image: https://raw.githubusercontent.com/abhinaykrupa/vertical-procurement-toolkit/main/docs/screenshots/demo-home.png
canonical_url: https://github.com/abhinaykrupa/vertical-procurement-toolkit
---

# I built a supplier invoice matching engine for a job interview. They passed. So I open-sourced it.

A few weeks ago I was working through a case study for a Head of AI Operations role at a dental Group Purchasing Organization. The core task: automate "savings analysis" — take a dental practice's supplier purchase history, match each line against a negotiated-price catalog, and surface where they're overpaying.

The role didn't work out. But the engineering problem turned out to be genuinely interesting, and the solution generalizes to basically any industry where small businesses buy from multiple distributors.

So I cleaned it up, removed all the company-specific branding, added 4 more verticals, and open-sourced it:

**[github.com/abhinaykrupa/vertical-procurement-toolkit](https://github.com/abhinaykrupa/vertical-procurement-toolkit)**

Here's what I built and why the architecture ended up the way it did.

---

## The actual problem: matching is hard

The surface problem is obvious: compare what a business paid against a catalog of negotiated prices.

The hard problem is **matching**. The same box of nitrile gloves is:

- `BEN-4471 Nitrile Exam PF MD 100/bx` at Benco
- `Nitrile Exam Gloves Powder-Free Medium` at Henry Schein
- `EXAM GLOVE NTRL MED PF 100PK` at Darby

Fuzzy string matching gets you ~60% and then breaks. The thing that kills you isn't descriptions — it's **unit-of-measure mismatches**.

"Box of 100" and "case of 10 boxes" look nearly identical by description but differ 10x in unit economics. Matching them without catching the pack-size difference gives you a wildly wrong savings calculation.

---

## The 3-stage architecture

After a few iterations I landed on a 3-stage pipeline:

### Stage 1: Deterministic (exact SKU / manufacturer SKU lookup)

Catches ~30–40% of lines at zero LLM cost. If the supplier exports a manufacturer SKU and the catalog has the same manufacturer SKU, it's a match — no ambiguity, no reasoning needed.

This is the stage most naive implementations skip, but it's the one that makes the economics work. You don't want to pay for LLM reasoning on lines where the answer is provably correct.

### Stage 2: Semantic retrieval (fuzzy + token overlap, top-K candidates)

For the lines Stage 1 misses, narrow the catalog down to the top 5 candidates using a combination of difflib sequence matching and token overlap scoring. The default uses no ML dependencies — pure Python, runs offline.

If you set `STAGE2_RETRIEVAL=embeddings`, it swaps in `sentence-transformers` (all-MiniLM-L6-v2) for better recall on messy descriptions. Falls back to difflib automatically if the package isn't installed.

### Stage 3: LLM judge (Claude / GPT-4o-mini, with mock fallback)

The remaining ~20–40% of lines need reasoning — manufacturer disambiguation, formulation matching, pack-size inference. This is where an LLM actually earns its cost.

The mock fallback uses rule-based logic so the demo runs fully offline. Set `LLM_JUDGE_PROVIDER=anthropic` (or `openai`) with the appropriate API key and Stage 3 becomes a real Claude Haiku or GPT-4o-mini call.

### UOM/pack-size normalizer (cross-cuts all 3 stages)

This runs on every line regardless of which stage matched it. The normalizer:

1. Extracts pack size and UOM from both the supplier line and the catalog entry
2. Normalizes to a common unit (all "box" variants → one canonical form per vertical)
3. Flags mismatches for forced human review, regardless of confidence score

This is the single most important check. It's also the part most heavily influenced by vertical — a "drum" in HVAC is a unit of refrigerant; a "drum" in restaurant supply is a 55-gallon oil container. So each vertical gets its own YAML vocabulary file.

### Confidence router

After the three stages, every line gets routed:

- **≥0.85 confidence + no UOM mismatch** → auto-accept → savings report
- **0.60–0.85** → review queue → human approval
- **UOM mismatch** → force review regardless of confidence
- **<0.60** → no-match bucket → catalog gap analysis

The review queue and no-match bucket are features, not failures. The no-match lines tell you what to add to the catalog. The review queue catches the cases where the model is uncertain and a human should decide.

---

## Per-supplier adapters: isolating the chaos

Real supplier exports are a mess. Here's a tiny sample of what the Patterson adapter has to handle:

```
"$1,234.56"    # dollar sign + comma in price field
"EXAM GLOVE, MEDIUM POWDER-FREE, 100/BX"   # description with commas
""             # blank rows between product groups
"Sub Total: $8,432.10"  # footer rows mixed with data
```

The adapter pattern isolates this per-supplier. Each adapter is ~40 lines:

```python
def parse(file_bytes: bytes, filename: str) -> pd.DataFrame:
    raw = pd.read_csv(io.BytesIO(file_bytes), skiprows=5)
    raw = raw.dropna(subset=["Item Number"])
    raw = raw.rename(columns=COLUMN_MAP)
    raw["unit_price"] = (
        raw["unit_price"].astype(str)
        .str.replace("$", "").str.replace(",", "").str.strip()
        .pipe(pd.to_numeric, errors="coerce").fillna(0)
    )
    return raw.reset_index(drop=True)
```

The matching engine never sees the raw chaos — it only ever sees the canonical schema.

---

## Five verticals, zero matcher changes

The claim I'm most proud of: the same matching engine runs across all five verticals with no changes. The vertical-specific parts are isolated to:

1. **The catalog CSV** — ~30 SKU reference catalog per vertical
2. **The adapter** — ~40 lines parsing that supplier's export format
3. **The UOM YAML** — vocabulary of pack-size synonyms and stop words

Here are the real numbers on the bundled samples:

| Vertical | Supplier | Lines | Auto-accept | Savings found |
|---|---|---|---|---|
| Dental | Benco | 34 | 94% | $5,119 (41% of spend) |
| Vet | Vetcove | 30 | 100% | $1,868 (13%) |
| HVAC | Ferguson | 30 | 97% | $10,411 (16%) |
| Restaurant | Sysco | 30 | 100% | $8,171 (11%) |
| Optometry | VSP/Essilor | 30 | 97% | $12,310 (12%) |

The variance is intentional. Files with clean manufacturer SKUs (Benco, Vetcove) auto-accept at 90–100%. Files with no mfg SKUs and messy formatting (Patterson dental) drop to 8% auto-accept and 44% no-match. Both are correct behavior — the system is calibrated to the data quality, not artificially inflated.

---

## Where it generalizes well — and where it doesn't

**Generalizes well:**
- Any vertical with 3+ distributors using different SKU schemes
- Any vertical where pack-size/UOM differences create matching pain
- Any vertical where savings analysis is itself a sales or audit artifact

**Doesn't generalize:**
- Verticals with standardized SKUs (pharma NDC, retail UPC) — Stage 1 trivially solves everything
- Verticals dominated by a single distributor (80%+ share) — nothing to compare
- Build-to-order or custom manufacturing — no stable catalog

---

## Try it

```bash
pip install pandas PyYAML
git clone https://github.com/abhinaykrupa/vertical-procurement-toolkit
cd vertical-procurement-toolkit

# Run the vet vertical end-to-end
python -m vpt.cli analyze \
  -s sample_data/sample_clinic_vetcove.csv \
  -c sample_data/vet_catalog.csv --pretty | head -40
```

Live Streamlit demo (all 5 verticals in the dropdown): https://vertical-procurement-toolkit.streamlit.app

---

The architecture isn't novel — it's a deliberate application of "use the cheapest tool that works for each failure mode." The interesting part is that it actually generalizes. If you're working in a fragmented-supplier vertical and want to adapt this, ADAPTING.md is a 30-minute walkthrough. Open an issue if you get stuck.

**GitHub:** https://github.com/abhinaykrupa/vertical-procurement-toolkit
