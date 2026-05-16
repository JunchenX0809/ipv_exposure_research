"""
Harmonized ID/geo checklist: map (slot label, candidate columns) to a summary DataFrame.

The candidate list is owned by the notebook author; this module only shapes and formats.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Mapping, Sequence

import pandas as pd

from .pi_width import pi_char_len

CHECKLIST_COLUMN_ORDER: Sequence[str] = (
    "slot",
    "column",
    "stata_label",
    "type_and_width",
    "suggested_layout",
    "dtype",
    "nunique",
    "missing_n",
    "missing_pct",
    "pi_digits_char_usual_display",
    "min_nonnull",
    "max_nonnull",
    "sample_first_3",
    "slot_notes",
)


def _dtype_short_for_codebook(dtype_str: str) -> str:
    """Short type label for harmonized codebook paste (e.g. float64 -> float)."""
    s = str(dtype_str).lower()
    if s.startswith("float"):
        return "float"
    if s.startswith("int") or s.startswith("uint"):
        return "int"
    if s in ("object", "string") or s.startswith("str"):
        return "str"
    if s.startswith("bool"):
        return "bool"
    if "datetime" in s:
        return "datetime"
    if "category" in s:
        return "category"
    return str(dtype_str)


def _valid_ymd(y: int, m: int, d: int) -> bool:
    try:
        datetime(y, m, d)
        return True
    except (ValueError, OverflowError):
        return False


def _suggest_value_layout(s: pd.Series) -> str | None:
    """
    Infer a codebook-friendly layout string from observed values (not Stata formats).

    Returns compact tokens (e.g. ``YYYYMMDD``) or separator forms (e.g. ``YYYY-MM-DD``)
    suitable for harmonized ``notes`` / ``type_and_width``.
    """
    sn = s.dropna()
    if len(sn) == 0:
        return None

    # Native pandas datetimes
    if pd.api.types.is_datetime64_any_dtype(s):
        ts = pd.to_datetime(sn, errors="coerce").dropna()
        if ts.empty:
            return None
        sub = ts.dt
        has_time = bool(
            (sub.hour != 0).any()
            or (sub.minute != 0).any()
            or (sub.second != 0).any()
            or (sub.microsecond != 0).any()
        )
        return "YYYY-MM-DD HH:MM:SS" if has_time else "YYYY-MM-DD"

    # Whole-number calendar dates (e.g. Rwanda ``hdate_vf`` as 20151221.0)
    if pd.api.types.is_numeric_dtype(s):
        vals = pd.to_numeric(sn, errors="coerce").dropna()
        if vals.empty or not (vals == vals.round()).all():
            return None
        ints = vals.round().astype("int64")
        lo, hi = int(ints.min()), int(ints.max())

        if 18000101 <= lo and hi <= 21001231:
            for v in ints.head(200):
                vi = int(v)
                y, m, d = vi // 10000, (vi // 100) % 100, vi % 100
                if not _valid_ymd(y, m, d):
                    return None
            return "YYYYMMDD"

        if 18000101000000 <= lo and hi <= 21001231235959:
            for v in ints.head(200):
                vi = int(v)
                ymd, hms = vi // 1000000, vi % 1000000
                y, mo, d = ymd // 10000, (ymd // 100) % 100, ymd % 100
                hh, mm, ss = hms // 10000, (hms // 100) % 100, hms % 100
                if not _valid_ymd(y, mo, d):
                    return None
                if not (0 <= hh <= 23 and 0 <= mm <= 59 and 0 <= ss <= 59):
                    return None
            return "YYYYMMDDHHMMSS"

    return None


def _type_and_width_cell(dtype_raw, dig, layout_hint: str | None = None) -> object:
    """
    Codebook-style ``type_and_width``: short dtype, PI width phrase, optional layout
    (e.g. ``float; 8 digits; YYYYMMDD``).
    """
    if dtype_raw is pd.NA or (isinstance(dtype_raw, float) and pd.isna(dtype_raw)):
        return pd.NA
    short = _dtype_short_for_codebook(str(dtype_raw))
    parts: list[str] = [short]
    if dig is not pd.NA and not (isinstance(dig, float) and pd.isna(dig)):
        ds = str(dig)
        if "\u2013" in ds or "–" in ds:
            parts.append(f"{ds} digits")
        elif ds == "1":
            parts.append("1 digit")
        else:
            parts.append(f"{ds} digits")
    if layout_hint:
        parts.append(layout_hint)
    if len(parts) == 1:
        return short
    return "; ".join(parts)


def format_sample_preview(
    series: pd.Series, *, n: int = 3, max_each: int = 40
) -> str:
    """First n non-null values as repr(), each truncated for a compact table cell."""
    parts: list[str] = []
    for v in series.dropna().head(n).tolist():
        t = repr(v)
        if len(t) > max_each:
            t = t[: max_each - 1] + "…"
        parts.append(t)
    return ", ".join(parts) if parts else ""


def build_checklist_df(
    df: pd.DataFrame,
    candidates: Iterable[tuple[str, Sequence[str]]],
    *,
    column_labels: Mapping[str, str] | None = None,
    stata_label_max_len: int = 200,
    sample_n: int = 3,
    sample_max_each: int = 40,
) -> pd.DataFrame:
    """
    Build one row per present candidate column; stub rows for empty slots or missing names.

    Parameters
    ----------
    df : DataFrame
        Loaded survey extract.
    candidates : iterable of (slot_label, [col_name, ...])
        Order preserved; only columns that exist in ``df`` get metric rows.
    column_labels : mapping, optional
        Stata variable labels keyed by column name (e.g. ``meta.column_names_to_labels``).
    """
    labels = dict(column_labels or {})
    rows: list[dict] = []

    for slot, cols in candidates:
        miss = [c for c in cols if c not in df.columns]
        hit = [c for c in cols if c in df.columns]

        if not hit:
            rows.append(
                {
                    "slot": slot,
                    "column": "",
                    "stata_label": (
                        "— no candidates —"
                        if not miss
                        else f"(not in df: {', '.join(miss)})"
                    ),
                    "type_and_width": pd.NA,
                    "suggested_layout": pd.NA,
                    "dtype": pd.NA,
                    "nunique": pd.NA,
                    "missing_n": pd.NA,
                    "missing_pct": pd.NA,
                    "pi_digits_char_usual_display": pd.NA,
                    "min_nonnull": pd.NA,
                    "max_nonnull": pd.NA,
                    "sample_first_3": pd.NA,
                    "slot_notes": pd.NA,
                }
            )
            continue

        for i, c in enumerate(hit):
            s = df[c]
            if pd.api.types.is_datetime64_any_dtype(s):
                dig = pd.NA
            else:
                lens = s.map(pi_char_len).dropna()
                if len(lens):
                    lo, hi = int(lens.min()), int(lens.max())
                    dig = f"{lo}–{hi}" if lo != hi else str(lo)
                else:
                    dig = pd.NA
            mn = mx = pd.NA
            if pd.api.types.is_numeric_dtype(s) and s.notna().any():
                sn = s.dropna()
                mn, mx = sn.min(), sn.max()
            elif pd.api.types.is_datetime64_any_dtype(s) and s.notna().any():
                sn = s.dropna()
                mn, mx = sn.min(), sn.max()
            miss_n = int(s.isna().sum())
            miss_pct = round(100 * float(s.isna().mean()), 2)
            note = pd.NA
            if miss and i == 0:
                note = f"also requested (not in df): {', '.join(miss)}"
            dt = str(s.dtype)
            layout = _suggest_value_layout(s)
            rows.append(
                {
                    "slot": slot,
                    "column": c,
                    "stata_label": (labels.get(c) or "")[:stata_label_max_len],
                    "type_and_width": _type_and_width_cell(dt, dig, layout),
                    "suggested_layout": pd.NA if layout is None else layout,
                    "dtype": dt,
                    "nunique": int(s.nunique()),
                    "missing_n": miss_n,
                    "missing_pct": miss_pct,
                    "pi_digits_char_usual_display": dig,
                    "min_nonnull": mn,
                    "max_nonnull": mx,
                    "sample_first_3": format_sample_preview(
                        s, n=sample_n, max_each=sample_max_each
                    ),
                    "slot_notes": note,
                }
            )

    out = pd.DataFrame(rows)
    return out.reindex(columns=list(CHECKLIST_COLUMN_ORDER))


def checklist_to_tsv(checklist_df: pd.DataFrame) -> str:
    """Tab-separated text for pasting into Excel / codebook."""
    return checklist_df.to_csv(sep="\t", index=False)
