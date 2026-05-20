"""PDF Ops Parser — Typer CLI entry point."""

from __future__ import annotations

from pathlib import Path

import typer

from packages.parser.classify_doc import classify_from_file
from packages.parser.export_csv import export_csv
from packages.parser.export_excel import export_excel
from packages.parser.export_json import export_json
from packages.parser.parse_invoice import parse_invoice
from packages.parser.parse_shipping import parse_shipping
from packages.parser.schemas import DocType, OutputFormat

app = typer.Typer(
    name="pdfops",
    help="PDF Ops Parser — Convert invoices and shipping PDFs into Excel, CSV and JSON",
)


@app.command()
def parse(
    pdf_path: str = typer.Argument(..., help="Path to the PDF file"),
    doc_type: str = typer.Option(
        None, "--type", "-t",
        help="Document type (invoice, shipping). If omitted, auto-detect.",
    ),
    output: str = typer.Option(
        "output.xlsx", "--out", "-o",
        help="Output file path. Extension determines format (.xlsx, .csv, .json)",
    ),
    template: str | None = typer.Option(
        None, "--template",
        help="Template name from templates/ directory",
    ),
):
    """
    Parse a PDF invoice or shipping document and export to the specified format.

    Usage examples:

        pdfops parse sample.pdf --type invoice --out output.xlsx

        pdfops parse sample.pdf --type shipping --out tracking.csv

        pdfops parse report.pdf --template ozon.settlement --out report.json
    """
    pdf = Path(pdf_path)
    if not pdf.exists():
        typer.echo(f"Error: File not found: {pdf_path}", err=True)
        raise typer.Exit(1)

    # Determine document type
    resolved_type: str | None = doc_type
    if resolved_type is None and template is None:
        typer.echo("Auto-detecting document type...", err=True)
        classified = classify_from_file(str(pdf))
        if classified:
            resolved_type = classified.value
            typer.echo(f"  Detected as: {resolved_type}", err=True)
        else:
            typer.echo(
                "Could not auto-detect document type. Use --type or --template.",
                err=True,
            )
            raise typer.Exit(1)

    # Parse
    typer.echo(f"Parsing {pdf_path}...", err=True)
    try:
        if resolved_type == DocType.INVOICE.value:
            result = parse_invoice(str(pdf))
        elif resolved_type == DocType.SHIPPING.value:
            result = parse_shipping(str(pdf))
        elif resolved_type in (DocType.OZON_SETTLEMENT.value, DocType.WILDBERRIES_REPORT.value):
            from packages.parser.parse_settlement import parse_settlement
            result = parse_settlement(str(pdf))
        else:
            result = parse_invoice(str(pdf))  # fallback
    except Exception as e:
        typer.echo(f"Parse error: {e}", err=True)
        raise typer.Exit(1)

    # Export
    out_path = Path(output)
    fmt = output.split(".")[-1].lower()

    try:
        if fmt == OutputFormat.CSV.value:
            export_csv(result, out_path)
            typer.echo(f"Exported to {out_path}")
        elif fmt == OutputFormat.JSON.value:
            export_json(result, out_path)
            typer.echo(f"Exported to {out_path}")
        else:
            # Default to xlsx for unknown extensions
            xlsx_path = out_path.with_suffix(".xlsx")
            export_excel(result, xlsx_path)
            if out_path.suffix != ".xlsx":
                typer.echo(f"Warning: unknown format '{fmt}', using .xlsx")
                out_path = xlsx_path
            typer.echo(f"Exported to {out_path}")
    except Exception as e:
        typer.echo(f"Export error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def classify(
    pdf_path: str = typer.Argument(..., help="Path to the PDF file"),
):
    """Detect the document type of a PDF."""
    pdf = Path(pdf_path)
    if not pdf.exists():
        typer.echo(f"Error: File not found: {pdf_path}", err=True)
        raise typer.Exit(1)

    doc_type = classify_from_file(str(pdf))
    if doc_type:
        typer.echo(doc_type.value)
    else:
        typer.echo("unknown", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
