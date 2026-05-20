"""Parse shipping / logistics PDFs into structured ShippingInfo."""

from __future__ import annotations

import re
from pathlib import Path

from packages.parser.extract_text import extract_text
from packages.parser.schemas import Address, ShippingInfo, TrackEvent


def parse_shipping(pdf_path: str | Path) -> ShippingInfo:
    """
    Parse a shipping/label PDF into structured data.

    Heuristic-based extraction for common shipping label formats.
    """
    text = extract_text(pdf_path)

    tracking = _find_first(text, [
        r"(?i)tracking\s*(?:#|number|no|id)?:?\s*(\S+)",
        r"(?i)tracking:\s*(\S+)",
    ])
    carrier = _find_first(text, [
        r"(?i)carrier:?\s*(.+)",
        r"(?i)(fedex|ups|dhl|usps|sf express|ems|中国邮政)",
    ])
    weight = _find_first(text, [
        r"(?i)weight:?\s*([\d.]+)\s*(kg|lb|g|oz)",
        r"(?i)([\d.]+)\s*(kg|lb)",
    ])

    events = _parse_events(text)

    return ShippingInfo(
        carrier=carrier,
        tracking_number=tracking,
        weight=weight,
        events=events,
        raw_text=text[:5000],
    )


def _find_first(text: str, patterns: list[str], group: int = 1) -> str | None:
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(group).strip()
    return None


def _parse_events(text: str) -> list[TrackEvent]:
    """Attempt to extract tracking events (date + location + status)."""
    events: list[TrackEvent] = []
    for line in text.split("\n"):
        line = line.strip()
        m = re.match(r"(\d{4}[-/]\d{2}[-/]\d{2})\s+(.+)", line)
        if m:
            date_str = m.group(1)
            rest = m.group(2).strip()
            parts = rest.split(None, 1)
            location = parts[0] if parts else None
            status = parts[1] if len(parts) > 1 else None
            events.append(TrackEvent(date=date_str, location=location, status=status))
    return events
