# Launch posts — ready to publish

All drafts below link to **https://github.com/abhinaykrupa/vertical-procurement-toolkit**.
Nothing here is posted automatically — pick what fits and publish when you're ready.

**Before posting:** add a real Streamlit screenshot to the README (the hero SVG works, but a product screenshot converts better), and pin the repo on your GitHub profile.

---

## 1. LinkedIn (≈600 words)

**Title options:**
- I built a procurement engine for a dental GPO interview. They passed. I open-sourced it — and it works for 4 industries now.
- The architecture pattern behind vertical procurement, open-sourced
- From one dental case study to a 4-vertical open-source toolkit

---

I built a savings-analysis engine for a job interview. The role didn't work out. So I open-sourced the work — and over the last few nights generalized it so it now runs on four different industries with zero changes to the core engine.

**The problem it solves:** small businesses — dental practices, vet clinics, HVAC contractors, independent restaurants — buy from 3-7 different distributors. Every distributor uses different SKUs, different descriptions, different pack sizes, different units of measure. Nobody has time to compare line-by-line whether they're overpaying. So they overpay.

The hard part isn't the comparison. It's the matching. "Box of 100 nitrile gloves" at one distributor and "Nitrile Exam PF MD 100/bx" at another are the same product — a human knows that instantly, software has to be taught.

**The architecture:**

→ **Per-supplier adapters** turn each distributor's bespoke export into one canonical schema. Real exports are chaos — $-prefixed prices, embedded commas, footer rows, mixed UOM formats. Isolate that mess in the adapter, keep the matcher clean.

→ **3-stage matcher.** Stage 1 (exact SKU match) catches the easy 30-40% at zero LLM cost. Stage 2 (semantic retrieval) narrows candidates. Stage 3 (LLM judge — Claude or GPT, with a mock fallback) does the reasoning. Each stage uses the right tool for its failure mode.

→ **UOM/pack-size normalizer** runs cross-cut to all three. "Box of 100" vs "case of 10 boxes" looks identical on description but the unit economics differ 10x. This is the single most important check, and it forces human review on mismatch even when everything else aligns.

→ **Confidence router** sends high-confidence matches to auto-accept, medium to a review queue, low to a no-match bucket that doubles as catalog-gap analysis.

**The part I'm proud of:** it actually generalizes. Same engine, four verticals, all shipping with working examples and real numbers:

- 🦷 Dental — 5 supplier adapters
- 🐾 Vet (Vetcove) — $1.9K savings found on a $14K sample
- 🔧 HVAC (Ferguson) — $10.4K on $65K, plus it correctly flagged 1 catalog gap
- 🍽️ Restaurant (Sysco) — $8.2K on $75K, handling foodservice pack-size chaos

Adding a vertical is ~30 minutes: a catalog CSV, a ~40-line adapter, a UOM vocabulary file. There's a guide.

It's MIT licensed, has a CLI, a Python API, a generic CSV adapter for unknown formats, 50 tests, CI on Python 3.10-3.12, and "good first issue" tickets for the next adapters (more HVAC brands, US Foods, auto parts, pharmacy).

🔗 https://github.com/abhinaykrupa/vertical-procurement-toolkit

If you work in procurement, vertical SaaS, or run a business that buys from multiple distributors — take a look. If you want to fork it for your industry, even better. Open an issue and I'll help.

#OpenSource #VerticalSaaS #Procurement #AI #Python

---

## 2. Show HN

**Title:** Show HN: Open-source supplier-invoice savings analysis (dental, vet, HVAC, restaurant)

**URL:** https://github.com/abhinaykrupa/vertical-procurement-toolkit

**Text (first comment):**

I built this for a dental Group Purchasing Organization job interview — the task was to automate "savings analysis": take a prospect's supplier purchase history, match each line against a negotiated-price catalog, show them what they'd save. The role didn't pan out, so I generalized the work and open-sourced it.

The interesting problem is matching. The same physical product has different SKUs, descriptions, and pack sizes across distributors. A box of gloves is "BEN-4471 Nitrile PF MD 100/bx" at one and "Nitrile Exam Gloves Powder-Free Medium" at another. Fuzzy string matching gets you ~60% and then breaks on unit-of-measure mismatches — "box of 100" vs "case of 10 boxes" looks like the same item but the economics differ 10x.

The approach is a 3-stage pipeline: (1) deterministic SKU match for the easy ~30-40% at zero LLM cost, (2) fuzzy/semantic retrieval to narrow candidates, (3) an LLM judge (Claude/GPT, with a rule-based mock fallback so it runs offline) for the ambiguous ones. A UOM/pack-size normalizer runs cross-cut and forces human review on mismatch regardless of confidence.

