"""
Adapter smoke tests — verify each adapter parses its sample file
into the canonical schema without errors.

Pattern for contributors: when you add a new adapter, add a row to
ADAPTER_CASES and the rest works automatically.
"""

from pathlib import Path

import pandas as pd
import pytest

from engine.adapters import ADAPTERS


CANONICAL_REQUIRED_COLUMNS = {
    "supplier_sku",
    "raw_description",
    "quantity",
    "unit_price",
    "supplier_name",
    "customer_name",
}


# (adapter_name, sample_filename, min_expected_rows)
ADAPTER_CASES = [
    ("Benco", "auburn_dental_benco.csv", 5),
    ("Henry Schein", "demit_dental_henry_schein.csv", 5),
    ("Darby", "quincy_smiles_darby.csv", 5),
    ("Base86", "auburn_dental_base86.csv", 5),
    ("Patterson", "harbor_view_patterson_messy.csv", 5),
    ("Vetcove", "sample_clinic_vetcove.csv", 10),
    ("Ferguson", "comfort_pro_ferguson.csv", 25),
    ("Sysco", "bistro_24_sysco.csv", 25),
    ("VSP/Essilor", "clearview_optical_vsp.csv", 25),
]


@pytest.mark.parametrize("adapter_name,sample_file,min_rows", ADAPTER_CASES)
def test_adapter_parses_sample(sample_dir: Path, adapter_name: str, sample_file: str, min_rows: int):
    """Each adapter should parse its sample file into a non-empty DataFrame
    with the canonical required columns present and numeric where expected."""
    path = sample_dir / sample_file
    assert path.exists(), f"Sample file missing: {path}"

    parse = ADAPTERS[adapter_name]
    file_bytes = path.read_bytes()
    df = parse(file_bytes, sample_file)

    assert isinstance(df, pd.DataFrame), f"{adapter_name} did not return a DataFrame"
    assert len(df) >= min_rows, f"{adapter_name} returned {len(df)} rows, expected >= {min_rows}"

    missing = CANONICAL_REQUIRED_COLUMNS - set(df.columns)
    assert not missing, f"{adapter_name} missing canonical columns: {missing}"

    assert pd.api.types.is_numeric_dtype(df["quantity"]), f"{adapter_name} quantity not numeric"
    assert pd.api.types.is_numeric_dtype(df["unit_price"]), f"{adapter_name} unit_price not numeric"

    # No row should have a totally empty supplier_sku AND raw_description
    sku_or_desc = df["supplier_sku"].astype(str).str.strip().ne("") | df["raw_description"].astype(str).str.strip().ne("")
    assert sku_or_desc.all(), f"{adapter_name} produced rows with empty sku AND description"


def test_adapters_registry_contains_known():
    """The adapter registry should contain all four verticals' adapters."""
    expected = {"Benco", "Henry Schein", "Darby", "Base86", "Patterson", "Vetcove", "Ferguson", "Sysco", "VSP/Essilor"}
    assert expected.issubset(set(ADAPTERS.keys())), f"Missing adapters: {expected - set(ADAPTERS.keys())}"


def test_adapter_vertical_mapping_complete():
    """Every adapter should map to a known vertical (so UOM tables auto-load)."""
    from engine.adapters import ADAPTER_VERTICAL
    for name in ADAPTERS:
        assert name in ADAPTER_VERTICAL, f"{name} missing from ADAPTER_VERTICAL"
    assert set(ADAPTER_VERTICAL.values()) <= {"dental", "vet", "hvac", "restaurant", "optometry"}


@pytest.mark.parametrize("supplier_file,catalog_file,vertical", [
    ("comfort_pro_ferguson.csv", "hvac_catalog.csv", "hvac"),
    ("bistro_24_sysco.csv", "restaurant_catalog.csv", "restaurant"),
    ("sample_clinic_vetcove.csv", "vet_catalog.csv", "vet"),
    ("auburn_dental_benco.csv", "sourceclub_catalog.csv", "dental"),
    ("clearview_optical_vsp.csv", "optometry_catalog.csv", "optometry"),
])
def test_vertical_end_to_end_produces_savings(sample_dir: Path, supplier_file, catalog_file, vertical):
    """Each vertical should parse + match + find some savings (proves generalization)."""
    from engine.matcher import match_invoice
    from engine.adapters import auto_detect

    file_bytes = (sample_dir / supplier_file).read_bytes()
    adapter_name = auto_detect.detect(file_bytes, supplier_file)
    assert adapter_name != "Unknown", f"auto-detect failed for {supplier_file}"

    invoice = ADAPTERS[adapter_name](file_bytes, supplier_file)
    catalog = pd.read_csv(sample_dir / catalog_file)
    results = match_invoice(invoice, catalog)

    assert len(results) == len(invoice)
    # At least half the lines should match (these samples are built to match the catalog)
    matched = results["sc_sku"].notna().sum()
    assert matched >= len(results) * 0.5, f"{vertical}: only {matched}/{len(results)} matched"
    total_savings = results["total_savings"].fillna(0).sum()
    assert total_savings > 0, f"{vertical}: no savings found"
