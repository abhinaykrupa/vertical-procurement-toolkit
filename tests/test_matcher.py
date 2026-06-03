"""
Matcher behavior tests — UOM extraction, pack-size detection, alignment.
"""

import pandas as pd
import pytest

from engine.matcher import (
    extract_pack_info,
    check_uom_alignment,
    classify_status,
    match_invoice,
)


@pytest.mark.parametrize("text,expected_pack,expected_uom", [
    ("Nitrile Gloves Med PF 100/bx", 100, "box"),
    ("Cotton Rolls 2000/case", 2000, "case"),
    ("Composite A2 4g Syringe", None, "syringe"),
    ("Box of 100 nitrile gloves", 100, "box"),
    ("Case of 2000 cotton", 2000, "case"),
    ("100 ct gauze", 100, None),
    ("Mystery item with no signal", None, None),
])
def test_extract_pack_info(text, expected_pack, expected_uom):
    info = extract_pack_info(text)
    assert info["pack_size"] == expected_pack, f"pack_size mismatch for {text!r}"
    if expected_uom is None:
        assert info["uom"] is None, f"expected no UOM for {text!r}, got {info['uom']!r}"
    else:
        assert info["uom"] == expected_uom, f"uom mismatch for {text!r}: got {info['uom']!r}"


def test_check_uom_alignment_aligned():
    prospect = pd.Series({"raw_description": "Nitrile Gloves Med PF 100/bx"})
    catalog = pd.Series({"unit_of_measure": "Box", "pack_size": 100})
    status, _ = check_uom_alignment(prospect, catalog)
    assert status == "aligned"


def test_check_uom_alignment_mismatch_pack():
    prospect = pd.Series({"raw_description": "Nitrile Gloves Med PF 100/bx"})
    catalog = pd.Series({"unit_of_measure": "Box", "pack_size": 200})
    status, note = check_uom_alignment(prospect, catalog)
    assert status == "mismatch"
    assert "Pack size differs" in note


def test_check_uom_alignment_mismatch_uom():
    prospect = pd.Series({"raw_description": "Cotton Rolls 2000/case"})
    catalog = pd.Series({"unit_of_measure": "Box", "pack_size": 2000})
    status, note = check_uom_alignment(prospect, catalog)
    assert status == "mismatch"
    assert "UOM differs" in note


def test_check_uom_alignment_unknown():
    prospect = pd.Series({"raw_description": "no signal here"})
    catalog = pd.Series({"unit_of_measure": "Box", "pack_size": 100})
    status, _ = check_uom_alignment(prospect, catalog)
    assert status == "unknown"


@pytest.mark.parametrize("confidence,spend,method,uom,expected", [
    (1.0, 100, "Deterministic", "aligned", "AUTO-ACCEPT"),
    (0.95, 100, "Semantic+Judge", "aligned", "AUTO-ACCEPT"),
    (0.95, 100, "Semantic+Judge", "mismatch", "FORCE-REVIEW"),
    (0.70, 1000, "Semantic+Judge", "aligned", "FORCE-REVIEW"),
    (0.70, 100, "Semantic+Judge", "aligned", "REVIEW-SUGGESTED"),
    (0.40, 100, "No Match", None, "NO-MATCH"),
])
def test_classify_status(confidence, spend, method, uom, expected):
    assert classify_status(confidence, spend, method, uom) == expected


def test_match_invoice_end_to_end(sample_dir, project_root):
    """Smoke test: parse one supplier file and run match_invoice end-to-end."""
    from engine.adapters import ADAPTERS

    catalog = pd.read_csv(sample_dir / "dental_catalog.csv")
    parse = ADAPTERS["Benco"]
    invoice = parse((sample_dir / "auburn_dental_benco.csv").read_bytes(), "auburn_dental_benco.csv")
    results = match_invoice(invoice, catalog)

    assert len(results) == len(invoice), "match_invoice should return one row per input line"
    expected_columns = {"status", "confidence", "match_method", "rationale", "sc_sku", "total_savings"}
    assert expected_columns.issubset(set(results.columns))
    assert results["status"].isin({"AUTO-ACCEPT", "REVIEW-SUGGESTED", "FORCE-REVIEW", "NO-MATCH"}).all()
