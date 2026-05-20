"""Export parsed data to CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from packages.parser.schemas import ParseResult
from packages.parser.normalize import normalize


def export_csv(result: ParseResult, output_path: str | Path) -> Path:
    """Export parsed data to CSV file."""
    rows = normalize(result)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows)
    df.to_csv(str(output), index=False)
    return output
