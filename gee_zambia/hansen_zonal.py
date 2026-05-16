"""
Hansen Global Forest Change — zonal loss area per admin-2 (Zambia).

Dataset (Earth Engine Data Catalog):
  UMD/hansen/global_forest_change_2025_v1_13
Band `lossyear`: 0 = no loss; 1–25 = loss in calendar years 2001–2025 respectively.
So calendar_year C maps to lossyear == (C - 2000) for C in 2001..2025.

Admin boundaries: FAO/GAUL/2015/level2 (see catalog FAO_GAUL_2015_level2), filtered ADM0_NAME == Zambia.

Authentication: see gee_zambia/README.md (earthengine authenticate).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import ee
import pandas as pd

HANSEN_IMAGE_ID = "UMD/hansen/global_forest_change_2025_v1_13"
GAUL_LEVEL2 = "FAO/GAUL/2015/level2"
GAUL_LEVEL2_SIMPLIFIED = "FAO/GAUL_SIMPLIFIED_500m/2015/level2"

# OSM / Nominatim Zambia extent (min_lon, min_lat, max_lon, max_lat) — same as FIRMS notebook
ZAMBIA_RECT_DEG = (21.9990553, -18.0762145, 33.7088556, -8.2749338)


def lossyear_value_for_calendar_year(calendar_year: int) -> int:
    """Map calendar year to Hansen `lossyear` band value (catalog encoding)."""
    if calendar_year < 2001 or calendar_year > 2025:
        raise ValueError(f"Hansen v1.13 supports loss years 2001–2025; got {calendar_year}")
    return calendar_year - 2000


def _load_dotenv_from_repo_root(root: Path) -> None:
    """Populate os.environ from ``root/.env`` when python-dotenv is installed."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = root / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def _apply_earthengine_project_from_dotenv_file(repo_root: Path) -> None:
    """
    If ``EARTHENGINE_PROJECT`` is unset, read it from ``repo_root/.env``.

    Works without ``python-dotenv`` so the CLI still picks up the project id
    when only ``earthengine-api`` is installed.
    """
    if os.environ.get("EARTHENGINE_PROJECT", "").strip():
        return
    env_path = repo_root / ".env"
    if not env_path.is_file():
        return
    try:
        text = env_path.read_text(encoding="utf-8")
    except OSError:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not line.upper().startswith("EARTHENGINE_PROJECT="):
            continue
        val = line.split("=", 1)[1].strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        if val:
            os.environ["EARTHENGINE_PROJECT"] = val
        return


def init_earth_engine(project: str | None = None) -> None:
    """Call ``ee.Initialize``. Uses default credentials (OAuth or service account)."""
    kwargs: dict[str, str] = {}
    if project and str(project).strip():
        kwargs["project"] = str(project).strip()
    elif (p := os.environ.get("EARTHENGINE_PROJECT", "").strip()):
        kwargs["project"] = p
    if "project" not in kwargs:
        raise SystemExit(
            "Earth Engine needs a Google Cloud project id for ee.Initialize(project=...).\n"
            "Fix one of:\n"
            "  • export EARTHENGINE_PROJECT=your-gcp-project-id\n"
            "  • add EARTHENGINE_PROJECT=... to the repository root .env (run this command from the repo, or use --root)\n"
            "  • python -m gee_zambia.hansen_zonal --year 2013 --project your-gcp-project-id\n"
            "Then (once per machine): earthengine authenticate\n"
            "Docs: https://developers.google.com/earth-engine/guides/python_install"
        )
    try:
        ee.Initialize(**kwargs)
    except Exception as e:
        raise SystemExit(
            "Earth Engine initialization failed.\n"
            "If this is an auth error: earthengine authenticate\n"
            "If this is a project error: set EARTHENGINE_PROJECT or use --project\n"
            "Docs: https://developers.google.com/earth-engine/guides/python_install\n"
            f"Original error: {type(e).__name__}: {e}"
        ) from e


def load_zambia_admin2_features(simplified: bool = False) -> ee.FeatureCollection:
    """Second-level admin units for Zambia from FAO GAUL 2015."""
    asset = GAUL_LEVEL2_SIMPLIFIED if simplified else GAUL_LEVEL2
    return ee.FeatureCollection(asset).filter(ee.Filter.eq("ADM0_NAME", "Zambia"))


def zambia_bbox_feature_collection() -> ee.FeatureCollection:
    """Single rectangle geometry as a fallback demo unit."""
    w, s, e, n = ZAMBIA_RECT_DEG
    geom = ee.Geometry.Rectangle([w, s, e, n], proj="EPSG:4326", geodesic=False)
    feat = ee.Feature(geom, {"ADM0_NAME": "Zambia", "ADM1_NAME": "", "ADM2_NAME": "bbox_demo", "ADM2_CODE": -1})
    return ee.FeatureCollection([feat])


