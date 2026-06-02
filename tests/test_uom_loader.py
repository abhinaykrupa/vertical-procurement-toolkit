"""
Tests for the per-vertical UOM table loader.
"""

import pytest

from vpt.uom import load_uom_table, list_available


def test_dental_uom_table_loads():
    table = load_uom_table("dental")
    assert "aliases" in table
    assert "stopwords" in table
    # Dental vocab sanity
    assert table["aliases"]["bx"] == "box"
    assert table["aliases"]["carp"] == "cartridge"  # dental anesthetic carpule
    assert "dental" in table["stopwords"]


def test_vet_uom_table_includes_pharma_vocab():
    table = load_uom_table("vet")
    assert table["aliases"]["ml"] == "ml"
    assert table["aliases"]["vial"] == "vial"
    assert table["aliases"]["dose"] == "dose"


def test_hvac_uom_table_includes_weight_volume_length():
    table = load_uom_table("hvac")
    assert table["aliases"]["lb"] == "lb"
    assert table["aliases"]["gallon"] == "gallon"
    assert table["aliases"]["ft"] == "ft"


def test_restaurant_uom_table_includes_foodservice_vocab():
    table = load_uom_table("restaurant")
    assert table["aliases"]["pail"] == "pail"
    assert table["aliases"]["bushel"] == "bushel"


def test_list_available_returns_known_verticals():
    available = list_available()
    for vertical in ("dental", "vet", "hvac", "restaurant"):
        assert vertical in available, f"{vertical} should be available"


def test_unknown_vertical_raises():
    with pytest.raises(FileNotFoundError):
        load_uom_table("not-a-real-vertical")
