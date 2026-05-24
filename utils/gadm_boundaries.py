"""
Load GADM administrative boundaries from local GeoJSON for Earth Engine zonal stats.

GADM is not available as a standard EE catalog layer. Country GeoJSON files live under
``data/raw/gadm/{version}/`` (see ``data/raw/gadm/README.md``).

District / province codes in export tables map from GADM ``ID_2`` / ``ID_1`` (teammate
``ISO_2`` / ``ISO_1`` in ``skills/GADM_admin_areas_v1.xlsx``). Properties are normalized
to ``ADM1_NAME``, ``ADM2_NAME``, ``ADM1_CODE``, ``ADM2_CODE`` so ``utils.adam_modis_export``
works unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import ee

from utils.repo_paths import find_repo_root

# Short key -> directory name under data/raw/gadm/
GADM_VERSIONS: dict[str, str] = {
    "40": "4.0",
    "36": "3.6",
    "28": "2.8",
}


def gadm_geojson_path(
    iso3: str,
    level: int,
    *,
    version: str = "40",
    root: Path | None = None,
) -> Path:
    """
    Path to ``gadm{version}_{ISO3}_{level}.json`` under ``data/raw/gadm/{version_dir}/``.

    ``iso3`` is GADM ``ID_0`` (e.g. ``ZWE`` for Zimbabwe), not always ISO 3166-1 alpha-3.
    """
    if version not in GADM_VERSIONS:
        raise ValueError(f"Unknown GADM version {version!r}; expected one of {list(GADM_VERSIONS)}")
    repo = root or find_repo_root()
    version_dir = GADM_VERSIONS[version]
    filename = f"gadm{version}_{iso3.upper()}_{level}.json"
    path = repo / "data" / "raw" / "gadm" / version_dir / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"GADM GeoJSON not found: {path}\n"
            f"Download from https://geodata.ucdavis.edu/gadm/gadm{version}/json/ "
            f"(see data/raw/gadm/README.md)."
        )
    return path


def load_gadm_geojson(
    iso3: str,
    level: int,
    *,
    version: str = "40",
    root: Path | None = None,
) -> dict[str, Any]:
    """Load a GADM GeoJSON ``FeatureCollection`` dict from disk."""
    path = gadm_geojson_path(iso3, level, version=version, root=root)
    data = json.loads(path.read_text(encoding="utf-8"))
    if "features" not in data or not isinstance(data["features"], list):
        raise ValueError(f"Expected GeoJSON FeatureCollection in {path}")
    return data


def adm1_id_by_name(
    iso3: str,
    *,
    version: str = "40",
    root: Path | None = None,
) -> dict[str, str]:
    """``NAME_1`` -> ``ID_1`` from the ADM1 GeoJSON (ADM2 features only carry ``NAME_1``)."""
    data = load_gadm_geojson(iso3, 1, version=version, root=root)
    out: dict[str, str] = {}
    for feat in data["features"]:
        props = feat.get("properties") or {}
        name = props.get("NAME_1")
        id1 = props.get("ID_1")
        if name is not None and id1 is not None:
            out[str(name)] = str(id1)
    return out


def normalize_gadm_level2_features(
    features: list[dict[str, Any]],
    *,
    adm1_ids: dict[str, str],
) -> list[dict[str, Any]]:
    """
    Copy features with properties aligned to GAUL-style names used in export code.

    ``ADM1_CODE`` / ``ADM2_CODE`` hold GADM ``ID_1`` / ``ID_2`` (export ``adm*_pcode``).
    """
    normalized: list[dict[str, Any]] = []
    for feat in features:
        props = dict(feat.get("properties") or {})
        name1 = props.get("NAME_1")
        name2 = props.get("NAME_2")
        id2 = props.get("ID_2")
        if name1 is None or name2 is None or id2 is None:
            raise ValueError(f"GADM ADM2 feature missing NAME_1/NAME_2/ID_2: {props!r}")
        id1 = adm1_ids.get(str(name1))
        if id1 is None:
            raise KeyError(f"No ADM1 ID_1 for NAME_1={name1!r}; check ADM1 GeoJSON.")

        new_props = {
            "ADM0_NAME": props.get("COUNTRY"),
            "ADM0_CODE": props.get("ID_0"),
            "ADM1_NAME": str(name1),
            "ADM1_CODE": id1,
            "ADM2_NAME": str(name2),
            "ADM2_CODE": str(id2),
            # Keep GADM originals for debugging / crosswalks
            "GADM_ID_1": id1,
            "GADM_ID_2": str(id2),
            "HASC_2": props.get("HASC_2"),
        }
        normalized.append(
            {
                "type": "Feature",
                "geometry": feat["geometry"],
                "properties": new_props,
            }
        )
    return normalized


def gadm_level2_feature_collection(
    iso3: str,
    *,
    version: str = "40",
    root: Path | None = None,
) -> ee.FeatureCollection:
    """
    GADM admin-2 ``ee.FeatureCollection`` with normalized property names for zonal export.

    Parameters
    ----------
    iso3:
        GADM country code (``ID_0``), e.g. ``ZWE`` for Zimbabwe.
    """
    adm1_ids = adm1_id_by_name(iso3, version=version, root=root)
    data = load_gadm_geojson(iso3, 2, version=version, root=root)
    features = normalize_gadm_level2_features(data["features"], adm1_ids=adm1_ids)
    return ee.FeatureCollection(features)
