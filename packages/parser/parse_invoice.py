"""Parse invoice PDFs into structured InvoiceInfo."""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from packages.parser.extract_text import extract_text
from packages.parser.extract_tables import extract_tables
from packages.parser.schemas import Address, InvoiceInfo, LineItem, PaymentInfo


def parse_invoice(pdf_path: str | Path) -> InvoiceInfo:
    """
    Parse an invoice PDF into structured data.

    Uses keyword extraction + table detection.
    This is a heuristic parser — works best for standard invoice layouts.
    """
    text = extract_text(pdf_path)

    # Simple regex-based field extraction
    invoice_number = _find_first(text, [r"(?i)invoice\s*(#|no|number):?\s*(\S+)"], group=2)
    invoice_date = _find_first(text, [
        r"(?i)(?:invoice\s+)?date:?\s*(\d{4}[-/]\d{2}[-/]\d{2})",
        r"(?i)(?:invoice\s+)?date:?\s*(\d{2}[-/]\d{2}[-/]\d{4})",
    ])

    tables = extract_tables(pdf_path)
    line_items = _parse_line_items(tables)

    # Simple totals extraction
    total = _find_decimal(text, [r"(?i)total:?\s*\$?([\d,]+\.?\d*)"])
    tax = _find_decimal(text, [r"(?i)tax:?\s*\$?([\d,]+\.?\d*)"])
    shipping = _find_decimal(text, [r"(?i)shipping:?\s*\$?([\d,]+\.?\d*)"])

    return InvoiceInfo(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        line_items=line_items,
        payment=PaymentInfo(total=total, tax=tax, shipping=shipping),
        raw_text=text[:5000],
    )


def _find_first(text: str, patterns: list[str], group: int = 1) -> str | None:
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            return m.group(group).strip()
    return None


def _find_decimal(text: str, patterns: list[str]) -> Decimal | None:
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            cleaned = m.group(1).replace(",", "")
            try:
                return Decimal(cleaned)
            except Exception:
                continue
    return None


def _parse_line_items(tables: list[list[list[str | None]]]) -> list[LineItem]:
    """Attempt to parse line items from detected tables."""
    items: list[LineItem] = []
    for table in tables:
        for row in table[1:]:  # skip header
            cells = [c.strip() if c else "" for c in row]
            if not any(cells):
                continue
            # Guess columns by header from first row, or fallback positional
            if len(cells) >= 5:
                # Standard: [SKU, Name, Qty, UnitPrice, Total]
                sku = cells[0]
                name = cells[1]
                qty = int(cells[2]) if cells[2].isdigit() else 1
                unit_price = _parse_money(cells[3])
                total_price = _parse_money(cells[4])
                items.append(LineItem(
                    sku=sku, name=name, quantity=qty,
                    unit_price=unit_price, total_price=total_price,
                ))
            elif len(cells) >= 2:
                items.append(LineItem(
                    name=cells[1],
                    quantity=int(cells[2]) if len(cells) > 2 and cells[2].isdigit() else 1,
                ))
    return items


def _parse_money(s: str) -> Decimal | None:
    """Parse a money string like '$10.00' or '10.00' into Decimal."""
    s = s.strip().lstrip("$").lstrip("\u20ac").replace(",", "")
    try:
        return Decimal(s)
    except Exception:
        return None
