"""Tests for Excel export."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from packages.parser.export_excel import export_excel
from packages.parser.schemas import InvoiceInfo, LineItem, PaymentInfo


class TestExportExcel:
    """Tests for Excel export."""

    def test_export_basic(self, tmp_path: Path):
        """Should export a basic invoice to Excel."""
        invoice = InvoiceInfo(
            invoice_number="INV-001",
            line_items=[
                LineItem(name="Widget A", quantity=2, unit_price=Decimal("10.00")),
                LineItem(name="Widget B", quantity=1, unit_price=Decimal("25.00")),
            ],
            payment=PaymentInfo(total=Decimal("45.00")),
        )

        out = tmp_path / "output.xlsx"
        result = export_excel(invoice, str(out))
        assert result.exists()
        assert result.suffix == ".xlsx"

        df = pd.read_excel(str(result))
        assert len(df) > 0

    def test_export_empty_invoice(self, tmp_path: Path):
        """Should export an invoice with no line items."""
        invoice = InvoiceInfo(invoice_number="INV-000")
        out = tmp_path / "empty.xlsx"
        result = export_excel(invoice, str(out))
        assert result.exists()

    def test_export_overwrite_excel(self, tmp_path: Path):
        """Should produce a valid Excel file."""
        invoice = InvoiceInfo(
            invoice_number="INV-002",
            line_items=[LineItem(name="Test", quantity=1)],
        )
        out = tmp_path / "overwrite.xlsx"
        result = export_excel(invoice, str(out))
        assert result.exists()
        df = pd.read_excel(str(result))
        assert len(df) > 0
