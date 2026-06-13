#!/usr/bin/env python3
"""Compare Moldova PUD ``reg`` values to GADM 3.6 ADM1 names (after GeoJSON conversion)."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import pyreadstat

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


# PUD abbreviations that do not prefix-match GADM after accent strip
_REG_MANUAL: dict[str, str] = {
    "balti": "Bălţi",
    "chisin": "Chişinău",
    "dubasa": "Dubăsari",
    "falest": "Făleşti",
    "hinces": "Hîncesti",
    "riscan": "Rîşcani",
    "singer": "Sîngerei",
    "soldan": "Şoldăneşti",
    "stefan": "Ştefan Voda",
    "strase": "Străşeni",
    "utaga": "Găgăuzia",
    "vulcan": "Găgăuzia",
}

# reg values where PUD label may be sub-ADM1 (locality) but mapped to ADM1 for GADM join
_REG_NOTES: dict[str, str] = {
    "vulcan": (
        "PUD reg likely Vulcănești/Vulcanesti (locality in Găgăuzia); mapped to GADM ADM1 "
        "Găgăuzia — raw survey geography may mix ADM1 and sub-ADM1 labels."
    ),
}


def main() -> None:
    root = find_repo_root()
    pud = root / "data" / "raw" / "Moldova Stata" / "MOLDOVA_VACS_2013_PUD.dta"
    if not pud.is_file():
        raise SystemExit(f"Missing PUD: {pud}")

    df, _ = pyreadstat.read_dta(pud)
    reg_vals = sorted(df["reg"].dropna().astype(str).unique())
    print(f"PUD reg: {len(reg_vals)} distinct values, {len(df):,} rows\n")

    adm1 = load_gadm_geojson("MDA", 1, version="36", root=root)
    gadm_names = sorted(
        {
            str(f["properties"].get("NAME_1") or f["properties"].get("NAME_0") or "")
            for f in adm1["features"]
        }
    )
    gadm_names = [n for n in gadm_names if n]
    print(f"GADM 3.6 ADM1: {len(gadm_names)} polygons")
    for n in gadm_names:
        print(f"  {n}")
    print()

    gadm_by_norm = {_norm(n): n for n in gadm_names}
    exact = []
    fuzzy = []
    unmatched_reg = []
    gadm_norm_to_name = {_norm(n): n for n in gadm_names}

    for r in reg_vals:
        key = _norm(r)
        if key in gadm_by_norm:
            exact.append((r, gadm_by_norm[key]))
            continue
        manual = _REG_MANUAL.get(key)
        if manual and manual in gadm_names:
            fuzzy.append((r, manual))
            continue
        hits = [gn for gn in gadm_names if _norm(gn).startswith(key) or key.startswith(_norm(gn)[:4])]
        if len(hits) == 1:
            fuzzy.append((r, hits[0]))
        else:
            unmatched_reg.append((r, hits))

    print(f"Exact normalized matches: {len(exact)}")
    for r, g in exact:
        if r != g:
            print(f"  reg={r!r} -> GADM {g!r}")

    print(f"\nFuzzy / single-prefix matches: {len(fuzzy)}")
    for r, g in fuzzy:
        print(f"  reg={r!r} -> GADM {g!r}")

    print(f"\nUnmatched reg ({len(unmatched_reg)}):")
    for r, hits in unmatched_reg:
        print(f"  {r!r}  candidates={hits}")

    matched_gadm = {g for _, g in exact} | {g for _, g in fuzzy}
    extra_gadm = [n for n in gadm_names if n not in matched_gadm]
    if extra_gadm:
        print(f"\nGADM ADM1 with no PUD reg match ({len(extra_gadm)}):")
        for n in extra_gadm:
            print(f"  {n!r}")

    def _row(r: str, g: str, match_type: str) -> dict[str, str]:
        return {
            "reg": r,
            "gadm_name_1": g,
            "match_type": match_type,
            "notes": _REG_NOTES.get(_norm(r), ""),
        }

    out = root / "data" / "processed" / "moldova_reg_to_gadm36_adm1.csv"
    rows = [_row(r, g, "exact") for r, g in exact]
    rows += [_row(r, g, "fuzzy") for r, g in fuzzy]
    rows += [_row(r, "", "unmatched") for r, _ in unmatched_reg]
    pd.DataFrame(rows).sort_values("reg").to_csv(out, index=False)
    print(f"\nWrote crosswalk draft: {out}")


if __name__ == "__main__":
    main()
