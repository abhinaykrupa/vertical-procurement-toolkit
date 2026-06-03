# Project Memory — vertical-procurement-toolkit

## Key URLs
- **Live Streamlit demo:** https://vertical-procurement-toolkit.streamlit.app/
- **GitHub repo:** https://github.com/abhinaykrupa/vertical-procurement-toolkit
- **Local path:** /Users/ag/vertical-procurement-toolkit

## Project state (as of 2026-06-03)
- **13 commits on main**, all pushed, CI green (Python 3.10/3.11/3.12)
- **60 tests passing**, ruff clean, pre-commit configured
- **5 working verticals:** dental, vet (Vetcove), HVAC (Ferguson), restaurant (Sysco), optometry (VSP/Essilor)
- **9 supplier adapters** + generic CSV adapter
- **Fully debranded** — no SourceClub references remain in the UI or app code

## What's built
| Layer | Detail |
|---|---|
| `vpt/` package | CLI (analyze, compare, validate, detect), Python API |
| `app/main.py` | Streamlit UI — 4 tabs (Dashboard, Savings Analysis, Billing Sync Demo, GPO Roadmap Example) |
| `app/engine/` | 3-stage matcher + UOM normalizer + per-vertical YAML tables |
| `app/engine/adapters/` | Benco, Henry Schein, Darby, Base86, Patterson, Vetcove, Ferguson, Sysco, VSP/Essilor, auto_detect |
| `app/sync/` | Generic GPO mock data (Apex Practice Group, Meridian Partners, etc.) — NOT dental-specific |
| `sample_data/` | dental_catalog.csv (renamed from sourceclub_catalog.csv), vet/hvac/restaurant/optometry catalogs + sample exports |

## Key decisions made this session
- Renamed `sourceclub_catalog.csv` → `dental_catalog.csv` everywhere (code, tests, scripts)
- Mock billing data (mock_data.py, pipeline_data.py) replaced with generic GPO member names
- Tab labels updated: "Stripe ↔ HubSpot Sync" → "Billing Sync Demo", "90-Day Roadmap" → "GPO Roadmap Example"
- Context banners added to Tab 2 + Tab 3 explaining demo context
- PDF generator now shows supplier name in header (not "SourceClub")
- Email drafter sign-off removed SourceClub branding

## What's left for user to do (browser/accounts)
- Add a real Streamlit screenshot to README (hero SVG is placeholder)
- Pin repo on GitHub profile
- Enable GitHub Discussions (Settings → Features)
- Post LinkedIn + Show HN drafts from LAUNCH_POST.md

## Catalog filename note
The dental catalog is `sample_data/dental_catalog.csv` — this is the same data as the old `sourceclub_catalog.csv`, just renamed. The file still exists under both names temporarily (the old one not yet deleted from git history).
