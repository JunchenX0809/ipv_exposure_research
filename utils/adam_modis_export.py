"""
Build MODIS MCD64A1 admin-2 tables in Adam's export shape (see ``skills/Adam_Modis.docx``).

Adam columns (Kenya reference: ``skills/Adam_kenya_modis_2010.csv``):
  adm0_name, adm0_pcode, adm1_name, adm1_pcode, adm2_name, adm2_pcode,
  month_start, month_end, rolling_start, rolling_end,
  monthly_burned_area_km2, rolling12_burned_area_avg_km2

Extra columns kept: ``burn_area_ha``, ``mom_pct_change``.

Rolling logic (from Adam's EE): ``rolling_start = month_end - 12 months``;
``rolling12_burned_area_avg_km2`` = mean of district ``monthly_burned_area_km2`` over the
12 month-starts ``rolling_start + 0..11 months``. Pull extra history before the exposure
window so early exposure months have full rolling windows.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import ee
import pandas as pd

from utils.gee_fire_zonal import reduce_sum_per_feature_to_df
from utils.vacs_survey_time import months_df_inclusive_range


def mcd64a1_monthly_burn_km2_image(date_start: str, date_end_exclusive: str) -> ee.Image:
    """Adam MODIS: sum of per-scene burned km² where ``BurnDate > 0`` (``Adam_Modis.docx``)."""
    mcd = (
        ee.ImageCollection("MODIS/061/MCD64A1")
        .filter(ee.Filter.date(date_start, date_end_exclusive))
        .select("BurnDate")
    )

    def _per_scene(img: ee.Image) -> ee.Image:
        burned = img.select("BurnDate").gt(0)
        return (
            ee.Image.pixelArea()
            .divide(1e6)
            .updateMask(burned)
            .rename("burned_area_km2")
        )

    summed = mcd.map(_per_scene).sum()
    empty = ee.Image.constant(0).rename("burned_area_km2")
    return ee.Image(ee.Algorithms.If(mcd.size().gt(0), summed, empty))


def adam_month_end_exclusive(month_start: date) -> date:
    """``monthEnd`` in Adam's script: ``month_start`` + 1 calendar month."""
    ts = pd.Timestamp(month_start) + pd.DateOffset(months=1)
    return ts.date()


def adam_date_fields(month_start: date) -> dict[str, str]:
    m_end = adam_month_end_exclusive(month_start)
    rs = pd.Timestamp(m_end) - pd.DateOffset(months=12)
    return {
        "month_start": month_start.isoformat(),
        "month_end": m_end.isoformat(),
        "rolling_start": rs.date().isoformat(),
        "rolling_end": m_end.isoformat(),
    }


def months_table_for_rolling(
    exposure_start: date,
    exposure_end: date,
    *,
    history_months: int = 11,
) -> pd.DataFrame:
    """
    Month rows for GEE: ``history_months`` of context before ``exposure_start``, through ``exposure_end``.

    Uses the same calendar clipping as ``months_df_inclusive_range``.
    """
    ext_start = (pd.Timestamp(exposure_start) - pd.DateOffset(months=history_months)).date()
    raw = months_df_inclusive_range(ext_start, exposure_end)
    rows: list[dict[str, Any]] = []
    for _, mr in raw.iterrows():
        ms = mr["month_start"]
        if not isinstance(ms, date):
            ms = pd.Timestamp(ms).date()
        m_end = adam_month_end_exclusive(ms)
        rows.append(
            {
                "month_start": ms,
                "month_end": m_end,
                "filter_end_exclusive": m_end,
            }
        )
    return pd.DataFrame(rows)


def district_monthly_burn_from_gee(
    months_table: pd.DataFrame,
    regions: ee.FeatureCollection,
    *,
    scale_m: float = 500.0,
) -> pd.DataFrame:
    """Long table: district × month with ``monthly_burned_area_km2`` and ``burn_area_ha``."""
    parts: list[pd.DataFrame] = []
    for _, mr in months_table.iterrows():
        ms = mr["month_start"]
        if not isinstance(ms, date):
            ms = pd.Timestamp(ms).date()
        mex_s = (
            mr["filter_end_exclusive"].isoformat()
            if hasattr(mr["filter_end_exclusive"], "isoformat")
            else str(mr["filter_end_exclusive"])[:10]
        )
        img = mcd64a1_monthly_burn_km2_image(ms.isoformat(), mex_s)
        bdf = reduce_sum_per_feature_to_df(
            img,
            regions,
            band_name="burned_area_km2",
            out_column="monthly_burned_area_km2",
            scale_m=scale_m,
        )
        bdf["burn_area_ha"] = bdf["monthly_burned_area_km2"] * 100.0
        bdf["month_start"] = ms
        parts.append(bdf)
    return pd.concat(parts, ignore_index=True)


