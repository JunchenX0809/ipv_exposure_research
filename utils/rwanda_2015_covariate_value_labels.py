"""
Curated code→meaning maps for Rwanda 2015–16 covariates.

The public PUD has variable labels but **no** Stata value labels. These maps apply
only where the instrument scale is explicit (yes/no, K6, trust/safety wording in
labels, smoking frequency text in q1201's label) and codes match ``value_counts``.
"""

from __future__ import annotations

# Shared VACS-style scales (title case for Word table readability)
_YES_NO: dict[float, str] = {1.0: "Yes", 2.0: "No"}
_YES_NO_99: dict[float, str] = {1.0: "Yes", 2.0: "No", 99.0: "Don't know"}

_K6: dict[float, str] = {
    1.0: "All of the time",
    2.0: "Most of the time",
    3.0: "Some of the time",
    4.0: "A little of the time",
    5.0: "None of the time",
    99.0: "Don't know",
}

_TRUST: dict[float, str] = {
    1.0: "A lot",
    2.0: "Some",
    3.0: "Not too much",
    4.0: "Not at all",
    99.0: "Don't know",
}

_SAFETY: dict[float, str] = {
    1.0: "Very safe",
    2.0: "Somewhat safe",
    3.0: "Not safe at all",
    99.0: "Don't know",
}

_SMOKING: dict[float, str] = {
    1.0: "Daily",
    2.0: "Occasionally",
    3.0: "Not at all",
    99.0: "Don't know",
}

_FRIENDS: dict[float, str] = {
    1.0: "A lot",
    2.0: "Some",
    3.0: "Not very much",
    4.0: "Not at all",
    99.0: "Don't know",
}

# column → {numeric_code: meaning}
RWANDA_KNOWN_VALUE_LABELS: dict[str, dict[float, str]] = {
    "sex": {1.0: "Male", 2.0: "Female"},
    "q13": dict(_YES_NO),
    "q19": dict(_YES_NO_99),
    "q11": dict(_YES_NO),
    "q25": dict(_YES_NO_99),
    "h25": dict(_YES_NO_99),
    "q36": dict(_TRUST),
    "q37": dict(_SAFETY),
    "q7": dict(_FRIENDS),
    "q1201": dict(_SMOKING),
    "q1203a": dict(_K6),
    "q1203b": dict(_K6),
    "q1203c": dict(_K6),
    "q1203d": dict(_K6),
    "q1203e": dict(_K6),
    "q1203f": dict(_K6),
    "h6": dict(_YES_NO),
    "h7a": dict(_YES_NO),
}
