"""
Researcher-owned Zambia 2014 covariate mapping (Step 2).

Each tuple: (category, variable_notation, qnum_male, qnum_female, qnum_hoh, type_override)

``type_override``: non-empty to force type; ``\"\"`` lets the build script classify from PUD.

Mirrors ``RAW_MAP`` in ``notebooks/zambia_v2_covariates.ipynb`` (kept in sync manually).
"""

from __future__ import annotations

# (category, variable_notation, qnum_male, qnum_female, qnum_hoh, type_override)
ZAMBIA_2014_COVARIATE_RAW_MAP: list[tuple[str, str, str, str, str, str]] = [
    ("Sex", "Two files", "", "", "", "categorical"),
    ("Age", "Q2; F2", "M2", "F2", "", ""),
    ("Highest Education Level", "Q5; F5", "M5", "F5", "", ""),
    ("Enough Money for…", "Q7AA", "", "", "", "binary"),
    ("Enough Money for…", "Q7AB", "", "", "", "binary"),
    ("Enough Money for…", "Q7AD", "", "", "", "binary"),
    ("Lives with biological mom", "Q13; F13", "M13", "F13", "", ""),
    ("Lives with biological dad", "Q19; F19", "M19", "F19", "", ""),
    ("Ever Married", "Q25; F25", "M25", "F25", "", ""),
    ("Disability", "NA", "", "", "", "NA"),
    ("Community Trust", "Q36; F36", "M36", "F36", "", ""),
    ("Community Safety", "Q37; F37", "M37", "F37", "", ""),
    ("Supportive friends", "Q7; F7", "M7", "F7", "", ""),
    (
        "Engage in work for pay in last 12 months",
        "Q11; F11",
        "M11",
        "F11",
        "",
        "",
    ),
    ("Drank alcohol in last 30 days", "Q1300; F1300", "M1300", "F1300", "", ""),
    ("Smoke Cigarettes in last 30 days", "Q1301; F1301", "M1301", "F1301", "", ""),
    (
        "Mental Health",
        "Q1303A–Q1303F; F1303A–F1303F",
        "M1303A",
        "F1303A",
        "",
        "categorical",
    ),
    (
        "Main source of drinking water (HH)",
        'H4 (and H4_OT if "other")',
        "",
        "",
        "H4",
        "",
    ),
    ("Flush toilet (HH)", "H5 (and H5_OT)", "", "", "H5", ""),
    ("Shared HH", "H6", "", "", "H6", ""),
    ("Electricity (HH)", "H7A–H7G", "", "", "H7A", ""),
    ("Dwelling floor (HH)", "H9", "", "", "H9", ""),
    ("Roof type (HH)", "H10", "", "", "H10", ""),
    ("Wall material (HH)", "H11", "", "", "H11", ""),
    ("# rooms in household (HH)", "H12", "", "", "H12", ""),
    ("# rooms in household (HH)", "H13", "", "", "H13", ""),
]