def add_rolling12_and_mom(long_df: pd.DataFrame) -> pd.DataFrame:
    out = long_df.copy()
    out["month_start"] = pd.to_datetime(out["month_start"])
    out = out.sort_values(["ADM2_NAME", "month_start"])

    rolling_vals: list[float] = []
    for _, row in out.iterrows():
        ms = row["month_start"].date()
        m_end = adam_month_end_exclusive(ms)
        rs = pd.Timestamp(m_end) - pd.DateOffset(months=12)
        starts = {(rs + pd.DateOffset(months=i)).date() for i in range(12)}
        md = out["month_start"].dt.date
        sub = out[(out["ADM2_NAME"] == row["ADM2_NAME"]) & (md.isin(starts))]
        rolling_vals.append(float(sub["monthly_burned_area_km2"].mean()) if len(sub) else float("nan"))
    out["rolling12_burned_area_avg_km2"] = rolling_vals
    out["mom_pct_change"] = out.groupby("ADM2_NAME", group_keys=False)[
        "monthly_burned_area_km2"
    ].transform(lambda s: s.pct_change() * 100.0)
    return out


def to_adam_modis_wide_columns(
    long_df: pd.DataFrame,
    *,
    adm0_name: str,
    adm0_pcode: str,
) -> pd.DataFrame:
    df = long_df.copy()
    df["adm0_name"] = adm0_name
    df["adm0_pcode"] = adm0_pcode
    df["adm1_name"] = df["ADM1_NAME"]
    df["adm2_name"] = df["ADM2_NAME"]
    # GAUL codes (Kenya file uses HDX GADM pcodes; these are GAUL ADM codes as strings)
    if "ADM1_CODE" in df.columns:
        df["adm1_pcode"] = df["ADM1_CODE"].astype(str)
    else:
        df["adm1_pcode"] = ""
    if "ADM2_CODE" in df.columns:
        df["adm2_pcode"] = df["ADM2_CODE"].astype(str)
    else:
        df["adm2_pcode"] = ""

    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    ms = pd.to_datetime(df["month_start"])
    date_rows = [adam_date_fields(pd.Timestamp(ts).date()) for ts in ms]
    for key in ("month_start", "month_end", "rolling_start", "rolling_end"):
        df[key] = [row[key] for row in date_rows]

    adam_first = [
        "adm0_name",
        "adm0_pcode",
        "adm1_name",
        "adm1_pcode",
        "adm2_name",
        "adm2_pcode",
        "month_start",
        "month_end",
        "rolling_start",
        "rolling_end",
        "monthly_burned_area_km2",
        "rolling12_burned_area_avg_km2",
        "burn_area_ha",
        "mom_pct_change",
    ]
    cols = [c for c in adam_first if c in df.columns]
    out = df.loc[:, cols]
    if out.columns.duplicated().any():
        out = out.loc[:, ~pd.Index(out.columns).duplicated(keep="first")]
    return out.sort_values(["adm1_name", "adm2_name", "month_start"])


def filter_export_months(df: pd.DataFrame, exposure_start: date, exposure_end: date) -> pd.DataFrame:
    ms = pd.to_datetime(df["month_start"])
    lo = pd.Timestamp(exposure_start)
    hi = pd.Timestamp(exposure_end)
    return df[(ms >= lo) & (ms <= hi)].copy()


def build_adam_modis_export(
    months_table: pd.DataFrame,
    regions: ee.FeatureCollection,
    *,
    adm0_name: str,
    adm0_pcode: str,
    exposure_start: date,
    exposure_end: date,
    scale_m: float = 500.0,
) -> pd.DataFrame:
    """GEE pull → rolling/mom → Adam column names → exposure-month filter."""
    long_df = district_monthly_burn_from_gee(months_table, regions, scale_m=scale_m)
    long_df = add_rolling12_and_mom(long_df)
    wide = to_adam_modis_wide_columns(long_df, adm0_name=adm0_name, adm0_pcode=adm0_pcode)
    return filter_export_months(wide, exposure_start, exposure_end)


def write_adam_modis_csv(df: pd.DataFrame, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
