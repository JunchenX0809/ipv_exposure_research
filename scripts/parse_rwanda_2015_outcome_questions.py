#!/usr/bin/env python3
"""Build the Rwanda 2015–16 five-column outcome codebook (no local questionnaire PDFs).

Sources: ``Rwanda VACYS 2015-16 Final Data set.dta`` variable labels (primary text),
cross-checked for PV 12-month gates with ``VACS_analysis_dofile.do`` / ``Rwanda PV_040517.sas``
(e.g. ``q102|q109`` intimate, ``q118|q123`` peer, ``q130|q136`` parent, ``q144|q149`` community).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.docx_export import export_minimal_codebook_docx
from utils.outcomes import OUTCOME_CODEBOOK_COLUMNS, build_outcome_codebook_df, outcome_codebook_to_tsv

RAW = ROOT / "data" / "raw" / "Rwanda Stata and SAS"
OUT_DIR = ROOT / "data" / "processed" / "outcome"
OUT_DOCX = OUT_DIR / "jcx_rwanda2015OutcomeCodebook.docx"
OUT_TSV = OUT_DIR / "jcx_rwanda2015OutcomeCodebook.tsv"

YES_NO_99 = "1-YES, 2-NO, 98-DON'T KNOW, 99-DECLINED"
LIFETIME_COUNT = "1-ONCE OR INDICATED, 66-TOO MANY TO RECALL, 98-DON'T KNOW, 99-DECLINED"
NUMBER = "NUMBER (see Data User Guide / instrument)"
REL_LIST = "relationship categories (see instrument)"
LIFETIME_NOTE = "(Form: lifetime perpetration item; no separate past-12-months gate in source do-file.)"
RW_DUAL12 = "(Rwanda: do-file treats past 12 months as yes if either paired timing item is yes—see both variables in Variable column.)"
META_NOTE = "(No local ENG questionnaire PDF in repo; wording is Stata variable label from final PUD, may be truncated.)"

QUESTION_TEXT: dict[str, str] = {
    "Q128A": "128A. Has a parent, adult caregiver, or other adult relative ever: punched, kicked, whipped, or beat you with an object?",
    "Q128B": "128B. Has a parent, adult caregiver, or other adult relative ever: choked, smothered, tried to drown you, or burned you intentionally?",
    "Q128C": "128C. Has a parent, adult caregiver, or other adult relative ever: used or threatened you with a knife, gun, or other weapon?",
    "Q130": "130. Did this happen in the last 12 months?",
    "Q136": "136. Did this happen in the last 12 months?",
    "Q142A": "142A. Has an adult in your community ever: punched, kicked, whipped, or beat you with an object?",
    "Q142B": "142B. Has an adult in your community ever: choked, smothered, tried to drown you, or burned you intentionally?",
    "Q142C": "142C. Has an adult in your community ever: used or threatened you with a knife, gun, or other weapon?",
    "Q144": "144. Did this happen in the last 12 months?",
    "Q146": "146. The adult in the community who did this to you the last time, what was this person’s relationship to you?",
    "Q149": "149. Did this happen in the last 12 months?",
    "Q100A": "100A. Has a romantic partner, boyfriend or husband ever: punched, kicked, whipped, or beat you with an object?",
    "Q100B": "100B. Has a romantic partner, boyfriend or husband ever: choked, smothered, tried to drown you, or burned you intentionally?",
    "Q100C": "100C. Has a romantic partner, boyfriend or husband ever: used or threatened you with a knife, gun, or other weapon?",
    "Q102": "102. Did this happen in the last 12 months?",
    "Q109": "109. Did this happen in the last 12 months?",
    "Q116A": "116A. Has a person within your age range ever: punched, kicked, whipped, or beat you with an object?",
    "Q116B": "116B. Has a person within your age range ever: choked, smothered, tried to drown you, or burned you intentionally?",
    "Q116C": "116C. Has a person within your age range ever: used or threatened you with a knife, gun, or other weapon?",
    "Q118": "118. Did this happen in the last 12 months?",
    "Q123": "123. Did this happen in the last 12 months?",
    "Q300C": "300C. Has a parent, adult caregiver or other adult relative often: insulted you?",
    "Q302": "302. Did this happen in the last 12 months?",
    "Q514": "514. In the last 12 months, how many times did someone ask you to have sex in exchange of food, favors or gifts?",
    "Q600": "600. Has anyone ever touched you in a sexual way without your permission, but did not try to force you to have sex?",
    "Q601": "601. How many times in your life has this happened?",
    "Q602": "602. Did this happen to you within the past 12 months?",
    "Q700": "700. Has anyone ever tried to make you have sex against your will but did not succeed?",
    "Q701": "701. How many times in your life has anyone tried to make you have sex against your will but did not succeed?",
    "Q702": "702. Did this happen to you within the past 12 months?",
    "Q800": "800. Has anyone ever physically forced you to have sex and did succeed?",
    "Q801": "801. How many times in your life have you been physically forced to have sex?",
    "Q802": "802. Did this happen to you within the past 12 months?",
    "Q900": "900. Has anyone ever pressured you to have sex, through harassment, threats or tricks and did succeed?",
    "Q901": "901. How many times in your life has someone pressured you to have sex through harassment, threats or tricks and did succeed?",
    "Q902": "902. Did this happen to you within the past 12 months?",
    "Q154": "154. Thinking about all these experiences with parents, other adults, romantic partners, people your own age, and someone in the community that we just discussed, did you ever have to miss school because of what happened?",
    "Q200A_M": "200A. Have you ever done to a current or previous boyfriend, romantic partner/husband any of the following: punched, kicked, whipped, or beaten with an object? (label truncated in PUD.)",
    "Q201A_M": "201A. Have you ever done any of the following to someone who is not a current or previous partner: punched, kicked, whipped, or beaten with an object? (label truncated in PUD.)",
    "Q200B_M": "200B. Choked, smothered, tried to drown, or burned intentionally toward partner (label truncated).",
    "Q200C_M": "200C. Used or threatened with knife, gun, or other weapon toward partner (label truncated).",
    "Q201B_M": "201B. Choked etc. toward non-partner (label truncated).",
    "Q201C_M": "201C. Weapon threat toward non-partner (label truncated).",
    "Q1100A": "1100A. Have you ever done any of the following: Forced a current or previous boyfriend/romantic partner to have sex when they did not want to? (label truncated.)",
}

FORMAT_OVERRIDES: dict[str, str] = {
    "Q146": REL_LIST,
    "Q601": LIFETIME_COUNT,
    "Q701": LIFETIME_COUNT,
    "Q801": LIFETIME_COUNT,
    "Q901": LIFETIME_COUNT,
    "Q514": NUMBER,
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
    questions_suffix: str = "",
) -> dict[str, object]:
    v = vars_ or []
    return {
        "category": category,
        "vars": v,
        "question_keys": list(question_keys or []),
        "questions_suffix": questions_suffix,
    }


OUTCOME_SPEC = [
    _row(
        "Hit etc from parents/caregivers/adult relatives in the last 12 months",
        ["q128a", "q130", "q136"],
        question_keys=["Q128A", "Q130", "Q136"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Hit with object etc from parents/caregivers/adult relatives in the last 12 months",
        ["q128a", "q130", "q136"],
        question_keys=["Q128A", "Q130", "Q136"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Choked etc from parents/caregivers/adult relatives in the last 12 months",
        ["q128b", "q130", "q136"],
        question_keys=["Q128B", "Q130", "Q136"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Burned etc from parents/caregivers/adult relatives in the last 12 months",
        ["q128b", "q130", "q136"],
        question_keys=["Q128B", "Q130", "Q136"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc from parents/caregivers/adult relatives in the last 12 months",
        ["q128c", "q130", "q136"],
        question_keys=["Q128C", "Q130", "Q136"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Hit etc from public authority figure in the last 12 months",
        ["q142a", "q144", "q149", "q146"],
        question_keys=["Q142A", "Q144", "Q149", "Q146"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Choked etc from public authority figure in the last 12 months",
        ["q142b", "q144", "q149", "q146"],
        question_keys=["Q142B", "Q144", "Q149", "Q146"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Burned etc from public authority figure in the last 12 months",
        ["q142b", "q144", "q149", "q146"],
        question_keys=["Q142B", "Q144", "Q149", "Q146"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc from public authority figure in the last 12 months",
        ["q142c", "q144", "q149", "q146"],
        question_keys=["Q142C", "Q144", "Q149", "Q146"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Hit etc from intimate partner in the last 12 months",
        questions_suffix="(No separate ‘slap/push only’ intimate PV item in Rwanda PUD labels; first harmonized IPV row left blank.)",
    ),
    _row(
        "Hit with object etc from intimate partner in the last 12 months",
        ["q100a", "q102", "q109"],
        question_keys=["Q100A", "Q102", "Q109"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Choked etc from intimate partner in the last 12 months",
        ["q100b", "q102", "q109"],
        question_keys=["Q100B", "Q102", "Q109"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc from intimate partner in the last 12 months",
        ["q100c", "q102", "q109"],
        question_keys=["Q100C", "Q102", "Q109"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Hit etc from peer in the last 12 months",
        ["q116a", "q118", "q123"],
        question_keys=["Q116A", "Q118", "Q123"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Hit with object etc from peer in the last 12 months",
        ["q116a", "q118", "q123"],
        question_keys=["Q116A", "Q118", "Q123"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Choked etc from peer in the last 12 months",
        ["q116b", "q118", "q123"],
        question_keys=["Q116B", "Q118", "Q123"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc from peer in the last 12 months",
        ["q116c", "q118", "q123"],
        question_keys=["Q116C", "Q118", "Q123"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Hit etc from neighbor in the last 12 months",
        ["q142a", "q144", "q149", "q146"],
        question_keys=["Q142A", "Q144", "Q149", "Q146"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Hit with object etc from neighbor in the last 12 months",
        ["q142a", "q144", "q149", "q146"],
        question_keys=["Q142A", "Q144", "Q149", "Q146"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Choked etc from neighbor in the last 12 months",
        ["q142b", "q144", "q149", "q146"],
        question_keys=["Q142B", "Q144", "Q149", "Q146"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc from neighbor in the last 12 months",
        ["q142c", "q144", "q149", "q146"],
        question_keys=["Q142C", "Q144", "Q149", "Q146"],
        questions_suffix=RW_DUAL12 + " " + META_NOTE,
    ),
    _row(
        "Witnessed parents/caregivers/adult relatives hit etc in the last 12 months",
        questions_suffix="(No ``q39``/``q40`` witnessing items in Rwanda final PUD column list; harmonized row left blank.)",
    ),
    _row(
        "Hit etc from teacher in the last 12 months",
        questions_suffix="(No dedicated teacher-corporal-punishment victim item located in PUD labels; ``q140`` is parent/PV injury stem, not teacher.)",
    ),
    _row(
        "Offensive names online in the last 12 months",
        questions_suffix="(No dedicated online harassment items in PUD labels.)",
    ),
    _row(
        "Physically threatened online in the last 12 months",
        questions_suffix="(No dedicated online harassment items in PUD labels.)",
    ),
    _row(
        "Harassed for sustained period online in the last 12 months",
        questions_suffix="(No dedicated online harassment items in PUD labels.)",
    ),
    _row(
        "Stalked online in the last 12 months",
        questions_suffix="(No dedicated online harassment items in PUD labels.)",
    ),
    _row(
        "Purposely embarrassed online in the last 12 months",
        questions_suffix="(No dedicated online harassment items in PUD labels.)",
    ),
    _row(
        "Not attended school due to safety in the last 12 months",
        ["q154"],
        question_keys=["Q154"],
        questions_suffix="(Closest match: miss school after PV experiences discussed in module; not a general ‘unsafe to leave home’ item.) " + META_NOTE,
    ),
    _row(
        "Said not loved etc from parents/caregivers/adult relatives in the last 12 months",
        questions_suffix="(Rwanda ``q300a``/``q300b`` wording differs from Nigeria EV1 ‘not loved’ / ‘wished dead’; no 1:1 match—left blank.)",
    ),
    _row(
        "Wished you were not born or dead etc from parents/caregivers/adult relatives in the last 12 months",
        questions_suffix="(Rwanda ``q300a``/``q300b`` wording differs from Nigeria EV1; no 1:1 match—left blank.)",
    ),
    _row(
        "Ridiculed you etc from parents/caregivers/adult relatives in the last 12 months",
        ["q300c", "q302"],
        question_keys=["Q300C", "Q302"],
        questions_suffix="(Partial match: Rwanda uses ‘insulted you’ (``q300c``) with ``q302`` past 12 months.) " + META_NOTE,
    ),
    _row(
        "Threatened to abandon you etc from parents/caregivers/adult relatives in the last 12 months",
        questions_suffix="(No matching item in PUD labels.)",
    ),
    _row(
        "Shouted at you etc from parents/caregivers/adult relatives in the last 12 months",
        questions_suffix="(No ``q46``-style discipline block in Rwanda PUD.)",
    ),
    _row(
        "Take away privileges etc from parents/caregivers/adult relatives in the last 12 months",
        questions_suffix="(No ``q46``-style discipline block in Rwanda PUD.)",
    ),
    _row(
        "Insulted you in front of others etc from intimate partner in the last 12 months",
        questions_suffix="(No ``q310a``–``e`` intimate emotional partner block in Rwanda PUD column list.)",
    ),
    _row(
        "Kept you from having your own money etc from intimate partner in the last 12 months",
        questions_suffix="(No ``q310a``–``e`` block in Rwanda PUD.)",
    ),
    _row(
        "Kept you from talking to friends or family etc from intimate partner in the last 12 months",
        questions_suffix="(No ``q310a``–``e`` block in Rwanda PUD.)",
    ),
    _row(
        "Demanded to know where you were etc from intimate partner in the last 12 months",
        questions_suffix="(No ``q310a``–``e`` block in Rwanda PUD.)",
    ),
    _row(
        "Threatened to physically harm you etc from intimate partner in the last 12 months",
        questions_suffix="(No ``q310a``–``e`` block in Rwanda PUD.)",
    ),
    _row(
        "Made you feel scared from saying mean things etc from peer in the last 12 months",
        questions_suffix="(No ``q315`` peer emotional items in Rwanda PUD.)",
    ),
    _row(
        "Told lies etc from peer in the last 12 months",
        questions_suffix="(No ``q315`` peer emotional items in Rwanda PUD.)",
    ),
    _row(
        "Kept you out of things on purpose etc from peer in the last 12 months",
        questions_suffix="(No ``q315`` peer emotional items in Rwanda PUD.)",
    ),
    _row(
        "Past 12 months money or goods for sex",
        ["q514"],
        question_keys=["Q514"],
        questions_suffix=META_NOTE,
    ),
    _row(
        "Most recent sexual touching in the last 12 months",
        ["q600", "q601", "q602"],
        question_keys=["Q600", "Q601", "Q602"],
        questions_suffix=META_NOTE,
    ),
    _row(
        "Most recent attempted sex without consent/forced sex in the last 12 months",
        ["q700", "q701", "q702"],
        question_keys=["Q700", "Q701", "Q702"],
        questions_suffix=META_NOTE,
    ),
    _row(
        "Most recent pressured into sex in the last 12 months",
        ["q900", "q901", "q902"],
        question_keys=["Q900", "Q901", "Q902"],
        questions_suffix=META_NOTE,
    ),
    _row(
        "Most recent forced into sex in the last 12 months",
        ["q800", "q801", "q802"],
        question_keys=["Q800", "Q801", "Q802"],
        questions_suffix=META_NOTE,
    ),
    _row(
        "Sex acts online in the last 12 months",
        questions_suffix="(No dedicated online sexual-behaviour items in PUD labels.)",
    ),
    _row(
        "Sent sexual photo/video online in the last 12 months",
        questions_suffix="(No dedicated online sexual-behaviour items in PUD labels.)",
    ),
    _row(
        "Anything else sexual online in the last 12 months",
        questions_suffix="(No dedicated online sexual-behaviour items in PUD labels.)",
    ),
    _row(
        "Sexually harassed online in the last 12 months",
        questions_suffix="(No dedicated online sexual-behaviour items in PUD labels.)",
    ),
    _row(
        "Hit etc your partner in the last 12 months",
        ["q200a"],
        question_keys=["Q200A_M"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Hit with object etc your partner in the last 12 months",
        ["q200a"],
        question_keys=["Q200A_M"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Choked etc your partner in the last 12 months",
        ["q200b"],
        question_keys=["Q200B_M"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc your partner in the last 12 months",
        ["q200c"],
        question_keys=["Q200C_M"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Hit etc someone else who is not your partner in the last 12 months",
        ["q201a"],
        question_keys=["Q201A_M"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Hit with object etc someone else who is not your partner in the last 12 months",
        ["q201a"],
        question_keys=["Q201A_M"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Choked etc someone else who is not your partner in the last 12 months",
        ["q201b"],
        question_keys=["Q201B_M"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc someone else who is not your partner in the last 12 months",
        ["q201c"],
        question_keys=["Q201C_M"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Forced your partner or ex to have sex in the last 12 months",
        ["q1100a"],
        question_keys=["Q1100A"],
        questions_suffix=LIFETIME_NOTE + " " + META_NOTE,
    ),
    _row(
        "Pressured your partner or ex to talk about sex online/virtual in the last 12 months",
        questions_suffix="(No matching items in PUD labels.)",
    ),
    _row(
        "Pressured someone else who is not your partner to talk about sex online/virtual in the last 12 months",
        questions_suffix="(No matching items in PUD labels.)",
    ),
    _row(
        "Pressured your partner or ex to send you sex material online/virtual in the last 12 months",
        questions_suffix="(No matching items in PUD labels.)",
    ),
    _row(
        "Pressured someone else who is not your partner to send you sex material online/virtual in the last 12 months",
        questions_suffix="(No matching items in PUD labels.)",
    ),
    _row(
        "Pressured your partner or ex to do anything else sexual online/virtual in the last 12 months",
        questions_suffix="(No matching items in PUD labels.)",
    ),
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
    if "TOO MANY" in f0 or "ONCE OR" in f0:
        return "categorical"
    return "categorical"


def main() -> None:
    ng_path = ROOT / "scripts" / "parse_nigeria_2014_outcome_questions.py"
    ng_spec = importlib.util.spec_from_file_location("nigeria", ng_path)
    ng_mod = importlib.util.module_from_spec(ng_spec)
    assert ng_spec.loader is not None
    ng_spec.loader.exec_module(ng_mod)
    assert [r["category"] for r in ng_mod.OUTCOME_SPEC] == [r["category"] for r in OUTCOME_SPEC]

    rows: list[dict[str, str]] = []
    for entry in OUTCOME_SPEC:
        vars_ = list(entry["vars"])
        qkeys = list(entry["question_keys"] or [])
        suffix = str(entry.get("questions_suffix") or "").strip()
        if not vars_:
            rows.append({
                "Category": entry["category"],
                "Variable": "",
                "Type": "",
                "Format": "",
                "Questions": suffix,
            })
            continue
        base_q = _questions(qkeys) if qkeys else ""
        if base_q and suffix:
            questions = f"{base_q} || {suffix}".strip()
        else:
            questions = (base_q or suffix).strip()
        rows.append({
            "Category": entry["category"],
            "Variable": "; ".join(vars_),
            "Type": _type_for(vars_),
            "Format": _fmt(vars_),
            "Questions": questions,
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
