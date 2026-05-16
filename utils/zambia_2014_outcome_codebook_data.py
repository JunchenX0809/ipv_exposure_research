"""
Zambia 2014 outcome codebook — researcher-owned rows.

Each dict:
  - ``category``: full label for the **Category** column (team wording only — no instrument notes).
  - ``format_vars``: Stata names whose formats are joined and whose names appear in **Variable**
    as ``"; "``.join(...) (screener first, then timing / follow-ups) so extractors see time columns.
  - ``questions_male_only``: optional; when True, **Questions** use the **male** respondent codebook
    only (used for violence / sexual **perpetration** rows).

All question text and coded formats come from parsed codebooks at build time — not stored here.
"""

from __future__ import annotations

from typing import Any


def _pv_block(
    *,
    generic_hit: str,
    hit_object: str,
    choked: str,
    weapon: str,
    qroot: str,
    timing: list[str],
) -> list[dict[str, Any]]:
    a, b, c = f"Q{qroot}A", f"Q{qroot}B", f"Q{qroot}C"
    return [
        {"category": generic_hit, "format_vars": []},
        {"category": hit_object, "format_vars": [a, *timing]},
        {"category": choked, "format_vars": [b, *timing]},
        {"category": weapon, "format_vars": [c, *timing]},
    ]


ZAMBIA_2014_OUTCOME_SPEC: list[dict[str, Any]] = []

# PV1 intimate partner — timing Q102 / Q109
ZAMBIA_2014_OUTCOME_SPEC += _pv_block(
    generic_hit="Hit etc from a current or previous intimate partner in the last 12 months",
    hit_object="Hit with object etc from a current or previous intimate partner in the last 12 months",
    choked=(
        "Choked, smothered, tried to drown, or burned intentionally by a current or previous "
        "intimate partner in the last 12 months"
    ),
    weapon=(
        "Used or threatened with a knife, gun, or other weapon by a current or previous "
        "intimate partner in the last 12 months"
    ),
    qroot="100",
    timing=["Q102", "Q109"],
)

# PV2 peer — Q118 / Q123
ZAMBIA_2014_OUTCOME_SPEC += _pv_block(
    generic_hit="Hit etc from a person your own age (peer) in the last 12 months",
    hit_object="Hit with object etc from a person your own age (peer) in the last 12 months",
    choked="Choked, smothered, tried to drown, or burned intentionally by a peer in the last 12 months",
    weapon="Used or threatened with a knife, gun, or other weapon by a peer in the last 12 months",
    qroot="116",
    timing=["Q118", "Q123"],
)

# PV3 parents / caregivers — Q130 / Q136
ZAMBIA_2014_OUTCOME_SPEC += _pv_block(
    generic_hit="Hit etc from parents, adult caregivers, or other adult relatives in the last 12 months",
    hit_object=(
        "Hit with object etc from parents, adult caregivers, or other adult relatives "
        "in the last 12 months"
    ),
    choked=(
        "Choked, smothered, tried to drown, or burned intentionally by a parent, adult caregiver, "
        "or other adult relative in the last 12 months"
    ),
    weapon=(
        "Used or threatened with a knife or other weapon by a parent, adult caregiver, "
        "or other adult relative in the last 12 months"
    ),
    qroot="128",
    timing=["Q130", "Q136"],
)

# PV4 neighbourhood adults — Q144 / Q149
ZAMBIA_2014_OUTCOME_SPEC += _pv_block(
    generic_hit="Hit etc from an adult in the neighbourhood or community in the last 12 months",
    hit_object=(
        "Hit with object etc from an adult in the neighbourhood or community in the last 12 months"
    ),
    choked=(
        "Choked, smothered, tried to drown, or burned intentionally by an adult in the "
        "neighbourhood or community in the last 12 months"
    ),
    weapon=(
        "Used or threatened with a knife, gun, or other weapon by an adult in the neighbourhood "
        "or community in the last 12 months"
    ),
    qroot="142",
    timing=["Q144", "Q149"],
)

# Witnessing
ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": (
            "Witnessed a parent physically hurt by the other parent or their partner "
            "in the last 12 months"
        ),
        "format_vars": ["Q39", "Q40"],
    },
    {
        "category": (
            "Witnessed a parent punch, kick, or beat brothers or sisters in the last 12 months"
        ),
        "format_vars": ["Q41", "Q42"],
    },
    {
        "category": (
            "Witnessed someone attacked outside the home or family environment in the last 12 months"
        ),
        "format_vars": ["Q43", "Q44"],
    },
]

# Emotional caregiver EV1
ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": (
            "Emotional abuse by a parent, adult caregiver, or other adult relative"
        ),
        "format_vars": [],
    },
    {
        "category": (
            "Told not loved or did not deserve to be loved by a parent, adult caregiver, "
            "or other adult relative in the last 12 months"
        ),
        "format_vars": ["Q300A", "Q302", "Q306"],
    },
    {
        "category": (
            "Told wished never born or dead by a parent, adult caregiver, or other adult relative "
            "in the last 12 months"
        ),
        "format_vars": ["Q300B", "Q302", "Q306"],
    },
    {
        "category": (
            "Ridiculed or put down by a parent, adult caregiver, or other adult relative "
            "in the last 12 months"
        ),
        "format_vars": ["Q300C", "Q302", "Q306"],
    },
]

