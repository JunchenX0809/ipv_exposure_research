#!/usr/bin/env python3
"""Compare Lesotho PUD ``District`` values to GADM 3.6 ADM1 names / codes.

Mirrors ``scripts/moldova_reg_gadm_match.py``. Lesotho has no GADM ADM2, and the
VACS PUD only carries the 10 districts (ADM1), so survey<->exposure linkage is a
district -> GADM ``ID_1`` crosswalk. Writes ``data/processed/lesotho_district_to_gadm36_adm1.csv``.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from utils.gadm_boundaries import load_gadm_geojson
from utils.repo_paths import find_repo_root


def _norm(s: str) -> str:
    """Loose match key: lowercase, strip accents/punctuation."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    return re.sub(r"[^a-z0-9]", "", s)


# PUD spellings that do not normalize-match GADM (same district, alternate spelling)
_DISTRICT_MANUAL: dict[str, str] = {
    "bothabotha": "Butha-Buthe",  # PUD "Botha-Botha" == GADM "Butha-Buthe" (LSO.2_1)
}

_DISTRICT_NOTES: dict[str, str] = {
    "bothabotha": "PUD 'Botha-Botha' is an alternate spelling of GADM 'Butha-Buthe'.",
}


def main() -> None:
    root = find_repo_root()
    pud = root / "data" / "raw" / "Lesotho Stata" / "LESOTHO_VACS_2018_PUD_UR.dta"
    if not pud.is_file():
        raise SystemExit(f"Missing PUD: {pud}")

    import pyreadstat

    df, _ = pyreadstat.read_dta(pud)
    dist_vals = sorted(df["District"].dropna().astype(str).unique())
    print(f"PUD District: {len(dist_vals)} distinct values, {len(df):,} rows\n")

    adm1 = load_gadm_geojson("LSO", 1, version="36", root=root)
    gadm = [
        (str(f["properties"].get("NAME_1") or ""), str(f["properties"].get("ID_1") or ""))
        for f in adm1["features"]
    ]
    gadm = [(n, gid) for n, gid in gadm if n]
    name_to_gid = {n: gid for n, gid in gadm}
    gadm_names = sorted(name_to_gid)
    print(f"GADM 3.6 ADM1: {len(gadm_names)} polygons")
    for n in gadm_names:
        print(f"  {n} ({name_to_gid[n]})")
    print()

    gadm_by_norm = {_norm(n): n for n in gadm_names}
    exact: list[tuple[str, str]] = []
    fuzzy: list[tuple[str, str]] = []
    unmatched: list[str] = []

    for d in dist_vals:
        key = _norm(d)
        if key in gadm_by_norm:
            exact.append((d, gadm_by_norm[key]))
            continue
        manual = _DISTRICT_MANUAL.get(key)
        if manual and manual in name_to_gid:
            fuzzy.append((d, manual))
            continue
        unmatched.append(d)

    print(f"Exact normalized matches: {len(exact)}")
    print(f"Manual / spelling matches: {len(fuzzy)}")
    for d, g in fuzzy:
        print(f"  District={d!r} -> GADM {g!r}")
    if unmatched:
        print(f"\nUnmatched District ({len(unmatched)}): {unmatched}")

    matched = {g for _, g in exact} | {g for _, g in fuzzy}
    extra = [n for n in gadm_names if n not in matched]
    if extra:
        print(f"\nGADM ADM1 with no PUD District match ({len(extra)}): {extra}")

    def _row(d: str, g: str, match_type: str) -> dict[str, str]:
        return {
            "district": d,
            "gadm_name_1": g,
            "gadm_id_1": name_to_gid.get(g, ""),
            "match_type": match_type,
            "notes": _DISTRICT_NOTES.get(_norm(d), ""),
        }

    rows = [_row(d, g, "exact") for d, g in exact]
    rows += [_row(d, g, "manual") for d, g in fuzzy]
    rows += [_row(d, "", "unmatched") for d in unmatched]

    out = root / "data" / "processed" / "lesotho_district_to_gadm36_adm1.csv"
    pd.DataFrame(rows).sort_values("district").to_csv(out, index=False)
    print(f"\nWrote crosswalk: {out}")


if __name__ == "__main__":
    main()
