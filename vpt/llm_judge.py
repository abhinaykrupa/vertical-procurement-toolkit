"""
Real LLM-backed Stage 3 judge.

Drop-in replacement for engine.matcher.stage3_llm_judge that uses a real LLM
(Anthropic Claude or OpenAI GPT) when configured. Falls back to the mock
when no credentials are present so the offline demo never breaks.

Configuration via env vars:
    LLM_JUDGE_PROVIDER  = "anthropic" | "openai" | "mock" (default: "mock")
    LLM_JUDGE_MODEL     = model name (default: claude-haiku-4 / gpt-4o-mini)
    ANTHROPIC_API_KEY   = required if provider=anthropic
    OPENAI_API_KEY      = required if provider=openai

Usage in user code:

    from vpt.llm_judge import judge_with_llm
    match, confidence, rationale = judge_with_llm(prospect_row, candidates)

Or monkey-patch the engine:

    import engine.matcher
    from vpt.llm_judge import judge_with_llm
    engine.matcher.stage3_llm_judge = judge_with_llm
"""

from __future__ import annotations

import json
import os
from typing import Optional, Sequence

import pandas as pd


# Production prompt — used verbatim against Claude Haiku / GPT-4o-mini
JUDGE_PROMPT_TEMPLATE = """You are matching a prospect's supplier purchase-history line item to a reference pricing catalog.

PROSPECT LINE:
  Description: {raw_description}
  Manufacturer: {manufacturer_name}
  Manufacturer SKU: {manufacturer_sku}
  Quantity: {quantity}
  Unit price: ${unit_price}

TOP {n} CATALOG CANDIDATES (from retrieval):
{candidates_block}

Return ONLY a JSON object with these fields:
  - best_match_sku: string (the sc_sku of the best candidate) or null if no candidate is a match
  - confidence: number 0.0 to 1.0
  - uom_alignment: "aligned" | "mismatch" | "unknown"
  - rationale: 1-2 sentence human-readable explanation

Be strict about UOM and pack size — "box of 100" vs "case of 10 boxes" is a mismatch even if the description matches."""


def judge_with_llm(prospect_row: pd.Series, candidates: Sequence[tuple]) -> tuple[Optional[pd.Series], float, str]:
    """
    Real LLM judge. Same signature as engine.matcher.stage3_llm_judge.

    Returns (best_match: Series | None, confidence: float, rationale: str).
    """
    if not candidates:
        return None, 0.0, "✗ No candidates retrieved"

    provider = os.environ.get("LLM_JUDGE_PROVIDER", "mock").lower()

    if provider == "mock":
        # Delegate to the existing mock
        from engine.matcher import stage3_llm_judge as _mock
        return _mock(prospect_row, list(candidates))

    if provider == "anthropic":
        return _judge_anthropic(prospect_row, candidates)

    if provider == "openai":
        return _judge_openai(prospect_row, candidates)

    raise ValueError(f"Unknown LLM_JUDGE_PROVIDER: {provider!r}. Use 'mock', 'anthropic', or 'openai'.")


def _format_candidates(candidates: Sequence[tuple]) -> str:
    lines = []
    for i, (score, cat_row) in enumerate(candidates[:5], start=1):
        lines.append(
            f"  {i}. sc_sku={cat_row.get('sc_sku', '?')} | "
            f"description={cat_row.get('description', '?')} | "
            f"manufacturer={cat_row.get('manufacturer', '?')} | "
            f"mfg_sku={cat_row.get('mfg_sku', '?')} | "
            f"pack_size={cat_row.get('pack_size', '?')} | "
            f"unit_of_measure={cat_row.get('unit_of_measure', '?')} | "
            f"unit_price=${cat_row.get('unit_price', '?')} | "
            f"retrieval_score={score:.3f}"
        )
    return "\n".join(lines)


def _build_prompt(prospect_row: pd.Series, candidates: Sequence[tuple]) -> str:
    return JUDGE_PROMPT_TEMPLATE.format(
        raw_description=prospect_row.get("raw_description", ""),
        manufacturer_name=prospect_row.get("manufacturer_name", ""),
        manufacturer_sku=prospect_row.get("manufacturer_sku", ""),
        quantity=prospect_row.get("quantity", ""),
        unit_price=prospect_row.get("unit_price", ""),
        n=min(5, len(candidates)),
        candidates_block=_format_candidates(candidates),
    )


def _parse_llm_response(raw_text: str, candidates: Sequence[tuple]) -> tuple[Optional[pd.Series], float, str]:
    """Parse the JSON response and resolve sc_sku back to the candidate row."""
    # Strip code fences if present
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.split("```")[1] if "```" in text[3:] else text
        if text.startswith("json"):
            text = text[4:]
    try:
        parsed = json.loads(text.strip())
    except json.JSONDecodeError as e:
        return None, 0.0, f"✗ LLM returned invalid JSON: {e}"

    best_sku = parsed.get("best_match_sku")
    confidence = float(parsed.get("confidence", 0.0))
    rationale = parsed.get("rationale", "(no rationale)")
    uom = parsed.get("uom_alignment", "unknown")

    if best_sku is None:
        return None, confidence, f"✗ {rationale}"

    # Look up the candidate row by sc_sku
    for _, cat_row in candidates:
        if str(cat_row.get("sc_sku", "")) == str(best_sku):
            tag = "✓" if uom == "aligned" else ("⚠" if uom == "mismatch" else "?")
            return cat_row, confidence, f"{tag} LLM: {rationale}"

    return None, confidence, f"✗ LLM picked sc_sku={best_sku} not in candidates: {rationale}"


def _judge_anthropic(prospect_row: pd.Series, candidates: Sequence[tuple]) -> tuple[Optional[pd.Series], float, str]:
    try:
        import anthropic
    except ImportError:
        return None, 0.0, "✗ anthropic SDK not installed. Run: pip install anthropic"

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, 0.0, "✗ ANTHROPIC_API_KEY not set"

    model = os.environ.get("LLM_JUDGE_MODEL", "claude-haiku-4-20250101")
    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_prompt(prospect_row, candidates)

    try:
        resp = client.messages.create(
            model=model,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text  # type: ignore[attr-defined]
    except Exception as e:
        return None, 0.0, f"✗ Anthropic API error: {e}"

    return _parse_llm_response(text, candidates)


def _judge_openai(prospect_row: pd.Series, candidates: Sequence[tuple]) -> tuple[Optional[pd.Series], float, str]:
    try:
        from openai import OpenAI
    except ImportError:
        return None, 0.0, "✗ openai SDK not installed. Run: pip install openai"

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None, 0.0, "✗ OPENAI_API_KEY not set"

    model = os.environ.get("LLM_JUDGE_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(prospect_row, candidates)

    try:
        resp = client.chat.completions.create(
            model=model,
            max_tokens=400,
            messages=[
                {"role": "system", "content": "You are a strict procurement-matching judge. Reply with JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content or ""
    except Exception as e:
        return None, 0.0, f"✗ OpenAI API error: {e}"

    return _parse_llm_response(text, candidates)
