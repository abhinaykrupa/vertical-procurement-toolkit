"""
Tests for the multi-supplier comparison feature.
"""

import pandas as pd

from vpt.compare import compare_suppliers, comparison_summary


def test_compare_finds_overlapping_items(sample_dir):
    from engine.adapters import ADAPTERS

    catalog = pd.read_csv(sample_dir / "sourceclub_catalog.csv")
    supplier_files = [
        ("Benco", (sample_dir / "auburn_dental_benco.csv").read_bytes(), "benco.csv"),
        ("Henry Schein", (sample_dir / "auburn_dental_henry_schein.csv").read_bytes(), "hs.csv"),
    ]
    result = compare_suppliers(supplier_files, catalog, adapters=ADAPTERS)

    assert not result.empty
    # Some items should be carried by both suppliers
    multi = result[result["suppliers_carrying"] > 1]
    assert len(multi) > 0, "expected overlapping items across the two suppliers"

    # Required columns present
    for col in ("sc_sku", "cheapest_supplier", "cheapest_price", "price_spread", "potential_savings"):
        assert col in result.columns

    # Spread is non-negative and cheapest_price > 0
    assert (result["price_spread"] >= 0).all()
    assert (result["cheapest_price"] > 0).all()


def test_compare_summary_rollup(sample_dir):
    from engine.adapters import ADAPTERS

    catalog = pd.read_csv(sample_dir / "sourceclub_catalog.csv")
    supplier_files = [
        ("Benco", (sample_dir / "auburn_dental_benco.csv").read_bytes(), "benco.csv"),
        ("Henry Schein", (sample_dir / "auburn_dental_henry_schein.csv").read_bytes(), "hs.csv"),
    ]
    result = compare_suppliers(supplier_files, catalog, adapters=ADAPTERS)
    summary = comparison_summary(result)

    assert summary["items_compared"] > 0
    assert summary["multi_supplier_items"] > 0
    assert summary["total_potential_savings"] > 0


def test_compare_empty_when_no_overlap():
    summary = comparison_summary(pd.DataFrame())
    assert summary["items_compared"] == 0
    assert summary["total_potential_savings"] == 0.0
