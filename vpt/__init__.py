"""
Vertical Procurement Toolkit (vpt) — public API.

Import the engine, run a match programmatically, or use the CLI:

    from vpt import match_invoice, load_catalog, get_adapter
    df = get_adapter("Benco")(open("file.csv", "rb").read(), "file.csv")
    results = match_invoice(df, load_catalog("sample_data/sourceclub_catalog.csv"))

Or use the CLI:

    vpt analyze --supplier-file invoice.csv --catalog catalog.csv --output results.json
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make app/ importable as a sibling package so the existing engine works without refactor.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_APP_DIR = _PROJECT_ROOT / "app"
if _APP_DIR.exists() and str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from engine.matcher import match_invoice, check_uom_alignment, extract_pack_info  # noqa: E402
from engine.adapters import ADAPTERS  # noqa: E402
from engine.adapters import auto_detect  # noqa: E402

__version__ = "0.1.0"

__all__ = [
    "match_invoice",
    "check_uom_alignment",
    "extract_pack_info",
    "load_catalog",
    "get_adapter",
    "ADAPTERS",
    "auto_detect",
    "__version__",
]


def load_catalog(path: str | Path):
    """Load a reference catalog CSV into a DataFrame."""
    import pandas as pd
    return pd.read_csv(path)


def get_adapter(supplier_name: str):
    """Return the parse function for a given supplier, or raise KeyError."""
    if supplier_name not in ADAPTERS:
        available = ", ".join(sorted(ADAPTERS.keys()))
        raise KeyError(f"No adapter for '{supplier_name}'. Available: {available}")
    return ADAPTERS[supplier_name]
