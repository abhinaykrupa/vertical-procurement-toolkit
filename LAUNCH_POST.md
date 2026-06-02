# Launch post — LinkedIn / Medium

Two versions: a shorter LinkedIn-native post, and a longer Medium / blog version. Pick one. Both link back to the repo.

---

## Version 1 — LinkedIn (650 words)

**Title options (pick one):**
- I open-sourced a procurement intelligence engine that started life as a dental GPO case study
- The architecture pattern behind vertical procurement: from a dental case study to an open-source toolkit
- Built a savings-analysis engine for an interview. Open-sourced it because the same architecture works for vet, HVAC, restaurant, auto.

---

I just open-sourced something I built for a job interview.

The role was Head of AI Powered Operations at a dental Group Purchasing Organization. The case study asked me to design a system that automates "savings analysis" — taking a prospect's supplier purchase history, comparing each line against the GPO's negotiated catalog, and showing the prospect their potential savings.

What looks simple is actually three different problems stacked:

**1. Every supplier exports a different shape.** Benco, Henry Schein, Darby, Patterson, Base86 — each has its own CSV format, its own column names, its own quirks. Patterson's export has $-prefixed prices, embedded commas, blank rows, and footer rows that look like data. You can't match anything until you've normalized the input.

**2. The same product has different SKUs across distributors.** "Nitrile Gloves, Medium, Powder-Free" might be Benco #4471-203, Henry Schein #100-1234, Darby #DG-MED-N. The manufacturer SKU is the same when present, but it often isn't. Fuzzy description matching gets you 60% of the way, then breaks on edge cases.

**3. UOM and pack-size mismatches are the actual killer.** "Box of 100" vs "case of 10 boxes" looks like the same product but the unit economics differ by 10x. This is the single most-called-out failure mode when you talk to people who do this work manually.

The architecture I landed on:

→ **Per-supplier adapters** — one Python module per distributor format, all producing the same canonical schema. This isolates "real-world chaos" from "matching logic."

→ **3-stage matching engine.** Stage 1 (deterministic SKU match) catches 30-40% at zero LLM cost. Stage 2 (semantic retrieval) narrows the candidate space. Stage 3 (LLM judge) does the reasoning that actually requires a model. Three stages because the failure modes are different and each stage uses the right tool for its problem.

→ **UOM/pack-size normalizer as its own concern.** Cross-cuts all 3 stages. Regex tables + alias dictionaries that detect "box vs case" style mismatches and force human review even when other signals align.

→ **Confidence router** sending high-confidence matches to auto-accept, medium to a review queue, low to a no-match bucket that feeds catalog gap analysis.

The interview didn't end up working out. But while researching the broader market, I realized this exact problem exists in every fragmented-supplier vertical: veterinary (~30K clinics), HVAC (~120K contractors), independent restaurants, auto repair (~160K shops), independent pharmacy, optometry.

Most of those verticals already have a vendor-funded incumbent — Vetcove in vet, PartsTech in auto, PSAOs in pharmacy. But **HVAC and independent restaurants have no Vetcove-equivalent**. And in every vertical, contractors / clinics / shops are still doing this analysis by hand or not at all.

So I extracted the engine, generalized it, and put it under MIT license:

🔗 **https://github.com/abhinaykrupa/vertical-procurement-toolkit**

What's there:
- Working Streamlit app with 5 dental supplier adapters
- The 3-stage matcher + UOM normalizer (the actual reusable IP)
- An ADAPTING.md that walks through how to swap in your vertical in ~30 minutes
- A live demo: https://sourceclub-poc.streamlit.app/
- Open issues tagged "good first issue" for the next adapters: Vetcove, Sysco, Ferguson HVAC

If you work in procurement, vertical SaaS, or just want to see a clean reference architecture for invoice matching with LLMs — take a look.

If you're in a fragmented-supplier vertical and want to fork it for your industry, even better. Open an issue and I'll help.

