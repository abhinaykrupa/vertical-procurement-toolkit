"""
UOM vocabulary loader — externalize per-vertical UOM aliases and stopwords.

Usage:
    from vpt.uom import load_uom_table
    table = load_uom_table("dental")  # or "vet", "hvac", "restaurant"

    # Patch the engine to use it
    import engine.matcher
    engine.matcher.UOM_ALIASES = table["aliases"]
    engine.matcher.STOPWORDS = set(table["stopwords"])

Or list available verticals:
    from vpt.uom import list_available
    list_available()  # ["dental", "vet", "hvac", "restaurant"]
"""

from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError as e:
    raise ImportError(
        "PyYAML required for UOM table loading. Run: pip install PyYAML"
    ) from e


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_UOM_DIR = _PROJECT_ROOT / "uom_tables"


def load_uom_table(vertical: str) -> dict:
    """
    Load the UOM vocabulary for a vertical.

    Returns dict with keys: aliases (dict), stopwords (list)
    Raises FileNotFoundError if no table exists for the vertical.
    """
    path = _UOM_DIR / f"{vertical.lower()}.yaml"
    if not path.exists():
        available = ", ".join(list_available())
        raise FileNotFoundError(
            f"No UOM table for vertical {vertical!r}. Available: {available}"
        )
    with open(path) as f:
        data = yaml.safe_load(f)
    return {
        "aliases": data.get("aliases", {}),
        "stopwords": data.get("stopwords", []),
    }


def list_available() -> list[str]:
    """Return list of verticals with bundled UOM tables."""
    if not _UOM_DIR.exists():
        return []
    return sorted(p.stem for p in _UOM_DIR.glob("*.yaml"))


def apply_to_engine(vertical: str) -> None:
    """
    Convenience: load the table and patch the matcher's global vocabulary.

    Call once at program start before any matching.
    """
    import sys
    _APP_DIR = _PROJECT_ROOT / "app"
    if _APP_DIR.exists() and str(_APP_DIR) not in sys.path:
        sys.path.insert(0, str(_APP_DIR))

    from engine import matcher
    table = load_uom_table(vertical)
    matcher.UOM_ALIASES = table["aliases"]
    matcher.STOPWORDS = set(table["stopwords"])
