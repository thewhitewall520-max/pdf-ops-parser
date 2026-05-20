"""Export parsed data to JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.parser.schemas import ParseResult


def export_json(result: ParseResult, output_path: str | Path, indent: int = 2) -> Path:
    """Export parsed data to JSON file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    data = _to_dict(result)
    with open(str(output), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
    return output


def _to_dict(result: ParseResult) -> dict[str, Any]:
    """Convert ParseResult to serializable dict."""
    return result.model_dump(mode="json")
