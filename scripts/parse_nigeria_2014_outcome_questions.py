#!/usr/bin/env python3
"""Build the Nigeria 2014 five-column outcome codebook from respondent questionnaire PDFs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.docx_export import export_minimal_codebook_docx
from utils.outcomes import OUTCOME_CODEBOOK_COLUMNS, build_outcome_codebook_df, outcome_codebook_to_tsv

RAW = ROOT / "data" / "raw" / "Nigeria Stata"
OUT_DIR = ROOT / "data" / "processed" / "outcome"
OUT_DOCX = OUT_DIR / "jcx_nigeria2014OutcomeCodebook.docx"
OUT_TSV = OUT_DIR / "jcx_nigeria2014OutcomeCodebook.tsv"

YES_NO_99 = "1-YES, 2-NO, 99-DON'T KNOW/DECLINED"
WITNESS_FREQ = "1-NEVER, 2-ONCE, 3-FEW, 4-MANY, 99-DON'T KNOW/DECLINED"
LIFETIME_COUNT = "1-ONCE OR INDICATED, 66-TOO MANY TO RECALL, 99-DON'T KNOW/DECLINED"
NUMBER = "NUMBER (see questionnaire)"
REL_LIST = "relationship categories in questionnaire (see questionnaire)"

QUESTION_TEXT: dict[str, str] = {
    "Q128A": "PV3: Has a parent, adult caregiver, or other adult relative ever punched, kicked, whipped, or beat you with an object?",
    "Q128B": "PV3: Has a parent, adult caregiver, or other adult relative ever choked, suffocated, tried to drown you, or burned you intentionally?",
    "Q128C": "PV3: Has a parent, adult caregiver, or other adult relative ever used or threatened you with a knife, gun, or other weapon?",
    "Q130": "PV3: Most recent time — Did this happen in the last 12 months?",
    "Q132": "PV3: The parent, adult caregiver, or adult relative who did this to you the last time — what was this person's relationship to you?",
    "Q142A": "PV4: Has an adult in your neighborhood ever punched, kicked, whipped, or beat you with an object?",
    "Q142B": "PV4: Has an adult in your neighborhood ever choked, suffocated, tried to drown you, or burned you intentionally?",
    "Q142C": "PV4: Has an adult in your neighborhood ever used or threatened you with a knife, gun, or other weapon?",
    "Q144": "PV4: Most recent time — Did this happen in the last 12 months?",
    "Q146": "PV4: The adult in the neighborhood who did this to you the last time — what was this person's relationship to you?",
    "Q100A": "PV1: Has a romantic partner, boyfriend, or husband ever punched, kicked, whipped, or beat you with an object?",
    "Q100B": "PV1: Has a romantic partner, boyfriend, or husband ever choked, suffocated, tried to drown you, or burned you intentionally?",
    "Q100C": "PV1: Has a romantic partner, boyfriend, or husband ever used or threatened you with a knife, gun, or other weapon?",
    "Q102": "PV1: Most recent time — Did this happen in the last 12 months?",
    "Q116A": "PV2: Has a person your own age ever punched, kicked, whipped, or beat you with an object?",
    "Q116B": "PV2: Has a person your own age ever choked, suffocated, tried to drown you, or burned you intentionally?",
    "Q116C": "PV2: Has a person your own age ever used or threatened you with a knife, gun, or other weapon?",
    "Q118": "PV2: Most recent time — Did this happen in the last 12 months?",
    "Q120": "PV2: The person your own age who did this to you the last time — what was this person's relationship to you?",
    "Q39": "How many times did you see or hear your parent punched, kicked, or beaten up by your other parent, or their boyfriend or girlfriend?",
    "Q40": "Did this happen in the last 12 months? (following witnessing IPV between parents)",
    "Q300A": "Has a parent, adult caregiver, or other adult relative ever told you that you were not loved, or did not deserve to be loved?",
    "Q300B": "Has a parent, adult caregiver, or other adult relative ever said they wished you had never been born or were dead?",
    "Q300C": "Has a parent, adult caregiver, or other adult relative ever ridiculed you or put you down (for example said you were stupid or useless)?",
    "Q302": "EV1: Most recent time — Did this happen in the last 12 months?",
    "Q515": "In the last 12 months, how many times did someone ask you to have sex in exchange for something?",
    "Q700": "Has anyone ever touched you in a sexual way without your permission, but did not try to force you to have sex?",
    "Q701": "SV1: How many times in your life has this happened?",
    "Q702": "SV1A: Touching — most recent — Did this happen to you within the past 12 months?",
    "Q800": "Has anyone ever tried to make you have sex against your will but did not succeed?",
    "Q801": "SV2: How many times in your life has anyone tried to make you have sex against your will but did not succeed?",
    "Q802": "SV2A: Attempted sex — most recent — Did this happen to you within the past 12 months?",
    "Q900": "Has anyone ever physically forced you to have sex and did succeed?",
    "Q901": "SV3: How many times in your life have you been physically forced to have sex?",
    "Q902": "SV3A: Physically forced sex — most recent — Did this happen to you within the past 12 months?",
    "Q1000": "Has anyone ever pressured you to have sex through harassment, threats, or tricks and did succeed?",
    "Q1001": "SV4: How many times in your life has someone pressured you to have sex through harassment, threats, and tricks and did succeed?",
    "Q1002": "SV4A: Pressured into sex — most recent — Did this happen to you within the past 12 months?",
    "Q601": "Have you ever participated in a sex photo or video, or shown your sexual body parts in front of a webcam, whether you wanted to or not?",
    "Q601A": "Were you forced to participate any of those times?",
    "Q200A_M": "PV perpetration (male form wording): Have you ever punched, kicked, whipped, or beaten a current or previous girlfriend, romantic partner, or wife?",
    "Q200B_M": "PV perpetration (male form wording): Have you ever choked, suffocated, tried to drown, or intentionally burned a current or previous partner/wife?",
    "Q200C_M": "PV perpetration (male form wording): Have you ever used or threatened to use a knife, gun, or other weapon against a current or previous partner/wife?",
    "Q201A_M": "PV perpetration (male form wording): Same acts toward someone who was not a current or previous girlfriend, romantic partner, or wife — punched, kicked, whipped, or beaten.",
    "Q201B_M": "PV perpetration (male form wording): Same — choked, suffocated, tried to drown, or intentionally burned.",
    "Q201C_M": "PV perpetration (male form wording): Same — used or threatened to use a knife, gun, or other weapon.",
    "Q1200A": "SV perpetration: Have you ever forced a current or previous partner/husband at the time to have sex when they did not want to?",
}

FORMAT_OVERRIDES: dict[str, str] = {
    "Q39": WITNESS_FREQ,
    "Q40": YES_NO_99,
    "Q132": REL_LIST,
    "Q146": REL_LIST,
    "Q120": REL_LIST,
    "Q701": LIFETIME_COUNT,
    "Q801": LIFETIME_COUNT,
    "Q901": LIFETIME_COUNT,
    "Q1001": LIFETIME_COUNT,
    "Q515": NUMBER,
}


def _format_for(var: str) -> str:
    v = var.upper()
    if v in FORMAT_OVERRIDES:
        return FORMAT_OVERRIDES[v]
    return YES_NO_99


def _fmt(vars_: list[str]) -> str:
    return "; ".join(f"{v}: {_format_for(v)}" for v in vars_)


def _questions(keys: list[str]) -> str:
    return " || ".join(dict.fromkeys(QUESTION_TEXT[k] for k in keys if k in QUESTION_TEXT))


def _row(
    category: str,
    vars_: list[str] | None = None,
    *,
    question_keys: list[str] | None = None,
) -> dict[str, object]:
    v = vars_ or []
    return {"category": category, "vars": v, "question_keys": list(question_keys or [])}


OUTCOME_SPEC = [
    _row(
        "Hit etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q128A", "Q130"],
        question_keys=["Q128A", "Q130"],
    ),
    _row(
        "Hit with object etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q128A", "Q130"],
        question_keys=["Q128A", "Q130"],
    ),
    _row(
        "Choked etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q128B", "Q130"],
        question_keys=["Q128B", "Q130"],
    ),
    _row(
        "Burned etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q128B", "Q130"],
        question_keys=["Q128B", "Q130"],
    ),
    _row(
        "Threatened with knife/weapon etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q128C", "Q130"],
        question_keys=["Q128C", "Q130"],
    ),
    _row(
        "Hit etc from public authority figure in the last 12 months",
        ["Q142A", "Q144", "Q146"],
        question_keys=["Q142A", "Q144", "Q146"],
    ),
    _row(
        "Choked etc from public authority figure in the last 12 months",
        ["Q142B", "Q144", "Q146"],
        question_keys=["Q142B", "Q144", "Q146"],
    ),
    _row(
        "Burned etc from public authority figure in the last 12 months",
        ["Q142B", "Q144", "Q146"],
        question_keys=["Q142B", "Q144", "Q146"],
    ),
    _row(
        "Threatened with knife/weapon etc from public authority figure in the last 12 months",
        ["Q142C", "Q144", "Q146"],
        question_keys=["Q142C", "Q144", "Q146"],
    ),
    _row("Hit etc from intimate partner in the last 12 months"),
    _row(
        "Hit with object etc from intimate partner in the last 12 months",
        ["Q100A", "Q102"],
        question_keys=["Q100A", "Q102"],
    ),
    _row(
        "Choked etc from intimate partner in the last 12 months",
        ["Q100B", "Q102"],
        question_keys=["Q100B", "Q102"],
    ),
    _row(
        "Threatened with knife/weapon etc from intimate partner in the last 12 months",
        ["Q100C", "Q102"],
        question_keys=["Q100C", "Q102"],
    ),
    _row(
        "Hit etc from peer in the last 12 months",
        ["Q116A", "Q118"],
        question_keys=["Q116A", "Q118"],
    ),
    _row(
        "Hit with object etc from peer in the last 12 months",
        ["Q116A", "Q118"],
        question_keys=["Q116A", "Q118"],
    ),
    _row(
        "Choked etc from peer in the last 12 months",
        ["Q116B", "Q118"],
        question_keys=["Q116B", "Q118"],
    ),
    _row(
        "Threatened with knife/weapon etc from peer in the last 12 months",
        ["Q116C", "Q118"],
        question_keys=["Q116C", "Q118"],
    ),
    _row(
        "Hit etc from neighbor in the last 12 months",
        ["Q142A", "Q144", "Q146"],
        question_keys=["Q142A", "Q144", "Q146"],
    ),
    _row(
        "Hit with object etc from neighbor in the last 12 months",
        ["Q142A", "Q144", "Q146"],
        question_keys=["Q142A", "Q144", "Q146"],
    ),
    _row(
        "Choked etc from neighbor in the last 12 months",
        ["Q142B", "Q144", "Q146"],
        question_keys=["Q142B", "Q144", "Q146"],
    ),
    _row(
        "Threatened with knife/weapon etc from neighbor in the last 12 months",
        ["Q142C", "Q144", "Q146"],
        question_keys=["Q142C", "Q144", "Q146"],
    ),
    _row(
        "Witnessed parents/caregivers/adult relatives hit etc in the last 12 months",
        ["Q39", "Q40"],
        question_keys=["Q39", "Q40"],
    ),
    _row("Hit etc from teacher in the last 12 months"),
    _row("Offensive names online in the last 12 months"),
    _row("Physically threatened online in the last 12 months"),
    _row("Harassed for sustained period online in the last 12 months"),
    _row("Stalked online in the last 12 months"),
    _row("Purposely embarrassed online in the last 12 months"),
    _row("Not attended school due to safety in the last 12 months"),
    _row(
        "Said not loved etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q300A", "Q302"],
        question_keys=["Q300A", "Q302"],
    ),
    _row(
        "Wished you were not born or dead etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q300B", "Q302"],
        question_keys=["Q300B", "Q302"],
    ),
    _row(
        "Ridiculed you etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q300C", "Q302"],
        question_keys=["Q300C", "Q302"],
    ),
    _row("Threatened to abandon you etc from parents/caregivers/adult relatives in the last 12 months"),
    _row("Shouted at you etc from parents/caregivers/adult relatives in the last 12 months"),
    _row("Take away privileges etc from parents/caregivers/adult relatives in the last 12 months"),
    _row("Insulted you in front of others etc from intimate partner in the last 12 months"),
    _row("Kept you from having your own money etc from intimate partner in the last 12 months"),
    _row("Kept you from talking to friends or family etc from intimate partner in the last 12 months"),
    _row("Demanded to know where you were etc from intimate partner in the last 12 months"),
    _row("Threatened to physically harm you etc from intimate partner in the last 12 months"),
    _row("Made you feel scared from saying mean things etc from peer in the last 12 months"),
    _row("Told lies etc from peer in the last 12 months"),
    _row("Kept you out of things on purpose etc from peer in the last 12 months"),
    _row(
        "Past 12 months money or goods for sex",
        ["Q515"],
        question_keys=["Q515"],
    ),
    _row(
        "Most recent sexual touching in the last 12 months",
        ["Q700", "Q701", "Q702"],
        question_keys=["Q700", "Q701", "Q702"],
    ),
    _row(
        "Most recent attempted sex without consent/forced sex in the last 12 months",
        ["Q800", "Q801", "Q802"],
        question_keys=["Q800", "Q801", "Q802"],
    ),
    _row(
        "Most recent pressured into sex in the last 12 months",
        ["Q1000", "Q1001", "Q1002"],
        question_keys=["Q1000", "Q1001", "Q1002"],
    ),
    _row(
        "Most recent forced into sex in the last 12 months",
        ["Q900", "Q901", "Q902"],
        question_keys=["Q900", "Q901", "Q902"],
    ),
    _row("Sex acts online in the last 12 months"),
    _row(
        "Sent sexual photo/video online in the last 12 months",
        ["Q601", "Q601A"],
        question_keys=["Q601", "Q601A"],
    ),
    _row("Anything else sexual online in the last 12 months"),
    _row("Sexually harassed online in the last 12 months"),
    _row(
        "Hit etc your partner in the last 12 months",
        ["Q200A"],
        question_keys=["Q200A_M"],
    ),
    _row(
        "Hit with object etc your partner in the last 12 months",
        ["Q200A"],
        question_keys=["Q200A_M"],
    ),
    _row(
        "Choked etc your partner in the last 12 months",
        ["Q200B"],
        question_keys=["Q200B_M"],
    ),
    _row(
        "Threatened with knife/weapon etc your partner in the last 12 months",
        ["Q200C"],
        question_keys=["Q200C_M"],
    ),
    _row(
        "Hit etc someone else who is not your partner in the last 12 months",
        ["Q201A"],
        question_keys=["Q201A_M"],
    ),
    _row(
        "Hit with object etc someone else who is not your partner in the last 12 months",
        ["Q201A"],
        question_keys=["Q201A_M"],
    ),
    _row(
        "Choked etc someone else who is not your partner in the last 12 months",
        ["Q201B"],
        question_keys=["Q201B_M"],
    ),
    _row(
        "Threatened with knife/weapon etc someone else who is not your partner in the last 12 months",
        ["Q201C"],
        question_keys=["Q201C_M"],
    ),
    _row(
        "Forced your partner or ex to have sex in the last 12 months",
        ["Q1200A"],
        question_keys=["Q1200A"],
    ),
    _row("Pressured your partner or ex to talk about sex online/virtual in the last 12 months"),
    _row("Pressured someone else who is not your partner to talk about sex online/virtual in the last 12 months"),
    _row("Pressured your partner or ex to send you sex material online/virtual in the last 12 months"),
    _row("Pressured someone else who is not your partner to send you sex material online/virtual in the last 12 months"),
    _row("Pressured your partner or ex to do anything else sexual online/virtual in the last 12 months"),
]


def _type_for(vars_: list[str]) -> str:
    if not vars_:
        return ""
    f0 = _format_for(vars_[0])
    if f0 == NUMBER:
        return "numerical"
    if f0.startswith("1-YES, 2-NO"):
        return "binary"
    if f0 == REL_LIST:
        return "categorical"
    if "NEVER" in f0 or "ONCE" in f0 and "FEW" in f0:
        return "categorical"
    if "TOO MANY" in f0 or "ONCE OR" in f0:
        return "categorical"
    return "categorical"


def main() -> None:
    rows: list[dict[str, str]] = []
    for spec in OUTCOME_SPEC:
        vars_ = list(spec["vars"])
        qkeys = list(spec["question_keys"] or [])
        if not vars_:
            rows.append({"Category": spec["category"], "Variable": "", "Type": "", "Format": "", "Questions": ""})
            continue
        rows.append({
            "Category": spec["category"],
            "Variable": "; ".join(vars_),
            "Type": _type_for(vars_),
            "Format": _fmt(vars_),
            "Questions": _questions(qkeys) if qkeys else "",
        })

    out_df = build_outcome_codebook_df(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TSV.write_text(outcome_codebook_to_tsv(out_df), encoding="utf-8")
    export_minimal_codebook_docx(out_df, OUT_DOCX, columns=OUTCOME_CODEBOOK_COLUMNS, merge_category_column="Category")
    print(f"Wrote {OUT_DOCX}")
    print(f"Wrote {OUT_TSV}")
    print(f"Rows: {len(out_df)}")


if __name__ == "__main__":
    main()
