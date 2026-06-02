"""
Vetcove order-history export parser (veterinary vertical).

Vetcove is the dominant procurement platform in US veterinary (15K+ clinics).
Its order-history export has a 3-line header block before the actual CSV.

Real-world Vetcove exports include orders from multiple distributors
(Patterson Vet, Covetrus, MWI). This adapter ingests all of them — the
'Vendor' field becomes context, not a parsing branch.
"""

import io

import pandas as pd


COLUMN_MAP = {
    "Item Number": "supplier_sku",
    "Item Description": "raw_description",
    "Manufacturer": "manufacturer_name",
    "Mfg Part #": "manufacturer_sku",
    "Qty Ordered": "quantity",
    "Unit Price": "unit_price",
    "Extended Total": "annual_spend",
    "UOM": "uom_raw",
    "Vendor": "distributor",
}


def parse(file_bytes: bytes, filename: str) -> pd.DataFrame:
    raw = pd.read_csv(
        io.BytesIO(file_bytes),
        skiprows=4,
        skip_blank_lines=True,
    )
    raw = raw.dropna(subset=["Item Number"])
    raw = raw.rename(columns=COLUMN_MAP)
    raw["supplier_name"] = "Vetcove"
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
        first_line = file_bytes.decode("utf-8", errors="ignore").split("\n", 1)[0]
        if "-" in first_line:
            parts = first_line.split("-")
            if len(parts) >= 2:
                return parts[1].strip()
        return "Unknown"
    except Exception:
        return "Unknown"


def _extract_period(file_bytes: bytes) -> str:
    try:
        head = file_bytes.decode("utf-8", errors="ignore").split("\n")[:4]
        for line in head:
            if "Period" in line:
                return line.split(":", 1)[1].strip()
        return "Unknown"
    except Exception:
        return "Unknown"
