"""
Researcher-owned Rwanda 2015–16 covariate mapping (Step 2).

Each tuple: (category, variable_notation, stata_column, type_override)

``variable_notation`` is the Stata column name in the merged PUD (single file, both sexes).
``type_override``: non-empty forces type; ``\"\"`` classifies from data; ``\"NA\"`` for absent rows.
"""

from __future__ import annotations

# (category, variable_notation, stata_column, type_override)
RWANDA_2015_COVARIATE_RAW_MAP: list[tuple[str, str, str, str]] = [
    ("Sex", "sex", "sex", "categorical"),
    ("Age", "q2", "q2", "numerical"),
    ("Highest Education Level", "q5", "q5", ""),
    ("Enough Money for…", "NA", "", "NA"),
    ("Lives with biological mom", "q13", "q13", ""),
    ("Lives with biological dad", "q19", "q19", ""),
    ("Lives in foster care", "h25", "h25", ""),
    ("Ever moved", "NA", "", "NA"),
    ("Ever Married", "q25", "q25", ""),
    ("Disability", "NA", "", "NA"),
    ("Community Trust", "q36", "q36", ""),
    ("Community Safety", "q37", "q37", ""),
    ("Supportive friends", "NA", "", "NA"),
    ("Engage in work for pay in last 12 months", "q11", "q11", ""),
    ("Drank alcohol in last 30 days", "q1200", "q1200", ""),
    ("Smoke Cigarettes in last 30 days", "q1201", "q1201", ""),
    ("Mental Health", "q1203a", "q1203a", ""),
    ("Mental Health", "q1203b", "q1203b", ""),
    ("Mental Health", "q1203c", "q1203c", ""),
    ("Mental Health", "q1203d", "q1203d", ""),
    ("Mental Health", "q1203e", "q1203e", ""),
    ("Mental Health", "q1203f", "q1203f", ""),
    ("Main source of drinking water (HH)", "h4", "h4", ""),
    ("Flush toilet (HH)", "h5", "h5", ""),
    ("Shared HH", "h6", "h6", ""),
    ("Electricity (HH)", "h7a", "h7a", ""),
    ("Dwelling floor (HH)", "h9", "h9", ""),
    ("Roof type (HH)", "h10", "h10", ""),
    ("Wall material (HH)", "h11", "h11", ""),
    ("# rooms in household (HH)", "h12", "h12", ""),
    ("# rooms in household (HH)", "h13", "h13", ""),
]
