#!/usr/bin/env python3
"""Build the Tanzania 2009 five-column outcome codebook from questionnaire PDFs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.docx_export import export_minimal_codebook_docx
from utils.outcomes import OUTCOME_CODEBOOK_COLUMNS, build_outcome_codebook_df, outcome_codebook_to_tsv

RAW = ROOT / "data" / "raw" / "Tanzania 2009 Stata"
OUT_DIR = ROOT / "data" / "processed" / "outcome"
OUT_DOCX = OUT_DIR / "jcx_tanzania2009OutcomeCodebook.docx"
OUT_TSV = OUT_DIR / "jcx_tanzania2009OutcomeCodebook.tsv"

YES_NO = "1-YES, 2-NO, 88-DON'T KNOW, 99-DECLINED"
LIFETIME_COUNT = "0-NONE, 1-AT LEAST ONCE, 88-DON'T KNOW, 99-DECLINED"
NUMBER = "NUMBER (see questionnaire)"

QUESTION_TEXT: dict[str, str] = {
    "F101_STAR": (
        "Female respondent (F101*): Has a parent or any adult relative ever punched, kicked or whipped you? "
        "Includes follow-up on frequency, age first happened, and past 12 months (item D in questionnaire)."
    ),
    "M101_STAR": (
        "Male respondent (M101*): Has a parent or any adult relative ever punched, kicked or whipped you? "
        "Includes follow-up on frequency, age first happened, and past 12 months (item D in questionnaire)."
    ),
    "F103_STAR": (
        "Female respondent (F103*): Have you ever been punched, kicked, or whipped by teachers, policemen, "
        "religious leaders, soldiers, or other authority figures? Includes follow-up including past 12 months."
    ),
    "M103_STAR": (
        "Male respondent (M103*): Have you ever been punched, kicked, or whipped by teachers, policemen, "
        "religious leaders, soldiers, or other authority figures? Includes follow-up including past 12 months."
    ),
    "F100_SLAP": (
        "Female respondent (F100*), sub-item (a): Slapped you or pushed you? "
        "Partner block includes lifetime counts and past 12 months for each act."
    ),
    "M100_SLAP": (
        "Male respondent (M100*), sub-item (a): Slapped you or pushed you? "
        "Partner block includes lifetime counts and past 12 months for each act."
    ),
    "F100_FIST": (
        "Female respondent (F100*), sub-item (b): Hit you with a fist or kicked you? "
        "Partner block includes lifetime counts and past 12 months for each act."
    ),
    "M100_FIST": (
        "Male respondent (M100*), sub-item (b): Hit you with a fist or kicked you? "
        "Partner block includes lifetime counts and past 12 months for each act."
    ),
    "F100_WEAPON": (
        "Female respondent (F100*), sub-item (c): Threatened or used a gun, knife, or other weapon against you? "
        "Partner block includes lifetime counts and past 12 months for each act."
    ),
    "M100_WEAPON": (
        "Male respondent (M100*), sub-item (c): Threatened or used a gun, knife, or other weapon against you? "
        "Partner block includes lifetime counts and past 12 months for each act."
    ),
    "F301": "Female (F301): How many times in your life has anyone touched you in a sexual way against your will, but did not try to force you to have sex?",
    "F317": "Female (F317): Did this incident happen to you within the past 12 months?",
    "M301": "Male (M301): How many times in your life has anyone touched you in a sexual way against your will, but did not try to force you to have sex?",
    "M317": "Male (M317): Did this incident happen to you within the past 12 months?",
    "F401": "Female (F401): How many times in your life has anyone tried to make you have sex against your will, but did not succeed?",
    "F419": "Female (F419): Did this incident happen to you within the past 12 months?",
    "M401": "Male (M401): How many times in your life has anyone tried to make you have sex against your will, but did not succeed?",
    "M419": "Male (M419): Did this incident happen to you within the past 12 months?",
    "F501": (
        "Female (F501): How many times in your life have you been physically forced to have sex against your will "
        "and the sex was completed?"
    ),
    "F531": "Female (F531): Did this incident happen to you within the past 12 months?",
    "M501": (
        "Male (M501): How many times in your life have you been physically forced to have sexual intercourse against your will and was completed?"
    ),
    "M432": "Male (M432): Did this incident happen to you within the past 12 months?",
    "F601": (
        "Female (F601): How many times in your life has someone pressured you to have sex and completed the sex "
        "when you actually did not want to have sex?"
    ),
    "F634": "Female (F634): Did this incident happen to you within the past 12 months?",
    "M601": (
        "Male (M601): How many times in your life has someone pressured you to have sex and completed the sex "
        "when you actually did not want to have sex?"
    ),
    "M632": "Male (M632): Did this incident happen to you within the past 12 months?",
    "F63": (
        "Female (F63): During the past 12 months, how many sexual partners gave you food, drugs or other favors "
        "so that you have sex with them?"
    ),
    "M56": "Male (M56): In the last 12 months, how many sexual partners were people who gave you money to have sex with them?",
    "F200_STAR": "Female (F200*): When you were a child, did anybody call you using bad names?",
    "F201_STAR": "Female (F201*): When you were a child, did any person ever make you feel unwanted?",
    "F202_STAR": "Female (F202*): When you were a child, did anyone threaten to abandon you?",
}


def _format_for(var: str) -> str:
    v = var.upper()
    if v in {"F301", "M301", "F401", "M401", "F501", "M501", "F601", "M601"}:
        return LIFETIME_COUNT
    if v in {"F63", "M56"}:
        return NUMBER
    return YES_NO


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
        ["F101*", "M101*"],
        question_keys=["F101_STAR", "M101_STAR"],
    ),
    _row(
        "Hit with object etc from parents/caregivers/adult relatives in the last 12 months",
        ["F101*", "M101*"],
        question_keys=["F101_STAR", "M101_STAR"],
    ),
    _row("Choked etc from parents/caregivers/adult relatives in the last 12 months"),
    _row("Burned etc from parents/caregivers/adult relatives in the last 12 months"),
    _row("Threatened with knife/weapon etc from parents/caregivers/adult relatives in the last 12 months"),
    _row(
        "Hit etc from public authority figure in the last 12 months",
        ["F103*", "M103*"],
        question_keys=["F103_STAR", "M103_STAR"],
    ),
    _row("Choked etc from public authority figure in the last 12 months"),
    _row("Burned etc from public authority figure in the last 12 months"),
    _row("Threatened with knife/weapon etc from public authority figure in the last 12 months"),
    _row(
        "Hit etc from intimate partner in the last 12 months",
        ["F100*", "M100*"],
        question_keys=["F100_SLAP", "M100_SLAP"],
    ),
    _row(
        "Hit with object etc from intimate partner in the last 12 months",
        ["F100*", "M100*"],
        question_keys=["F100_FIST", "M100_FIST"],
    ),
    _row("Choked etc from intimate partner in the last 12 months"),
    _row(
        "Threatened with knife/weapon etc from intimate partner in the last 12 months",
        ["F100*", "M100*"],
        question_keys=["F100_WEAPON", "M100_WEAPON"],
    ),
    _row("Hit etc from peer in the last 12 months"),
    _row("Hit with object etc from peer in the last 12 months"),
    _row("Choked etc from peer in the last 12 months"),
    _row("Threatened with knife/weapon etc from peer in the last 12 months"),
    _row("Hit etc from neighbor in the last 12 months"),
    _row("Hit with object etc from neighbor in the last 12 months"),
    _row("Choked etc from neighbor in the last 12 months"),
    _row("Threatened with knife/weapon etc from neighbor in the last 12 months"),
    _row("Witnessed parents/caregivers/adult relatives hit etc in the last 12 months"),
    _row("Hit etc from teacher in the last 12 months"),
    _row("Offensive names online in the last 12 months"),
    _row("Physically threatened online in the last 12 months"),
    _row("Harassed for sustained period online in the last 12 months"),
    _row("Stalked online in the last 12 months"),
    _row("Purposely embarrassed online in the last 12 months"),
    _row("Not attended school due to safety in the last 12 months"),
    _row(
        "Said not loved etc from parents/caregivers/adult relatives in the last 12 months",
        ["F201*"],
        question_keys=["F201_STAR"],
    ),
    _row("Wished you were not born or dead etc from parents/caregivers/adult relatives in the last 12 months"),
    _row(
        "Ridiculed you etc from parents/caregivers/adult relatives in the last 12 months",
        ["F200*"],
        question_keys=["F200_STAR"],
    ),
    _row(
        "Threatened to abandon you etc from parents/caregivers/adult relatives in the last 12 months",
        ["F202*"],
        question_keys=["F202_STAR"],
    ),
    _row(
        "Shouted at you etc from parents/caregivers/adult relatives in the last 12 months",
        ["F200*"],
        question_keys=["F200_STAR"],
    ),
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
        ["F63", "M56"],
        question_keys=["F63", "M56"],
    ),
    _row(
        "Most recent sexual touching in the last 12 months",
        ["F301", "F317", "M301", "M317"],
        question_keys=["F301", "F317", "M301", "M317"],
    ),
    _row(
        "Most recent attempted sex without consent/forced sex in the last 12 months",
        ["F401", "F419", "M401", "M419"],
        question_keys=["F401", "F419", "M401", "M419"],
    ),
    _row(
        "Most recent pressured into sex in the last 12 months",
        ["F601", "F634", "M601", "M632"],
        question_keys=["F601", "F634", "M601", "M632"],
    ),
    _row(
        "Most recent forced into sex in the last 12 months",
        ["F501", "F531", "M501", "M432"],
        question_keys=["F501", "F531", "M501", "M432"],
    ),
    _row("Sex acts online in the last 12 months"),
    _row("Sent sexual photo/video online in the last 12 months"),
    _row("Anything else sexual online in the last 12 months"),
    _row("Sexually harassed online in the last 12 months"),
    _row("Hit etc your partner in the last 12 months"),
    _row("Hit with object etc your partner in the last 12 months"),
    _row("Choked etc your partner in the last 12 months"),
    _row("Threatened with knife/weapon etc your partner in the last 12 months"),
    _row("Hit etc someone else who is not your partner in the last 12 months"),
    _row("Hit with object etc someone else who is not your partner in the last 12 months"),
    _row("Choked etc someone else who is not your partner in the last 12 months"),
    _row("Threatened with knife/weapon etc someone else who is not your partner in the last 12 months"),
    _row("Forced your partner or ex to have sex in the last 12 months"),
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
