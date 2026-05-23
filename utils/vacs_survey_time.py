"""Load and parse ``VACS_survey_time.csv`` (same rules as ``satellite_data_exp_v1.ipynb`` §1–§2)."""

from __future__ import annotations

import calendar
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

# Logic mirrored from exposure_notebooks/satellite_data_exp_v1.ipynb (§2 parse cell).


RANGE_SPLIT = re.compile(r"\s*(?:-|–|—|to)\s*", re.I)
MONTH_NAME = "january|february|march|april|may|june|july|august|september|october|november|december"
MONTH_PAIR_YEAR = re.compile(rf"(?i)^\s*({MONTH_NAME})\s*[-–—]\s*({MONTH_NAME})\s+(\d{{4}})\s*$")


def resolve_vacs_survey_time_csv(repo_root: Path) -> Path:
    """Prefer tracked ``data/raw/`` copy; fall back to ``skills/`` if present locally."""
    candidates = [
        repo_root / "data" / "raw" / "VACS_survey_time.csv",
        repo_root / "skills" / "VACS_survey_time.csv",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "VACS_survey_time.csv not found. Expected one of:\n  "
        + "\n  ".join(str(c) for c in candidates)
    )


def load_survey_time_table(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    raw.columns = [c.strip() if isinstance(c, str) else c for c in raw.columns]
    if "Unnamed: 2" in raw.columns:
        raw = raw.rename(columns={"Unnamed: 2": "notes"})
    elif len(raw.columns) == 2:
        raw["notes"] = ""
    return raw.rename(
        columns={
            "Country": "country_wave",
            "Date": "field_period_raw",
        }
    ).copy()


def split_range(s: str) -> tuple[str | None, str | None]:
    s = (s or "").strip()
    if not s:
        return None, None
    parts = [p.strip() for p in RANGE_SPLIT.split(s, maxsplit=1)]
    if len(parts) == 2:
        return parts[0], parts[1]
    return s, None


def try_parse_date(txt: str | None) -> pd.Timestamp:
    if txt is None or not str(txt).strip():
        return pd.NaT
    t = pd.to_datetime(txt, errors="coerce", dayfirst=False)
    if pd.isna(t):
        t = pd.to_datetime(txt, errors="coerce", dayfirst=True)
    return t


def add_parsed_field_dates(survey_time: pd.DataFrame) -> pd.DataFrame:
    """Add ``field_start``, ``field_end``, ``date_parse_flag`` (mutates a copy)."""
    out = survey_time.copy()
    starts: list[pd.Timestamp] = []
    ends: list[pd.Timestamp] = []
    parse_flag: list[str] = []

    for _, row in out.iterrows():
        raw_txt = str(row.get("field_period_raw", "")).strip()
        low = raw_txt.lower()
        if not raw_txt:
            starts.append(pd.NaT)
            ends.append(pd.NaT)
            parse_flag.append("empty")
        elif "june" in low and "september" in low:
            starts.append(pd.NaT)
            ends.append(pd.NaT)
            parse_flag.append("month_name_range_manual")
        elif re.match(r"^[a-z]+\s+\d{4}$", low):
            starts.append(pd.NaT)
            ends.append(pd.NaT)
            parse_flag.append("month_year_only_manual")
        elif "october" in low and "february" in low:
            starts.append(pd.NaT)
            ends.append(pd.NaT)
            parse_flag.append("cross_year_month_manual")
        elif MONTH_PAIR_YEAR.match(raw_txt):
            starts.append(pd.NaT)
            ends.append(pd.NaT)
            parse_flag.append("month_name_pair_manual")
        else:
            a, b = split_range(raw_txt)
            ts_a, ts_b = try_parse_date(a), try_parse_date(b)
            if b is None and pd.notna(ts_a):
                starts.append(ts_a)
                ends.append(ts_a)
                parse_flag.append("single_day")
            elif pd.notna(ts_a) and pd.notna(ts_b):
                starts.append(min(ts_a, ts_b))
                ends.append(max(ts_a, ts_b))
                parse_flag.append("range_ok")
            else:
                starts.append(ts_a)
                ends.append(ts_b)
                parse_flag.append("needs_review")

    out["field_start"] = starts
    out["field_end"] = ends
    out["date_parse_flag"] = parse_flag

    BAD_YEAR = 1900

    def _year(ts: pd.Timestamp) -> int | None:
        if pd.isna(ts):
            return None
        return int(ts.year)

    for i in range(len(out)):
        ys, ye = _year(out.at[i, "field_start"]), _year(out.at[i, "field_end"])
        if ys is not None and ys < BAD_YEAR:
            out.at[i, "field_start"] = pd.NaT
            out.at[i, "field_end"] = pd.NaT
            out.at[i, "date_parse_flag"] = "month_name_pair_manual"
        elif ye is not None and ye < BAD_YEAR:
            out.at[i, "field_start"] = pd.NaT
            out.at[i, "field_end"] = pd.NaT
            out.at[i, "date_parse_flag"] = "month_name_pair_manual"

    return out


def get_country_wave_row(survey_time_parsed: pd.DataFrame, country_wave: str) -> pd.Series:
    m = survey_time_parsed["country_wave"] == country_wave
    if not m.any():
        raise KeyError(f"No row for country_wave={country_wave!r}")
    return survey_time_parsed.loc[m].iloc[0]


def field_dates_as_python_dates(row: pd.Series) -> tuple[date, date]:
    """Return ``(field_start, field_end)`` as ``datetime.date`` (raises if NaT)."""
    fs, fe = row["field_start"], row["field_end"]
    if pd.isna(fs) or pd.isna(fe):
        raise ValueError(
            f"Missing parsed dates for {row.get('country_wave')!r} "
            f"(date_parse_flag={row.get('date_parse_flag')!r})."
        )
    return fs.date(), fe.date()


def exposure_window_inclusive_before_field_start(
    field_start: date,
    *,
    years_before: int = 1,
) -> tuple[date, date]:
    """
    Match Zambia fire v3 convention: inclusive window ending the day before first field day.

    ``exposure_start`` = ``field_start`` minus ``years_before`` (calendar-safe via year arithmetic);
    ``exposure_end`` = ``field_start`` minus one day.
    """
    exposure_end = field_start - timedelta(days=1)
    exposure_start = date(field_start.year - years_before, field_start.month, field_start.day)
    return exposure_start, exposure_end


def next_day(d: date) -> date:
    return d + timedelta(days=1)


def months_df_inclusive_range(exposure_start: date, exposure_end: date) -> pd.DataFrame:
    """Calendar month slices clipped to [exposure_start, exposure_end] (inclusive); EE filter end exclusive."""
    rows: list[dict[str, Any]] = []
    y, m = exposure_start.year, exposure_start.month
    while True:
        ms = date(y, m, 1)
        last = date(y, m, calendar.monthrange(y, m)[1])
        s = max(ms, exposure_start)
        e = min(last, exposure_end)
        if s <= e:
            rows.append(
                {
                    "month_start": s,
                    "month_end": e,
                    "filter_end_exclusive": next_day(e),
                }
            )
        if (y, m) >= (exposure_end.year, exposure_end.month):
            break
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1
    return pd.DataFrame(rows)
