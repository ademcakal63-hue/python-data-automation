# Invoice → Structured JSON

Drop a PDF invoice, get clean structured data back — **vendor, invoice number, dates, currency, subtotal, tax, total, and line items** — as JSON you can pipe into a database, ERP, or accounting system.

Built in Python. Two extraction paths:

- **LLM path (Claude)** — layout-agnostic. Handles invoices it has never seen. Needs an `ANTHROPIC_API_KEY`.
- **Regex fallback** — no API key, no cost. Extracts the most common fields. Always available. Note: `line_items` are populated only on the Claude (LLM) path; the regex path returns `[]`.

## Demo

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then drop a PDF in the browser. Or from the terminal:

```bash
python extractor.py path/to/invoice.pdf
```

For layout-agnostic extraction, set your key first:

```bash
export ANTHROPIC_API_KEY=sk-...        # Windows: set ANTHROPIC_API_KEY=sk-...
```

## What it does

| Step | Tool |
|------|------|
| PDF text | `pdfplumber` |
| Layout-agnostic field extraction | Claude (`claude-haiku-4-5`) with a fixed JSON schema |
| No-key fallback | regex heuristics |
| UI | Streamlit (upload → JSON + download) |

## Roadmap (easy adds)

- Scanned/image invoices → OCR (Tesseract / Claude vision)
- Per-vendor templates for 100% accuracy on recurring suppliers
- Batch mode: a folder of PDFs → one CSV
- FastAPI endpoint for system-to-system integration

---

*Send a sample invoice and get the structured JSON back before you commit — that's the whole pitch.*
