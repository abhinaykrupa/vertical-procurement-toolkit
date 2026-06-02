"""
VSP / Essilor order-history parser (optometry vertical).

VSP and Essilor are dominant in US optometry distribution (contacts, lenses,
frames, coatings, solutions). Their order export has a 5-line header block.

Optometry-specific quirks:
- Mixed UOM: contacts by box-pack (6/box, 90/box), lenses by pair, frames by each
- Custom service lines with no mfg code → route to no-match
- Quoted-comma totals
"""

import io

import pandas as pd


COLUMN_MAP = {
    "Product Code": "supplier_sku",
    "Product Description": "raw_description",
    "Brand": "manufacturer_name",
    "Mfr Code": "manufacturer_sku",
    "Units": "quantity",
    "Unit Cost": "unit_price",
    "Total Cost": "annual_spend",
    "Pack": "uom_raw",
}


def parse(file_bytes: bytes, filename: str) -> pd.DataFrame:
    raw = pd.read_csv(
        io.BytesIO(file_bytes),
        skiprows=5,
        skip_blank_lines=True,
    )
    raw = raw.dropna(subset=["Product Code"])
    raw = raw[raw["Product Code"].astype(str).str.startswith("VSP")]
    raw = raw.rename(columns=COLUMN_MAP)
    raw["supplier_name"] = "VSP/Essilor"
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
            if "Practice:" in line:
                return line.split("Practice:")[-1].strip()
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
