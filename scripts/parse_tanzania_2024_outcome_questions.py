#!/usr/bin/env python3
"""Build the Tanzania 2024 five-column outcome codebook."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.docx_export import export_minimal_codebook_docx
from utils.outcomes import OUTCOME_CODEBOOK_COLUMNS, build_outcome_codebook_df, outcome_codebook_to_tsv

RAW = ROOT / "data" / "raw" / "Tanzania 2024"
OUT_DIR = ROOT / "data" / "processed" / "outcome"
OUT_DOCX = OUT_DIR / "jcx_tanzania2024OutcomeCodebook.docx"
OUT_TSV = OUT_DIR / "jcx_tanzania2024OutcomeCodebook.tsv"

YES_NO = "1-YES, 2-NO, 98-DON'T KNOW, 99-DECLINED"
YES_NO_ACASI = "1-YES, 2-NO, 98-DON'T KNOW THE ANSWER, 99-DECLINE TO ANSWER"
COUNT = "66-TOO MANY TO RECALL, 98-DON'T KNOW, 99-DECLINED"
TIMES = "1-ONCE, 2-MORE THAN ONE TIME, 98-DON'T KNOW, 99-DECLINED"
RELATIONSHIP = "relationship categories in questionnaire"


QUESTION_TEXT = {
    "PV1HRT": "PV1: INTIMATE PARTNER VIOLENCE. Slapped, pushed, shoved, shook, or intentionally threw something at you to hurt you?",
    "PV1OBJ": "PV1: INTIMATE PARTNER VIOLENCE. Punched, kicked, whipped, or beat you with an object?",
    "PV1CSD": "PV1: INTIMATE PARTNER VIOLENCE. Choked, smothered, tried to drown you, or burned you intentionally?",
    "PV1WPN": "PV1: INTIMATE PARTNER VIOLENCE. Used or threatened you with a knife, gun or other weapon?",
    "PV112": "PV1: MOST RECENT TIME. Did this happen in the past 12 months?",
    "PV2HRT": "PV2: PEER VIOLENCE. Slapped, pushed, shoved, shook, or intentionally threw something at you to hurt you?",
    "PV2OBJ": "PV2: PEER VIOLENCE. Punched, kicked, whipped, or beat you with an object?",
    "PV2CSD": "PV2: PEER VIOLENCE. Choked, smothered, tried to drown you, or burned you intentionally?",
    "PV2WPN": "PV2: PEER VIOLENCE. Used or threatened you with a knife, gun or other weapon?",
    "PV212": "PV2: MOST RECENT TIME. Did this happen in the past 12 months?",
    "PV2WHO": "The person your own age who did this to you the last time, what was this person's relationship to you?",
    "PV3HRT": "PV3: PARENTS, ADULT CAREGIVERS AND OTHER ADULT RELATIVES. Slapped, pushed, shoved, shook, or intentionally threw something at you to hurt you?",
    "PV3OBJ": "PV3: PARENTS, ADULT CAREGIVERS AND OTHER ADULT RELATIVES. Punched, kicked, whipped, or beat you with an object?",
    "PV3CSD": "PV3: PARENTS, ADULT CAREGIVERS AND OTHER ADULT RELATIVES. Choked, smothered, tried to drown you, or burned you intentionally?",
    "PV3WPN": "PV3: PARENTS, ADULT CAREGIVERS AND OTHER ADULT RELATIVES. Used or threatened you with a knife, gun or other weapon?",
    "PV312": "PV3: MOST RECENT TIME. Did this happen in the past 12 months?",
    "PV3WHO": "The parent, adult caregiver, or adult relative who did this to you the last time, what was this person's relationship to you?",
    "PV4HRT": "PV4: ADULTS IN THE COMMUNITY/NEIGHBORHOOD. Slapped, pushed, shoved, shook, or intentionally threw something at you to hurt you?",
    "PV4OBJ": "PV4: ADULTS IN THE COMMUNITY/NEIGHBORHOOD. Punched, kicked, whipped, or beat you with an object?",
    "PV4CSD": "PV4: ADULTS IN THE COMMUNITY/NEIGHBORHOOD. Choked, smothered, tried to drown you, or burned you intentionally?",
    "PV4WPN": "PV4: ADULTS IN THE COMMUNITY/NEIGHBORHOOD. Used or threatened you with a knife, gun or other weapon?",
    "PV412": "PV4: MOST RECENT TIME. Did this happen in the past 12 months?",
    "PV4WHO": "The adult in the community who did this to you the last time, what was this person's relationship to you?",
    "PVMSCH": "Thinking about all these experiences with parents, other adults, romantic partners, people your own age, or others in the community that we just discussed, did you ever have to miss school because of what happened?",
    "CPTEACH": "In the past 12 months, has a teacher punished or corrected you by shaking you, hitting or slapping you anywhere on your body with a bare hand or a hard object?",
    "WVMHOM": "How many times did you see or hear your parent punched, kicked or beaten up by your other parent, or their partner?",
    "WVMH12": "Did this happen in the past 12 months?",
    "SCHRSN": "What is the main reason for you not attending school?",
    "EV1LOVE": "EV1: PARENT, ADULT CAREGIVER OR OTHER ADULT RELATIVE. Told you that you were not loved, or did not deserve to be loved?",
    "EV1DEAD": "EV1: PARENT, ADULT CAREGIVER OR OTHER ADULT RELATIVE. Said they wished you had never been born or were dead?",
    "EV1DOWN": "EV1: PARENT, ADULT CAREGIVER OR OTHER ADULT RELATIVE. Ridiculed you or put you down, for example said that you were stupid or useless?",
    "EV112M": "EV1: MOST RECENT TIME. Did this happen in the past 12 months?",
    "WVSHOM": "Shouting, yelling, or screaming at you; calling you offensive names, such as 'dumb' or 'lazy'; taking away food; or ignoring you for several hours?",
    "WVSH12": "Did this happen in the past 12 months?",
    "WVCOM": "Taking away privileges, forbidding something you liked or wanted to do; explaining why the behavior is wrong; or giving you a reminder or warning not to do it again?",
    "WVCOM12": "Did this happen in the past 12 months?",
    "EV2HUM": "EV2: INTIMATE PARTNER EMOTIONAL VIOLENCE. Insulted you or humiliated you in front of others?",
    "EV2MON": "EV2: INTIMATE PARTNER EMOTIONAL VIOLENCE. Kept you from having your own money?",
    "EV2TLK": "EV2: INTIMATE PARTNER EMOTIONAL VIOLENCE. Kept you from talking to your friends or family?",
    "EV2KNW": "EV2: INTIMATE PARTNER EMOTIONAL VIOLENCE. Kept track of you by demanding to know where you were and what you were doing?",
    "EV2HRM": "EV2: INTIMATE PARTNER EMOTIONAL VIOLENCE. Threatened to physically harm you?",
    "EV212M": "EV2: MOST RECENT TIME. Did this happen in the past 12 months?",
    "EV3TEASE": "EV3: PEER EMOTIONAL VIOLENCE. Made you get scared or feel really bad because they were calling you names, saying mean things to you, or saying they didn't want you around?",
    "EV3LIE": "EV3: PEER EMOTIONAL VIOLENCE. Told lies or spread rumors about you, or tried to make others dislike you?",
    "EV3EXCL": "EV3: PEER EMOTIONAL VIOLENCE. Kept you out of things on purpose, excluded you from their group of friends, or completely ignored you?",
    "EV312M": "EV3: MOST RECENT TIME. Did this happen in the past 12 months?",
    "TS12M2": "In the past 12 months, did you enter into a sexual relationship with someone mainly in order to get things that you need, money, gifts or other things that are important to you?",
    "SVTCH": "Has anyone ever touched you in a sexual way against your will, but did not try and force you to have sex?",
    "SV112M": "SV1A: TOUCHING - MOST RECENT. Did this happen to you within the past 12 months?",
    "SV2TME": "SV2: ATTEMPTED SEX - LIFETIME. How many times in your life has anyone tried to make you have sex against your will but the sex did not happen?",
    "SV212M": "SV2A: ATTEMPTED SEX - MOST RECENT. Did this happen to you within the past 12 months?",
    "SV3TME": "SV3: PHYSICALLY FORCED SEX - LIFETIME. How many times in your life have you been physically forced to have sex?",
    "SV312M": "SV3A: PHYSICALLY FORCED SEX - MOST RECENT. Did this happen to you within the past 12 months?",
    "SV4TME": "SV4: PRESSURED SEX - LIFETIME. How many times in your life has someone pressured you to have sex against your will, such as through harassment or threats, and the sex happened?",
    "SV412M": "SV4A: PRESSURED INTO SEX - MOST RECENT. Did this happen to you within the past 12 months?",
    "ONLINESXTLK": "In the past 12 months did you talk about sexual acts with someone on the internet, on social media, through email or through text messaging because you were pressured to do so against your will?",
    "ONLINEPIC": "In the past 12 months, did you send a photo or video showing your private parts on the internet, on social media, through email or through text messaging?",
    "PRESSPIC": "Were you ever pressured to send a photo or video showing your private parts against your will?",
    "INTERSEX": "In the past 12 months, did you do anything else sexual on the internet, on social media, through email or through text messaging?",
    "PRESSINTSX": "Were you ever pressured to do anything else sexual online against your will?",
    "OFFNAME": "In the past 12 months, have you been called offensive names on the internet, on social media, through email or through text message?",
    "PHYSTHREAT": "In the past 12 months, have you been physically threatened on the internet, on social media, through email or through text message?",
    "HARRASED": "In the past 12 months, have you been harassed for a sustained period on the internet, on social media, through email or through text message?",
    "STALKED": "In the past 12 months, have you been stalked on the internet, on social media, through email or through text message?",
    "EMBARRASS": "In the past 12 months, have you been purposely embarrassed on the internet, on social media, through email or through text message?",
    "SEXHARASS": "In the past 12 months, have you been sexually harassed on the internet, on social media, through email or through text message?",
    "PVPHRT": "PV PERPETRATION. Slapped, pushed, shoved, shook, or intentionally threw something at a current or ex-partner to hurt them?",
    "PVPOBJ": "PV PERPETRATION. Punched, kicked, whipped, or beat a current or ex-partner with an object?",
    "PVPCSD": "PV PERPETRATION. Choked, smothered, tried to drown, or burned a current or ex-partner intentionally?",
    "PVPWPN": "PV PERPETRATION. Used or threatened a current or ex-partner with a knife, gun or other weapon?",
    "PVP12M": "For physical violence perpetration against a current or ex-partner, did this happen in the past 12 months?",
    "PVPHR1": "PV PERPETRATION. Slapped, pushed, shoved, shook, or intentionally threw something at someone who is not a current or ex-partner to hurt them?",
    "PVPOB1": "PV PERPETRATION. Punched, kicked, whipped, or beat someone who is not a current or ex-partner with an object?",
    "PVPCS1": "PV PERPETRATION. Choked, smothered, tried to drown, or burned someone who is not a current or ex-partner intentionally?",
    "PVPWP1": "PV PERPETRATION. Used or threatened someone who is not a current or ex-partner with a knife, gun or other weapon?",
    "PVP112": "For physical violence perpetration against someone who is not a current or ex-partner, did this happen in the past 12 months?",
    "SVPP": "SV PERPETRATION. Have you ever forced a current or ex-partner to have sex with you against their will?",
    "SVP12M": "Did this happen in the past 12 months?",
    "ONLINEVPART": "In the past 12 months did you pressure a partner or ex-partner against their will to talk about sexual acts online?",
    "ONLINEVOTH": "In the past 12 months did you pressure anyone else against their will to talk about sexual acts online?",
    "ONLINEPICPART": "In the past 12 months did you pressure a partner or ex-partner against their will to send you a photo or video showing their private parts online?",
    "ONLINEPICOTH": "In the past 12 months did you pressure anyone else against their will to send you a photo or video showing their private parts online?",
    "ONLINEOTHPART": "In the past 12 months did you pressure a partner or ex-partner against their will to do anything else sexual online?",
}

# PDF questionnaire question numbers. These are the variables used in the output.
QUESTION_TEXT.update({
    "Q51A": "Shouting, yelling, or screaming at you; calling you offensive names, such as 'dumb' or 'lazy'; taking away food; or ignoring you for several hours?",
    "Q52": "During the past 12 months, were there times you did not go to school or did not leave home because you felt it would be unsafe for any reason?",
    "Q53": "At any time in your life, how many times did you see or hear a parent punch, kick, or beat your other parent or their partner?",
    "Q55": "How many times did you see or hear a parent punch, kick, or beat your brothers or sisters?",
    "Q100A": "Has your current or ex partner ever slapped, pushed, shoved, shook, or intentionally threw something at you to hurt you?",
    "Q100B": "Has your current or ex partner ever punched, kicked, whipped, or beat you with an object?",
    "Q100C": "Has your current or ex partner ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q100D": "Has your current or ex partner ever used or threatened you with a knife, gun or other weapon?",
    "Q102A": "Most recent time. Did this happen in the past 12 months?",
    "Q110A": "Has a person your own age ever slapped, pushed, shoved, shook, or intentionally threw something at you to hurt you?",
    "Q110B": "Has a person your own age ever punched, kicked, whipped, or beat you with an object?",
    "Q110C": "Has a person your own age ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q110D": "Has a person your own age ever used or threatened you with a knife, gun or other weapon?",
    "Q112": "Most recent time. Did this happen in the past 12 months?",
    "Q114": "The person your own age who did this to you the last time, what was this person's relationship to you?",
    "Q120A": "Has a parent, adult caregiver, or other adult relative ever slapped, pushed, shoved, shook, or intentionally threw something at you to hurt you?",
    "Q120B": "Has a parent, adult caregiver, or other adult relative ever punched, kicked, whipped, or beat you with an object?",
    "Q120C": "Has a parent, adult caregiver, or other adult relative ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q120D": "Has a parent, adult caregiver, or other adult relative ever used or threatened you with a knife, gun or other weapon?",
    "Q124": "The parent, adult caregiver, or adult relative who did this to you the last time, what was this person's relationship to you?",
    "Q132A": "Has an adult in your community/neighborhood ever slapped, pushed, shoved, shook, or intentionally threw something at you to hurt you?",
    "Q132B": "Has an adult in your community/neighborhood ever punched, kicked, whipped, or beat you with an object?",
    "Q132C": "Has an adult in your community/neighborhood ever choked, smothered, tried to drown you, or burned you intentionally?",
    "Q132D": "Has an adult in your community/neighborhood ever used or threatened you with a knife, gun or other weapon?",
    "Q136": "The adult in the community who did this to you the last time, what was this person's relationship to you?",
    "Q142": "In the past 12 months, has a teacher punished or corrected you by shaking you, hitting or slapping you anywhere on your body with a bare hand or a hard object?",
    "Q300A": "Told you that you were not loved, or did not deserve to be loved?",
    "Q300B": "Said they wished you had never been born or were dead?",
    "Q300C": "Ridiculed you or put you down, for example said that you were stupid or useless?",
    "Q302": "Most recent time. Did this happen in the past 12 months?",
    "Q310A": "Has a current or ex partner ever insulted, humiliated, or made fun of you in front of others?",
    "Q310B": "Has a current or ex partner ever kept you from having your own money?",
    "Q310C": "Has a current or ex partner ever tried to keep you from seeing or talking to your family or friends?",
    "Q310D": "Has a current or ex partner ever kept track of you by demanding to know where you were and what you were doing?",
    "Q310E": "Has a current or ex partner ever threatened to physically harm you?",
    "Q312": "Most recent time. Did this happen in the past 12 months?",
    "Q317A": "Has someone about your own age ever made you get scared or feel really bad because they were calling you names, saying mean things to you, or saying they did not want you around?",
    "Q317B": "Has someone about your own age ever told lies or spread rumors about you, or tried to make others dislike you?",
    "Q317C": "Has someone about your own age ever kept you out of things on purpose, excluded you from their group of friends, or completely ignored you?",
    "Q502": "In the past 12 months, did you enter into a sexual relationship with someone mainly in order to get things that you need, money, gifts or other things that are important to you?",
    "Q600": "Has anyone ever touched you in a sexual way against your will, but did not try and force you to have sex?",
    "Q602": "Touching, most recent. Did this happen to you within the past 12 months?",
    "Q700A": "Has a current or ex-partner ever tried to make you have sex against your will but the sex did not happen?",
    "Q700B": "Has anyone else ever tried to make you have sex against your will but the sex did not happen?",
    "Q702": "Attempted sex, most recent. Did this happen to you within the past 12 months?",
    "Q800A": "Has a current or ex partner ever physically forced you to have sex against your will?",
    "Q800B": "Has anyone else ever physically forced you to have sex against your will?",
    "Q802": "Physically forced sex, most recent. Did this happen to you within the past 12 months?",
    "Q900A": "Has a current or ex partner ever pressured you to have sex against your will, such as through harassment or threats, and the sex did happen?",
    "Q900B": "Has anyone else ever pressured you to have sex against your will, such as through harassment or threats, and the sex did happen?",
    "Q902": "Pressured into sex, most recent. Did this happen to you within the past 12 months?",
    "Q1300": "Have you ever forced a current or ex partner to have sex with you against their will?",
    "Q1301": "Did this happen in the past 12 months?",
    "Q1302": "Have you ever forced someone who was not your current or ex partner to have sex with you against their will?",
    "Q1303": "Did this happen in the past 12 months?",
    "Q1305": "In the past 12 months did you talk about sexual acts with someone online because you were pressured to do so against your will?",
    "Q1307": "In the past 12 months, did you send a photo or video showing your private parts online?",
    "Q1308": "Were you ever pressured to send a photo or video showing your private parts against your will?",
    "Q1310": "In the past 12 months, did you do anything else sexual online?",
    "Q1311": "Were you ever pressured to do anything else sexual online against your will?",
    "Q1315A": "Being called offensive names online in the past 12 months.",
    "Q1315B": "Being physically threatened online in the past 12 months.",
    "Q1315C": "Being harassed for a sustained period online in the past 12 months.",
    "Q1315D": "Being stalked online in the past 12 months.",
    "Q1315E": "Had someone try to purposely embarrass you online in the past 12 months.",
    "Q1315F": "Being sexually harassed online in the past 12 months.",
    "Q1318": "In the past 12 months did you pressure a partner or ex-partner against their will to talk about sexual acts online?",
    "Q1319": "In the past 12 months did you pressure anyone else against their will to talk about sexual acts online?",
    "Q1320": "In the past 12 months did you pressure a partner or ex-partner against their will to send you a photo or video showing their private parts online?",
    "Q1321": "In the past 12 months did you pressure anyone else against their will to send you a photo or video showing their private parts online?",
    "Q1322": "In the past 12 months did you pressure a partner or ex-partner against their will to do anything else sexual online?",
    "Q200A": "Have you ever slapped, pushed, shoved, shook, or intentionally threw something to hurt a current or ex partner?",
    "Q200B": "Have you ever punched, kicked, whipped, or beat a current or ex partner with an object?",
    "Q200C": "Have you ever choked, smothered, tried to drown, or burned a current or ex partner intentionally?",
    "Q200D": "Have you ever used or threatened a current or ex partner with a knife, gun or other weapon?",
    "Q200E": "Thinking about all of these experiences with your current or ex-partner, did this happen in the past 12 months?",
    "Q201A": "Have you ever slapped, pushed, shoved, shook, or intentionally threw something to hurt someone who is not a current or ex partner?",
    "Q201B": "Have you ever punched, kicked, whipped, or beat someone who is not a current or ex partner with an object?",
    "Q201C": "Have you ever choked, smothered, tried to drown, or burned someone who is not a current or ex partner intentionally?",
    "Q201D": "Have you ever used or threatened someone who is not a current or ex partner with a knife, gun or other weapon?",
    "Q201E": "Thinking about all of these experiences with someone who is not your current or ex partner, did this happen in the past 12 months?",
})

FORMAT_OVERRIDES = {
    "SCHRSN": "1-VIOLENCE, 2-NO MONEY FOR SCHOOL/SUPPLIES, 3-HAVE TO WORK, 4-DON'T LIKE SCHOOL, 5-GRADUATED/FINISHED SCHOOL, 6-PREGNANT/MARRIED, 7-SCHOOL TOO FAR AWAY, 8-ILLNESS/SICKNESS, 9-EXPULSION, 10-CARING FOR SICK/CHILDREN, 77-OTHER, 98-DON'T KNOW, 99-DECLINED",
    "PV4WHO": "1-MALE POLICE/SECURITY PERSON, 2-MALE HEALTH CARE WORKER, 4-MALE EMPLOYER, 6-MALE COMMUNITY LEADER, 8-MALE RELIGIOUS LEADER, 9-MALE TRADITIONAL HEALER, 12-MALE NEIGHBOR, 77-OTHER MALE, 88-OTHER FEMALE, 98-DON'T KNOW, 99-DECLINED",
    "PV2WHO": "1-MALE RELATIVE, 2-MALE FRIEND, 3-MALE CLASSMATE/SCHOOLMATE, 4-MALE NEIGHBOR, 5-MALE STRANGER, 77-OTHER MALE, 88-OTHER FEMALE, 98-DON'T KNOW, 99-DECLINED",
    "PV3WHO": "1-MALE FATHER, 2-STEP FATHER, 3-BROTHER, 4-STEP BROTHER, 5-UNCLE, 6-GRANDFATHER, 77-OTHER MALE CAREGIVER, 88-OTHER FEMALE CAREGIVER, 98-DON'T KNOW, 99-DECLINED",
    "Q53": TIMES,
    "Q55": TIMES,
    "Q114": RELATIONSHIP,
    "Q124": RELATIONSHIP,
    "Q136": RELATIONSHIP,
}


def _format_for(var: str) -> str:
    vu = var.upper()
    if vu in FORMAT_OVERRIDES:
        return FORMAT_OVERRIDES[vu]
    return YES_NO_ACASI if vu in {
        "Q1300", "Q1301", "Q1302", "Q1303",
        "Q1318", "Q1319", "Q1320", "Q1321", "Q1322",
        "Q200A", "Q200B", "Q200C", "Q200D", "Q200E",
        "Q201A", "Q201B", "Q201C", "Q201D", "Q201E",
    } else YES_NO


def _fmt(vars_: list[str]) -> str:
    return "; ".join(f"{v}: {_format_for(v)}" for v in vars_)


def _questions(vars_: list[str]) -> str:
    return " || ".join(dict.fromkeys(QUESTION_TEXT[v] for v in vars_ if v in QUESTION_TEXT))


def _row(category: str, vars_: list[str] | None = None, *, question_vars: list[str] | None = None) -> dict[str, object]:
    return {"category": category, "vars": vars_ or [], "question_vars": question_vars}


OUTCOME_SPEC = [
    _row("Hit etc from parents/caregivers/adult relatives in the last 12 months", ["Q120A"]),
    _row("Hit with object etc from parents/caregivers/adult relatives in the last 12 months", ["Q120B"]),
    _row("Choked etc from parents/caregivers/adult relatives in the last 12 months", ["Q120C"]),
    _row("Burned etc from parents/caregivers/adult relatives in the last 12 months", ["Q120C"]),
    _row("Threatened with knife/weapon etc from parents/caregivers/adult relatives in the last 12 months", ["Q120D"]),
    _row("Hit etc from public authority figure in the last 12 months", ["Q132A", "Q136"]),
    _row("Choked etc from public authority figure in the last 12 months", ["Q132C", "Q136"]),
    _row("Burned etc from public authority figure in the last 12 months", ["Q132C", "Q136"]),
    _row("Threatened with knife/weapon etc from public authority figure in the last 12 months", ["Q132D", "Q136"]),
    _row("Hit etc from intimate partner in the last 12 months", ["Q100A", "Q102A"]),
    _row("Hit with object etc from intimate partner in the last 12 months", ["Q100B", "Q102A"]),
    _row("Choked etc from intimate partner in the last 12 months", ["Q100C", "Q102A"]),
    _row("Threatened with knife/weapon etc from intimate partner in the last 12 months", ["Q100D", "Q102A"]),
    _row("Hit etc from peer in the last 12 months", ["Q110A", "Q112"]),
    _row("Hit with object etc from peer in the last 12 months", ["Q110B", "Q112"]),
    _row("Choked etc from peer in the last 12 months", ["Q110C", "Q112"]),
    _row("Threatened with knife/weapon etc from peer in the last 12 months", ["Q110D", "Q112"]),
    _row("Hit etc from neighbor in the last 12 months", ["Q132A", "Q136"]),
    _row("Hit with object etc from neighbor in the last 12 months", ["Q132B", "Q136"]),
    _row("Choked etc from neighbor in the last 12 months", ["Q132C", "Q136"]),
    _row("Threatened with knife/weapon etc from neighbor in the last 12 months", ["Q132D", "Q136"]),
    _row("Witnessed parents/caregivers/adult relatives hit etc in the last 12 months", ["Q53"]),
    _row("Hit etc from teacher in the last 12 months", ["Q142"]),
    _row("Offensive names online in the last 12 months", ["Q1315A"]),
    _row("Physically threatened online in the last 12 months", ["Q1315B"]),
    _row("Harassed for sustained period online in the last 12 months", ["Q1315C"]),
    _row("Stalked online in the last 12 months", ["Q1315D"]),
    _row("Purposely embarrassed online in the last 12 months", ["Q1315E"]),
    _row("Not attended school due to safety in the last 12 months", ["Q52"]),
    _row("Said not loved etc from parents/caregivers/adult relatives in the last 12 months", ["Q300A", "Q302"]),
    _row("Wished you were not born or dead etc from parents/caregivers/adult relatives in the last 12 months", ["Q300B", "Q302"]),
    _row("Ridiculed you etc from parents/caregivers/adult relatives in the last 12 months", ["Q300C", "Q302"]),
    _row("Threatened to abandon you etc from parents/caregivers/adult relatives in the last 12 months"),
    _row("Shouted at you etc from parents/caregivers/adult relatives in the last 12 months", ["Q51A"]),
    _row("Take away privileges etc from parents/caregivers/adult relatives in the last 12 months"),
    _row("Insulted you in front of others etc from intimate partner in the last 12 months", ["Q310A", "Q312"]),
    _row("Kept you from having your own money etc from intimate partner in the last 12 months", ["Q310B", "Q312"]),
    _row("Kept you from talking to friends or family etc from intimate partner in the last 12 months", ["Q310C", "Q312"]),
    _row("Demanded to know where you were etc from intimate partner in the last 12 months", ["Q310D", "Q312"]),
    _row("Threatened to physically harm you etc from intimate partner in the last 12 months", ["Q310E", "Q312"]),
    _row("Made you feel scared from saying mean things etc from peer in the last 12 months", ["Q317A"]),
    _row("Told lies etc from peer in the last 12 months", ["Q317B"]),
    _row("Kept you out of things on purpose etc from peer in the last 12 months", ["Q317C"]),
    _row("Past 12 months money or goods for sex", ["Q502"]),
    _row("Most recent sexual touching in the last 12 months", ["Q600", "Q602"]),
    _row("Most recent attempted sex without consent/forced sex in the last 12 months", ["Q700A", "Q700B", "Q702"]),
    _row("Most recent pressured into sex in the last 12 months", ["Q900A", "Q900B", "Q902"]),
    _row("Most recent forced into sex in the last 12 months", ["Q800A", "Q800B", "Q802"]),
    _row("Sex acts online in the last 12 months", ["Q1305"]),
    _row("Sent sexual photo/video online in the last 12 months", ["Q1307", "Q1308"]),
    _row("Anything else sexual online in the last 12 months", ["Q1310", "Q1311"]),
    _row("Sexually harassed online in the last 12 months", ["Q1315F"]),
    _row("Hit etc your partner in the last 12 months", ["Q200A", "Q200E"]),
    _row("Hit with object etc your partner in the last 12 months", ["Q200B", "Q200E"]),
    _row("Choked etc your partner in the last 12 months", ["Q200C", "Q200E"]),
    _row("Threatened with knife/weapon etc your partner in the last 12 months", ["Q200D", "Q200E"]),
    _row("Hit etc someone else who is not your partner in the last 12 months", ["Q201A", "Q201E"]),
    _row("Hit with object etc someone else who is not your partner in the last 12 months", ["Q201B", "Q201E"]),
    _row("Choked etc someone else who is not your partner in the last 12 months", ["Q201C", "Q201E"]),
    _row("Threatened with knife/weapon etc someone else who is not your partner in the last 12 months", ["Q201D", "Q201E"]),
    _row("Forced your partner or ex to have sex in the last 12 months", ["Q1300", "Q1301"]),
    _row("Pressured your partner or ex to talk about sex online/virtual in the last 12 months", ["Q1318"]),
    _row("Pressured someone else who is not your partner to talk about sex online/virtual in the last 12 months", ["Q1319"]),
    _row("Pressured your partner or ex to send you sex material online/virtual in the last 12 months", ["Q1320"]),
    _row("Pressured someone else who is not your partner to send you sex material online/virtual in the last 12 months", ["Q1321"]),
    _row("Pressured your partner or ex to do anything else sexual online/virtual in the last 12 months", ["Q1322"]),
]


def _type_for(vars_: list[str]) -> str:
    if not vars_:
        return ""
    return "binary" if _format_for(vars_[0]).startswith("1-YES, 2-NO") else "categorical"


def main() -> None:
    rows: list[dict[str, str]] = []
    for spec in OUTCOME_SPEC:
        vars_ = list(spec["vars"])
        question_vars = list(spec["question_vars"] or vars_)
        if not vars_:
            rows.append({"Category": spec["category"], "Variable": "", "Type": "", "Format": "", "Questions": ""})
            continue
        rows.append({
            "Category": spec["category"],
            "Variable": "; ".join(vars_),
            "Type": _type_for(vars_),
            "Format": _fmt(vars_),
            "Questions": _questions(question_vars),
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
