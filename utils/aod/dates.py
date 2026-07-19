"""AOD exposure-window dates, matching the repository's shipped output convention."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from utils.vacs_survey_time import (
    add_parsed_field_dates,
    exposure_window_inclusive_before_field_start,
    field_dates_as_python_dates,
    get_country_wave_row,
    load_survey_time_table,
    resolve_vacs_survey_time_csv,
)

ALLOWED_DATE_FLAGS = frozenset(
    {
        "range_ok",
        "single_day",
        "month_year_range_ok",
        "month_pair_year_ok",
        "month_abbr_year_ok",
        "month_only_year_ok",
        "month_name_pair_manual",
    }
)


def resolve_exposure_window(repo_root: Path, country_wave: str) -> tuple[date, date]:
    """Resolve the exact inclusive one-year pre-fieldwork interval."""
    survey = add_parsed_field_dates(
        load_survey_time_table(resolve_vacs_survey_time_csv(repo_root))
    )
    row = get_country_wave_row(survey, country_wave)
    flag = str(row.get("date_parse_flag", ""))
    if flag not in ALLOWED_DATE_FLAGS:
        raise ValueError(
            f"{country_wave!r}: date_parse_flag={flag!r}; survey date requires review"
        )
    field_start, _ = field_dates_as_python_dates(row)
    return exposure_window_inclusive_before_field_start(field_start)


def complete_calendar_months(
    exposure_start: date, exposure_end: date
) -> pd.DataFrame:
    """Return the 12 complete calendar months used by the existing exposure files.

    Month starts must fall inside the exact pre-fieldwork interval. A partial first
    month is therefore excluded, while the last selected month is represented as a
    complete calendar month with an exclusive ``month_end``.
    """
    first = pd.Timestamp(exposure_start).replace(day=1)
    if exposure_start.day != 1:
        first += pd.DateOffset(months=1)
    starts = pd.date_range(first, periods=12, freq="MS")
    if starts[-1].date() > exposure_end:
        raise ValueError(
            f"Cannot form 12 complete calendar months inside {exposure_start}..{exposure_end}"
        )
    ends = starts + pd.DateOffset(months=1)
    return pd.DataFrame(
        {
            "month_start": [ts.date() for ts in starts],
            "month_end": [ts.date() for ts in ends],
        }
    )
