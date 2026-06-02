"""
Generic CSV adapter — works on any CSV given a column mapping.

Unlocks ANY supplier export without writing a dedicated adapter, at the cost of
the caller having to specify which columns mean what. Useful for one-offs,
quick experiments, or unknown verticals.

Usage:
    from vpt.generic_adapter import parse_generic

    column_map = {
        "supplier_sku": "ItemNumber",
        "raw_description": "ProductName",
        "manufacturer_name": "Brand",
        "manufacturer_sku": "MfgPart",
        "quantity": "Qty",
        "unit_price": "Price",
        "annual_spend": "ExtPrice",
    }
    df = parse_generic(file_bytes, "any.csv", column_map=column_map,
                       supplier_name="MyVendor", customer_name="Acme Co")

If a target column is missing from the source, the adapter:
- Auto-computes annual_spend from quantity * unit_price when missing
- Defaults missing manufacturer fields to empty string
- Errors only when supplier_sku / raw_description / unit_price are all absent
"""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd


REQUIRED_AT_LEAST_ONE = ["supplier_sku", "raw_description"]
CANONICAL_COLUMNS = [
    "supplier_sku",
    "raw_description",
    "manufacturer_name",
    "manufacturer_sku",
    "quantity",
    "unit_price",
    "annual_spend",
]


def parse_generic(
    file_bytes: bytes,
    filename: str,
    column_map: dict[str, str],
    supplier_name: str = "Unknown",
    customer_name: str = "Unknown",
    report_period: str = "Unknown",
    skiprows: int = 0,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """
    Parse an arbitrary CSV using a caller-provided column mapping.

    column_map keys are CANONICAL field names (supplier_sku, raw_description, etc.).
    column_map values are the actual column names in the source CSV.

    Returns a DataFrame in the canonical schema the matcher expects.
    """
    raw = pd.read_csv(io.BytesIO(file_bytes), skiprows=skiprows, encoding=encoding, skip_blank_lines=True)
    raw.columns = [str(c).strip() for c in raw.columns]

    # Build inverse mapping: source col → canonical col
    rename = {src: canon for canon, src in column_map.items() if src in raw.columns}
    out = raw.rename(columns=rename)

    # Verify we have at least one key field
    if not any(col in out.columns for col in REQUIRED_AT_LEAST_ONE):
        raise ValueError(
            f"Generic adapter requires at least one of {REQUIRED_AT_LEAST_ONE}. "
            f"Got columns: {list(out.columns)}. "
            f"Provided mapping: {column_map}"
        )

    # Keep only canonical columns we have
    keep = [c for c in CANONICAL_COLUMNS if c in out.columns]
    out = out[keep].copy()

    # Drop rows where supplier_sku is missing AND raw_description is missing
    if "supplier_sku" in out.columns and "raw_description" in out.columns:
        out = out.dropna(subset=["supplier_sku", "raw_description"], how="all")
    elif "supplier_sku" in out.columns:
        out = out.dropna(subset=["supplier_sku"])
    elif "raw_description" in out.columns:
        out = out.dropna(subset=["raw_description"])

    # Numeric cleanup
    for col in ("quantity", "unit_price", "annual_spend"):
        if col in out.columns:
            out[col] = _to_numeric(out[col])

    # Compute annual_spend if missing
    if "annual_spend" not in out.columns and "quantity" in out.columns and "unit_price" in out.columns:
        out["annual_spend"] = out["quantity"] * out["unit_price"]

    # Fill missing optional fields
    for col in ("manufacturer_name", "manufacturer_sku"):
        if col not in out.columns:
            out[col] = ""

    # Metadata
    out["supplier_name"] = supplier_name
    out["customer_name"] = customer_name
    out["report_period"] = report_period

    return out.reset_index(drop=True)


def _to_numeric(series: pd.Series) -> pd.Series:
    """Strip $ and commas, coerce to numeric, fill NaN with 0."""
    cleaned = (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)


def suggest_column_map(file_bytes: bytes, filename: str, encoding: str = "utf-8") -> dict[str, list[str]]:
    """
    Best-effort heuristic mapping suggestion — for the UI / interactive use.
    Returns dict mapping each canonical field to a ranked list of plausible source columns.
    """
    raw = pd.read_csv(io.BytesIO(file_bytes), nrows=5, encoding=encoding, skip_blank_lines=True)
    cols = [str(c).strip() for c in raw.columns]

    suggestions: dict[str, list[str]] = {c: [] for c in CANONICAL_COLUMNS}
    hints = {
        "supplier_sku": ["item", "sku", "part", "product", "code", "number", "id"],
        "raw_description": ["desc", "name", "product", "item name", "title"],
        "manufacturer_name": ["manufacturer", "mfg", "mfr", "brand", "vendor", "make"],
        "manufacturer_sku": ["mfg sku", "mfr sku", "mpn", "mfg part", "manufacturer part"],
        "quantity": ["qty", "quantity", "ordered", "count"],
        "unit_price": ["unit price", "price", "rate", "cost", "each"],
        "annual_spend": ["extended", "total", "ext", "spend", "amount", "subtotal"],
    }
    for canonical, keywords in hints.items():
        for col in cols:
            col_l = col.lower()
            if any(kw in col_l for kw in keywords):
                suggestions[canonical].append(col)
    return suggestions
