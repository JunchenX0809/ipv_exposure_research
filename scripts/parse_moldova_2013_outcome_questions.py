#!/usr/bin/env python3
"""Build the Moldova 2013 five-column outcome codebook from respondent questionnaire PDFs (PDF-first, ENG)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.docx_export import export_minimal_codebook_docx
from utils.outcomes import OUTCOME_CODEBOOK_COLUMNS, build_outcome_codebook_df, outcome_codebook_to_tsv

RAW = ROOT / "data" / "raw" / "Moldova Stata"
OUT_DIR = ROOT / "data" / "processed" / "outcome"
OUT_DOCX = OUT_DIR / "jcx_moldova2013OutcomeCodebook.docx"
OUT_TSV = OUT_DIR / "jcx_moldova2013OutcomeCodebook.tsv"

YES_NO_99 = "1-YES, 2-NO, 99-DON'T KNOW/DECLINED"
WITNESS_FREQ = "1-NEVER, 2-ONCE, 3-MORE THAN ONCE, 99-DON'T KNOW/DECLINED"
LIFETIME_COUNT = "1-ONCE OR INDICATED, 66-TOO MANY TO RECALL, 99-DON'T KNOW/DECLINED"
NUMBER = "NUMBER (see questionnaire)"
REL_LIST = "relationship categories in questionnaire (see questionnaire)"
LIFETIME_NOTE = "(Form: lifetime act; no separate past-12-months item.)"
DISCIPLINE_30D_NOTE = "(Q46 refers to the past 30 days, not the past 12 months.)"

QUESTION_TEXT: dict[str, str] = {
    "Q120A": "PV3: Has a parent, adult caregiver, or other adult relative ever slapped, pushed, shoved, shook, or intentionally thrown something at you to hurt you?",
    "Q120B": "PV3: Has a parent, adult caregiver, or other adult relative ever punched, kicked, whipped, hit/smashed, or beaten you with an object (including kicked/beaten with legs)?",
    "Q120C": "PV3: Has a parent, adult caregiver, or other adult relative ever choked, smothered, tried to drown you, or burned you intentionally (including with chemical substances)?",
    "Q120D": "PV3: Has a parent, adult caregiver, or other adult relative ever used or threatened you with a knife, gun, or other weapon (ax, hammer, hoe, fork, etc.)?",
    "Q122": "PV3: Most recent time — Did this happen in the last 12 months?",
    "Q132A": "PV4: Has an adult in your community or neighborhood ever slapped, pushed, shoved, shook, or intentionally thrown something at you to hurt you?",
    "Q132B": "PV4: Has an adult in your community or neighborhood ever punched, kicked, whipped, hit/smashed, or beaten you with an object (including kicked/beaten with legs)?",
    "Q132C": "PV4: Has an adult in your community or neighborhood ever choked, smothered, tried to drown you, or burned you intentionally (including with chemical substances)?",
    "Q132D": "PV4: Has an adult in your community or neighborhood ever used or threatened you with a knife, gun, or other weapon (ax, hammer, hoe, fork, etc.)?",
    "Q134": "PV4: Most recent time — Did this happen in the last 12 months?",
    "Q136": "PV4: The adult in the community who did this to you the last time — what was this person’s relationship to you?",
    "Q100B": "PV1: Has a boyfriend/intimate partner, ex-boyfriend/intimate partner, concubine, or husband ever punched, kicked, whipped, hit/smashed, or beaten you with an object?",
    "Q100B1": "PV1: Item B — Has this happened in the past 12 months?",
    "Q100C": "PV1: Has a boyfriend/intimate partner, ex-boyfriend/intimate partner, concubine, or husband ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q100C1": "PV1: Item C — Has this happened in the past 12 months?",
    "Q100D": "PV1: Has a boyfriend/intimate partner, ex-boyfriend/intimate partner, concubine, or husband ever used or threatened you with a knife, gun, or other weapon?",
    "Q100D1": "PV1: Item D — Has this happened in the past 12 months?",
    "Q110A": "PV2: Has a person your own age ever slapped, pushed, shoved, shook, or intentionally thrown something at you to hurt you?",
    "Q110B": "PV2: Has a person your own age ever punched, kicked, whipped, hit/smashed, or beaten you with an object (including kicked/beaten with legs)?",
    "Q110C": "PV2: Has a person your own age ever choked, smothered, tried to drown you, or burned you intentionally (including with chemical substances)?",
    "Q110D": "PV2: Has a person your own age ever used or threatened you with a knife, gun, or other weapon (ax, hammer, hoe, fork, etc.)?",
    "Q112": "PV2: Most recent time — Did this happen in the last 12 months?",
    "Q114": "PV2: The person your own age who did this to you the last time — what was this person’s relationship to you?",
    "Q51": "Witnessing: How many times did you see or hear your mother or step-mother being hit, punched, kicked, or beaten by your father or step-father? (Never, once, or more than once.)",
    "Q52": "Witnessing (following mother being hit by father or step-father): Did this happen in the last 12 months?",
    "Q140": "In the past 12 months, has a teacher punished you by shaking you, hitting or slapping you anywhere on your body with a bare hand or a hard object?",
    "Q49": "During the past 12 months, were there any days you missed school or didn’t leave your home because you felt it would be unsafe for any reason?",
    "Q300A": "EV1: Has a parent, adult caregiver, or other adult relative ever told you that you were not loved, or did not deserve to be loved?",
    "Q300B": "EV1: Has a parent, adult caregiver, or other adult relative ever said they wished you had never been born or were dead?",
    "Q300C": "EV1: Has a parent, adult caregiver, or other adult relative ever made fun of you or humiliated you (for instance, told you that you are stupid, ugly and useless)?",
    "Q302": "EV1: Most recent time — Did this happen in the last 12 months?",
    "Q46_A": "DISCIPLINE: In the past 30 days, has a parent or adult caregiver punished or corrected you by (emotional violence): shouting, yelling, or screaming at you; calling you offensive names; taking away food; or ignoring you for several hours?",
    "Q46_C": "DISCIPLINE: In the past 30 days, has a parent or adult caregiver punished or corrected you by (positive discipline): taken away privileges, forbade something you liked or wanted to do; explained why the behavior is wrong; or given you a reminder or warning?",
    "Q310A": "EV2: In the last 12 months, has a boyfriend/intimate partner, ex-boyfriend/intimate partner, or husband insulted, humiliated, or made fun of you in front of others?",
    "Q310B": "EV2: In the last 12 months, has a boyfriend/intimate partner, ex-boyfriend/intimate partner, or husband kept you from having your own money?",
    "Q310C": "EV2: In the last 12 months, has a boyfriend/intimate partner, ex-boyfriend/intimate partner, or husband tried to keep you from seeing or talking to your family or friends?",
    "Q310D": "EV2: In the last 12 months, has a boyfriend/intimate partner, ex-boyfriend/intimate partner, or husband kept track of you by demanding to know where you were and what you were doing?",
    "Q310E": "EV2: In the last 12 months, has a boyfriend/intimate partner, ex-boyfriend/intimate partner, or husband made threats to physically harm you?",
    "Q315_A": "EV3: In the last 12 months, has someone your own age made you get scared or feel really bad because they were calling you names, saying mean things to you, or saying they didn’t want you around?",
    "Q315_B": "EV3: In the last 12 months, has someone your own age told lies or spread rumors about you, or tried to make others dislike you?",
    "Q315_C": "EV3: In the last 12 months, has someone your own age kept you out of things on purpose, excluded you from their group of friends, or completely ignored you?",
    "Q507": "In the last 12 months, how many times did you have sex with someone because they provided you with material support or help?",
    "Q600": "Has anyone ever touched you in a sexual way without your permission, but did not try to force you to have sex?",
    "Q601": "SV1: How many times in your life has this happened?",
    "Q602": "SV1A: Touching — most recent — Did this happen to you within the past 12 months?",
    "Q700A": "SV2: Has a boyfriend/intimate partner, ex-boyfriend/intimate partner, husband, or ex-husband ever tried to make you have sex against your will but did not succeed?",
    "Q701": "SV2: How many times in your life has anyone tried to make you have sex against your will but did not succeed?",
    "Q702": "SV2A: Attempted sex — most recent — Did this happen to you within the past 12 months?",
    "Q800A": "SV3: Has a boyfriend/intimate partner, ex-boyfriend/intimate partner, husband, or ex-husband ever physically forced you to have sex and did succeed?",
    "Q801": "SV3: How many times in your life have you been physically forced to have sex?",
    "Q802": "SV3A: Physically forced sex — most recent — Did this happen to you within the past 12 months?",
    "Q900A": "SV4: Has a boyfriend/intimate partner, ex-boyfriend/intimate partner, husband, or ex-husband ever pressured you to have sex and did succeed? They might have verbally pressured you to have sex, or they might have pressured you to have sex through harassment, threats and tricks, or you were too drunk to say no to them.",
    "Q901": "SV4: How many times in your life has someone pressured you to have sex through harassment or threats and did succeed?",
    "Q902": "SV4A: Pressured into sex — most recent — Did this happen to you within the past 12 months?",
    "Q200A_M": "PV perpetration (male form): Have you ever slapped, pushed, shoved, shook, or intentionally thrown something at a current or previous girlfriend, intimate partner, or wife to hurt them?",
    "Q200B_M": "PV perpetration (male form): Have you ever punched, kicked, hit, whipped, or beaten a current or previous girlfriend, intimate partner, or wife with an object?",
    "Q200C_M": "PV perpetration (male form): Have you ever choked, smothered, tried to drown, or burned/scalded a current or previous girlfriend, intimate partner, or wife intentionally?",
    "Q200D_M": "PV perpetration (male form): Have you ever used or threatened a current or previous girlfriend, intimate partner, or wife with a knife, gun, or other weapon?",
    "Q201A_M": "PV perpetration (male form): Same acts toward someone who was not a current or previous girlfriend, intimate partner, or wife — slapped, pushed, shoved, shook, or intentionally thrown something at them to hurt them.",
    "Q201B_M": "PV perpetration (male form): Same — punched, kicked, whipped, or beaten with an object.",
    "Q201C_M": "PV perpetration (male form): Same — choked, smothered, tried to drown, or burned intentionally.",
    "Q201D_M": "PV perpetration (male form): Same — used or threatened with a knife, gun, or other weapon.",
    "Q1300_M": "SV perpetration (male form): Have you ever forced a girlfriend, intimate partner, ex-girlfriend/intimate partner, wife, or ex-wife to have sex with you when they did not want to?",
}

FORMAT_OVERRIDES: dict[str, str] = {
    "Q51": WITNESS_FREQ,
    "Q52": YES_NO_99,
    "Q136": REL_LIST,
    "Q114": REL_LIST,
    "Q124": REL_LIST,
    "Q128": REL_LIST,
    "Q139": REL_LIST,
    "Q601": LIFETIME_COUNT,
    "Q701": LIFETIME_COUNT,
    "Q801": LIFETIME_COUNT,
    "Q901": LIFETIME_COUNT,
    "Q507": NUMBER,
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
        ["Q120A", "Q122"],
        question_keys=["Q120A", "Q122"],
    ),
    _row(
        "Hit with object etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q120B", "Q122"],
        question_keys=["Q120B", "Q122"],
    ),
    _row(
        "Choked etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q120C", "Q122"],
        question_keys=["Q120C", "Q122"],
    ),
    _row(
        "Burned etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q120C", "Q122"],
        question_keys=["Q120C", "Q122"],
    ),
    _row(
        "Threatened with knife/weapon etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q120D", "Q122"],
        question_keys=["Q120D", "Q122"],
    ),
    _row(
        "Hit etc from public authority figure in the last 12 months",
        ["Q132A", "Q134", "Q136"],
        question_keys=["Q132A", "Q134", "Q136"],
    ),
    _row(
        "Choked etc from public authority figure in the last 12 months",
        ["Q132C", "Q134", "Q136"],
        question_keys=["Q132C", "Q134", "Q136"],
    ),
    _row(
        "Burned etc from public authority figure in the last 12 months",
        ["Q132C", "Q134", "Q136"],
        question_keys=["Q132C", "Q134", "Q136"],
    ),
    _row(
        "Threatened with knife/weapon etc from public authority figure in the last 12 months",
        ["Q132D", "Q134", "Q136"],
        question_keys=["Q132D", "Q134", "Q136"],
    ),
    _row("Hit etc from intimate partner in the last 12 months"),
    _row(
        "Hit with object etc from intimate partner in the last 12 months",
        ["Q100B", "Q100B1"],
        question_keys=["Q100B", "Q100B1"],
    ),
    _row(
        "Choked etc from intimate partner in the last 12 months",
        ["Q100C", "Q100C1"],
        question_keys=["Q100C", "Q100C1"],
    ),
    _row(
        "Threatened with knife/weapon etc from intimate partner in the last 12 months",
        ["Q100D", "Q100D1"],
        question_keys=["Q100D", "Q100D1"],
    ),
    _row(
        "Hit etc from peer in the last 12 months",
        ["Q110A", "Q112", "Q114"],
        question_keys=["Q110A", "Q112", "Q114"],
    ),
    _row(
        "Hit with object etc from peer in the last 12 months",
        ["Q110B", "Q112", "Q114"],
        question_keys=["Q110B", "Q112", "Q114"],
    ),
    _row(
        "Choked etc from peer in the last 12 months",
        ["Q110C", "Q112", "Q114"],
        question_keys=["Q110C", "Q112", "Q114"],
    ),
    _row(
        "Threatened with knife/weapon etc from peer in the last 12 months",
        ["Q110D", "Q112", "Q114"],
        question_keys=["Q110D", "Q112", "Q114"],
    ),
    _row(
        "Hit etc from neighbor in the last 12 months",
        ["Q132A", "Q134", "Q136"],
        question_keys=["Q132A", "Q134", "Q136"],
    ),
    _row(
        "Hit with object etc from neighbor in the last 12 months",
        ["Q132A", "Q134", "Q136"],
        question_keys=["Q132A", "Q134", "Q136"],
    ),
    _row(
        "Choked etc from neighbor in the last 12 months",
        ["Q132C", "Q134", "Q136"],
        question_keys=["Q132C", "Q134", "Q136"],
    ),
    _row(
        "Threatened with knife/weapon etc from neighbor in the last 12 months",
        ["Q132D", "Q134", "Q136"],
        question_keys=["Q132D", "Q134", "Q136"],
    ),
    _row(
        "Witnessed parents/caregivers/adult relatives hit etc in the last 12 months",
        ["Q51", "Q52"],
        question_keys=["Q51", "Q52"],
        questions_suffix="Q52 is 13–17 only (per questionnaire).",
    ),
    _row(
        "Hit etc from teacher in the last 12 months",
        ["Q140"],
        question_keys=["Q140"],
    ),
    _row("Offensive names online in the last 12 months"),
    _row("Physically threatened online in the last 12 months"),
    _row("Harassed for sustained period online in the last 12 months"),
    _row("Stalked online in the last 12 months"),
    _row("Purposely embarrassed online in the last 12 months"),
    _row(
        "Not attended school due to safety in the last 12 months",
        ["Q49"],
        question_keys=["Q49"],
    ),
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
    _row(
        "Shouted at you etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q46"],
        question_keys=["Q46_A"],
        questions_suffix=DISCIPLINE_30D_NOTE,
    ),
    _row(
        "Take away privileges etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q46"],
        question_keys=["Q46_C"],
        questions_suffix=DISCIPLINE_30D_NOTE,
    ),
    _row(
        "Insulted you in front of others etc from intimate partner in the last 12 months",
        ["Q310A"],
        question_keys=["Q310A"],
    ),
    _row(
        "Kept you from having your own money etc from intimate partner in the last 12 months",
        ["Q310B"],
        question_keys=["Q310B"],
    ),
    _row(
        "Kept you from talking to friends or family etc from intimate partner in the last 12 months",
        ["Q310C"],
        question_keys=["Q310C"],
    ),
    _row(
        "Demanded to know where you were etc from intimate partner in the last 12 months",
        ["Q310D"],
        question_keys=["Q310D"],
    ),
    _row(
        "Threatened to physically harm you etc from intimate partner in the last 12 months",
        ["Q310E"],
        question_keys=["Q310E"],
    ),
    _row(
        "Made you feel scared from saying mean things etc from peer in the last 12 months",
        ["Q315"],
        question_keys=["Q315_A"],
    ),
    _row(
        "Told lies etc from peer in the last 12 months",
        ["Q315"],
        question_keys=["Q315_B"],
    ),
    _row(
        "Kept you out of things on purpose etc from peer in the last 12 months",
        ["Q315"],
        question_keys=["Q315_C"],
    ),
    _row(
        "Past 12 months money or goods for sex",
        ["Q507"],
        question_keys=["Q507"],
    ),
    _row(
        "Most recent sexual touching in the last 12 months",
        ["Q600", "Q601", "Q602"],
        question_keys=["Q600", "Q601", "Q602"],
    ),
    _row(
        "Most recent attempted sex without consent/forced sex in the last 12 months",
        ["Q700A", "Q701", "Q702"],
        question_keys=["Q700A", "Q701", "Q702"],
    ),
    _row(
        "Most recent pressured into sex in the last 12 months",
        ["Q900A", "Q901", "Q902"],
        question_keys=["Q900A", "Q901", "Q902"],
    ),
    _row(
        "Most recent forced into sex in the last 12 months",
        ["Q800A", "Q801", "Q802"],
        question_keys=["Q800A", "Q801", "Q802"],
    ),
    _row("Sex acts online in the last 12 months"),
    _row("Sent sexual photo/video online in the last 12 months"),
    _row("Anything else sexual online in the last 12 months"),
    _row("Sexually harassed online in the last 12 months"),
    _row(
        "Hit etc your partner in the last 12 months",
        ["Q200A"],
        question_keys=["Q200A_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Hit with object etc your partner in the last 12 months",
        ["Q200B"],
        question_keys=["Q200B_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Choked etc your partner in the last 12 months",
        ["Q200C"],
        question_keys=["Q200C_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc your partner in the last 12 months",
        ["Q200D"],
        question_keys=["Q200D_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Hit etc someone else who is not your partner in the last 12 months",
        ["Q201A"],
        question_keys=["Q201A_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Hit with object etc someone else who is not your partner in the last 12 months",
        ["Q201B"],
        question_keys=["Q201B_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Choked etc someone else who is not your partner in the last 12 months",
        ["Q201C"],
        question_keys=["Q201C_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Threatened with knife/weapon etc someone else who is not your partner in the last 12 months",
        ["Q201D"],
        question_keys=["Q201D_M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Forced your partner or ex to have sex in the last 12 months",
        ["Q1300"],
        question_keys=["Q1300_M"],
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
    spec = importlib.util.spec_from_file_location("nigeria", ng_path)
    ng = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(ng)
    assert [r["category"] for r in ng.OUTCOME_SPEC] == [r["category"] for r in OUTCOME_SPEC]

    rows: list[dict[str, str]] = []
    for spec in OUTCOME_SPEC:
        vars_ = list(spec["vars"])
        qkeys = list(spec["question_keys"] or [])
        suffix = str(spec.get("questions_suffix") or "").strip()
        if not vars_:
            rows.append({"Category": spec["category"], "Variable": "", "Type": "", "Format": "", "Questions": ""})
            continue
        base_q = _questions(qkeys) if qkeys else ""
        if base_q and suffix:
            questions = f"{base_q} || {suffix}".strip()
        else:
            questions = (base_q or suffix).strip()
        rows.append({
            "Category": spec["category"],
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
