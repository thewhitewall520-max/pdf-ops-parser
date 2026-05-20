"""Tests for settlement parsing (Ozon, Wildberries)."""

from __future__ import annotations

from pathlib import Path

import fpdf
import pytest

from packages.parser.parse_settlement import parse_settlement
from packages.parser.schemas import SettlementInfo


def _gen_ozon_settlement(tmp_path: str | Path, filename: str = "ozon.pdf") -> Path:
    """Generate a valid Ozon settlement report PDF."""
    p = Path(tmp_path) / filename
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="OZON SETTLEMENT REPORT", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(text="Period: 2024-03-01 to 2024-03-31", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Seller ID: OZ-SELLER-001", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Ozon Platform", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.cell(text="Total Sales: 200,000.00 RUB", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Total Fees: 20,000.00 RUB", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Total Refunds: 10,000.00 RUB", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text="Net Payout: 170,000.00 RUB", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(p))
    return p


class TestParseSettlement:
    """Tests for settlement report parsing."""

    def test_parse_nonexistent(self):
        """Should raise on missing file."""
        with pytest.raises(Exception):
            parse_settlement("/nonexistent/settlement.pdf")

    def test_parse_result_type(self, tmp_path: Path):
        """Should return SettlementInfo type."""
        pdf_path = _gen_ozon_settlement(tmp_path)
        result = parse_settlement(str(pdf_path))
        assert isinstance(result, SettlementInfo)
        assert hasattr(result, "platform")
        assert hasattr(result, "total_sales")

    def test_parse_platform(self, tmp_path: Path):
        """Should detect Ozon platform."""
        pdf_path = _gen_ozon_settlement(tmp_path)
        result = parse_settlement(str(pdf_path))
        assert result.platform == "ozon"

    def test_parse_seller_id(self, tmp_path: Path):
        """Should extract seller ID."""
        pdf_path = _gen_ozon_settlement(tmp_path)
        result = parse_settlement(str(pdf_path))
        assert result.seller_id == "OZ-SELLER-001"

    def test_parse_period(self, tmp_path: Path):
        """Should extract period from combined line."""
        pdf_path = _gen_ozon_settlement(tmp_path)
        result = parse_settlement(str(pdf_path))
        assert str(result.period_start) == "2024-03-01"
        assert str(result.period_end) == "2024-03-31"

    def test_parse_financials(self, tmp_path: Path):
        """Should extract financial figures."""
        pdf_path = _gen_ozon_settlement(tmp_path)
        result = parse_settlement(str(pdf_path))
        assert float(result.total_sales) == 200000.00  # type: ignore[arg-type]
        assert float(result.total_fees) == 20000.00  # type: ignore[arg-type]
        assert float(result.total_refunds) == 10000.00  # type: ignore[arg-type]
        assert float(result.net_payout) == 170000.00  # type: ignore[arg-type]

    def test_parse_currency(self, tmp_path: Path):
        """Should detect RUB for Ozon."""
        pdf_path = _gen_ozon_settlement(tmp_path)
        result = parse_settlement(str(pdf_path))
        assert result.currency == "RUB"

    def test_regression_no_cross_parse_invoice_as_settlement(self, tmp_path: Path):
        """Settlement parser should NOT match an invoice's 'Total:' as total_sales."""
        from packages.parser.extract_text import extract_text

        # Parse invoice with settlement parser — should NOT extract total_sales
        result = parse_settlement("samples/invoice.pdf")
        # In an invoice, there's no settlement context, so total_sales should be None
        # The regex must not match bare "Total: $122.50"
        assert result.total_sales is None, (
            f"Settlement parser should not extract 'Total:' from invoice, "
            f"got total_sales={result.total_sales}"
        )
        assert result.platform is None
