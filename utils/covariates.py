"""
Covariate codebook helpers: auto-scan .dta labels for covariate candidates,
classify variable types, and build the 5-column harmonized DataFrame.

The covariate mapping is owned by the notebook author; this module provides
scanning heuristics and output formatting.
"""

from __future__ import annotations

import re
from typing import Mapping, Sequence

import pandas as pd

# ---------------------------------------------------------------------------
# Canonical covariate categories with keyword patterns for label matching
# ---------------------------------------------------------------------------

COVARIATE_CATEGORIES: Sequence[tuple[str, list[str]]] = [
    ("Sex", [
        r"^sex of respondent",
        r"^sex of.*head",
        r"^sex$",
        r"sex of household member",
    ]),
    ("Age", [
        r"how old are you",
        r"^age$",
        r"^age of respondent",
    ]),
    ("Highest Education Level", [
        "highest level of schooling",
        "highest level of education",
        "highest grade",
    ]),
    ("Enough Money for…", [
        "enough money",
        "household has enough",
        r"worried about.*\$.*food",
        "worried about money for food",
    ]),
    ("Lives with biological mom", [
        "biological mother.*living with",
        "is your biological mother",
    ]),
    ("Lives with biological dad", [
        "biological father.*living with",
        "is your biological father",
    ]),
    ("Lives in foster care", [
        "foster care",
        "foster parent",
        "foster home",
    ]),
    ("Ever moved", [
        "ever moved",
        "moved from one place",
        "changed residence",
    ]),
    ("Ever Married", [
        "ever been married",
        "ever married",
        "lived like married",
    ]),
    ("Disability", [
        "disability",
        "difficulty seeing",
        "difficulty hearing",
        "difficulty walking",
    ]),
    ("Community Trust", [
        "trust.*people.*community",
        "trust people.*living",
        "community.*trust",
    ]),
    ("Community Safety", [
        r"how safe.*community",
        r"safe do you feel.*community",
    ]),
    ("Supportive friends", [
        "talk to friends.*important",
        "friends about important",
    ]),
    ("Engage in work for pay in last 12 months", [
        r"past 12 months.*engage.*work",
        r"engage in any work",
    ]),
    ("Drank alcohol in last 30 days", [
        "drink alcohol",
        "drank alcohol",
        r"days.*drink.*alcohol",
        r"alcohol.*drunk",
    ]),
    ("Smoke Cigarettes in last 30 days", [
        "smoke cigarettes",
        "smoked cigarettes",
        r"cigarettes.*daily",
    ]),
    ("Mental Health", [
        r"how often did you feel",
        r"\bNERVOUS\b",
        r"\bHOPELESS\b",
        r"\bRESTLESS\b",
        r"everything was an effort",
        r"\bWORTHLESS\b",
    ]),
    ("Main source of drinking water (HH)", [
        "source of drinking water",
        "main source.*water",
    ]),
    ("Flush toilet (HH)", [
        "toilet facility",
        "kind of toilet",
    ]),
    ("Shared HH", [
        "share this facility",
    ]),
    ("Electricity (HH)", [
        r"^h\d.*electricity",
        r"^electricity$",
    ]),
    ("Dwelling floor (HH)", [
        "material.*dwelling.*floor",
        "material of the.*floor",
    ]),
    ("Roof type (HH)", [
        "material.*roof",
        "material of the roof",
    ]),
    ("Wall material (HH)", [
        "material.*wall",
        "material of the wall",
    ]),
    ("# rooms in household (HH)", [
        "how many rooms",
        "rooms.*household",
        "rooms.*sleeping",
    ]),
]


def _label_matches(label: str | None, patterns: list[str]) -> bool:
    """Case-insensitive regex match of any pattern against a label string."""
    if not label:
        return False
    return any(re.search(p, label, re.IGNORECASE) for p in patterns)


def search_dta_for_covariates(
    df: pd.DataFrame,
    meta,
    *,
    categories: Sequence[tuple[str, list[str]]] | None = None,
) -> pd.DataFrame:
    """
    Scan Stata variable labels for keyword hits against each covariate category.

    Returns a DataFrame with columns: category, column, stata_label, dtype,
    nunique. One row per (category, matching column) pair; categories with
    no matches get a stub row.
    """
    cats = categories or COVARIATE_CATEGORIES
    labels: dict[str, str] = dict(meta.column_names_to_labels or {})
    rows: list[dict] = []

    for cat_name, patterns in cats:
        hits: list[str] = []
        for col in df.columns:
            lab = labels.get(col, "")
            if _label_matches(lab, patterns):
                hits.append(col)

        if not hits:
            rows.append({
                "category": cat_name,
                "column": "",
                "stata_label": "— no match —",
                "dtype": "",
                "nunique": pd.NA,
            })
        else:
            for col in hits:
                rows.append({
                    "category": cat_name,
                    "column": col,
                    "stata_label": labels.get(col, ""),
                    "dtype": str(df[col].dtype),
                    "nunique": int(df[col].nunique()),
                })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Variable type classification
# ---------------------------------------------------------------------------

def classify_variable_type(
    series: pd.Series,
    *,
    binary_max_unique: int = 3,
    categorical_max_unique: int = 30,
) -> str:
    """
    Heuristic classification: binary, categorical, or numerical.

    - binary: <= binary_max_unique non-null distinct values (accounts for
      1/2 plus a don't-know code like 98/99)
    - categorical: int or object with <= categorical_max_unique levels
    - numerical: everything else (continuous floats, large-range ints)
    """
    sn = series.dropna()
    if sn.empty:
        return "NA"
    n = int(sn.nunique())
    if n <= binary_max_unique:
        return "binary"
    if n <= categorical_max_unique:
        return "categorical"
    return "numerical"


# ---------------------------------------------------------------------------
# Build the 5-column harmonized codebook DataFrame
# ---------------------------------------------------------------------------

CODEBOOK_COLUMNS: Sequence[str] = (
    "category",
    "variable",
    "type",
    "format",
    "question",
)


def build_covariate_codebook_df(
    entries: Sequence[Mapping[str, str]],
) -> pd.DataFrame:
    """
    Build the 5-column covariate codebook DataFrame from researcher-provided
    entries.

    Each entry is a dict with keys matching ``CODEBOOK_COLUMNS``:
    category, variable, type, format, question. Missing keys become empty
    strings.
    """
    rows = []
    for entry in entries:
        rows.append({col: entry.get(col, "") for col in CODEBOOK_COLUMNS})
    return pd.DataFrame(rows, columns=list(CODEBOOK_COLUMNS))


def covariate_codebook_to_tsv(codebook_df: pd.DataFrame) -> str:
    """Tab-separated text for pasting into Excel / codebook."""
    return codebook_df.to_csv(sep="\t", index=False)