#OpenSource #VerticalSaaS #Procurement #AI #LLM

---

## Version 2 — Medium / blog (1,400 words)

**Title:** What I learned building a procurement intelligence engine for a dental GPO interview — and why I open-sourced it after they passed

---

Three months ago I started preparing for an interview at a small dental Group Purchasing Organization (GPO). The role was Head of AI Powered Operations, Systems & RevOps — a player-coach position at a 7-person company growing through what the CEO called "hockey-stick" growth.

The case study had three assignments. The headline one was: automate the savings analysis.

### What "savings analysis" actually means

When a dental practice is considering joining a GPO, the GPO runs a "savings analysis." They take the practice's purchase history — a CSV export of everything they buy from their current supplier — and compare each line against the GPO's negotiated pricing catalog. The output is a report showing the practice their potential savings.

This is the close. At this GPO, 90% of practices who see their numbers join. The savings analysis isn't a step toward the close — it *is* the close.

The catch: the founder did this by hand. About 10 minutes per analysis, 20-40 times a month. The case study asked me to design how I'd automate it.

### Why the matching problem is harder than it looks

The naive approach — VLOOKUP the prospect's SKUs against the GPO catalog — fails immediately. Here's why:

**Supplier exports are bespoke.** Every distributor has their own format. Benco's CSV has 3 header rows and SKUs prefixed with "BEN". Henry Schein's report has a totally different column structure. Patterson's export — which I built a deliberately messy sample of — has $-prefixed prices, embedded commas, blank rows, and footer rows that look like real data. Before you can match anything, you have to parse five different shapes into one.

**The same physical product has different SKUs across distributors.** A box of nitrile gloves might be Benco #4471-203, Henry Schein #100-1234, Darby #DG-MED-N. When the manufacturer SKU is present, you can match on that — but often it's missing, abbreviated, or wrong.

**Pack-size and unit-of-measure mismatches break the economics.** "Box of 100" vs "case of 10 boxes" looks like the same product if you're just comparing descriptions. But the unit price differs by 10x. This was the single most-called-out failure mode when I watched videos of the founder doing this work manually.

### The architecture

After two days of prototyping and tearing up two versions, I landed on this shape:

```
Upload → Auto-detect supplier → Per-supplier adapter → Canonical schema
   ↓
3-stage matching engine (per line item):
   Stage 1: Deterministic   — exact SKU / mfg SKU lookup
   Stage 2: Semantic         — fuzzy description + token overlap retrieval
   Stage 3: LLM judge        — adjudicates candidates, generates rationale
   Cross-cut: UOM/pack-size normalizer
   ↓
Confidence router:
   ≥ 0.85 → Auto-accept   → Savings report
   0.60-0.85 → Review queue (human approval)
   UOM mismatch → Force review
   < 0.60 → No-match bucket (catalog gap analysis)
```

**Three observations on why this shape works:**

1. **Three stages, not one.** Stage 1 catches the easy 30-40% of line items (clean SKU matches) at zero LLM cost. Stage 2 narrows the candidate space — having an LLM judge 500 catalog items per line is wasteful and noisy. Stage 3 is where actual reasoning happens. Each stage uses the right tool for its problem.

2. **Adapters before matching, not embedded in matching.** This is the biggest lesson from real-world supplier data: you cannot do matching and parsing in the same pass. Separating them means adding a new supplier is a 40-line module, not a refactor of the matcher.

3. **UOM normalization is its own concern.** It cross-cuts the 3 stages and runs as a parallel check. UOM mismatches force review even when description and manufacturer align — because the unit economics math breaks.

### The interview didn't work out

I built the POC. Shipped it as a Streamlit app you can drive end-to-end. Wrote a 27-page submission doc covering the architecture, a Stripe-HubSpot multi-location sync proposal for assignment 2, and a 90-day roadmap for assignment 3 — with 10 new project proposals sized in dollars.

