"""
PDF parsing helpers for VACS codebook and questionnaire PDFs.

Extracts question numbers, question text, response options, and (from
codebook PDFs) the Stata variable name mapped to each question.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import fitz  # PyMuPDF


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class CodebookEntry:
    """One question block parsed from a codebook or questionnaire PDF."""

    question_number: str
    variable_name: str
    question_text: str
    response_options: list[tuple[str, str]] = field(default_factory=list)

    @property
    def format_string(self) -> str:
        """Response options formatted as ``code-label, code-label, ...``."""
        if not self.response_options:
            return ""
        return ", ".join(f"{code}-{label}" for code, label in self.response_options)


# ---------------------------------------------------------------------------
# Question-number detection
# ---------------------------------------------------------------------------

# Matches question IDs like F2, M13, Q25, Q7AA, Q1303A, H4, H7A, F1300
_Q_NUM_RE = re.compile(
    r"^([FMQ]\d+[A-Z]?[A-Z]?|H\d+[A-Z]?)$"
)

# Stata variable name in codebook (appears after TOTAL line): Q2, Q7AA, H4...
_VAR_NAME_RE = re.compile(
    r"^(Q\d+[A-Z_]*|H\d+[A-Z_]*)$"
)

# TOTAL = NNN line in codebook
_TOTAL_RE = re.compile(r"^TOTAL\s*=\s*\d+", re.IGNORECASE)

# Response code line: starts with a number (1, 2, 88, 99, etc.)
_RESP_CODE_RE = re.compile(r"^(\d{1,3})\s*$")

# Response range like "18-24", "13-17", "1-98", "1-30"
_RESP_RANGE_RE = re.compile(r"^(\d{1,4})-(\d{1,4})\s*$")

# Page headers that repeat across codebook pages
_PAGE_HEADERS = frozenset({
    "Questions", "Coding Categories", "Skip", "Wgted%", "No.", "n",
    "Questions Coding Categories Skip Wgted% n No.",
})


def _is_question_number(line: str) -> bool:
    """True if ``line`` is a questionnaire question id (F2, M100*, Q7AA, …)."""
    s = line.strip()
    if s.endswith("*"):
        s = s[:-1]
    return bool(_Q_NUM_RE.match(s))


def _clean_lines(text: str) -> list[str]:
    """Split page text into stripped, non-empty lines."""
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


# ---------------------------------------------------------------------------
# Codebook PDF parser
# ---------------------------------------------------------------------------

def extract_codebook_entries(pdf_path: str | Path) -> list[CodebookEntry]:
    """
    Parse a VACS codebook PDF into a list of ``CodebookEntry`` objects.

    The expected format per question block is::

        F2                          <- question number
        Question text...            <- may span lines
        TOTAL = N
        Q2                          <- Stata variable name
        1                           <- response code
        YES                         <- response label
        ...

    Returns entries in document order.
    """
    pdf = fitz.open(str(pdf_path))
    all_lines: list[str] = []
    for page in pdf:
        all_lines.extend(_clean_lines(page.get_text()))
    pdf.close()

    entries: list[CodebookEntry] = []
    i = 0
    n = len(all_lines)

    while i < n:
        line = all_lines[i]

        if not _is_question_number(line):
            i += 1
            continue

        q_num = line.strip()

        # Collect question text until TOTAL or next question number
        i += 1
        text_parts: list[str] = []
        while i < n:
            cur = all_lines[i]
            if _TOTAL_RE.match(cur) or _is_question_number(cur):
                break
            if cur in _PAGE_HEADERS:
                i += 1
                continue
            text_parts.append(cur)
            i += 1

        question_text = " ".join(text_parts).strip()

        # Look for TOTAL = N  ->  variable name
        var_name = ""
        if i < n and _TOTAL_RE.match(all_lines[i]):
            i += 1
            if i < n and _VAR_NAME_RE.match(all_lines[i].strip()):
                var_name = all_lines[i].strip()
                i += 1

        # Parse response options until next question number
        responses: list[tuple[str, str]] = []
        while i < n:
            cur = all_lines[i]
            if _is_question_number(cur):
                break
            # Skip page headers
            if cur in _PAGE_HEADERS:
                i += 1
                continue

            # Response code followed by label
            code_m = _RESP_CODE_RE.match(cur)
            range_m = _RESP_RANGE_RE.match(cur)

            if code_m:
                code = code_m.group(1)
                i += 1
                # Next non-numeric line is the label
                label_parts: list[str] = []
                while i < n:
                    nxt = all_lines[i]
                    if (
                        _RESP_CODE_RE.match(nxt)
                        or _RESP_RANGE_RE.match(nxt)
                        or _is_question_number(nxt)
                        or _TOTAL_RE.match(nxt)
                    ):
                        break
                    # Skip purely numeric values (counts, percentages)
                    try:
                        float(nxt.replace(",", ""))
                        i += 1
                        continue
                    except ValueError:
                        pass
                    # Skip skip-pattern references like "> Q7"
                    if nxt.startswith(">"):
                        i += 1
                        continue
                    # Skip page headers that appear mid-block
                    if nxt in _PAGE_HEADERS:
                        i += 1
                        continue
                    label_parts.append(nxt)
                    i += 1
                label = " ".join(label_parts).strip()
                if label:
                    responses.append((code, label))
            elif range_m:
                # Range like 18-24 — skip the associated counts
                i += 1
                while i < n:
                    nxt = all_lines[i]
                    try:
                        float(nxt.replace(",", ""))
                        i += 1
                        continue
                    except ValueError:
                        break
            else:
                # May be a label line for a previous code, or noise — skip
                i += 1

        entries.append(CodebookEntry(
            question_number=q_num,
            variable_name=var_name,
            question_text=question_text,
            response_options=responses,
        ))

    return entries


# ---------------------------------------------------------------------------
# Questionnaire PDF parser (lighter)
# ---------------------------------------------------------------------------

def extract_questionnaire_questions(
    pdf_path: str | Path,
) -> list[CodebookEntry]:
    """
    Parse a VACS questionnaire PDF into ``CodebookEntry`` objects.

    Questionnaire PDFs have question numbers (F2, M2, H4) followed by
    question text and response options with codes. No Stata variable names
    or TOTAL lines.
    """
    pdf = fitz.open(str(pdf_path))
    all_lines: list[str] = []
    for page in pdf:
        all_lines.extend(_clean_lines(page.get_text()))
    pdf.close()

    entries: list[CodebookEntry] = []
    i = 0
    n = len(all_lines)

    while i < n:
        line = all_lines[i]
        if not _is_question_number(line):
            i += 1
            continue

        # Keep trailing * when present (e.g. Tanzania 2009 F100*, M100*).
        q_num = line.strip()
        i += 1

        # Collect everything until next question number
        block_lines: list[str] = []
        while i < n and not _is_question_number(all_lines[i]):
            block_lines.append(all_lines[i])
            i += 1

        # Split block into question text and response options.
        #
        # Many questionnaire PDFs extract as:
        #   YES................
        #   NO.................
        #   1
        #   2
        # rather than "YES....1"; collect dot-leader labels and code-only
        # lines, then zip them when they align.
        text_parts: list[str] = []
        responses: list[tuple[str, str]] = []
        dot_labels: list[str] = []
        dot_codes: list[str] = []
        seen_response = False

        for bline in block_lines:
            resp_match = re.match(r"^(.+?)[.…]{3,}\s*(\d{1,3})\s*$", bline)
            dot_label = re.match(r"^(.+?)[.…]{3,}\s*$", bline)
            code_label = re.match(r"^(\d{1,3})\s*[-–]\s*(.+)$", bline)
            code_only = re.match(r"^(\d{1,3})\s*$", bline)

            if resp_match:
                seen_response = True
                label = resp_match.group(1).strip()
                code = resp_match.group(2).strip()
                responses.append((code, label))
            elif code_label:
                seen_response = True
                responses.append((code_label.group(1), code_label.group(2).strip()))
            elif dot_label:
                seen_response = True
                dot_labels.append(dot_label.group(1).strip())
            elif seen_response and code_only:
                dot_codes.append(code_only.group(1).strip())
            elif not seen_response:
                skip = False
                try:
                    float(bline.replace(",", ""))
                    skip = True
                except ValueError:
                    pass
                if not skip and bline not in (
                    "HEAD OF HOUSEHOLD QUESTIONNAIRE COMPLETED FOR THIS HOUSEHOLD: YES          NO",
                ):
                    text_parts.append(bline)

        if not responses and dot_labels and len(dot_labels) == len(dot_codes):
            responses.extend(zip(dot_codes, dot_labels))

        question_text = " ".join(text_parts).strip()
        # Remove section headers that got captured
        question_text = re.sub(
            r"^(EDUCATION:|FRIENDSHIPS:|SECTION \d+[:.]\s*)", "", question_text
        ).strip()

        entries.append(CodebookEntry(
            question_number=q_num,
            variable_name="",
            question_text=question_text,
            response_options=responses,
        ))

    return entries


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def entries_by_question_number(
    entries: Sequence[CodebookEntry],
) -> dict[str, CodebookEntry]:
    """Index entries by question number (first occurrence wins)."""
    idx: dict[str, CodebookEntry] = {}
    for e in entries:
        idx.setdefault(e.question_number, e)
    return idx


def entries_by_variable_name(
    entries: Sequence[CodebookEntry],
) -> dict[str, CodebookEntry]:
    """Index codebook entries by Stata variable name (first wins)."""
    idx: dict[str, CodebookEntry] = {}
    for e in entries:
        if e.variable_name:
            idx.setdefault(e.variable_name, e)
    return idx
