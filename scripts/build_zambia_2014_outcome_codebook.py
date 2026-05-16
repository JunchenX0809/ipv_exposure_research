#!/usr/bin/env python3
"""
Zambia 2014 outcome codebook — **five columns**: Category, Variable, Type, Format, Questions.

- **Category**: full team outcome label (from ``ZAMBIA_2014_OUTCOME_SPEC``).
- **Variable**: ``"; "``.join(format_vars)`` (screener first, then timing columns); blank when no match.
- **Type** / **Format**: from Female/Male PUD + parsed **codebook** PDFs for all ``format_vars``.
- **Questions**: verbatim respondent codebook text for each name in ``format_vars`` (joined with
  `` || ``). Default: **Female** + **Male** where both exist; rows with ``questions_male_only`` use
  **male** codebook only (perpetration). HOH items use the HOH codebook only.

Run::

    .venv/bin/python scripts/build_zambia_2014_outcome_codebook.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import pandas as pd
    import pyreadstat
except ImportError:
    venv_py = ROOT / ".venv" / "bin" / "python"
    sys.stderr.write(
        "Missing dependencies. Use:\n"
        f"  {venv_py} {Path(__file__).resolve().relative_to(ROOT)}\n"
    )
    raise SystemExit(1) from None

from utils.covariates import classify_variable_type
from utils.docx_export import export_minimal_codebook_docx
from utils.outcomes import (
    OUTCOME_CODEBOOK_COLUMNS,
    build_outcome_codebook_df,
    outcome_codebook_to_tsv,
    verify_variable_against_dta,
)
from utils.pdf_parse import extract_codebook_entries, entries_by_variable_name
from utils.zambia_2014_outcome_codebook_data import ZAMBIA_2014_OUTCOME_SPEC

ZAMBIA_DIR = ROOT / "data" / "raw" / "Zambia Stata"
FEMALE_DTA = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Female_PUD.dta"
MALE_DTA = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Male_PUD.dta"
FEMALE_CODEBOOK = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Females_Codebook.pdf"
MALE_CODEBOOK = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Males_Codebook.pdf"
FEMALE_HOH_CODEBOOK = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Females_HOHCodebook.pdf"
OUT_DOCX = ROOT / "data" / "processed" / "jcx_zambiaOutcomeCodebook.docx"
OUT_TSV = ROOT / "data" / "processed" / "jcx_zambiaOutcomeCodebook.tsv"


def _join_formats(idx: dict[str, object], vars_: list[str]) -> str:
    parts: list[str] = []
    for vn in vars_:
        key = vn.upper()
        if key not in idx:
            parts.append(f"{vn}: — missing from codebook index —")
            continue
        e = idx[key]
        fs = e.format_string or ""
        parts.append(f"{e.variable_name}: {fs}" if fs else f"{e.variable_name}: ")
    return "; ".join(parts)


def _dual_question_block(var: str, *, idx_f: dict, idx_m: dict, idx_h: dict) -> str:
    v = var.strip().upper()
    if v.startswith("H"):
        e = idx_h.get(v)
        return (e.question_text or "").strip() if e else ""
    ef = idx_f.get(v)
    em = idx_m.get(v)
    tf = (ef.question_text or "").strip() if ef else ""
    tm = (em.question_text or "").strip() if em else ""
    if not tf and not tm:
        return ""
    if tf == tm:
        return tf
    return f"Female: {tf} Male: {tm}"


def _male_question_block(var: str, *, idx_m: dict, idx_h: dict) -> str:
    v = var.strip().upper()
    if v.startswith("H"):
        e = idx_h.get(v)
        return (e.question_text or "").strip() if e else ""
    em = idx_m.get(v)
    return (em.question_text or "").strip() if em else ""


def _prepend_pv_stem_for_bc(
    var: str,
    text: str,
    *,
    idx_f: dict,
    idx_m: dict,
    male_only: bool = False,
) -> str:
    """Prefix Q…A module stem before Q…B / Q…C continuation text (codebook often omits stem on B/C)."""
    v = var.strip().upper()
    if not v.startswith("Q") or len(v) < 2 or v[-1] not in "BC":
        return text
    root_a = v[:-1] + "A"
    if male_only:
        am = idx_m.get(root_a)
        ta = (am.question_text or "").strip() if am else ""
    else:
        af = idx_f.get(root_a)
        ta = (af.question_text or "").strip() if af else ""
    if not ta:
        return text
    m = re.search(r"^(.*?)\s*A\)", ta, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return text
    stem = m.group(1).strip()
    ts = text.strip()
    if not stem or not ts:
        return text
    if ts.lower().startswith(stem.lower()):
        return ts
    # B/C entries often repeat the Q…A intro; keep only from B)/C) onward when present.
    cont = re.search(rf"{re.escape(v[-1])}\)\s*.+", ts, flags=re.IGNORECASE | re.DOTALL)
    if cont:
        ts = cont.group(0).strip()
    return f"{stem} {ts}".strip()


def _questions_for_vars(
    vars_: list[str],
    *,
    idx_f: dict,
    idx_m: dict,
    idx_h: dict,
    male_only: bool = False,
) -> str:
    if not vars_:
        return ""
    blocks: list[str] = []
    for t in vars_:
        t = t.strip()
        if not t:
            continue
        if male_only:
            blk = _male_question_block(t, idx_m=idx_m, idx_h=idx_h)
            merged = _prepend_pv_stem_for_bc(t, blk, idx_f=idx_f, idx_m=idx_m, male_only=True)
            if merged.strip():
                blocks.append(merged)
            continue
        blk = _dual_question_block(t, idx_f=idx_f, idx_m=idx_m, idx_h=idx_h)
        if not blk:
            continue
        if "Female:" in blk and "Male:" in blk:
            parts = blk.split(" Male: ", 1)
            tf = parts[0].replace("Female: ", "", 1).strip()
            tm = parts[1].strip() if len(parts) > 1 else ""
            tf2 = _prepend_pv_stem_for_bc(t, tf, idx_f=idx_f, idx_m=idx_m)
            tm2 = _prepend_pv_stem_for_bc(t, tm, idx_f=idx_f, idx_m=idx_m)
            if tf2 == tm2:
                blocks.append(tf2)
            else:
                blocks.append(f"Female: {tf2} Male: {tm2}")
        else:
            blocks.append(_prepend_pv_stem_for_bc(t, blk, idx_f=idx_f, idx_m=idx_m))
    return " || ".join(blocks)


def main() -> None:
    ent_f = extract_codebook_entries(FEMALE_CODEBOOK)
    ent_m = extract_codebook_entries(MALE_CODEBOOK)
    ent_hoh_f = extract_codebook_entries(FEMALE_HOH_CODEBOOK)
    idx_f = entries_by_variable_name(ent_f)
    idx_m = entries_by_variable_name(ent_m)
    idx_h = entries_by_variable_name(ent_hoh_f)
    idx_lookup = {**idx_f, **idx_h}

    df_f, _ = pyreadstat.read_dta(FEMALE_DTA)
    df_m, _ = pyreadstat.read_dta(MALE_DTA)

    built: list[dict[str, str]] = []
    verify_lines: list[str] = []

    for spec in ZAMBIA_2014_OUTCOME_SPEC:
        cat = spec["category"]
        fmt_vars: list[str] = list(spec.get("format_vars") or [])
        male_q = bool(spec.get("questions_male_only"))

        if not fmt_vars:
            built.append({
                "Category": cat,
                "Variable": "",
                "Type": "",
                "Format": "",
                "Questions": "",
            })
            continue

        var_display = "; ".join(fmt_vars)
        fmt = _join_formats(idx_lookup, fmt_vars)
        questions = _questions_for_vars(
            fmt_vars, idx_f=idx_f, idx_m=idx_m, idx_h=idx_h, male_only=male_q
        )

        first = fmt_vars[0].strip()
        assert first
        frames = [(df_f, "female"), (df_m, "male")]
        for vn in fmt_vars:
            for fr, _lab in frames:
                if vn not in fr.columns:
                    raise KeyError(f"{vn} not in {_lab} PUD")
            ef = idx_lookup.get(vn.upper()) or idx_f.get(vn.upper()) or idx_m.get(vn.upper())
            em = idx_m.get(vn.upper()) if not vn.upper().startswith("H") else idx_h.get(vn.upper())
            fs = ef.format_string if ef else ""
            if vn.upper().startswith("H"):
                ok_f, msg_f = verify_variable_against_dta(df_f[vn], fs)
                if not ok_f:
                    verify_lines.append(f"{vn} HOH: {msg_f}")
            else:
                ok_f, msg_f = verify_variable_against_dta(df_f[vn], fs)
                ok_m, msg_m = verify_variable_against_dta(df_m[vn], fs)
                if not ok_f or not ok_m:
                    verify_lines.append(
                        f"{vn}: female ok={ok_f} ({msg_f}); male ok={ok_m} ({msg_m})\n"
                        f"female vc:\n{df_f[vn].value_counts(dropna=False).head(12)}"
                    )
                ff = ef.format_string if ef else ""
                mf = em.format_string if em else ""
                if em and ff != mf:
                    verify_lines.append(f"  format F vs M for {vn}: {ff!r} vs {mf!r}")

        types = []
        for fr in (df_f, df_m):
            types.append(classify_variable_type(fr[first]))
        type_col = types[0] if types[0] == types[1] else "mixed"

        built.append({
            "Category": cat,
            "Variable": var_display,
            "Type": type_col,
            "Format": fmt,
            "Questions": questions,
        })

    out_df = build_outcome_codebook_df(built)
    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    export_minimal_codebook_docx(
        out_df,
        OUT_DOCX,
        columns=list(OUTCOME_CODEBOOK_COLUMNS),
        merge_category_column="Category",
    )
    OUT_TSV.write_text(outcome_codebook_to_tsv(out_df), encoding="utf-8")
    print(f"Wrote {OUT_DOCX}\nWrote {OUT_TSV}\nRows: {len(out_df)}")

    if verify_lines:
        print("\n--- Verification (sample) ---\n")
        for ln in verify_lines[:25]:
            print(ln)
            print()


if __name__ == "__main__":
    main()