# Emotional peer EV2
ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": "Emotional abuse by a person your own age (peer)",
        "format_vars": [],
    },
    {
        "category": (
            "Scared or made to feel really bad on purpose by a peer in the last 12 months"
        ),
        "format_vars": ["Q310A", "Q312", "Q319"],
    },
    {
        "category": "Lies, rumours, or others disliked by a peer in the last 12 months",
        "format_vars": ["Q310B", "Q312", "Q319"],
    },
    {
        "category": "Excluded or left out on purpose by a peer in the last 12 months",
        "format_vars": ["Q310C", "Q312", "Q319"],
    },
    {
        "category": (
            "Emotional abuse by a current or previous intimate partner in the last 12 months"
        ),
        "format_vars": [],
    },
]

# Sexual violence
ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": "Unwanted sexual touching without permission in the last 12 months",
        "format_vars": ["Q700", "Q702", "Q712"],
    },
    {
        "category": "Attempted sex against your will without success in the last 12 months",
        "format_vars": ["Q800", "Q802", "Q812"],
    },
    {
        "category": "Physically forced to have sex when someone succeeded in the last 12 months",
        "format_vars": ["Q900", "Q902", "Q915"],
    },
    {
        "category": (
            "Pressured or tricked into sex through harassment, threats, or tricks when someone "
            "succeeded in the last 12 months"
        ),
        "format_vars": ["Q1000", "Q1002", "Q1014"],
    },
]

# Counts / technology
ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": "Received food, favours, or gifts in exchange for sex in the last 12 months",
        "format_vars": ["Q508"],
    },
    {
        "category": "Asked to have sex in exchange for something in the last 12 months",
        "format_vars": ["Q515"],
    },
    {
        "category": (
            "Participated in a sexual photo or video or showed sexual body parts on camera "
            "in the last 12 months"
        ),
        "format_vars": ["Q606"],
    },
    {
        "category": (
            "Asked or pressured to participate in a sexual photo or video or show body parts "
            "in the last 12 months"
        ),
        "format_vars": ["Q612"],
    },
    {
        "category": "Internet- or technology-facilitated violence in the last 12 months",
        "format_vars": [],
    },
]

# Community / school / mental health — no 12-month item as specified
ZAMBIA_2014_OUTCOME_SPEC += [
    {"category": "Missed school due to violence in the past 12 months", "format_vars": []},
    {"category": "Felt unsafe at school in the past 12 months", "format_vars": []},
    {"category": "Community trust in the past 12 months", "format_vars": []},
    {"category": "Community safety in the past 12 months", "format_vars": []},
    {"category": "Knew where to seek help after violence in the past 12 months", "format_vars": []},
    {
        "category": "Psychological distress frequency in the past 12 months",
        "format_vars": [],
    },
    {
        "category": (
            "Physical violence by a teacher, police officer, or other authority figure "
            "in the last 12 months"
        ),
        "format_vars": [],
    },
]

# Violence perpetration — physical (male questionnaire wording in output)
ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": "Hit etc your partner in the last 12 months",
        "format_vars": ["Q200A"],
        "questions_male_only": True,
    },
    {
        "category": "Hit with object etc your partner in the last 12 months",
        "format_vars": [],
    },
    {
        "category": "Choked etc your partner in the last 12 months",
        "format_vars": ["Q200B"],
        "questions_male_only": True,
    },
    {
        "category": "Threatened with knife/weapon etc your partner in the last 12 months",
        "format_vars": ["Q200C"],
        "questions_male_only": True,
    },
    {
        "category": "Hit etc someone else who is not your partner in the last 12 months",
        "format_vars": ["Q201A"],
        "questions_male_only": True,
    },
    {
        "category": "Hit with object etc someone else who is not your partner in the last 12 months",
        "format_vars": [],
    },
    {
        "category": "Choked etc someone else who is not your partner in the last 12 months",
        "format_vars": ["Q201B"],
        "questions_male_only": True,
    },
    {
        "category": (
            "Threatened with knife/weapon etc someone else who is not your partner "
            "in the last 12 months"
        ),
        "format_vars": ["Q201C"],
        "questions_male_only": True,
    },
]

# Sexual perpetration (male questionnaire wording in output)
ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": (
            "Forced sex on a current or previous partner when they did not want to "
            "in the last 12 months"
        ),
        "format_vars": ["Q1200A"],
        "questions_male_only": True,
    },
    {
        "category": (
            "Forced sex on someone who was not your partner when they did not want to "
            "in the last 12 months"
        ),
        "format_vars": ["Q1200B"],
        "questions_male_only": True,
    },
]

ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": "Online sexual perpetration",
        "format_vars": [],
    },
]

# Household
ZAMBIA_2014_OUTCOME_SPEC += [
    {
        "category": "Adult household member died in the past 12 months",
        "format_vars": ["H19"],
    },
]
