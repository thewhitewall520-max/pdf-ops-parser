"""Normalize parsed data into a flat dict/list structure for export."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from packages.parser.schemas import (
    InvoiceInfo,
    ParseResult,
    SettlementInfo,
    ShippingInfo,
)


def _fmt(v: Any) -> str:
    """Format any value to string for CSV/Excel export."""
    if v is None:
        return ""
    if isinstance(v, (date, datetime)):
        return str(v)
    if isinstance(v, Decimal):
        return str(v)
    return str(v)


def normalize(result: ParseResult) -> list[dict[str, Any]]:
    """
    Convert any ParseResult into a list of flat dicts for export.

    - Invoice: one row per line item + summary row
    - Shipping: one row per tracking event + header row
    - Settlement: one row per transaction + summary row
    """
    if isinstance(result, InvoiceInfo):
        return _normalize_invoice(result)
    elif isinstance(result, ShippingInfo):
        return _normalize_shipping(result)
    elif isinstance(result, SettlementInfo):
        return _normalize_settlement(result)
    raise TypeError(f"Unknown result type: {type(result)}")


def _normalize_invoice(inv: InvoiceInfo) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in inv.line_items:
        rows.append({
            "invoice_number": _fmt(inv.invoice_number),
            "invoice_date": _fmt(inv.invoice_date),
            "type": "line_item",
            "sku": item.sku or "",
            "name": item.name,
            "quantity": item.quantity,
            "unit_price": _d(item.unit_price),
            "total_price": _d(item.total_price),
        })
    if inv.payment.total is not None:
        rows.append({
            "invoice_number": _fmt(inv.invoice_number),
            "type": "summary",
            "total": _d(inv.payment.total),
            "tax": _d(inv.payment.tax),
            "shipping": _d(inv.payment.shipping),
            "currency": inv.payment.currency,
        })
    return rows


def _normalize_shipping(ship: ShippingInfo) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Header row
    rows.append({
        "type": "header",
        "carrier": ship.carrier or "",
        "tracking_number": ship.tracking_number or "",
        "weight": ship.weight or "",
        "estimated_delivery": str(ship.estimated_delivery or ""),
    })
    for event in ship.events:
        rows.append({
            "type": "event",
            "date": event.date or "",
            "location": event.location or "",
            "status": event.status or "",
            "description": event.description or "",
        })
    return rows


def _normalize_settlement(stl: SettlementInfo) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for txn in stl.transactions:
        row = {"type": "transaction", **txn}
        rows.append(row)
    rows.append({
        "type": "summary",
        "total_sales": _d(stl.total_sales),
        "total_fees": _d(stl.total_fees),
        "total_refunds": _d(stl.total_refunds),
        "net_payout": _d(stl.net_payout),
        "currency": stl.currency,
    })
    return rows if len(rows) > 1 else [
        {"type": "summary",
         "total_sales": _d(stl.total_sales),
         "total_fees": _d(stl.total_fees),
         "total_refunds": _d(stl.total_refunds),
         "net_payout": _d(stl.net_payout),
         "currency": stl.currency}
    ]


def _d(v: Decimal | None) -> str:
    return str(v) if v is not None else ""
