#!/usr/bin/env python3
"""
Benchmark the matcher across all bundled verticals.

Runs every sample supplier file through the pipeline and prints an honest
match-rate table per vertical. Run from the project root:

    python scripts/benchmark.py

This is intentionally transparent — it reports the real numbers the engine
produces on the bundled samples, including where matching is weaker (no-match
buckets are a feature, not a hidden failure).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "app"))
sys.path.insert(0, str(PROJECT_ROOT))

from engine.adapters import ADAPTERS, ADAPTER_VERTICAL, auto_detect  # noqa: E402
from engine.matcher import match_invoice  # noqa: E402

SAMPLE_DIR = PROJECT_ROOT / "sample_data"

# (sample_file, catalog_file)
CASES = [
    ("auburn_dental_benco.csv", "dental_catalog.csv"),
    ("demit_dental_henry_schein.csv", "dental_catalog.csv"),
    ("quincy_smiles_darby.csv", "dental_catalog.csv"),
    ("auburn_dental_base86.csv", "dental_catalog.csv"),
    ("harbor_view_patterson_messy.csv", "dental_catalog.csv"),
    ("auburn_dental_henry_schein.csv", "dental_catalog.csv"),
    ("sample_clinic_vetcove.csv", "vet_catalog.csv"),
    ("comfort_pro_ferguson.csv", "hvac_catalog.csv"),
    ("bistro_24_sysco.csv", "restaurant_catalog.csv"),
    ("clearview_optical_vsp.csv", "optometry_catalog.csv"),
]


def run() -> int:
    rows = []
    for sample_file, catalog_file in CASES:
        sample_path = SAMPLE_DIR / sample_file
        catalog_path = SAMPLE_DIR / catalog_file
        if not sample_path.exists() or not catalog_path.exists():
            continue

        file_bytes = sample_path.read_bytes()
        adapter_name = auto_detect.detect(file_bytes, sample_file)
        if adapter_name == "Unknown":
            rows.append({"file": sample_file, "adapter": "UNKNOWN", "lines": 0})
            continue

        invoice = ADAPTERS[adapter_name](file_bytes, sample_file)
        catalog = pd.read_csv(catalog_path)
        results = match_invoice(invoice, catalog)

        n = len(results)
        auto = (results["status"] == "AUTO-ACCEPT").sum()
        review = results["status"].isin(["REVIEW-SUGGESTED", "FORCE-REVIEW"]).sum()
        nomatch = (results["status"] == "NO-MATCH").sum()
        savings = results["total_savings"].fillna(0).sum()
        spend = results["annual_spend"].sum()

        rows.append({
            "vertical": ADAPTER_VERTICAL.get(adapter_name, "?"),
            "adapter": adapter_name,
            "lines": n,
            "auto%": f"{auto / n * 100:.0f}%" if n else "-",
            "review%": f"{review / n * 100:.0f}%" if n else "-",
            "nomatch%": f"{nomatch / n * 100:.0f}%" if n else "-",
            "spend": f"${spend:,.0f}",
            "savings": f"${savings:,.0f}",
            "savings%": f"{savings / spend * 100:.1f}%" if spend else "-",
        })

    df = pd.DataFrame(rows)
    print("\nMatch-rate benchmark across bundled samples")
    print("=" * 92)
    print(df.to_string(index=False))
    print("=" * 92)
    print("\nNotes:")
    print("- auto% = auto-accepted (high confidence or exact SKU match)")
    print("- review% = routed to human review (medium confidence, high-dollar, or UOM mismatch)")
    print("- nomatch% = no catalog equivalent found (feeds catalog-gap analysis — a feature)")
    print("- These are the real numbers on the bundled samples. Your data will vary.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
