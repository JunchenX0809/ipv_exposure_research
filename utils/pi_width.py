"""Character-width helpers for PI-facing documentation (usual display, no zero-padding)."""

from __future__ import annotations

import math

import pandas as pd


def pi_char_len(value):
    """
    Character count for a single value as the PI typically sees it:
    integers use len(str(int(x))) (no zero-padding); strings use len(s).
    Returns float('nan') for missing values (works with Series.map + dropna).
    """
    if pd.isna(value):
        return float("nan")
    if isinstance(value, str):
        return len(value)
    try:
        x = float(value)
        if math.isfinite(x) and x == int(x):
            return len(str(int(x)))
    except (TypeError, ValueError):
        pass
    return len(str(value))
