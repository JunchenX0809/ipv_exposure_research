#!/usr/bin/env python3
"""
Rebuild Zambia 2014 **covariate** codebook (Step 2) from ``zambia_v2_covariates.ipynb`` logic.

Outputs:
  - ``data/processed/jcx_zambiaCovariateCodebook.docx`` (minimal table, merge ``category``)
  - ``data/processed/jcx_zambiaCovariateCodebook.tsv``

Run from repo root::

    .venv/bin/python scripts/build_zambia_2014_covariate_codebook.py
"""

from __future__ import annotations

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
        "or: pip install -r requirements.txt\n"
    )
    raise SystemExit(1) from None

from utils.covariates import (
    build_covariate_codebook_df,
    classify_variable_type,
    covariate_codebook_to_tsv,
)
from utils.docx_export import export_minimal_codebook_docx
from utils.pdf_parse import extract_codebook_entries, entries_by_question_number
from utils.zambia_2014_covariate_codebook_data import ZAMBIA_2014_COVARIATE_RAW_MAP

ZAMBIA_DIR = ROOT / "data" / "raw" / "Zambia Stata"
MALE_DTA = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Male_PUD.dta"
FEMALE_DTA = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Female_PUD.dta"
FEMALE_CODEBOOK = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Females_Codebook.pdf"
MALE_CODEBOOK = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Males_Codebook.pdf"
HOH_CODEBOOK_F = ZAMBIA_DIR / "ZAMBIA_VACS_2014_Females_HOHCodebook.pdf"

OUT_DOCX = ROOT / "data" / "processed" / "jcx_zambiaCovariateCodebook.docx"
OUT_TSV = ROOT / "data" / "processed" / "jcx_zambiaCovariateCodebook.tsv"

COV_COLUMNS = ("category", "variable", "type", "format", "question")


def main() -> None:
    df, meta = pyreadstat.read_dta(MALE_DTA)
    df_f, _meta_f = pyreadstat.read_dta(FEMALE_DTA)

    cb_f = extract_codebook_entries(FEMALE_CODEBOOK)
    cb_m = extract_codebook_entries(MALE_CODEBOOK)
    cb_hoh = extract_codebook_entries(HOH_CODEBOOK_F)

    by_qnum_f = entries_by_question_number(cb_f)
    by_qnum_m = entries_by_question_number(cb_m)
    by_qnum_hoh = entries_by_question_number(cb_hoh)

    def lookup(qnum_male: str, qnum_female: str = "", qnum_hoh: str = "") -> tuple[str, str]:
        e = None
        if qnum_hoh:
            e = by_qnum_hoh.get(qnum_hoh)
        if not e and qnum_female:
            e = by_qnum_f.get(qnum_female)
        if not e and qnum_male:
            e = by_qnum_m.get(qnum_male)
        if e:
            return e.question_text, e.format_string
        return "", ""

    entries: list[dict[str, str]] = []

    for cat, var_notation, qm, qf, qh, type_ov in ZAMBIA_2014_COVARIATE_RAW_MAP:
        q_text, q_format = lookup(qm, qf, qh)

        if type_ov:
            var_type = type_ov
        elif var_notation == "NA":
            var_type = "NA"
        else:
            stata_var = None
            if qm:
                e = by_qnum_m.get(qm)
                if e and e.variable_name and e.variable_name in df.columns:
                    stata_var = e.variable_name
            if not stata_var and qf:
                e = by_qnum_f.get(qf)
                if e and e.variable_name and e.variable_name in df_f.columns:
                    stata_var = e.variable_name
            if not stata_var and qh:
                e = by_qnum_hoh.get(qh)
                if e and e.variable_name and e.variable_name in df.columns:
                    stata_var = e.variable_name

            if stata_var:
                src = df[stata_var] if stata_var in df.columns else df_f[stata_var]
                var_type = classify_variable_type(src)
            else:
                var_type = ""

        entries.append({
            "category": cat,
            "variable": var_notation,
            "type": var_type,
            "format": q_format,
            "question": q_text,
        })

    codebook_df = build_covariate_codebook_df(entries)

    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    export_minimal_codebook_docx(
        codebook_df,
        OUT_DOCX,
        columns=list(COV_COLUMNS),
        merge_category_column="category",
    )
    OUT_TSV.write_text(covariate_codebook_to_tsv(codebook_df), encoding="utf-8")

    print(f"Wrote {OUT_DOCX}")
    print(f"Wrote {OUT_TSV}")
    print(f"Rows: {len(codebook_df)}")


if __name__ == "__main__":
    main()
