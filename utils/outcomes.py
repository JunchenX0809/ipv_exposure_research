"""
Outcome codebook helpers: normalized DataFrame, TSV export, and PUD verification.
"""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

import pandas as pd

# Five-column template (same headers as covariate codebooks / user spec).
OUTCOME_CODEBOOK_COLUMNS: Sequence[str] = (
    "Category",
    "Variable",
    "Type",
    "Format",
    "Questions",
)


def build_outcome_codebook_df(
    entries: Sequence[Mapping[str, Any]],
) -> pd.DataFrame:
    """Build the outcome codebook DataFrame from researcher-provided dict rows."""
    rows: list[dict[str, Any]] = []
    for entry in entries:
        rows.append({col: entry.get(col, "") for col in OUTCOME_CODEBOOK_COLUMNS})
    return pd.DataFrame(rows, columns=list(OUTCOME_CODEBOOK_COLUMNS))


def outcome_codebook_to_tsv(df: pd.DataFrame) -> str:
    """Tab-separated text for pasting into Excel."""
    return df.to_csv(sep="\t", index=False)


def _format_codes_from_format_string(fmt: str) -> set[int]:
    """Extract integer response codes from a parser ``format_string``."""
    if not fmt or not str(fmt).strip():
        return set()
    out: set[int] = set()
    for part in str(fmt).split(","):
        part = part.strip()
        m = re.match(r"^(\d+)\s*-\s*", part)
        if m:
            out.add(int(m.group(1)))
    return out


def verify_variable_against_dta(
    series: pd.Series,
    format_string: str,
    *,
    extra_allowed: Sequence[int | float] | None = None,
) -> tuple[bool, str]:
    """
    Check that observed non-null values are compatible with the codebook format.

    Returns (ok, message). Allows Stata-style float codes (e.g. 1.0) by
    comparing rounded integers. Empty ``format_string`` skips code-set check.
    """
    allowed = _format_codes_from_format_string(format_string)
    if extra_allowed:
        allowed |= {int(x) if float(x).is_integer() else x for x in extra_allowed}
    sn = series.dropna()
    if sn.empty:
        return True, "no non-null values"
    obs: set[int] = set()
    for v in sn:
        try:
            fv = float(v)
        except (TypeError, ValueError):
            return False, f"non-numeric observed value {v!r}"
        if fv != int(fv):
            return False, f"non-integer code observed: {v!r}"
        obs.add(int(fv))

    if not allowed:
        return True, f"format empty; observed distinct = {sorted(obs)}"

    bad = obs - allowed
    if bad:
        special_only = allowed.issubset({77, 88, 98, 99})
        if special_only:
            return (
                True,
                f"format lists only special codes {sorted(allowed)}; observed distinct={sorted(obs)} "
                "(full category list may be incomplete in parser output — verify PDF / PUD)",
            )
        return False, f"observed codes not in format: {sorted(bad)} (allowed {sorted(allowed)})"
    return True, f"ok; distinct={sorted(obs)}"
