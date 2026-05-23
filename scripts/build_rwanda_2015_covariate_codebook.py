#!/usr/bin/env python3
"""
Build Rwanda 2015–16 **covariate** codebook (Step 2) from Stata labels + observed codes.

No questionnaire/codebook PDFs — sources are ``Rwanda VACYS 2015-16 Final Data set.dta`` only.

Outputs:
  - ``data/processed/jcx_rwandaCovariateCodebook.docx``
  - ``data/processed/jcx_rwandaCovariateCodebook.tsv``

Run from repo root::

    .venv/bin/python scripts/build_rwanda_2015_covariate_codebook.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
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
from utils.rwanda_2015_covariate_codebook_data import RWANDA_2015_COVARIATE_RAW_MAP
from utils.rwanda_covariate_enhance import format_from_series, question_from_label

RWANDA_DIR = ROOT / "data" / "raw" / "Rwanda Stata and SAS"
PUD_PATH = RWANDA_DIR / "Rwanda VACYS 2015-16 Final Data set.dta"

OUT_DOCX = ROOT / "data" / "processed" / "jcx_rwandaCovariateCodebook.docx"
OUT_TSV = ROOT / "data" / "processed" / "jcx_rwandaCovariateCodebook.tsv"

# Match jcx_zimbabweCovariateCodebook_V2.docx header casing
DOCX_COLUMNS = ("Category", "Variable", "Type", "Format", "Question")
DF_COLUMNS = ("category", "variable", "type", "format", "question")


def main() -> None:
    df, meta = pyreadstat.read_dta(PUD_PATH)
    entries: list[dict[str, str]] = []

    for cat, var_notation, stata_col, type_ov in RWANDA_2015_COVARIATE_RAW_MAP:
        if var_notation == "NA":
            entries.append({
                "category": cat,
                "variable": "NA",
                "type": "NA",
                "format": "",
                "question": "",
            })
            continue

        if stata_col not in df.columns:
            raise KeyError(f"Expected column {stata_col!r} missing from {PUD_PATH.name}")

        series = df[stata_col]
        q_text = question_from_label(stata_col, meta)
        q_format = format_from_series(stata_col, series, meta)

        if type_ov:
            var_type = type_ov
        else:
            var_type = classify_variable_type(series)

        entries.append({
            "category": cat,
            "variable": var_notation,
            "type": var_type,
            "format": q_format,
            "question": q_text,
        })

    codebook_df = build_covariate_codebook_df(entries)
    export_df = codebook_df.rename(
        columns=dict(zip(DF_COLUMNS, DOCX_COLUMNS, strict=True)),
    )

    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    export_minimal_codebook_docx(
        export_df,
        OUT_DOCX,
        columns=list(DOCX_COLUMNS),
        merge_category_column="Category",
    )
    OUT_TSV.write_text(covariate_codebook_to_tsv(codebook_df), encoding="utf-8")

    print(f"Wrote {OUT_DOCX}")
    print(f"Wrote {OUT_TSV}")
    print(f"Rows: {len(codebook_df)}")


if __name__ == "__main__":
    main()
