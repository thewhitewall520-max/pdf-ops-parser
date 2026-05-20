# PDF Ops Parser

```
┌─────────────────────────────────────────────────┐
│  PDF Ops Parser                                  │
│  Invoice PDF → Excel / CSV / JSON in seconds     │
│                                                   │
│  $ pdfops parse invoice.pdf --type invoice        │
│  ─────────────────────────────────────             │
│  ✓ INVOICE  → INV-2024-001                       │
│  ✓ 3 line items extracted                        │
│  ✓ Total: $122.50 • Tax: $12.25                  │
│  ✓ Exported to output.xlsx                        │
└─────────────────────────────────────────────────┘
```

Convert invoices, shipping labels and marketplace settlement PDFs into Excel, CSV and JSON.

> **⚠️ This is not a universal AI PDF parser.**  
> It is a **rule-based operational document parser** — best suited for structured invoices, shipping documents and e-commerce settlement reports. For general-purpose PDF extraction, use pdfplumber, PyMuPDF or a document AI API.

A lightweight, open-source tool for e-commerce operations teams and cross-border sellers who need to extract structured data from PDF invoices, shipping labels, and marketplace settlement reports (Ozon, Wildberries).

## Quick Start

```bash
# Install
$ pip install -e .

# CLI: parse an invoice to Excel
$ pdfops parse samples/invoice.pdf --type invoice --out output.xlsx
Parsing samples/invoice.pdf...
Exported to output.xlsx

# CLI: parse a shipping label to CSV
$ pdfops parse samples/shipping.pdf --type shipping --out tracking.csv
Parsing samples/shipping.pdf...
Exported to tracking.csv

# CLI: parse an Ozon settlement report to JSON
$ pdfops parse samples/ozon_settlement.pdf --type ozon.settlement --out report.json
Parsing samples/ozon_settlement.pdf...
Exported to report.json

# CLI: auto-detect document type
$ pdfops parse samples/invoice.pdf --out output.xlsx
Auto-detecting document type...
  Detected as: invoice
Parsing samples/invoice.pdf...
Exported to output.xlsx

# CLI: classify a document
$ pdfops classify samples/invoice.pdf
invoice

# API: start the REST server
$ uvicorn apps.api.main:app --reload

# API: parse via curl
$ curl -X POST http://localhost:8000/parse \
  -F "file=@samples/invoice.pdf" \
  -F "doc_type=invoice" \
  -F "output_format=xlsx" -o output.xlsx
```

## Features

| Feature | Description |
|---------|-------------|
| 🧾 Invoice parsing | Extract line items, SKU, quantities, totals, taxes |
| 📦 Shipping parsing | Extract carrier, tracking number, weight, events |
| 📊 Settlement parsing | Ozon marketplace — sales, fees, refunds, net payout |
| 🧠 Auto-classify | Detects document type without `--type` flag |
| 📁 3 export formats | Excel (`.xlsx`), CSV (`.csv`), JSON (`.json`) |
| 🖥️ CLI + API | `pdfops` command or FastAPI REST server |
| 🐳 Docker | `docker compose up` for instant start |

## Sample Documents

| File | Description | Content |
|------|-------------|---------|
| `samples/invoice.pdf` | Standard invoice | 3 line items, SKU WGT-001/002/003, total $122.50, tax $12.25 |
| `samples/shipping.pdf` | FedEx shipping label | Tracking FX1234567890US, 5 events, 2.5 kg |
| `samples/ozon_settlement.pdf` | Ozon settlement report | 150,000 RUB sales, 15,000 RUB fees, 130,000 RUB payout |

All samples are **generated** — no real personal or business data.

## Supported Document Types

| Type | Auto-classify? | Example |
|------|:--------------:|---------|
| Invoice | ✅ | `pdfops parse file.pdf --type invoice` |
| Shipping label | ✅ | `pdfops parse file.pdf --type shipping` |
| Ozon settlement | ✅ | `pdfops parse file.pdf --type ozon.settlement` |
| Wildberries report | ✅ | (parser ready, templates available) |

## Project Structure

```
pdf-ops-parser/
├── apps/api/              — FastAPI REST API
│   └── routes/parse.py    — POST /parse endpoint
├── packages/parser/       — core parsing engine
│   ├── schemas.py         — pydantic data models
│   ├── extract_text.py    — pdfplumber + PyMuPDF text extraction
│   ├── extract_tables.py  — table detection & extraction
│   ├── classify_doc.py    — keyword-based document type detection
│   ├── parse_invoice.py   — invoice field & line item extraction
│   ├── parse_shipping.py  — shipping label & event extraction
│   ├── parse_settlement.py— Ozon/Wildberries settlement parser
│   ├── normalize.py       — unified flat-rows export format
│   ├── export_excel.py    — pandas → xlsx
│   ├── export_csv.py      — pandas → csv
│   └── export_json.py     — pydantic → json
├── cli/main.py            — Typer CLI (pdfops command)
├── templates/             — YAML field definitions (extensible)
├── tests/                 — pytest suite (24 tests)
└── samples/               — generated example PDFs
```

## Roadmap

- YAML-based template system (define custom document parsers without code)
- Wildberries full settlement parser
- Multi-page document support
- OAuth-based API key management
- Web UI

## GitHub Release Readiness

- [x] `pytest tests/` — 24 tests pass
- [x] `pdfops parse` — CLI works for all 3 document types
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
