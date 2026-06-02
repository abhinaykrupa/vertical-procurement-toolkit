# Overnight handoff — vertical-procurement-toolkit

**Date:** 2026-06-02 (built overnight while you slept)
**Repo:** https://github.com/abhinaykrupa/vertical-procurement-toolkit
**CI:** green on Python 3.10 / 3.11 / 3.12
**Tests:** 60 passing
**Local path:** `/Users/ag/vertical-procurement-toolkit` (separate from `/Users/ag/sourceclub`, fully independent)

> This file is for you (Abhi). It summarizes everything done overnight, the current state, and what's left that I couldn't do without you (browser, posting, account settings). Delete it from the repo whenever you like — it's a personal handoff, not project docs.

---

## TL;DR — what happened overnight

You asked me to turn the SourceClub case-study POC into a genuinely useful open-source toolkit while you slept. I did. It went from "a dental Streamlit demo" to **a 5-vertical, pip-installable, tested, CI-backed open-source procurement toolkit** with a CLI, a Python API, real-LLM and real-embedding options, and a multi-supplier price-comparison feature.

11 commits, all green. Nothing is half-finished — every commit passed lint + 60 tests + CI before push.

---

## What's in the repo now

### Five working verticals (was: one)

| Vertical | Adapter | Sample result |
|---|---|---|
| 🦷 Dental | Benco, Henry Schein, Darby, Base86, Patterson | up to 94% auto-accept |
| 🐾 Vet | Vetcove | 30 lines, $1.9K savings |
| 🔧 HVAC | Ferguson | 30 lines, $10.4K savings |
| 🍽️ Restaurant | Sysco | 30 lines, $8.2K savings |
| 👓 Optometry | VSP/Essilor | 30 lines, $12.3K savings |

Each = a catalog CSV + adapter + sample export + UOM table. Run `python scripts/benchmark.py` to see the full match-rate table.

### New capabilities (was: Streamlit demo only)

| Capability | How to use |
|---|---|
| **CLI** | `python -m vpt.cli analyze -s file.csv -c catalog.csv --pretty` |
| **Python API** | `from vpt import match_invoice, get_adapter, load_catalog` |
| **Generic adapter** | Any CSV via `--adapter generic --map supplier_sku=Col ...` |
| **Multi-supplier compare** | `vpt compare -s f1.csv f2.csv -c catalog.csv` → cheapest per item |
| **Catalog validation** | `vpt validate -c catalog.csv` |
| **Real LLM Stage 3** | `export LLM_JUDGE_PROVIDER=anthropic` (mock fallback) |
| **Real embeddings Stage 2** | `export STAGE2_RETRIEVAL=embeddings` (difflib fallback) |
| **Auto UOM loading** | Correct vertical vocabulary loads from the detected adapter |

### OSS hygiene (was: just a LICENSE)

- `pyproject.toml` (pip-installable, `[streamlit] [llm] [embeddings] [dev]` extras)
- 60 tests, GitHub Actions CI on 3.10/3.11/3.12, ruff lint, pre-commit config
- SECURITY.md, ROADMAP.md, CHANGELOG.md
- PR template + 3 issue templates (bug / feature / new-adapter)
- examples/quickstart.md, case-study/README.md
- Mermaid architecture diagram + custom hero SVG in README
- Honest match-rate benchmark table in README

### GitHub issues

- 8 "good first issue" tickets created
- 6 closed (the work shipped: CLI, generic adapter, LLM judge, tests, UOM YAML, HVAC, restaurant)
- 1 still open (#1 Vetcove — left open for standalone Patterson Vet/Covetrus/MWI follow-ups)

---

## What's LEFT — needs you (I can't do these)

These all require a browser, your accounts, or your judgment:

| Task | Why I couldn't | Effort |
|---|---|---|
| **Real Streamlit screenshot** in README | Needs a browser to capture the live app | 5 min — screenshot https://sourceclub-poc.streamlit.app, save to `docs/`, edit README image |
| **Pin the repo** on your GitHub profile | UI-only action | 30 sec |
| **Enable GitHub Discussions** | Repo settings | 1 min — Settings → Features → Discussions (issue templates already route to it) |
| **Publish launch posts** | Your voice, your accounts | see `LAUNCH_POST.md` — LinkedIn + Show HN + Reddit drafts all ready |
| **Decide: deploy the toolkit's own demo?** | The live demo still points at the old SourceClub Streamlit. You may want a fresh deploy reflecting the 5-vertical version. | 10 min on Streamlit Cloud |

---

## Recommended next moves (my opinion, unfiltered)

1. **Screenshot + pin first.** Cheapest credibility wins. A repo with a screenshot and a pin looks 10x more legit than one without.
2. **Post the LinkedIn version, not Show HN, first.** Lower risk, warms up the repo with some stars before HN's harsher crowd sees it. Show HN second, once you have a few stars and the screenshot.
3. **Don't over-invest further until you see signal.** The repo is now genuinely good. Whether to keep building depends on whether anyone engages. If the LinkedIn post gets traction or someone opens a PR, lean in. If it's crickets after a week, it's still a strong portfolio piece — leave it.
4. **It's a portfolio asset regardless.** Even with zero stars, "I open-sourced a 5-vertical procurement engine with a CLI, tests, and CI, generalized from a real case study" is a strong line in any RevOps / applied-AI / vertical-SaaS interview. The repo *is* the proof.

---

## Honest assessment

**What's genuinely good:** the architecture is clean, it actually generalizes (5 verticals prove it, not just claims), the code is tested and CI-backed, and the docs are thorough. Someone landing cold can run it in 60 seconds and contribute in an afternoon. That's rare for a solo project.

**What's still weak / honest caveats:**
- Stage-2 default retrieval (difflib) is mediocre — that's why I added the embeddings option, but it's off by default.
- The sample data is fabricated (realistic, but not real supplier exports). Real exports will surface edge cases the adapters don't handle yet.
- No real users yet. Everything is "this works on bundled samples." Real-world validation is unproven.
- The market research (from earlier) said OSS-first procurement tooling has weak demand signal. This is a great portfolio piece and a fine toolkit, but it's **not validated as a business**. Don't quit your job for it.

**Bottom line:** you woke up to a real, polished, working open-source project where last night you had a single-purpose demo. It's worth showing people. It's not yet worth betting the farm on. Both things are true.

---

## Quick reference — run it yourself

```bash
cd /Users/ag/vertical-procurement-toolkit
python3.10 -m venv .venv && .venv/bin/pip install pandas PyYAML pytest ruff

# Tests
.venv/bin/python -m pytest tests/ -q

# Benchmark across all 5 verticals
.venv/bin/python scripts/benchmark.py

# Try the CLI
.venv/bin/python -m vpt.cli analyze -s sample_data/clearview_optical_vsp.csv -c sample_data/optometry_catalog.csv --pretty

# Multi-supplier compare
.venv/bin/python -m vpt.cli compare -s sample_data/auburn_dental_benco.csv sample_data/auburn_dental_henry_schein.csv -c sample_data/sourceclub_catalog.csv
```
