"""
Multi-supplier comparison — the "shop across distributors" feature.

Given the same vertical's purchase history from multiple distributors,
find which distributor is cheapest for each catalog item. This is the
value prop single-vendor buying clubs structurally can't offer.

Usage:
    from vpt.compare import compare_suppliers

    results = compare_suppliers(
        supplier_files=[("Benco", benco_bytes, "benco.csv"),
                        ("Henry Schein", hs_bytes, "hs.csv")],
        catalog=catalog_df,
    )
    # results: per-catalog-SKU, the cheapest supplier and the spread

CLI:
    vpt compare -s file1.csv file2.csv file3.csv -c catalog.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_APP_DIR = _PROJECT_ROOT / "app"
if _APP_DIR.exists() and str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from engine.matcher import match_invoice  # noqa: E402


def compare_suppliers(
    supplier_files: list[tuple[str, bytes, str]],
    catalog: pd.DataFrame,
    adapters: dict | None = None,
) -> pd.DataFrame:
    """
    Compare prices for the same catalog items across multiple suppliers.

    supplier_files: list of (adapter_name, file_bytes, filename)
    catalog: reference catalog DataFrame
    adapters: optional adapter registry override (defaults to engine.adapters.ADAPTERS)

    Returns a DataFrame indexed by catalog SKU with columns:
      - sc_description
      - <supplier>_price for each supplier (NaN if they don't carry it)
      - cheapest_supplier
      - cheapest_price
      - price_spread       (max - min across suppliers carrying the item)
      - potential_savings  (spread × quantity, if you always bought cheapest)
    """
    if adapters is None:
        from engine.adapters import ADAPTERS as adapters

    per_supplier_matches = {}
    for adapter_name, file_bytes, filename in supplier_files:
        parse = adapters[adapter_name]
        invoice = parse(file_bytes, filename)
        matched = match_invoice(invoice, catalog)
        # Keep only rows that matched a catalog SKU
        matched = matched[matched["sc_sku"].notna()].copy()
        per_supplier_matches[adapter_name] = matched

    # Build a per-SKU price table
    rows = {}
    for supplier, matched in per_supplier_matches.items():
        for _, r in matched.iterrows():
            sku = r["sc_sku"]
            if sku not in rows:
                rows[sku] = {
                    "sc_sku": sku,
                    "sc_description": r.get("sc_description", ""),
                    "_quantities": {},
                }
            rows[sku][f"{supplier}_price"] = r["current_unit_price"]
            rows[sku]["_quantities"][supplier] = r.get("quantity", 0)

    out_rows = []
    for sku, data in rows.items():
        price_cols = {k: v for k, v in data.items() if k.endswith("_price") and pd.notna(v) and v > 0}
        if not price_cols:
            continue
        cheapest_supplier = min(price_cols, key=price_cols.get).replace("_price", "")
        cheapest_price = price_cols[min(price_cols, key=price_cols.get)]
        max_price = max(price_cols.values())
        spread = max_price - cheapest_price
        # Savings if you bought the highest-priced supplier's volume at the cheapest price
        total_qty = sum(data["_quantities"].values())
        potential_savings = spread * total_qty if len(price_cols) > 1 else 0.0

        row = {
            "sc_sku": sku,
            "sc_description": data["sc_description"],
            "cheapest_supplier": cheapest_supplier,
            "cheapest_price": round(cheapest_price, 2),
            "price_spread": round(spread, 2),
            "suppliers_carrying": len(price_cols),
            "potential_savings": round(potential_savings, 2),
        }
        for k, v in price_cols.items():
            row[k] = round(v, 2)
        out_rows.append(row)

    if not out_rows:
        return pd.DataFrame()

    df = pd.DataFrame(out_rows)
    return df.sort_values("price_spread", ascending=False).reset_index(drop=True)


def comparison_summary(comparison_df: pd.DataFrame) -> dict:
    """Roll up a comparison into headline numbers."""
    if comparison_df.empty:
        return {"items_compared": 0, "multi_supplier_items": 0, "total_potential_savings": 0.0}
    multi = comparison_df[comparison_df["suppliers_carrying"] > 1]
    return {
        "items_compared": int(len(comparison_df)),
        "multi_supplier_items": int(len(multi)),
        "total_potential_savings": float(comparison_df["potential_savings"].sum()),
        "biggest_spread_item": (
            comparison_df.iloc[0]["sc_description"] if len(comparison_df) else None
        ),
        "biggest_spread": float(comparison_df.iloc[0]["price_spread"]) if len(comparison_df) else 0.0,
    }
