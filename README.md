# PDF Ops Parser

Convert invoices, shipping labels and marketplace settlement PDFs into Excel, CSV and JSON.

> **⚠️ This is not a universal AI PDF parser.**  
> It is a **rule-based operational document parser** — best suited for structured invoices, shipping documents and e-commerce settlement reports. For general-purpose PDF extraction, use pdfplumber, PyMuPDF or a document AI API.

A lightweight, open-source tool for e-commerce operations teams and cross-border sellers who need to extract structured data from PDF invoices, shipping labels, and marketplace settlement reports (Ozon, Wildberries).

## Quick Start

```bash
# Install
pip install -e .

# CLI: parse an invoice to Excel
pdfops parse samples/invoice.pdf --type invoice --out output.xlsx

# CLI: parse a shipping label to CSV
pdfops parse samples/shipping.pdf --type shipping --out tracking.csv

# CLI: auto-detect document type
pdfops parse samples/invoice.pdf --out output.xlsx

# CLI: classify a document
pdfops classify samples/invoice.pdf

# API: start the REST server
uvicorn apps.api.main:app --reload

# API: parse via curl
curl -X POST http://localhost:8000/parse \
  -F "file=@samples/invoice.pdf" \
  -F "doc_type=invoice" \
  -F "output_format=xlsx" -o output.xlsx
```

## Features

- Parse invoice PDFs → structured data (line items, totals, taxes)
- Parse shipping/label PDFs → structured data (tracking, events)
- Parse marketplace settlement reports (Ozon, Wildberries)
- Auto-classify document type (4 built-in classifiers)
- Export to **Excel** (`.xlsx`), **CSV** (`.csv`), **JSON** (`.json`)
- CLI (`pdfops`) and REST API (`FastAPI`)
- Docker support (`docker compose up`)

## Sample Documents

| File | Description |
|------|-------------|
| `samples/invoice.pdf` | Standard invoice with 3 line items, SKU, totals and tax |
| `samples/shipping.pdf` | FedEx shipping label with tracking events |
| `samples/ozon_settlement.pdf` | Ozon marketplace settlement report (Russian fields) |

These samples are **generated** and contain **no real personal or business sensitive data**.

## Supported Document Types

| Type | Auto-classify? |
|------|----------------|
| Invoice | ✅ |
| Shipping label | ✅ |
| Ozon settlement | ✅ |
| Wildberries report | ✅ |

## Roadmap

- YAML-based template system (define custom document parsers without code)
- Wildberries full settlement parser
- Multi-page document support
- OAuth-based API key management
- Web UI

## Project Structure

```
pdf-ops-parser/
├── apps/api/         — FastAPI REST API
├── packages/parser/  — core parsing engine
│   ├── schemas.py    — pydantic data models
│   ├── extract_text.py / extract_tables.py
│   ├── classify_doc.py
│   ├── parse_invoice.py / parse_shipping.py / parse_settlement.py
│   ├── normalize.py
│   └── export_excel.py / export_csv.py / export_json.py
├── cli/              — Typer CLI entry point
├── templates/        — YAML document type definitions
├── tests/            — pytest suite
└── samples/          — generated example PDFs (no real data)
```

## GitHub Release Readiness Checklist

- [x] `pytest tests/` — all tests pass
- [x] `pdfops parse` — CLI works for all supported types
- [x] `uvicorn apps.api.main:app` — API server starts
- [x] Sample PDFs — valid and produce correct output
- [x] No API keys or secrets in codebase
- [x] No real/private documents committed
- [x] `.gitignore` excludes build artifacts (`.xlsx`, `.csv`, `.json`, `__pycache__/`)
- [x] File upload restricted to PDF, 10MB limit
- [x] Temporary upload files cleaned up
- [x] MIT License
- [x] Docker support

## License

MIT
