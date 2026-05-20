"""Pydantic schemas for parsed document data."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DocType(str, Enum):
    INVOICE = "invoice"
    SHIPPING = "shipping"
    OZON_SETTLEMENT = "ozon.settlement"
    WILDBERRIES_REPORT = "wildberries.report"


class OutputFormat(str, Enum):
    EXCEL = "xlsx"
    CSV = "csv"
    JSON = "json"


class LineItem(BaseModel):
    """A single line item in an invoice or shipping document."""
    sku: str | None = None
    name: str
    quantity: int = 1
    unit_price: Decimal | None = None
    total_price: Decimal | None = None
    currency: str = "USD"


class Address(BaseModel):
    """Address block."""
    name: str | None = None
    company: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None


class PaymentInfo(BaseModel):
    """Payment details."""
    method: str | None = None
    account: str | None = None
    due_date: date | None = None
    total: Decimal | None = None
    tax: Decimal | None = None
    shipping: Decimal | None = None
    currency: str = "USD"


class TrackEvent(BaseModel):
    """A shipping tracking event."""
    date: str | None = None
    location: str | None = None
    status: str | None = None
    description: str | None = None


class ShippingInfo(BaseModel):
    """Shipping / logistics document data."""
    carrier: str | None = None
    tracking_number: str | None = None
    sender: Address = Field(default_factory=Address)
    recipient: Address = Field(default_factory=Address)
    weight: str | None = None
    package_count: int | None = None
    events: list[TrackEvent] = Field(default_factory=list)
    estimated_delivery: date | None = None
    raw_text: str = ""


class InvoiceInfo(BaseModel):
    """Invoice document data."""
    invoice_number: str | None = None
    invoice_date: date | None = None
    seller: Address = Field(default_factory=Address)
    buyer: Address = Field(default_factory=Address)
    line_items: list[LineItem] = Field(default_factory=list)
    payment: PaymentInfo = Field(default_factory=PaymentInfo)
    raw_text: str = ""


class SettlementInfo(BaseModel):
    """Marketplace settlement / payout report data."""
    period_start: date | None = None
    period_end: date | None = None
    platform: str | None = None  # ozon, wildberries
    seller_id: str | None = None
    total_sales: Decimal | None = None
    total_fees: Decimal | None = None
    total_refunds: Decimal | None = None
    net_payout: Decimal | None = None
    currency: str = "RUB"
    transactions: list[dict[str, Any]] = Field(default_factory=list)
    raw_text: str = ""


ParseResult = InvoiceInfo | ShippingInfo | SettlementInfo
