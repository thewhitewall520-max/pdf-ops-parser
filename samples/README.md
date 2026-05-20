# Sample PDFs

These sample PDFs are **generated** for testing purposes. They contain **no real personal or business sensitive data**.

## Available Samples

| File | Type | Content |
|------|------|---------|
| `invoice.pdf` | Invoice | 3 line items (Widget Alpha, Widget Beta, Gadget Gamma), invoice number INV-2024-001, date 2024-01-15, total $122.50, tax $12.25 |
| `shipping.pdf` | Shipping label | FedEx carrier, tracking FX1234567890US, weight 2.5 kg, 5 tracking events with dates/locations |
| `ozon_settlement.pdf` | Ozon settlement report | Ozon Platform, seller ID SELLER-12345, period 2024-01-01 to 2024-01-31, sales 150,000 RUB, fees 15,000 RUB, refunds 5,000 RUB, payout 130,000 RUB |

## Usage

```bash
# Parse invoice
pdfops parse samples/invoice.pdf --type invoice --out /tmp/invoice_output.xlsx

# Parse shipping label to CSV
pdfops parse samples/shipping.pdf --type shipping --out /tmp/tracking.csv

# Parse Ozon settlement to JSON
pdfops parse samples/ozon_settlement.pdf --type ozon.settlement --out /tmp/settlement.json

# Auto-classify
pdfops classify samples/invoice.pdf
```

## Regenerating

These PDFs were generated using `fpdf2`. To regenerate:

```python
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)
pdf.cell(text="INVOICE", new_x="LMARGIN", new_y="NEXT", align="C")
# ... add fields ...
pdf.output("samples/invoice.pdf")
```

See `tests/test_parse_invoice.py` for a working example.
