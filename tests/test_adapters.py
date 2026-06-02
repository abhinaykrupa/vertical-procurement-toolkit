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
    """The adapter registry should at minimum contain the dental + vet adapters."""
    expected = {"Benco", "Henry Schein", "Darby", "Base86", "Patterson", "Vetcove"}
    assert expected.issubset(set(ADAPTERS.keys())), f"Missing adapters: {expected - set(ADAPTERS.keys())}"