I interviewed with their VP of Growth. Wrote a 4-page strategic addendum the night before about how I'd position SourceClub against Synergy (the dominant dental GPO) and Alara (the YC-backed challenger). Did the prep, did the call.

A week later, the recruiter passed. No specific feedback. My guess: comp expectations.

### Why I open-sourced it

While researching the broader market for the interview prep, I realized something. This exact problem — fragmented suppliers, inconsistent SKUs, UOM chaos, manual savings analysis — exists in every vertical I looked at:

- **Veterinary** (~30K clinics) — Vetcove already solved it, owns the vertical
- **Auto repair** (~160K shops) — PartsTech already solved it, 30K+ shops adopted
- **Independent pharmacy** (~25K) — PSAOs already solved it, 89% coverage
- **Independent restaurants** — Dining Alliance exists but coverage uncertain
- **HVAC** (~120K contractors) — **no equivalent identified**

Three verticals captured. Two open. And in every vertical, the small shops not on a platform are still doing the analysis by hand or not at all.

The architecture I built for dental isn't dental-specific. The catalog graph, the 3-stage matcher, the UOM normalizer — they work for any fragmented-supplier vertical. The only vertical-specific pieces are (a) the catalog file and (b) the supplier adapters.

So I extracted the engine, generalized the docs, and put it under MIT license.

🔗 **https://github.com/abhinaykrupa/vertical-procurement-toolkit**

### What's in the repo

- A working Streamlit app you can run locally in 2 minutes (`pip install -r requirements.txt` + `streamlit run app/main.py`)
- 5 dental supplier adapters as worked examples
- The 3-stage matching engine + UOM normalizer — the actual reusable IP
- An ADAPTING.md walkthrough for swapping in your own vertical (~30 min for a basic adapter)
- A CONTRIBUTING.md explaining the contribution process
- "Good first issue" entry points for the next adapters: Vetcove, Sysco, Ferguson HVAC, generic-CSV
- Production-architecture doc covering the swap-in points: pgvector for Stage 2, real LLM calls for Stage 3, etc.
- The original SourceClub case-study deliverables in `case-study/` if you want to see how the architecture was justified to a business audience

### Who this is for

- **Vertical SaaS founders** building procurement tools for vet, HVAC, restaurant, auto, or any other fragmented-supplier industry — fork it, ship faster
- **GPO operators** in non-dental verticals who want a starting point for their own savings analysis tooling
- **Engineers** who want a clean reference architecture for invoice matching with LLM augmentation
- **Anyone interviewing for procurement / RevOps / vertical SaaS roles** who wants to see a worked example

### Where it goes from here

Honestly, I'm not sure. I'm not planning to build a company around this. But I'd love to see other contributors add adapters for their verticals, and I'm happy to maintain the core architecture and review PRs.

If you build something on top of it, I want to hear about it.

If you fork it for your vertical and it works, open a PR with the adapter so the next person doesn't have to do it from scratch.

If you're in HVAC or independent restaurants and want to do something interesting with this, reach out.

🔗 **https://github.com/abhinaykrupa/vertical-procurement-toolkit**
🔗 **Live demo:** https://sourceclub-poc.streamlit.app/

---

## Posting checklist

- [ ] Push repo to GitHub first (so links work when post goes live)
- [ ] Add a hero screenshot to README before posting (Patterson messy file → matched results, or Leadership Dashboard)
- [ ] Post on LinkedIn (Version 1)
- [ ] Cross-post on Medium / personal blog (Version 2)
- [ ] Cross-post to HackerNews? Risky — they'll either love it or eat you alive on the OSS-without-clear-moat angle. Skip unless you have thick skin.
- [ ] Cross-post to relevant subreddits: r/programming (Version 1), r/Python (Version 1), r/smallbusiness (link only with a 1-line summary), r/dentistry (if you want to test the dental community)
- [ ] Submit to Indie Hackers as a "milestone"
