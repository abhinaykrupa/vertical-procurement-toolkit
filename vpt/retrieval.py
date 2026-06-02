"""
Optional embedding-based Stage-2 retrieval.

The default matcher (engine.matcher.stage2_candidates) uses difflib + token
overlap — zero dependencies, runs everywhere, ~good enough for clean catalogs.
For messier catalogs, real sentence embeddings retrieve better candidates.

This module provides a drop-in replacement that uses sentence-transformers
when installed and configured, and falls back to the default otherwise — so
the offline, zero-dep demo never breaks.

Enable with:
    export STAGE2_RETRIEVAL=embeddings
    pip install sentence-transformers

Usage:
    from vpt.retrieval import make_stage2
    import engine.matcher
    engine.matcher.stage2_candidates = make_stage2(catalog)

The embedding model is loaded once and the catalog is embedded once, then
queried per line item — same shape as a production pgvector setup, just
in-memory.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_APP_DIR = _PROJECT_ROOT / "app"
if _APP_DIR.exists() and str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def make_stage2(catalog: pd.DataFrame, top_k: int = 5):
    """
    Return a stage2_candidates(row, catalog, top_k) compatible function.

    If STAGE2_RETRIEVAL=embeddings and sentence-transformers is available,
    returns an embedding-backed retriever. Otherwise returns the default
    difflib-based one (imported lazily to avoid circular import).
    """
    mode = os.environ.get("STAGE2_RETRIEVAL", "default").lower()

    if mode != "embeddings":
        from engine.matcher import stage2_candidates as _default
        return _default

    try:
        from sentence_transformers import SentenceTransformer, util
    except ImportError:
        # Graceful fallback — keep the demo working
        from engine.matcher import stage2_candidates as _default
        return _default

    model_name = os.environ.get("STAGE2_MODEL", DEFAULT_MODEL)
    model = SentenceTransformer(model_name)

    descriptions = catalog["description"].astype(str).tolist()
    catalog_embeddings = model.encode(descriptions, convert_to_tensor=True, normalize_embeddings=True)
    catalog_rows = [row for _, row in catalog.iterrows()]

    def stage2_embeddings(row, _catalog=None, k: int = top_k):
        query = str(row.get("raw_description", ""))
        if not query.strip():
            return []
        q_emb = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
        scores = util.cos_sim(q_emb, catalog_embeddings)[0]
        top = scores.topk(min(k, len(catalog_rows)))
        out = []
        for score, idx in zip(top.values.tolist(), top.indices.tolist()):
            out.append((float(score), catalog_rows[idx]))
        return out

    return stage2_embeddings


def is_embeddings_available() -> bool:
    """True if embedding retrieval can actually run (deps installed)."""
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False
