"""
Rwanda 2015–16 covariate codebook: question text and formats from approved
variable-label metadata.

Formats use ``code=meaning`` pairs when value labels or curated maps exist;
otherwise observed numeric codes only (no invented meanings).
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from utils.rwanda_2015_covariate_value_labels import RWANDA_KNOWN_VALUE_LABELS

MANUAL_QUESTIONS: dict[str, str] = {
    "sex": "Sex of respondent",
}


def question_from_label(col: str, meta) -> str:
    """Full question text from source variable labels, with manual overrides."""
    if col in MANUAL_QUESTIONS:
        return MANUAL_QUESTIONS[col]
    labels = meta.column_names_to_labels or {}
    return (labels.get(col) or "").strip()


def format_from_series(col: str, series: pd.Series, meta) -> str:
    """
    Response format: ``1=Yes, 2=No`` when meanings are known; else ``1, 2, 88``.
    """
    vl = (meta.variable_value_labels or {}).get(col) or {}
    if vl:
        return _join_code_meaning_pairs(
            _codes_in_series(series),
            {float(k): str(v) for k, v in vl.items()},
        )

    known = RWANDA_KNOWN_VALUE_LABELS.get(col)
    if known:
        return _join_code_meaning_pairs(_codes_in_series(series), known)

    if col == "q1200":
        codes = _codes_in_series(series)
        if codes:
            lo, hi = int(min(codes)), int(max(codes))
            return f"{lo}-{hi} (number of days)"
        return ""

    codes = _codes_in_series(series)
    if not codes:
        return ""
    return ", ".join(_format_code(c) for c in codes)


def _codes_in_series(series: pd.Series) -> list[float]:
    vals = series.dropna().unique()

    def sort_key(x: Any) -> tuple:
        try:
            return (0, float(x))
        except (TypeError, ValueError):
            return (1, str(x))

    return sorted(vals, key=sort_key)


def _join_code_meaning_pairs(
    observed: list[float],
    label_map: dict[float, str],
) -> str:
    parts: list[str] = []
    for code in observed:
        c = float(code) if code == int(code) else float(code)
        key = float(int(c)) if c == int(c) else c
        meaning = label_map.get(key) or label_map.get(c)
        code_str = _format_code(code)
        if meaning:
            parts.append(f"{code_str}={meaning}")
        else:
            parts.append(code_str)
    return ", ".join(parts)


def _format_code(val: Any) -> str:
    if isinstance(val, float) and not math.isnan(val) and val == int(val):
        return str(int(val))
    return str(val)
