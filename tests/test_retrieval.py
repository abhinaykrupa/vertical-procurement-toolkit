"""
Tests for the optional embedding-based Stage-2 retrieval.

These verify the graceful-fallback contract: with no env flag (or no
sentence-transformers installed) make_stage2 returns the default difflib
retriever, so the offline demo never breaks.
"""


import pandas as pd

from vpt.retrieval import make_stage2, is_embeddings_available


def _toy_catalog():
    return pd.DataFrame([
        {"sc_sku": "A-1", "description": "Nitrile Exam Gloves Medium", "unit_price": 7.0},
        {"sc_sku": "A-2", "description": "Latex Exam Gloves Large", "unit_price": 6.0},
        {"sc_sku": "A-3", "description": "Face Mask Level 3 Blue", "unit_price": 5.0},
    ])


def test_default_mode_returns_difflib_retriever(monkeypatch):
    monkeypatch.delenv("STAGE2_RETRIEVAL", raising=False)
    from engine.matcher import stage2_candidates as default_fn
    fn = make_stage2(_toy_catalog())
    assert fn is default_fn


def test_embeddings_mode_falls_back_when_unavailable(monkeypatch):
    """If embeddings requested but sentence-transformers absent, fall back cleanly."""
    monkeypatch.setenv("STAGE2_RETRIEVAL", "embeddings")
    fn = make_stage2(_toy_catalog())
    # Either it's the embedding fn (deps present) or the default fallback (deps absent).
    # Either way it must be callable and return candidates without error.
    row = pd.Series({"raw_description": "Nitrile Gloves Med"})
    result = fn(row, _toy_catalog(), 3)
    assert isinstance(result, list)
    assert len(result) <= 3
    if result:
        score, cat_row = result[0]
        assert isinstance(score, float)
        assert "sc_sku" in cat_row


def test_is_embeddings_available_returns_bool():
    assert isinstance(is_embeddings_available(), bool)