What I think is interesting for HN: it genuinely generalizes across verticals. Same matcher, zero changes, four working examples — dental, vet (Vetcove exports), HVAC (Ferguson), restaurant (Sysco, including their delightful "6/#10 CAN" pack notation). Adding a vertical is a catalog CSV + a ~40-line adapter + a YAML UOM vocab file.

Stack is deliberately boring: pandas, a CLI, a Streamlit demo, optional real-LLM behind an env flag. MIT. 50 tests, CI on 3.10-3.12.

Happy to answer questions about the matching design, the UOM problem (which is the actual hard part), or where this does and doesn't generalize. Notably it does NOT make sense in verticals with standardized SKUs (pharma NDC, retail UPC) where stage-1 is trivial, or where one distributor has >80% share so there's nothing to compare.

**Notes on Show HN:**
- Post Tue-Thu, 8-10am ET for best visibility
- Be present in comments for the first 2 hours — HN rewards engagement
- Expect pushback on "why not just use [X]" and "where's the moat" — lean into honest answers (it's a toolkit, not a business; the moat in a real product would be catalog data, not the code)

---

## 3. Reddit

### r/Python (focus: the engineering)

**Title:** I open-sourced a supplier-invoice matching engine — 3-stage matcher (deterministic → semantic → LLM judge) that generalizes across industries

**Body:**

Built originally for a dental procurement case study, generalized to four verticals (dental, vet, HVAC, restaurant). The core problem: match a messy supplier CSV against a price catalog when SKUs, descriptions, and pack sizes all differ across distributors.

Design highlights Pythonistas might find interesting:
- Per-supplier adapters (each ~40 lines) isolate real-world CSV chaos from matching logic
- 3-stage matcher: exact SKU → fuzzy/token retrieval → LLM judge (Claude/GPT behind an env flag, mock fallback so it runs with just `pip install pandas`)
- UOM/pack-size normalizer with per-vertical YAML vocabularies
- Clean `vpt` package + CLI + Streamlit demo
- 50 tests, CI on 3.10-3.12, ruff, pre-commit

MIT licensed, "good first issue" tickets open for new adapters.

🔗 https://github.com/abhinaykrupa/vertical-procurement-toolkit

Feedback on the architecture welcome — especially the stage-2 retrieval, which currently uses difflib + token overlap and is the obvious place to swap in real embeddings.

### r/smallbusiness (focus: the use case — link sparingly, lead with value)

**Title:** If you buy supplies from multiple distributors, you're probably overpaying on items you can't easily compare — built a free tool for this

**Body:**

If your business orders from 3+ suppliers (think dental, vet, HVAC, restaurant, auto), you've probably had the nagging feeling you're overpaying somewhere but never had time to compare every line item across every distributor. The problem is that the same product is listed differently everywhere — different codes, different pack sizes — so a simple spreadsheet comparison doesn't work.

I built a free, open-source tool that does the matching automatically: upload your purchase history, it compares against a price catalog and shows you where you're overpaying. It's currently set up with examples for dental, vet, HVAC, and restaurant supply.

Full disclosure: it's a developer tool right now (you run it locally), not a polished consumer app — but it's free, and if there's interest I'm happy to make it more accessible. Mostly sharing because the "you're overpaying and can't easily see it" problem is so common.

🔗 https://github.com/abhinaykrupa/vertical-procurement-toolkit (GitHub)

Would genuinely like to hear: which suppliers do you use, and would a simple "upload invoice, see savings" tool be useful to you?

**Notes on Reddit:**
- r/Python and r/programming are safe to link directly
- r/smallbusiness, r/restaurateur, r/HVAC, r/Dentistry are stricter on self-promo — read each sub's rules, lead with value, and don't drop the same text in multiple subs the same day (looks like spam)
- The vertical subs (r/HVAC, r/restaurateur) are higher-value but higher-risk — consider posting as a question/discussion rather than a launch

---

## 4. Indie Hackers / Dev.to (optional)

Cross-post the Medium long-form version (below) as a Dev.to article with tags `#opensource #python #ai`. On Indie Hackers, post as a "milestone" with the short LinkedIn version. Both are low-effort cross-posts once the Medium piece exists.

---

## Posting checklist

- [ ] Add a real Streamlit screenshot to README (replaces or supplements the hero SVG)
- [ ] Pin the repo on your GitHub profile
- [ ] Enable GitHub Discussions (Settings → Features) — issue templates already route questions there
- [ ] Post LinkedIn version
- [ ] Post Show HN (Tue-Thu morning ET, be present for comments)
- [ ] Post r/Python
- [ ] Cross-post Medium long-form (see git history / earlier draft if you want the 1,400-word version)
- [ ] Optional: r/smallbusiness, vertical subs, Dev.to, Indie Hackers
