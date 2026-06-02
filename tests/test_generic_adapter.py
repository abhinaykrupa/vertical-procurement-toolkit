"""
Tests for the generic CSV adapter — confirms it handles arbitrary column mappings,
missing columns, and computes annual_spend when absent.
"""

import pandas as pd

from vpt.generic_adapter import parse_generic, suggest_column_map


def _csv(rows: list[dict]) -> bytes:
    return pd.DataFrame(rows).to_csv(index=False).encode()


def test_generic_adapter_basic_mapping():
    file_bytes = _csv([
        {"ItemNum": "ABC-1", "Name": "Widget A", "Qty": 10, "Price": 5.50, "Ext": 55.00},
        {"ItemNum": "ABC-2", "Name": "Widget B", "Qty": 4, "Price": 12.00, "Ext": 48.00},
    ])
    df = parse_generic(
        file_bytes, "test.csv",
        column_map={
            "supplier_sku": "ItemNum",
            "raw_description": "Name",
            "quantity": "Qty",
            "unit_price": "Price",
            "annual_spend": "Ext",
        },
        supplier_name="TestVendor",
        customer_name="TestCo",
    )
    assert len(df) == 2
    assert list(df["supplier_sku"]) == ["ABC-1", "ABC-2"]
    assert df.loc[0, "quantity"] == 10
    assert df.loc[1, "unit_price"] == 12.00
    assert df["supplier_name"].iloc[0] == "TestVendor"


def test_generic_adapter_computes_annual_spend_when_missing():
    file_bytes = _csv([
        {"sku": "X-1", "desc": "Item", "qty": 4, "price": 25.00},
    ])
    df = parse_generic(
        file_bytes, "test.csv",
        column_map={
            "supplier_sku": "sku",
            "raw_description": "desc",
            "quantity": "qty",
            "unit_price": "price",
        },
    )
    assert df.loc[0, "annual_spend"] == 100.0


def test_generic_adapter_strips_dollar_signs_and_commas():
    file_bytes = _csv([
        {"sku": "X-1", "desc": "Item", "qty": "1,000", "price": "$2.50"},
    ])
    df = parse_generic(
        file_bytes, "test.csv",
        column_map={
            "supplier_sku": "sku",
            "raw_description": "desc",
            "quantity": "qty",
            "unit_price": "price",
        },
    )
    assert df.loc[0, "quantity"] == 1000
    assert df.loc[0, "unit_price"] == 2.50


def test_generic_adapter_raises_when_no_key_columns_mapped():
    file_bytes = _csv([{"foo": "1", "bar": "2"}])
    import pytest
    with pytest.raises(ValueError, match="at least one of"):
        parse_generic(file_bytes, "test.csv", column_map={"quantity": "foo"})


def test_suggest_column_map_finds_obvious_matches():
    file_bytes = _csv([
        {"Item Number": "X", "Product Name": "Y", "Quantity": 1, "Unit Price": 1.0},
    ])
    suggestions = suggest_column_map(file_bytes, "test.csv")
    assert "Item Number" in suggestions["supplier_sku"]
    assert "Product Name" in suggestions["raw_description"]
    assert "Quantity" in suggestions["quantity"]
    assert "Unit Price" in suggestions["unit_price"]
