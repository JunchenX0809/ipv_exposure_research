#!/usr/bin/env python3
"""Build the Malawi 2013 five-column outcome codebook from respondent questionnaire PDFs (PDF-first).

Female respondent form uses F-prefixed question IDs; male form uses the same numbers with M-prefix
(e.g. F100A and M100A). Variables below follow the female questionnaire unless noted (male perpetration: M200*, M1200*).
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

RAW = ROOT / "data" / "raw" / "Malawi Stata"
OUT_DIR = ROOT / "data" / "processed" / "outcome"
OUT_DOCX = OUT_DIR / "jcx_malawi2013OutcomeCodebook.docx"
OUT_TSV = OUT_DIR / "jcx_malawi2013OutcomeCodebook.tsv"

YES_NO_99 = "1-YES, 2-NO, 99-DON'T KNOW/DECLINED"
WITNESS_FREQ = (
    "1-NEVER, 2-ONCE, 3-A FEW TIMES, 4-MANY TIMES, 99-DON'T KNOW/DECLINED"
)
LIFETIME_COUNT = "1-ONCE OR INDICATED, 66-TOO MANY TO RECALL, 99-DON'T KNOW/DECLINED"
NUMBER = "NUMBER (see questionnaire)"
REL_LIST = "relationship categories in questionnaire (see questionnaire)"
LIFETIME_NOTE = "(Form: lifetime act; no separate past-12-months item.)"
SCHOOL_NOTE = "(Closest match: missing school due to prior discussed violence experiences, not general “unsafe to leave home” wording.)"
PHOTO_NOTE = "(F601 lifetime participation; F606 past-12-month frequency.)"

QUESTION_TEXT: dict[str, str] = {
    "F128A": "PV3: Has a parent, adult caregiver, or other adult relative ever punched, kicked, whipped, or beaten you with an object?",
    "F128B": "PV3: Has a parent, adult caregiver, or other adult relative ever choked, smothered, tried to drown you, or burned you intentionally?",
    "F128C": "PV3: Has a parent, adult caregiver, or other adult relative ever used or threatened you with a knife, gun, or other weapon?",
    "F130": "PV3: Most recent time — Did this happen in the last 12 months?",
    "F132": "PV3: The parent, adult caregiver, or adult relative who did this to you the last time — what was this person’s relationship to you?",
    "F142A": "PV4: Has an adult in your community ever punched, kicked, whipped, or beaten you with an object?",
    "F142B": "PV4: Has an adult in your community ever choked, smothered, tried to drown you, or burned you intentionally?",
    "F142C": "PV4: Has an adult in your community ever used or threatened you with a knife, gun, or other weapon?",
    "F144": "PV4: Most recent time — Did this happen in the last 12 months?",
    "F146": "PV4: The adult in the community who did this to you the last time — what was this person’s relationship to you?",
    "F100A": "PV1: Has a romantic partner, boyfriend, or husband ever punched, kicked, whipped, or beaten you with an object?",
    "F100B": "PV1: Has a romantic partner, boyfriend, or husband ever choked, smothered, tried to drown you, or burned you intentionally?",
    "F100C": "PV1: Has a romantic partner, boyfriend, or husband ever used or threatened you with a knife, gun, or other weapon?",
    "F102": "PV1: Most recent time — Did this happen in the last 12 months?",
    "F116A": "PV2: Has a person your own age ever punched, kicked, whipped, or beaten you with an object?",
    "F116B": "PV2: Has a person your own age ever choked, smothered, tried to drown you, or burned you intentionally?",
    "F116C": "PV2: Has a person your own age ever used or threatened you with a knife, gun, or other weapon?",
    "F118": "PV2: Most recent time — Did this happen in the last 12 months?",
    "F120": "PV2: The person your own age who did this to you the last time — what was this person’s relationship to you?",
    "F42": "How many times did you see or hear your parent punched, kicked, or beaten up by your other parent, or their boyfriend or girlfriend?",
    "F43": "Did this happen in the last 12 months?",
    "F154": "PV services: Thinking about experiences with parents, other adults, romantic partners, and people your own age discussed, did you ever have to miss school because of what happened?",
    "F300A": "EV1: Has a parent, adult caregiver, or other adult relative ever told you that you were not loved, or did not deserve to be loved?",
    "F300B": "EV1: Has a parent, adult caregiver, or other adult relative ever said they wished you had never been born or were dead?",
    "F300C": "EV1: Has a parent, adult caregiver, or other adult relative ever ridiculed you or put you down (for example said that you were stupid or useless)?",
    "F302": "EV1: Most recent time — Did this happen in the last 12 months?",
    "F515": "In the last 12 months, how many times did someone ask you to have sex in exchange for something?",
    "F700": "Has anyone ever touched you in a sexual way without your permission, but did not try to force you to have sex?",
    "F701": "SV1: How many times in your life has this happened?",
    "F702": "SV1A: Touching — most recent — Did this happen to you within the past 12 months?",
    "F800": "Has anyone ever tried to make you have sex against your will but did not succeed?",
    "F801": "SV2: How many times in your life has anyone tried to make you have sex against your will but did not succeed?",
    "F802": "SV2A: Attempted sex — most recent — Did this happen to you within the past 12 months?",
    "F900": "Has anyone ever physically forced you to have sex and did succeed?",
    "F901": "SV3: How many times in your life have you been physically forced to have sex?",
    "F902": "SV3A: Physically forced sex — most recent — Did this happen to you within the past 12 months?",
    "F1000": "Has anyone ever pressured you to have sex through harassment, threats, or tricks and did succeed?",
    "F1001": "SV4: How many times in your life has someone pressured you to have sex through harassment, threats, and tricks and did succeed?",
    "F1002": "SV4A: Pressured into sex — most recent — Did this happen to you within the past 12 months?",
    "F601": "Have you ever participated in a sex photo or video, or shown your sexual body parts in front of a webcam, whether you wanted to or not?",
    "F606": "In the last 12 months, how many times did you participate in a sex photo or video, or show your sexual body parts in front of a webcam?",
    "M200A_M": "PV perpetration (male form): Have you ever punched, kicked, whipped, or beaten a current or previous girlfriend, romantic partner, or wife?",
    "M200B_M": "PV perpetration (male form): Have you ever choked, smothered, tried to drown, or intentionally burned them?",
    "M200C_M": "PV perpetration (male form): Have you ever used or threatened to use a knife, gun, or other weapon against them?",
    "M201A_M": "PV perpetration (male form): Same acts toward someone who was not a current or previous girlfriend, romantic partner, or wife — punched, kicked, whipped, or beaten.",
    "M201B_M": "PV perpetration (male form): Same — choked, smothered, tried to drown, or intentionally burned.",
    "M201C_M": "PV perpetration (male form): Same — used or threatened to use a knife, gun, or other weapon.",
    "F1200A": "SV perpetration (female form): Have you ever forced a current or previous partner/husband at the time to have sex with them when they did not want to?",
    "M1200A": "SV perpetration (male form): Have you ever forced a current or previous partner/wife at the time to have sex with you when they did not want to?",
}

FORMAT_OVERRIDES: dict[str, str] = {
    "F42": WITNESS_FREQ,
    "F43": YES_NO_99,
    "F132": REL_LIST,
    "F120": REL_LIST,
    "F146": REL_LIST,
    "F701": LIFETIME_COUNT,
    "F801": LIFETIME_COUNT,
    "F901": LIFETIME_COUNT,
    "F1001": LIFETIME_COUNT,
    "F515": NUMBER,
    "F606": NUMBER,
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
        ["F128A", "F130"],
        question_keys=["F128A", "F130"],
    ),
    _row(
        "Hit with object etc from parents/caregivers/adult relatives in the last 12 months",
        ["F128A", "F130"],
        question_keys=["F128A", "F130"],
    ),
    _row(
        "Choked etc from parents/caregivers/adult relatives in the last 12 months",
        ["F128B", "F130"],
        question_keys=["F128B", "F130"],
    ),
    _row(
        "Burned etc from parents/caregivers/adult relatives in the last 12 months",
        ["F128B", "F130"],
        question_keys=["F128B", "F130"],
    ),
    _row(
        "Threatened with knife/weapon etc from parents/caregivers/adult relatives in the last 12 months",
        ["F128C", "F130"],
        question_keys=["F128C", "F130"],
    ),
    _row(
        "Hit etc from public authority figure in the last 12 months",
        ["F142A", "F144", "F146"],
        question_keys=["F142A", "F144", "F146"],
    ),
    _row(
        "Choked etc from public authority figure in the last 12 months",
        ["F142B", "F144", "F146"],
        question_keys=["F142B", "F144", "F146"],
    ),
    _row(
        "Burned etc from public authority figure in the last 12 months",
        ["F142B", "F144", "F146"],
        question_keys=["F142B", "F144", "F146"],
    ),
    _row(
        "Threatened with knife/weapon etc from public authority figure in the last 12 months",
        ["F142C", "F144", "F146"],
        question_keys=["F142C", "F144", "F146"],
    ),
    _row("Hit etc from intimate partner in the last 12 months"),
    _row(
        "Hit with object etc from intimate partner in the last 12 months",
        ["F100A", "F102"],
        question_keys=["F100A", "F102"],
    ),
    _row(
        "Choked etc from intimate partner in the last 12 months",
        ["F100B", "F102"],
        question_keys=["F100B", "F102"],
    ),
    _row(
        "Threatened with knife/weapon etc from intimate partner in the last 12 months",
        ["F100C", "F102"],
        question_keys=["F100C", "F102"],
    ),
    _row(
        "Hit etc from peer in the last 12 months",
        ["F116A", "F118"],
        question_keys=["F116A", "F118"],
    ),
    _row(
        "Hit with object etc from peer in the last 12 months",
        ["F116A", "F118"],
        question_keys=["F116A", "F118"],
    ),
    _row(
        "Choked etc from peer in the last 12 months",
        ["F116B", "F118"],
        question_keys=["F116B", "F118"],
    ),
    _row(
        "Threatened with knife/weapon etc from peer in the last 12 months",
        ["F116C", "F118"],
        question_keys=["F116C", "F118"],
    ),
    _row(
        "Hit etc from neighbor in the last 12 months",
        ["F142A", "F144", "F146"],
        question_keys=["F142A", "F144", "F146"],
    ),
    _row(
        "Hit with object etc from neighbor in the last 12 months",
        ["F142A", "F144", "F146"],
        question_keys=["F142A", "F144", "F146"],
    ),
    _row(
        "Choked etc from neighbor in the last 12 months",
        ["F142B", "F144", "F146"],
        question_keys=["F142B", "F144", "F146"],
    ),
    _row(
        "Threatened with knife/weapon etc from neighbor in the last 12 months",
        ["F142C", "F144", "F146"],
        question_keys=["F142C", "F144", "F146"],
    ),
    _row(
        "Witnessed parents/caregivers/adult relatives hit etc in the last 12 months",
        ["F42", "F43"],
        question_keys=["F42", "F43"],
    ),
    _row("Hit etc from teacher in the last 12 months"),
    _row("Offensive names online in the last 12 months"),
    _row("Physically threatened online in the last 12 months"),
    _row("Harassed for sustained period online in the last 12 months"),
    _row("Stalked online in the last 12 months"),
    _row("Purposely embarrassed online in the last 12 months"),
    _row(
        "Not attended school due to safety in the last 12 months",
        ["F154"],
        question_keys=["F154"],
        questions_suffix=SCHOOL_NOTE,
    ),
    _row(
        "Said not loved etc from parents/caregivers/adult relatives in the last 12 months",
        ["F300A", "F302"],
        question_keys=["F300A", "F302"],
    ),
    _row(
        "Wished you were not born or dead etc from parents/caregivers/adult relatives in the last 12 months",
        ["F300B", "F302"],
        question_keys=["F300B", "F302"],
    ),
    _row(
        "Ridiculed you etc from parents/caregivers/adult relatives in the last 12 months",
        ["F300C", "F302"],
        question_keys=["F300C", "F302"],
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
        ["F515"],
        question_keys=["F515"],
    ),
    _row(
        "Most recent sexual touching in the last 12 months",
        ["F700", "F701", "F702"],
        question_keys=["F700", "F701", "F702"],
    ),
    _row(
        "Most recent attempted sex without consent/forced sex in the last 12 months",
        ["F800", "F801", "F802"],
        question_keys=["F800", "F801", "F802"],
    ),
    _row(
        "Most recent pressured into sex in the last 12 months",
        ["F1000", "F1001", "F1002"],
        question_keys=["F1000", "F1001", "F1002"],
    ),
    _row(
        "Most recent forced into sex in the last 12 months",
        ["F900", "F901", "F902"],
        question_keys=["F900", "F901", "F902"],
    ),
    _row(
        "Sex acts online in the last 12 months",
        ["F606"],
        question_keys=["F606"],
    ),
    _row(
        "Sent sexual photo/video online in the last 12 months",
        ["F601", "F606"],
        question_keys=["F601", "F606"],
        questions_suffix=PHOTO_NOTE,
    ),
    _row("Anything else sexual online in the last 12 months"),
    _row("Sexually harassed online in the last 12 months"),
    _row(
        "Hit etc your partner in the last 12 months",
        ["M200A"],
        question_keys=["M200A_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Hit with object etc your partner in the last 12 months",
        ["M200A"],
        question_keys=["M200A_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Choked etc your partner in the last 12 months",
        ["M200B"],
        question_keys=["M200B_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc your partner in the last 12 months",
        ["M200C"],
        question_keys=["M200C_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Hit etc someone else who is not your partner in the last 12 months",
        ["M201A"],
        question_keys=["M201A_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Hit with object etc someone else who is not your partner in the last 12 months",
        ["M201A"],
        question_keys=["M201A_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Choked etc someone else who is not your partner in the last 12 months",
        ["M201B"],
        question_keys=["M201B_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc someone else who is not your partner in the last 12 months",
        ["M201C"],
        question_keys=["M201C_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Forced your partner or ex to have sex in the last 12 months",
        ["F1200A", "M1200A"],
        question_keys=["F1200A", "M1200A"],
        questions_suffix=LIFETIME_NOTE,
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
    if "NEVER" in f0 and "ONCE" in f0:
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
            rows.append({"Category": entry["category"], "Variable": "", "Type": "", "Format": "", "Questions": ""})
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
