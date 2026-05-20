"""Parse marketplace settlement reports (Ozon, Wildberries)."""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from packages.parser.extract_text import extract_text
from packages.parser.schemas import SettlementInfo


def parse_settlement(pdf_path: str | Path) -> SettlementInfo:
    """
    Parse a marketplace settlement report PDF.

    Supports Ozon and Wildberries settlement/payout reports.
    Uses regex on extracted text.
    """
    text = extract_text(pdf_path)

    period_start = _find_date(text, [
        r"(?i)(?:period|отчет|пeриод)\s*(?:from|start|с)\s*(\d{4}[-/]\d{2}[-/]\d{2})",
        r"(?i)(?:period|отчет|пeриод)[:\s]+(\d{4}[-/]\d{2}[-/]\d{2})",
    ])
    period_end = _find_date(text, [
        # On same line after "to": "Period: 2024-01-01 to 2024-01-31"
        r"(?i)(?:period|отчет|пeриод).*?(?:to|end|по)\s*(\d{4}[-/]\d{2}[-/]\d{2})",
        r"(?i)(?:to|по|end)\s*(\d{4}[-/]\d{2}[-/]\d{2})",
    ])

    seller_id = _find_first(text, [
        r"(?i)seller\s*(?:id|#|number):?\s*(\S+)",
        r"(?i)(?:id|идентификатор)\s*продавца:?\s*(\S+)",
    ])

    # Detect platform
    platform = None
    if re.search(r"(?i)\bozon\b|озон", text):
        platform = "ozon"
    elif re.search(r"(?i)\bwildberries\b|вайлдберриз", text):
        platform = "wildberries"

    total_sales = _find_decimal(text, [
        r"(?i)(?:total\s+sales|выручка|продажи).*?([\d,]+\.?\d*)",
    ])
    total_fees = _find_decimal(text, [
        r"(?i)(?:total\s+fees|комиссия|комиссионные|сборы).*?([\d,]+\.?\d*)",
    ])
    total_refunds = _find_decimal(text, [
        r"(?i)(?:total\s+refunds|возвраты).*?([\d,]+\.?\d*)",
    ])
    net_payout = _find_decimal(text, [
        r"(?i)(?:net\s+payout|к\s+выплате|payout).*?([\d,]+\.?\d*)",
    ])

    return SettlementInfo(
        period_start=period_start,
        period_end=period_end,
        platform=platform,
        seller_id=seller_id,
        total_sales=total_sales,
        total_fees=total_fees,
        total_refunds=total_refunds,
        net_payout=net_payout,
        currency="RUB" if platform in ("ozon", "wildberries") else "USD",
        raw_text=text[:5000],
    )


def _find_first(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            return m.group(1).strip()
    return None


def _find_date(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            return m.group(1).strip()
    return None


def _find_decimal(text: str, patterns: list[str]) -> Decimal | None:
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            cleaned = m.group(1).replace(",", "").strip()
            try:
                return Decimal(cleaned)
            except Exception:
                continue
    return None
