"""Parse route — handle file upload and parse."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from packages.parser.classify_doc import classify_from_file
from packages.parser.export_csv import export_csv
from packages.parser.export_excel import export_excel
from packages.parser.export_json import export_json
from packages.parser.parse_invoice import parse_invoice
from packages.parser.parse_shipping import parse_shipping
from packages.parser.parse_settlement import parse_settlement
from packages.parser.schemas import OutputFormat

router = APIRouter(prefix="/parse", tags=["parse"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf"}


@router.post("")
async def parse_pdf(
    file: UploadFile = File(...),
    doc_type: str | None = Form(None, description="Document type (invoice, shipping)"),
    output_format: str = Form("excel", description="Output format: xlsx, csv, json"),
):
    """Upload a PDF and get back parsed data in the chosen format."""
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are accepted (got {ext})",
        )

    # Read content with size check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {len(content)} bytes (max {MAX_FILE_SIZE} bytes)",
        )

    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    out_path: Path | None = None

    try:
        # Determine document type
        resolved_type = doc_type
        if resolved_type is None:
            classified = classify_from_file(tmp_path)
            resolved_type = classified.value if classified else "invoice"

        # Parse
        if resolved_type == "invoice":
            result = parse_invoice(tmp_path)
        elif resolved_type == "shipping":
            result = parse_shipping(tmp_path)
        elif resolved_type in ("ozon.settlement", "wildberries.report"):
            result = parse_settlement(tmp_path)
        else:
            result = parse_invoice(tmp_path)  # fallback

        # Export
        out_fmt = output_format.lower()
        out_suffix = {
            OutputFormat.EXCEL.value: ".xlsx",
            OutputFormat.CSV.value: ".csv",
            OutputFormat.JSON.value: ".json",
        }.get(out_fmt, ".xlsx")

        out_path = Path(tempfile.mktemp(suffix=out_suffix))

        if out_fmt == OutputFormat.CSV.value:
            export_csv(result, out_path)
        elif out_fmt == OutputFormat.JSON.value:
            export_json(result, out_path)
        else:
            export_excel(result, out_path)

        return FileResponse(
            str(out_path),
            filename=f"parsed_{file.filename.rsplit('.', 1)[0]}{out_suffix}",
            media_type="application/octet-stream",
        )
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        Path(tmp_path).unlink(missing_ok=True)
        if out_path:
            out_path.unlink(missing_ok=True)
