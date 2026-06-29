"""
Build MODIS FRP admin tables in the same shape as the GADM fire exports.

The FRP demo uses Terra ``MODIS/061/MOD14A1`` and Aqua ``MODIS/061/MYD14A1`` daily
thermal-anomaly products. ``MaxFRP`` is scaled by 0.1 to MW per the Earth Engine catalog,
masked to fire pixels (``FireMask >= 7``), then summarized as a monthly maximum per admin
unit.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import ee
import pandas as pd

from utils.adam_modis_export import (
    adam_date_fields,
    add_mom,
    add_window_avg,
    filter_export_months,
    months_table_for_rolling,
)
from utils.gee_fire_zonal import reduce_max_per_feature_to_df

__all__ = [
    "build_adam_frp_export",
    "modis_monthly_max_frp_mw_image",
    "months_table_for_rolling",
    "to_adam_frp_wide_columns",
    "write_adam_frp_csv",
]

MODIS_FRP_COLLECTIONS = (
    "MODIS/061/MOD14A1",  # Terra
    "MODIS/061/MYD14A1",  # Aqua
)
MAX_FRP_SCALE = 0.1
FIREMASK_FIRE_MIN = 7


def _scaled_frp_image(img: ee.Image) -> ee.Image:
    fire = img.select("FireMask").gte(FIREMASK_FIRE_MIN)
    return (
        img.select("MaxFRP")
        .multiply(MAX_FRP_SCALE)
        .updateMask(fire)
        .rename("max_frp_mw")
    )


def modis_monthly_max_frp_mw_image(date_start: str, date_end_exclusive: str) -> ee.Image:
    """Monthly maximum FRP (MW) from Terra + Aqua MODIS daily fire products."""
    collections = [
        ee.ImageCollection(asset).filter(ee.Filter.date(date_start, date_end_exclusive))
        for asset in MODIS_FRP_COLLECTIONS
    ]
    frp = collections[0].merge(collections[1])
    max_frp = frp.map(_scaled_frp_image).max().unmask(0).rename("max_frp_mw")
    empty = ee.Image.constant(0).rename("max_frp_mw")
    return ee.Image(ee.Algorithms.If(frp.size().gt(0), max_frp, empty))


def district_monthly_frp_from_gee(
    months_table: pd.DataFrame,
    regions: ee.FeatureCollection,
    *,
    scale_m: float = 1000.0,
    region_features: list[dict] | None = None,
) -> pd.DataFrame:
    """Long table: district x month with ``monthly_max_frp_mw``."""
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
        img = modis_monthly_max_frp_mw_image(ms.isoformat(), mex_s)
        fdf = reduce_max_per_feature_to_df(
            img,
            regions,
            band_name="max_frp_mw",
            out_column="monthly_max_frp_mw",
            scale_m=scale_m,
            region_features=region_features,
        )
        fdf["month_start"] = ms
        parts.append(fdf)
    return pd.concat(parts, ignore_index=True)


def to_adam_frp_wide_columns(
    long_df: pd.DataFrame,
    *,
    adm0_name: str,
    adm0_pcode: str,
    unit_level: int = 2,
) -> pd.DataFrame:
    df = long_df.copy()
    df["adm0_name"] = adm0_name
    df["adm0_pcode"] = adm0_pcode
    if unit_level >= 1:
        df["adm1_name"] = df["ADM1_NAME"]
        df["adm1_gid"] = df["ADM1_CODE"].astype(str) if "ADM1_CODE" in df.columns else ""
    if unit_level >= 2:
        df["adm2_name"] = df["ADM2_NAME"]
        df["adm2_gid"] = df["ADM2_CODE"].astype(str) if "ADM2_CODE" in df.columns else ""
    area_src = f"ADM{unit_level}_AREA_KM2"
    if area_src in df.columns:
        df[f"adm{unit_level}_area_km2"] = df[area_src]

    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    ms = pd.to_datetime(df["month_start"])
    date_rows = [adam_date_fields(pd.Timestamp(ts).date()) for ts in ms]
    for key in ("month_start", "month_end"):
        df[key] = [row[key] for row in date_rows]

    adam_cols = [
        "adm0_name",
        "adm0_pcode",
        "adm1_name",
        "adm1_gid",
        "adm1_area_km2",
        "adm2_name",
        "adm2_gid",
        "adm2_area_km2",
        "month_start",
        "month_end",
        "monthly_max_frp_mw",
        "avg12_max_frp_mw",
        "mom_pct_change",
    ]
    cols = [c for c in adam_cols if c in df.columns]
    out = df.loc[:, cols]
    if out.columns.duplicated().any():
        out = out.loc[:, ~pd.Index(out.columns).duplicated(keep="first")]
    sort_cols = [c for c in ("adm1_name", "adm2_name") if c in out.columns] + ["month_start"]
    return out.sort_values(sort_cols)


def build_adam_frp_export(
    months_table: pd.DataFrame,
    regions: ee.FeatureCollection,
    *,
    adm0_name: str,
    adm0_pcode: str,
    exposure_start: date,
    exposure_end: date,
    scale_m: float = 1000.0,
    region_features: list[dict] | None = None,
    unit_level: int = 2,
) -> pd.DataFrame:
    """GEE pull -> MoM -> exposure-month filter -> fixed 12-month avg -> CSV columns."""
    unit_col = f"ADM{unit_level}_NAME"
    long_df = district_monthly_frp_from_gee(
        months_table, regions, scale_m=scale_m, region_features=region_features
    )
    long_df = add_mom(long_df, unit_col=unit_col, value_col="monthly_max_frp_mw")
    long_df = filter_export_months(long_df, exposure_start, exposure_end)
    long_df = add_window_avg(
        long_df,
        unit_col=unit_col,
        value_col="monthly_max_frp_mw",
        out_col="avg12_max_frp_mw",
    )
    return to_adam_frp_wide_columns(
        long_df, adm0_name=adm0_name, adm0_pcode=adm0_pcode, unit_level=unit_level
    )


def write_adam_frp_csv(df: pd.DataFrame, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
