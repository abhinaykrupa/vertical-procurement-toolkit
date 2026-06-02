"""
Sysco purchase-history parser (restaurant / foodservice vertical).

Sysco is the largest US foodservice distributor. Their exports are notoriously
inconsistent — this adapter handles the common shape:
- 5-line header block (customer info)
- SUPC = Sysco Product Code (their internal SKU)
- "Pack Size" combines pack count + unit (e.g. "6/#10 CAN", "40 LB CS", "4/1 GAL")
- Prices and totals are $-prefixed; totals have thousands commas wrapped in quotes
- UPPERCASE descriptions

The "Pack Size" column is preserved as uom_raw so the UOM normalizer can
parse foodservice conventions (#10 can, 5 gal pail, etc.).
"""

import io

import pandas as pd


COLUMN_MAP = {
    "SUPC": "supplier_sku",
    "Item Description": "raw_description",
    "Brand": "manufacturer_name",
    "Mfr Item": "manufacturer_sku",
    "Cases": "quantity",
    "Price/Case": "unit_price",
    "Total": "annual_spend",
    "Pack Size": "uom_raw",
}


def parse(file_bytes: bytes, filename: str) -> pd.DataFrame:
    raw = pd.read_csv(
        io.BytesIO(file_bytes),
        skiprows=5,
        skip_blank_lines=True,
    )
    raw = raw.dropna(subset=["SUPC"])
    raw = raw[raw["SUPC"].astype(str).str.startswith("SYS")]
    raw = raw.rename(columns=COLUMN_MAP)
    raw["supplier_name"] = "Sysco"
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
            if "Customer:" in line:
                return line.split("Customer:")[-1].strip()
        return "Unknown"
    except Exception:
        return "Unknown"


def _extract_period(file_bytes: bytes) -> str:
    try:
        for line in file_bytes.decode("utf-8", errors="ignore").split("\n")[:5]:
            if "Date Range" in line:
                return line.split(":", 1)[1].strip()
        return "Unknown"
    except Exception:
        return "Unknown"
