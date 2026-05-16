#!/usr/bin/env python3
"""Build the Lesotho 2018 five-column outcome codebook from ENG respondent questionnaire PDFs (PDF-first).

Variable names (Q…) were cross-checked against ``LESOTHO_VACS_2018_PUD_UR.dta`` column names. Question
wording is taken from ``LESOTHO_VACS_2018_Female_RespondentQuestionnaire_ENG.pdf`` and the male PDF where
perpetration wording differs. Where the Lesotho instrument does not support a per-act past-12-months gate,
notes are appended in the Questions column (Category strings stay aligned with Nigeria for QA).
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

RAW = ROOT / "data" / "raw" / "Lesotho Stata"
OUT_DIR = ROOT / "data" / "processed" / "outcome"
OUT_DOCX = OUT_DIR / "jcx_lesotho2018OutcomeCodebook.docx"
OUT_TSV = OUT_DIR / "jcx_lesotho2018OutcomeCodebook.tsv"

YES_NO_99 = "1-YES, 2-NO, 98-DON'T KNOW, 99-DECLINED"
WITNESS_LESOTHO = "1-NEVER, 2-ONCE, 3-MORE THAN ONE TIME, 98-DON'T KNOW, 99-DECLINED"
LIFETIME_COUNT = "1-ONCE OR INDICATED, 66-TOO MANY TO RECALL, 98-DON'T KNOW, 99-DECLINED"
NUMBER = "NUMBER (see questionnaire)"
REL_LIST = "relationship categories in questionnaire (see questionnaire)"
LIFETIME_NOTE = "(Form: lifetime act; no separate past-12-months perpetration item.)"
PV_AGG_12 = "(Lesotho: one past-12-months item per PV module—Q112 peer, Q122 parent, Q134 community—for the most recent incident overall, not necessarily the same letter as the lifetime act.)"
EV2_12 = "(Lesotho: Q312 is past 12 months for the most recent intimate emotional incident overall, not necessarily item A–E alone.)"
SCHOOL_NOTE = "(Closest match: Q143 follows PV modules; not a general ‘unsafe to leave home’ item.)"
WITNESS_NOTE = "(Witnessing stem is mother/stepmother hit by father/stepfather; not all caregiver configurations.)"
Q46A_NOTE = "(Q46A is past 12 months and bundles shouting, offensive names, taking away food, or ignoring for several hours.)"
Q46C_NOTE = "(Q46C bundles taking away privileges with explanatory discipline and reminders; past 12 months.)"
ONLINE_GAP = "(No dedicated online-harassment or cyber-sexual items found in ENG respondent PDFs; EV3 Q315 intro mentions technology/social media only.)"

QUESTION_TEXT: dict[str, str] = {
    "Q120A": "PV3: Has a parent, adult caregiver, or other adult relative ever slapped, pushed, shoved, shook, pulled hair, twisted arm, pinched, or intentionally thrown something at you to hurt you?",
    "Q120B": "PV3: Has a parent, adult caregiver, or other adult relative ever punched, kicked, whipped, or beat you with an object?",
    "Q120C": "PV3: Has a parent, adult caregiver, or other adult relative ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q120D": "PV3: Has a parent, adult caregiver, or other adult relative ever used or threatened you with a stick, knife, gun or other weapon?",
    "Q122": "PV3: MOST RECENT TIME — Did this happen in the last 12 months?",
    "Q132A": "PV4: Has an adult in your community/neighborhood ever slapped, pushed, shoved, shook, pulled hair, twisted arm, pinched or intentionally thrown something at you to hurt you?",
    "Q132B": "PV4: Has an adult in your community/neighborhood ever punched, kicked, whipped, or beat you with an object?",
    "Q132C": "PV4: Has an adult in your community/neighborhood ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q132D": "PV4: Has an adult in your community/neighborhood ever used or threatened you with a stick, knife, gun or other weapon?",
    "Q134": "PV4: MOST RECENT TIME — Did this happen in the last 12 months?",
    "Q136": "PV4: The adult in the community who did this to you the last time — what was this person’s relationship to you?",
    "Q100A": "PV1: Has a romantic partner ever slapped, pushed, shoved, shook, pulled hair, twisted arm, pinched, or intentionally thrown something at you to hurt you? (stem includes partner types in questionnaire.)",
    "Q100A1": "PV1: Item A — Has this happened in the past 12 months?",
    "Q100B": "PV1: Has a romantic partner ever punched, kicked, whipped, or beat you with an object?",
    "Q100B1": "PV1: Item B — Has this happened in the past 12 months?",
    "Q100C": "PV1: Has a romantic partner ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q100C1": "PV1: Item C — Has this happened in the past 12 months?",
    "Q100D": "PV1: Has a romantic partner ever used or threatened you with a stick, knife, gun or other weapon?",
    "Q100D1": "PV1: Item D — Has this happened in the past 12 months?",
    "Q110A": "PV2: Has a person your own age ever slapped, pushed, shoved, shook, pulled hair, twisted arm, pinched, or intentionally thrown something at you to hurt you?",
    "Q110B": "PV2: Has a person your own age ever punched, kicked, whipped, or beat you with an object?",
    "Q110C": "PV2: Has a person your own age ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q110D": "PV2: Has a person your own age ever used or threatened you with a stick, knife, gun or other weapon?",
    "Q112": "PV2: MOST RECENT TIME — Did this happen in the last 12 months?",
    "Q51": "How many times did you see or hear your mother or step-mother being hit, punched, kicked or beaten by your father or step-father?",
    "Q52": "Did this happen in the last 12 months?",
    "Q140": "In the past 12 months, has a teacher punished or corrected you by shaking you, hitting or slapping you anywhere on your body with a bare hand or a hard object?",
    "Q143": "PV SERVICES: Thinking about all these experiences with parents, other adults, romantic partners, people your own age, and someone in the community that we just discussed, did you ever have to miss school because of what happened?",
    "Q300A": "EV1: Has a parent, adult caregiver or other adult relative ever told you that you were not loved, or did not deserve to be loved?",
    "Q300B": "EV1: Has a parent, adult caregiver or other adult relative ever said they wished you had never been born or were dead?",
    "Q300C": "EV1: Has a parent, adult caregiver or other adult relative ever ridiculed you or put you down, for example said that you were stupid or useless?",
    "Q302": "EV1: MOST RECENT TIME — Did this happen in the last 12 months?",
    "Q46A": "DISCIPLINE (past 12 months): Has a parent or adult caregiver punished or corrected you by shouting, yelling, or screaming at you; calling you offensive names; taking away food; or ignoring you for several hours?",
    "Q46C": "DISCIPLINE (past 12 months): Has a parent or adult caregiver punished or corrected you by taking away privileges, forbidding something you liked or wanted to do; explaining why the behavior is wrong; or giving you a reminder or warning not to do it again?",
    "Q310A": "EV2: Has a romantic partner ever insulted, humiliated, or made fun of you in front of others?",
    "Q310B": "EV2: Has a romantic partner ever kept you from having your own money?",
    "Q310C": "EV2: Has a romantic partner ever tried to keep you from seeing or talking to your family or friends?",
    "Q310D": "EV2: Has a romantic partner ever kept track of you by demanding to know where you were and what you were doing?",
    "Q310E": "EV2: Has a romantic partner ever made threats to physically harm you?",
    "Q312": "EV2: Did this happen in the last 12 months? (follows frequency stem in questionnaire.)",
    "Q315A": "EV3 (past 12 months): Has someone your own age made you get scared or feel really bad because they were calling you names, saying mean things to you, or saying they didn’t want you around?",
    "Q315B": "EV3 (past 12 months): Has someone your own age told lies or spread rumors about you, or tried to make others dislike you?",
    "Q315C": "EV3 (past 12 months): Has someone your own age kept you out of things on purpose, excluded you from their group of friends, or completely ignored you?",
    "Q507": "In the last 12 months, how many times did you have sex with someone mainly in order to get things that you need such as money, gifts, or other things that are important to you?",
    "Q600": "Has anyone ever touched you in a sexual way without your permission, but did not try and force you to have sex?",
    "Q601": "SV1: How many times in your life has this happened?",
    "Q602": "SV1A: TOUCHING — MOST RECENT — Did this happen to you within the past 12 months?",
    "Q700A": "ATTEMPTED FORCED SEX: Has a romantic partner ever tried to make you have sex against your will but did not succeed?",
    "Q700B": "ATTEMPTED FORCED SEX: Has anyone [else] ever tried to make you have sex against your will but did not succeed?",
    "Q701": "SV2: How many times in your life has anyone tried to make you have sex against your will but did not succeed?",
    "Q702": "SV2A: ATTEMPTED SEX — MOST RECENT — Did this happen to you within the past 12 months?",
    "Q800A": "PHYSICALLY FORCED SEX: Has a romantic partner ever physically forced you to have sex and did succeed?",
    "Q800B": "PHYSICALLY FORCED SEX: Has anyone [else] ever physically forced you to have sex against your will and did succeed?",
    "Q801": "SV3: How many times in your life have you been physically forced to have sex?",
    "Q802": "SV3A: PHYSICALLY FORCED SEX — MOST RECENT — Did this happen to you within the past 12 months?",
    "Q900A": "PRESSURED SEX: Has a romantic partner ever pressured you in a non-physical way to have sex against your will and did succeed?",
    "Q900B": "PRESSURED SEX: Has anyone [else] ever pressured you in a non-physical way to have sex against your will and did succeed?",
    "Q901": "SV4: How many times in your life has someone pressured you in a non-physical way to have sex against your will and did succeed?",
    "Q902": "SV4A: PRESSURED INTO SEX — MOST RECENT — Did this happen to you within the past 12 months?",
    "Q200A_M": "PV perpetration (male form): Have you ever slapped, pushed, shoved, shook, pulled hair, twisted arm, pinched or intentionally thrown something to hurt a current or previous partner?",
    "Q200B_M": "PV perpetration (male form): Have you ever punched, kicked, whipped, or beat them with an object?",
    "Q200C_M": "PV perpetration (male form): Have you ever choked, smothered, tried to drown them, or burned them intentionally?",
    "Q200D_M": "PV perpetration (male form): Have you ever used or threatened them with a stick, knife, gun or other weapon?",
    "Q201A_M": "PV perpetration (male form): Same toward someone who is not a current or previous partner — slapped, pushed, shoved, etc.",
    "Q201B_M": "PV perpetration (male form): Same — punched, kicked, whipped, or beat with an object.",
    "Q201C_M": "PV perpetration (male form): Same — choked, smothered, tried to drown, or burned intentionally.",
    "Q201D_M": "PV perpetration (male form): Same — used or threatened with a stick, knife, gun or other weapon.",
    "Q1300F": "SV perpetration (female form): Have you ever forced a romantic partner to have sex with you when they did not want to?",
    "Q1300M": "SV perpetration (male form): Have you ever forced a romantic partner to have sex with you when they did not want to?",
}

FORMAT_OVERRIDES: dict[str, str] = {
    "Q51": WITNESS_LESOTHO,
    "Q52": YES_NO_99,
    "Q136": REL_LIST,
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
        questions_suffix=PV_AGG_12,
    ),
    _row(
        "Hit with object etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q120B", "Q122"],
        question_keys=["Q120B", "Q122"],
        questions_suffix=PV_AGG_12,
    ),
    _row(
        "Choked etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q120C", "Q122"],
        question_keys=["Q120C", "Q122"],
        questions_suffix=PV_AGG_12,
    ),
    _row(
        "Burned etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q120C", "Q122"],
        question_keys=["Q120C", "Q122"],
        questions_suffix=PV_AGG_12,
    ),
    _row(
        "Threatened with knife/weapon etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q120D", "Q122"],
        question_keys=["Q120D", "Q122"],
        questions_suffix=PV_AGG_12,
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
    _row(
        "Hit etc from intimate partner in the last 12 months",
        ["Q100A", "Q100A1"],
        question_keys=["Q100A", "Q100A1"],
    ),
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
        ["Q110A", "Q112"],
        question_keys=["Q110A", "Q112"],
        questions_suffix=PV_AGG_12,
    ),
    _row(
        "Hit with object etc from peer in the last 12 months",
        ["Q110B", "Q112"],
        question_keys=["Q110B", "Q112"],
        questions_suffix=PV_AGG_12,
    ),
    _row(
        "Choked etc from peer in the last 12 months",
        ["Q110C", "Q112"],
        question_keys=["Q110C", "Q112"],
        questions_suffix=PV_AGG_12,
    ),
    _row(
        "Threatened with knife/weapon etc from peer in the last 12 months",
        ["Q110D", "Q112"],
        question_keys=["Q110D", "Q112"],
        questions_suffix=PV_AGG_12,
    ),
    _row(
        "Hit etc from neighbor in the last 12 months",
        ["Q132A", "Q134", "Q136"],
        question_keys=["Q132A", "Q134", "Q136"],
    ),
    _row(
        "Hit with object etc from neighbor in the last 12 months",
        ["Q132B", "Q134", "Q136"],
        question_keys=["Q132B", "Q134", "Q136"],
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
        questions_suffix=WITNESS_NOTE,
    ),
    _row(
        "Hit etc from teacher in the last 12 months",
        ["Q140"],
        question_keys=["Q140"],
    ),
    _row(
        "Offensive names online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Physically threatened online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Harassed for sustained period online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Stalked online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Purposely embarrassed online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Not attended school due to safety in the last 12 months",
        ["Q143"],
        question_keys=["Q143"],
        questions_suffix=SCHOOL_NOTE,
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
    _row(
        "Threatened to abandon you etc from parents/caregivers/adult relatives in the last 12 months",
        questions_suffix="(No matching item located in ENG respondent PDF.)",
    ),
    _row(
        "Shouted at you etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q46A"],
        question_keys=["Q46A"],
        questions_suffix=Q46A_NOTE,
    ),
    _row(
        "Take away privileges etc from parents/caregivers/adult relatives in the last 12 months",
        ["Q46C"],
        question_keys=["Q46C"],
        questions_suffix=Q46C_NOTE,
    ),
    _row(
        "Insulted you in front of others etc from intimate partner in the last 12 months",
        ["Q310A", "Q312"],
        question_keys=["Q310A", "Q312"],
        questions_suffix=EV2_12,
    ),
    _row(
        "Kept you from having your own money etc from intimate partner in the last 12 months",
        ["Q310B", "Q312"],
        question_keys=["Q310B", "Q312"],
        questions_suffix=EV2_12,
    ),
    _row(
        "Kept you from talking to friends or family etc from intimate partner in the last 12 months",
        ["Q310C", "Q312"],
        question_keys=["Q310C", "Q312"],
        questions_suffix=EV2_12,
    ),
    _row(
        "Demanded to know where you were etc from intimate partner in the last 12 months",
        ["Q310D", "Q312"],
        question_keys=["Q310D", "Q312"],
        questions_suffix=EV2_12,
    ),
    _row(
        "Threatened to physically harm you etc from intimate partner in the last 12 months",
        ["Q310E", "Q312"],
        question_keys=["Q310E", "Q312"],
        questions_suffix=EV2_12,
    ),
    _row(
        "Made you feel scared from saying mean things etc from peer in the last 12 months",
        ["Q315A"],
        question_keys=["Q315A"],
    ),
    _row(
        "Told lies etc from peer in the last 12 months",
        ["Q315B"],
        question_keys=["Q315B"],
    ),
    _row(
        "Kept you out of things on purpose etc from peer in the last 12 months",
        ["Q315C"],
        question_keys=["Q315C"],
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
        ["Q700A", "Q700B", "Q701", "Q702"],
        question_keys=["Q700A", "Q700B", "Q701", "Q702"],
    ),
    _row(
        "Most recent pressured into sex in the last 12 months",
        ["Q900A", "Q900B", "Q901", "Q902"],
        question_keys=["Q900A", "Q900B", "Q901", "Q902"],
    ),
    _row(
        "Most recent forced into sex in the last 12 months",
        ["Q800A", "Q800B", "Q801", "Q802"],
        question_keys=["Q800A", "Q800B", "Q801", "Q802"],
    ),
    _row(
        "Sex acts online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Sent sexual photo/video online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Anything else sexual online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Sexually harassed online in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
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
        question_keys=["Q1300F", "Q1300M"],
        questions_suffix=LIFETIME_NOTE,
    ),
    _row(
        "Pressured your partner or ex to talk about sex online/virtual in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Pressured someone else who is not your partner to talk about sex online/virtual in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Pressured your partner or ex to send you sex material online/virtual in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Pressured someone else who is not your partner to send you sex material online/virtual in the last 12 months",
        questions_suffix=ONLINE_GAP,
    ),
    _row(
        "Pressured your partner or ex to do anything else sexual online/virtual in the last 12 months",
        questions_suffix=ONLINE_GAP,
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
