"""Export parsed data to Excel (.xlsx)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from packages.parser.schemas import ParseResult
from packages.parser.normalize import normalize


def export_excel(result: ParseResult, output_path: str | Path) -> Path:
    """Export parsed data to Excel file."""
    rows = normalize(result)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows)
    df.to_excel(str(output), index=False, engine="openpyxl")
    return output


def export_excel_multi(
    results: dict[str, ParseResult],
    output_path: str | Path,
) -> Path:
    """Export multiple parsed results as separate sheets."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(str(output), engine="openpyxl") as writer:
        for sheet_name, result in results.items():
            rows = normalize(result)
            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output
