"""
Ferguson HVAC Supply purchase-history parser (HVAC vertical).

Ferguson is one of the largest US distributors of HVAC, plumbing, and
industrial supplies. Their export has a 5-line header block.

HVAC-specific quirks this adapter handles:
- Refrigerant sold by cylinder weight (25lb, 10lb, 30lb)
- "Misc Shop Supplies Bundle" line with no mfg SKU — passes through to no-match
- $-prefixed prices with commas
"""

import io

import pandas as pd


COLUMN_MAP = {
    "Item #": "supplier_sku",
    "Description": "raw_description",
    "Mfr": "manufacturer_name",
    "Mfr Part": "manufacturer_sku",
    "Qty": "quantity",
    "Unit Price": "unit_price",
    "Ext Price": "annual_spend",
    "UOM": "uom_raw",
}


def parse(file_bytes: bytes, filename: str) -> pd.DataFrame:
    raw = pd.read_csv(
        io.BytesIO(file_bytes),
        skiprows=5,
        skip_blank_lines=True,
    )
    raw = raw.dropna(subset=["Item #"])
    raw = raw[raw["Item #"].astype(str).str.startswith("FRG")]
    raw = raw.rename(columns=COLUMN_MAP)
    raw["supplier_name"] = "Ferguson"
    raw["customer_name"] = _extract_customer(file_bytes)
    raw["report_period"] = _extract_period(file_bytes)
    keep = list(COLUMN_MAP.values()) + ["supplier_name", "customer_name", "report_period"]
    raw = raw[[c for c in keep if c in raw.columns]]

    for col in ("quantity", "unit_price", "annual_spend"):
        if col in raw.columns:
            raw[col] = pd.to_numeric(
                raw[col].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.strip(),
                errors="coerce",
            ).fillna(0)

    return raw.reset_index(drop=True)


def _extract_customer(file_bytes: bytes) -> str:
    try:
        for line in file_bytes.decode("utf-8", errors="ignore").split("\n")[:5]:
            if "Account:" in line and "#" not in line:
                return line.split("Account:")[-1].strip()
        return "Unknown"
    except Exception:
        return "Unknown"


def _extract_period(file_bytes: bytes) -> str:
    try:
        for line in file_bytes.decode("utf-8", errors="ignore").split("\n")[:5]:
            if "Period" in line:
                return line.split(":", 1)[1].strip()
        return "Unknown"
    except Exception:
        return "Unknown"
