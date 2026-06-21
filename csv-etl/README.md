# Messy CSV → Clean Database + API

Takes a messy CSV (duplicates, inconsistent casing, currency symbols, mixed date formats) and turns it into a clean, normalized table in SQLite — then exposes it over a small FastAPI service.

A typical "data automation" job: *"I have ugly spreadsheets, I need them clean and queryable."*

## Run

```bash
pip install -r requirements.txt
python etl.py sample_messy.csv          # clean + load -> data.db
uvicorn api:app --reload                # http://127.0.0.1:8000/docs
```

## What it cleans

| Problem | Fix |
|--------|-----|
| `  john doe ` | trimmed + Title Cased → `John Doe` |
| `JOHN@X.COM` | lowercased |
| `$1,200.00` | parsed → `1200.0` |
| `01/06/2026` vs `2026-01-05` | normalized → `YYYY-MM-DD` |
| duplicate rows | dropped |

## Stack
`pandas` (clean) · `sqlite3` (store) · `FastAPI` (serve). Swap SQLite for Postgres in one line.
