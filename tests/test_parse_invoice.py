"""Tests for invoice parsing."""

from __future__ import annotations

from pathlib import Path

import fpdf
import pytest

from packages.parser.parse_invoice import parse_invoice
from packages.parser.schemas import InvoiceInfo


def _gen_real_invoice(tmp_path: str | Path, filename: str = "inv.pdf") -> Path:
    """Generate a real PDF invoice for testing."""
    p = Path(tmp_path) / filename
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="INVOICE", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(text="Invoice #: INV-TEST-999", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Date: 2024-06-01", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Due Date: 2024-07-01", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", style="B", size=10)
    for h, w in zip(["SKU", "Description", "Qty", "Unit Price", "Total"], [20, 60, 15, 25, 25]):
        pdf.cell(text=h, w=w, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", size=10)
    for r in [("TST-001", "Test Widget", "3", "$12.00", "$36.00")]:
        for v, w in zip(r, [20, 60, 15, 25, 25]):
            pdf.cell(text=v, w=w, border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(text="Total: $36.00", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Tax: $3.60", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(p))
    return p


class TestParseInvoice:
    """Tests for invoice PDF parsing."""

    def test_parse_nonexistent(self):
        """Should raise on missing file."""
        with pytest.raises(Exception):
            parse_invoice("/nonexistent/invoice.pdf")

    def test_parse_empty_pdf(self, tmp_path: Path):
        """Should raise on invalid PDF (plain text, not PDF)."""
        bad = tmp_path / "bad.txt"
        bad.write_text("not a real pdf")
        with pytest.raises(Exception):
            parse_invoice(str(bad))

    def test_parse_result_type(self, tmp_path: Path):
        """Should return InvoiceInfo type from a real invoice PDF."""
        pdf_path = _gen_real_invoice(tmp_path)
        result = parse_invoice(str(pdf_path))
        assert isinstance(result, InvoiceInfo)
        assert hasattr(result, "invoice_number")
        assert hasattr(result, "line_items")

    def test_parse_invoice_number(self, tmp_path: Path):
        """Should extract invoice number from a real PDF."""
        pdf_path = _gen_real_invoice(tmp_path)
        result = parse_invoice(str(pdf_path))
        assert result.invoice_number == "INV-TEST-999"

    def test_parse_line_items(self, tmp_path: Path):
        """Should extract line items from a table in the PDF."""
        pdf_path = _gen_real_invoice(tmp_path)
        result = parse_invoice(str(pdf_path))
        assert len(result.line_items) >= 1
        item = result.line_items[0]
        assert item.sku == "TST-001"
        assert item.quantity == 3
        assert item.name == "Test Widget"

    def test_parse_total(self, tmp_path: Path):
        """Should extract total amount."""
        pdf_path = _gen_real_invoice(tmp_path)
        result = parse_invoice(str(pdf_path))
        assert result.payment.total is not None
        assert float(result.payment.total) == 36.00

    def test_parse_tax(self, tmp_path: Path):
        """Should extract tax amount."""
        pdf_path = _gen_real_invoice(tmp_path)
        result = parse_invoice(str(pdf_path))
        assert result.payment.tax is not None
        assert float(result.payment.tax) == 3.60
