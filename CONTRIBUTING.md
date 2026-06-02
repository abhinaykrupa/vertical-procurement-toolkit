# Contributing

Thanks for considering a contribution. This project is designed to grow — every new supplier adapter and every new vertical example makes it more useful for the next person.

## Highest-value contributions

In rough priority order:

1. **New supplier adapter** for an existing vertical (dental, vet, HVAC, restaurant, etc.) — most impactful, see [ADAPTING.md](./ADAPTING.md) step 2.
2. **A new vertical example** — adapter(s) + sample data + a catalog. Makes the "this generalizes" claim concrete.
3. **UOM normalizer improvements** for your industry's vocabulary.
4. **Real LLM integration** behind a feature flag (Claude / OpenAI / local) for Stage 3.
5. **Vector retrieval** (pgvector + sentence-transformers) replacing the fuzzy match in Stage 2.
6. **Bug fixes, type hints, tests, docs.**

If you're not sure where to start, look for issues tagged `good first issue` or `help wanted`.

---

## Process

### For small changes (typo, docs fix, single adapter)

1. Fork
2. Branch
3. Commit
4. PR with a one-line description

### For larger changes (new vertical, architecture, new feature)

1. **Open an issue first** describing what you want to do and why
2. Wait for a maintainer thumbs-up (so you don't waste effort on something that won't be merged)
3. Branch from `main`
4. Implement with tests where reasonable
5. Update docs (README, ADAPTING.md) if the change affects how users adopt the toolkit
6. Open a PR linking the issue

---

## Code style

- Python 3.10+
- `black` for formatting
- Type hints on new functions where it adds clarity
- Keep adapters under ~100 lines — if your adapter needs more, the supplier export is probably worth splitting into a parsing helper + an adapter
- Match the style of existing code; don't refactor unrelated code in the same PR

---

## Testing

There's no full test suite yet (one of the open contributions). When you add a new adapter:

- Include at least one sample export file under `sample_data/`
- Verify the Streamlit UI loads it without errors
- Verify the 3-stage matcher produces sane output
- If you can, add a simple `tests/test_<adapter>.py` that parses the sample and asserts row count + key columns

---

## Adding a new supplier adapter — checklist

When you submit a PR for a new adapter, please include:

- [ ] `app/engine/adapters/<supplier>.py` — the adapter module
- [ ] `sample_data/<example_customer>_<supplier>.csv` — at least one sample export
- [ ] Updated `app/engine/adapters/auto_detect.py` with detection rules
- [ ] Updated `app/main.py` dispatch logic
- [ ] Updated README "Supplier adapters" table if one exists
- [ ] Note in PR description: which supplier, what vertical, what's unusual about the export format

---

## Adding a new vertical — checklist

A "new vertical" PR is more substantial. Please include:

- [ ] At least one supplier adapter (more is better)
- [ ] A catalog file (`sample_data/<vertical>_catalog.csv`) with realistic SKU coverage
- [ ] Sample export(s) for the supplier(s) you added
- [ ] A short `case-study/<vertical>.md` explaining the vertical's procurement landscape (top suppliers, typical pain points, GPO incumbents if any) — helps future contributors
- [ ] Updates to ADAPTING.md if your vertical revealed new edge cases

---

## What we won't merge

- PRs that ship real API keys or credentials
- PRs that add heavy dependencies (large ML models, paid services) to the core path — these go behind feature flags
- PRs that break the offline demo
- PRs that fork the architecture in ways that make the engine vertical-specific (the value of this toolkit is that it stays vertical-agnostic at the core)

---

## License

By contributing, you agree your contributions are licensed under [MIT](./LICENSE).

---

## Maintainer

Currently maintained by [@abhinaykrupa](https://github.com/abhinaykrupa). Open an issue or reach out via GitHub for questions.
