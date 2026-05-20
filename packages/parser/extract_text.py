"""Extract raw text from PDF using pdfplumber and PyMuPDF."""

from __future__ import annotations

from pathlib import Path

import pdfplumber
import fitz  # PyMuPDF


def extract_text_pdfplumber(pdf_path: str | Path) -> str:
    """Extract text from PDF using pdfplumber (best for structured text)."""
    text_parts: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {i} ---\n{page_text}")
    return "\n\n".join(text_parts)


def extract_text_pymupdf(pdf_path: str | Path) -> str:
    """Extract text from PDF using PyMuPDF (better for complex layouts)."""
    doc = fitz.open(str(pdf_path))
    text_parts: list[str] = []
    for i, page in enumerate(doc, 1):
        text = page.get_text("text")
        if text.strip():
            text_parts.append(f"--- Page {i} ---\n{text}")
    doc.close()
    return "\n\n".join(text_parts)


def extract_text(pdf_path: str | Path, engine: str = "pdfplumber") -> str:
    """Extract text from PDF, auto-fallback between engines."""
    if engine == "pymupdf":
        return extract_text_pymupdf(pdf_path)
    try:
        return extract_text_pdfplumber(pdf_path)
    except Exception:
        return extract_text_pymupdf(pdf_path)
