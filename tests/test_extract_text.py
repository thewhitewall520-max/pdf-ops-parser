"""Tests for text extraction."""

from __future__ import annotations

from pathlib import Path

import fpdf
import pytest

from packages.parser.extract_text import extract_text, extract_text_pdfplumber, extract_text_pymupdf


def _gen_mini_pdf(tmp_path: str | Path, filename: str = "test.pdf") -> Path:
    """Generate a small but valid PDF for testing."""
    p = Path(tmp_path) / filename
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    pdf.cell(text="Test PDF content here", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Invoice # TEST-001", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(p))
    return p


class TestExtractText:
    """Tests for PDF text extraction."""

    def test_extract_text_empty_pdf(self, tmp_path: Path):
        """Should handle non-PDF file or raise (depends on fallback)."""
        empty = tmp_path / "empty.txt"
        empty.write_text("not a pdf")
        # extract_text has a fallback mechanism: pdfplumber error -> PyMuPDF
        # PyMuPDF may still return text for non-PDF files.
        result = extract_text(str(empty))
        # Should at least return a string (may be empty or contain text)
        assert isinstance(result, str)

    def test_extract_text_nonexistent(self):
        """Should raise on missing file."""
        with pytest.raises(Exception):
            extract_text("/nonexistent/file.pdf")

    def test_extract_text_fallback(self, tmp_path: Path):
        """Should handle engine fallback gracefully."""
        pdf_path = _gen_mini_pdf(tmp_path, "fallback.pdf")
        result = extract_text(str(pdf_path), engine="pdfplumber")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Invoice" in result or "Test" in result

    def test_extract_text_both_engines(self, tmp_path: Path):
        """Both pdfplumber and PyMuPDF should work on a real PDF."""
        pdf_path = _gen_mini_pdf(tmp_path, "dual.pdf")
        t1 = extract_text_pdfplumber(str(pdf_path))
        t2 = extract_text_pymupdf(str(pdf_path))
        assert isinstance(t1, str) and len(t1) > 0
        assert isinstance(t2, str) and len(t2) > 0

    def test_extract_auto_engine(self, tmp_path: Path):
        """Default engine (pdfplumber) should work."""
        pdf_path = _gen_mini_pdf(tmp_path, "auto.pdf")
        result = extract_text(str(pdf_path))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_extract_pymupdf_engine(self, tmp_path: Path):
        """PyMuPDF engine should work."""
        pdf_path = _gen_mini_pdf(tmp_path, "pymu.pdf")
        result = extract_text(str(pdf_path), engine="pymupdf")
        assert isinstance(result, str)
        assert len(result) > 0
