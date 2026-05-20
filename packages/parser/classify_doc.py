"""Classify a PDF document type based on extracted text."""

from __future__ import annotations

import re

from packages.parser.schemas import DocType


# Simple keyword-based classification
_SIGNATURES: dict[str, list[str]] = {
    DocType.INVOICE: [
        r"(?i)\binvoice\b",
        r"(?i)\bbill\b",
        r"(?i)tax\s+invoice",
        r"(?i)due\s+date",
    ],
    DocType.SHIPPING: [
        r"(?i)\btracking\s*(#|number|no|id)\b",
        r"(?i)\bship\s*(to|from)\b",
        r"(?i)\bcarrier\b",
        r"(?i)\bdelivery\b",
        r"(?i)\bparcel\b",
    ],
    DocType.OZON_SETTLEMENT: [
        r"(?i)\bozon\b",
        r"(?i)\bозон\b",
        r"(?i)отчет\s+реализации",
        r"(?i)settlement\s+report",
    ],
    DocType.WILDBERRIES_REPORT: [
        r"(?i)\bwildberries\b",
        r"(?i)\bвайлдберриз\b",
        r"(?i)\bwb\s+report\b",
        r"(?i)\bреализация\b",
    ],
}


def classify(text: str) -> DocType | None:
    """
    Classify document type from extracted text.

    Returns DocType or None if cannot determine.
    """
    scores: dict[str, int] = {}
    for doc_type, patterns in _SIGNATURES.items():
        score = sum(1 for p in patterns if re.search(p, text))
        if score > 0:
            scores[doc_type] = score

    if not scores:
        return None

    # Return the doc type with the most keyword matches
    return max(scores, key=scores.get)  # type: ignore[arg-type]


def classify_from_file(pdf_path: str, engine: str = "pdfplumber") -> DocType | None:
    """Classify document type from PDF file."""
    from packages.parser.extract_text import extract_text

    text = extract_text(pdf_path, engine=engine)
    if not text.strip():
        return None
    return classify(text)