def hansen_lossyear_mask(hansen: ee.Image, calendar_year: int) -> ee.Image:
    """Binary mask (0/1) where Hansen attributes loss to the given calendar year."""
    ly = lossyear_value_for_calendar_year(calendar_year)
    return hansen.select("lossyear").eq(ly).rename("loss_mask")


def loss_area_image_m2(hansen: ee.Image, calendar_year: int) -> ee.Image:
    """Per-pixel forest loss area (m²) for pixels matching ``calendar_year``."""
    mask = hansen_lossyear_mask(hansen, calendar_year).selfMask()
    return mask.multiply(ee.Image.pixelArea()).rename("loss_area_m2")


def summarize_loss_area_ha(
    hansen: ee.Image,
    regions: ee.FeatureCollection,
    calendar_year: int,
    *,
    scale_m: int = 30,
    tile_scale: int = 4,
    max_pixels_per_region: float = 1e13,
) -> pd.DataFrame:
    """
    Sum ``loss_area_m2`` per region; returns table with ``loss_area_ha`` and original properties.

    ``max_pixels_per_region`` maps to Earth Engine's ``maxPixelsPerRegion`` on ``reduceRegions``.
    """
    area_img = loss_area_image_m2(hansen, calendar_year)
    reduced = area_img.reduceRegions(
        collection=regions,
        reducer=ee.Reducer.sum(),
        scale=scale_m,
        tileScale=tile_scale,
        maxPixelsPerRegion=max_pixels_per_region,
    )
    info = reduced.getInfo()
    rows = []
    for feat in info.get("features", []):
        props = dict(feat.get("properties") or {})
        m2 = props.get("loss_area_m2")
        if m2 is None:
            m2 = props.get("sum")
        if m2 is None:
            props["loss_area_ha"] = None
        else:
            props["loss_area_ha"] = float(m2) / 10000.0
        props["_hansen_image"] = HANSEN_IMAGE_ID
        props["_loss_calendar_year"] = calendar_year
        props["_lossyear_band_value"] = lossyear_value_for_calendar_year(calendar_year)
        rows.append(props)
    return pd.DataFrame(rows)


def find_repo_root(start: Path | None = None) -> Path:
    cwd = (start or Path.cwd()).resolve()
    if cwd.name == "exposure_notebooks":
        parent = cwd.parent
        if (parent / "gee_zambia").is_dir():
            return parent
    for d in [cwd, *cwd.parents][:20]:
        if (d / "gee_zambia").is_dir() and (d / "data" / "raw").is_dir():
            return d
    return cwd


def run_zambia_hansen_loss_demo(
    calendar_year: int = 2013,
    *,
    output_csv: Path | None = None,
    simplified_geometry: bool = False,
    repo_root: Path | None = None,
    ee_project: str | None = None,
) -> Path:
    """
    Initialize EE, summarize Hansen loss for ``calendar_year`` per Zambia ADM2, write CSV.

    Returns path to the written CSV.
    """
    root = repo_root or find_repo_root()
    _load_dotenv_from_repo_root(root)
    _apply_earthengine_project_from_dotenv_file(root)
    init_earth_engine(project=ee_project)
    out_dir = root / "data" / "raw" / "exposure_gee" / "zambia"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_csv or (out_dir / f"hansen_loss_y{calendar_year}_admin2_zambia.csv")
    hansen = ee.Image(HANSEN_IMAGE_ID)
    regions = load_zambia_admin2_features(simplified=simplified_geometry)
    n = int(regions.size().getInfo())
    if n == 0:
        regions = zambia_bbox_feature_collection()
        print("WARN: GAUL returned 0 features for ADM0_NAME=Zambia; using bbox fallback feature.", file=sys.stderr)

    df = summarize_loss_area_ha(hansen, regions, calendar_year)
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path} ({len(df)} rows).")
    return out_path


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Hansen forest loss area (ha) per Zambia admin-2 (GEE).")
    p.add_argument("--year", type=int, default=2013, help="Calendar year of Hansen loss (2001–2025).")
    p.add_argument("--output", type=Path, default=None, help="Output CSV path (default under data/raw/exposure_gee/zambia/).")
    p.add_argument("--simplified", action="store_true", help="Use GAUL simplified 500m geometries (faster).")
    p.add_argument("--root", type=Path, default=None, help="Repository root (default: auto-detect).")
    p.add_argument(
        "--project",
        type=str,
        default=None,
        metavar="GCP_PROJECT_ID",
        help="Google Cloud project id for ee.Initialize (overrides EARTHENGINE_PROJECT / .env).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    run_zambia_hansen_loss_demo(
        calendar_year=args.year,
        output_csv=args.output,
        simplified_geometry=args.simplified,
        repo_root=args.root,
        ee_project=args.project,
    )


if __name__ == "__main__":
    main()
