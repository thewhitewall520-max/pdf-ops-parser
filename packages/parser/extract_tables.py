"""Extract tables from PDF using pdfplumber."""

from __future__ import annotations

from pathlib import Path

import pdfplumber


def extract_tables(pdf_path: str | Path) -> list[list[list[str | None]]]:
    """
    Extract all tables from a PDF.

    Returns a list of tables, where each table is a list of rows,
    and each row is a list of cell values.
    """
    all_tables: list[list[list[str | None]]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                all_tables.append(table)
    return all_tables


def extract_first_table(pdf_path: str | Path) -> list[list[str | None]] | None:
    """Extract the first table found in a PDF."""
    tables = extract_tables(pdf_path)
    return tables[0] if tables else None
