"""Reusable Earth Engine helpers for fire / burned-area zonal stats (admin-2 GAUL).

Notebooks should import from here instead of duplicating collection IDs and
``reduceRegions`` boilerplate. Requires ``earthengine-api`` (``import ee``).
"""

from __future__ import annotations

import os
from typing import Any

import ee
import pandas as pd


def gaul2015_level2_regions(adm0_name: str, *, use_simplified: bool = False) -> ee.FeatureCollection:
    """FAO GAUL 2015 admin-2 polygons for one country (``ADM0_NAME`` match)."""
    asset = (
        "FAO/GAUL_SIMPLIFIED_500m/2015/level2"
        if use_simplified
        else "FAO/GAUL/2015/level2"
    )
    return ee.FeatureCollection(asset).filter(ee.Filter.eq("ADM0_NAME", adm0_name))


def mcd64a1_burn_area_m2_image(date_start: str, date_end_exclusive: str) -> ee.Image:
    """
    One month (or any window): max BurnDate > 0 → binary mask × pixel area (m²).

    ``date_*`` are ISO date strings for ``ee.Filter.date`` (upper bound exclusive).
    """
    mcd = (
        ee.ImageCollection("MODIS/061/MCD64A1")
        .filter(ee.Filter.date(date_start, date_end_exclusive))
        .select("BurnDate")
    )
    burned = mcd.max().gt(0).rename("burn_mask")
    return burned.multiply(ee.Image.pixelArea()).rename("burn_area_m2")


def firms_hot_area_m2_image(
    date_start: str,
    date_end_exclusive: str,
    *,
    t21_min_kelvin: float = 325.0,
) -> ee.Image:
    """Monthly mosaic: max T21 over window, threshold (K), × pixel area (m²)."""
    firms = (
        ee.ImageCollection("FIRMS")
        .filter(ee.Filter.date(date_start, date_end_exclusive))
        .select("T21")
    )
    hot = firms.max().gt(t21_min_kelvin).rename("hot_mask")
    return hot.multiply(ee.Image.pixelArea()).rename("hot_area_m2")


def reduce_sum_m2_per_feature_to_df(
    area_m2: ee.Image,
    regions: ee.FeatureCollection,
    *,
    band_name: str,
    out_ha_column: str,
    scale_m: float,
    tile_scale: int = 4,
    max_pixels_per_region: float = 1e13,
) -> pd.DataFrame:
    """
    ``reduceRegions`` with ``Reducer.sum()``; maps m² → ha in ``out_ha_column``.

    EE often names the summed band ``sum`` in properties; we accept either.
    """
    reduced = area_m2.reduceRegions(
        collection=regions,
        reducer=ee.Reducer.sum(),
        scale=scale_m,
        tileScale=tile_scale,
        maxPixelsPerRegion=max_pixels_per_region,
    )
    info = reduced.getInfo()
    rows: list[dict[str, Any]] = []
    for f in info.get("features", []):
        p = dict(f.get("properties") or {})
        m2 = p.get(band_name) if p.get(band_name) is not None else p.get("sum")
        p[out_ha_column] = float(m2) / 10000.0 if m2 is not None else None
        rows.append(p)
    return pd.DataFrame(rows)


def reduce_sum_per_feature_to_df(
    image: ee.Image,
    regions: ee.FeatureCollection,
    *,
    band_name: str,
    out_column: str,
    scale_m: float,
    tile_scale: int = 4,
    max_pixels_per_region: float = 1e13,
) -> pd.DataFrame:
    """``reduceRegions`` sum; copy summed band to ``out_column`` without unit conversion."""
    reduced = image.reduceRegions(
        collection=regions,
        reducer=ee.Reducer.sum(),
        scale=scale_m,
        tileScale=tile_scale,
        maxPixelsPerRegion=max_pixels_per_region,
    )
    info = reduced.getInfo()
    rows: list[dict[str, Any]] = []
    for f in info.get("features", []):
        p = dict(f.get("properties") or {})
        val = p.get(band_name) if p.get(band_name) is not None else p.get("sum")
        p[out_column] = float(val) if val is not None else None
        rows.append(p)
    return pd.DataFrame(rows)


def ee_initialize_from_environ(default_project: str = "ipv-exposure-research") -> str:
    """``ee.Initialize(project=...)`` using ``EARTHENGINE_PROJECT`` or default."""
    pid = (os.environ.get("EARTHENGINE_PROJECT") or default_project).strip()
    ee.Initialize(project=pid)
    return pid
