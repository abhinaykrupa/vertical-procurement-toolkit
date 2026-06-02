# Roadmap

What's planned, what we'd accept PRs for, and what's explicitly out of scope.
Roadmap items are directional — order and priority can change based on demand.

## Now (v0.2 — June 2026)

Shipped:
- ✅ `vpt` Python package with public API
- ✅ CLI (`vpt analyze`, `vpt detect`, `vpt adapters`)
- ✅ Generic CSV adapter (no per-supplier code needed)
- ✅ Real LLM-backed Stage 3 (Anthropic + OpenAI) with mock fallback
- ✅ Per-vertical UOM tables (YAML) — dental, vet, HVAC, restaurant, auto-loaded per adapter
- ✅ **Four working vertical examples** — dental, vet (Vetcove), HVAC (Ferguson), restaurant (Sysco)
- ✅ `vpt validate` command for catalog QA
- ✅ Pytest suite (50 tests) + GitHub Actions CI (Py 3.10/3.11/3.12) + ruff + pre-commit
- ✅ Standard OSS hygiene — pyproject.toml, SECURITY.md, PR/issue templates, CHANGELOG, ROADMAP

## Next (v0.3 — community-driven)

Highest-leverage adds. Each is a "good first issue" if you want to grab it.

### More verticals — by demand
- HVAC adapter (Ferguson HVAC, Carrier, Trane) + sample catalog — see [#3](https://github.com/abhinaykrupa/vertical-procurement-toolkit/issues/3)
- Restaurant adapter (Sysco, US Foods, PFG) + sample catalog — see [#2](https://github.com/abhinaykrupa/vertical-procurement-toolkit/issues/2)
- Auto repair (NAPA, AutoZone Commercial, O'Reilly Pro, WorldPac)
- Independent pharmacy (McKesson, Cardinal, Cencora)
- Optometry (VSP, Essilor, Hoya)

### Matcher quality
- Real vector retrieval for Stage 2 (sentence-transformers + FAISS or pgvector)
  — replaces the current fuzzy + token-overlap approach
- Reviewer feedback loop — approve/reject decisions become labeled training pairs
- Catalog versioning so historical analyses remain reproducible

### Production hardening
- Auth + multi-tenant isolation for the Streamlit app
- Persistent review queue (Postgres / Supabase)
- Background job queue for batch ingestion (Celery / RQ)
- Stripe webhook handler + idempotent processing (currently mocked)
- HubSpot API writer (currently mocked)

### Developer experience
- Pre-commit hooks (ruff + black + pytest)
- More descriptive error messages from adapters
- A `vpt validate` CLI command for checking catalog files
- Sphinx/mkdocs site

## Later (v0.4+)

Bigger bets. PRs welcome but discuss in an issue first.

- **Confidence model** — train a per-vertical classifier on reviewer decisions, replacing the hard 0.85/0.60 thresholds with learned ones
- **Synonym memory** — manufacturer aliases, brand-equivalence relationships built up from reviewer corrections (e.g. "Ansell == Microflex" learned)
- **Cross-supplier substitute recommender** — "this item is out at supplier A; here's the equivalent at supplier B at this price"
- **Reverse mode** — given a member's catalog, find which suppliers in the network have the best prices for each item
- **A vet-specific Streamlit example tab** demonstrating the vet vertical end-to-end (parallel to the existing dental Leadership Dashboard)

## Out of scope (won't be merged)

- Vertical-specific business logic baked into the matcher core — verticals stay in adapters + UOM tables, the matcher stays generic
- Heavyweight ML in the default path — large models go behind feature flags, the offline demo must keep working with `pip install pandas`
- Direct supplier API integrations (Benco, Schein, etc.) — those belong in downstream products, not this toolkit. The toolkit operates on **exports**, not live APIs.
- Anything that requires committing real customer data or proprietary supplier price files
- A SaaS product — this is a toolkit, not a hosted service. If you build a SaaS on top, that's your repo

## How to influence the roadmap

- Open a [feature request](https://github.com/abhinaykrupa/vertical-procurement-toolkit/issues/new?template=feature_request.yml) for a new direction
- Open a [new adapter request](https://github.com/abhinaykrupa/vertical-procurement-toolkit/issues/new?template=new_adapter.yml) for a specific supplier
- Send a PR — implementation moves things up the list faster than asking does

## Versioning

This project follows [Semantic Versioning](https://semver.org). Until v1.0:
- Breaking changes to the public Python API may happen in minor versions but will be documented in `CHANGELOG.md`
- New adapters and new verticals never count as breaking changes
- The CLI interface follows the same policy as the Python API
