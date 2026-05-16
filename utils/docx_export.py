"""
Minimal Word export for harmonized codebook tables (plain python-docx, no styling).
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd
from docx import Document


def export_minimal_codebook_docx(
    df: pd.DataFrame,
    path: str | Path,
    *,
    columns: Sequence[str] | None = None,
    merge_category_column: str | None = "Category",
) -> None:
    """
    Write a bare table: header row + one row per DataFrame row, cell text only.

    If ``merge_category_column`` is set and present in ``columns``, consecutive
    data rows with the same category value have that column merged vertically
    (first row of each group spans the block).
    """
    path = Path(path)
    cols = list(columns) if columns is not None else list(df.columns)
    for c in cols:
        if c not in df.columns:
            raise KeyError(f"Column {c!r} not in DataFrame")

    doc = Document()
    nrows = len(df) + 1
    ncols = len(cols)
    table = doc.add_table(rows=nrows, cols=ncols)

    for j, name in enumerate(cols):
        table.rows[0].cells[j].text = str(name)

    for ri in range(len(df)):
        for j, col in enumerate(cols):
            val = df.iloc[ri][col]
            text = "" if (pd.isna(val) or val is None) else str(val)
            table.rows[ri + 1].cells[j].text = text

    if merge_category_column and merge_category_column in cols:
        cat_j = cols.index(merge_category_column)
        ri = 0
        while ri < len(df):
            cat_val = df.iloc[ri][merge_category_column]
            rj = ri + 1
            while rj < len(df) and df.iloc[rj][merge_category_column] == cat_val:
                rj += 1
            if rj - ri > 1:
                top = table.rows[ri + 1].cells[cat_j]
                bot = table.rows[rj].cells[cat_j]
                top.merge(bot)
            ri = rj

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
