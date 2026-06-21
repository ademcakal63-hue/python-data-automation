"""
FastAPI layer over the cleaned data.
Run:  uvicorn api:app --reload    (then open http://127.0.0.1:8000/docs)
"""
import sqlite3
from fastapi import FastAPI

app = FastAPI(title="Clean Data API", description="Query the normalized records.")

DB = "data.db"


def q(sql, params=()):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(sql, params).fetchall()]
    con.close()
    return rows


@app.get("/records")
def records(limit: int = 50):
    """Return cleaned rows."""
    return q("SELECT * FROM records LIMIT ?", (limit,))


@app.get("/summary")
def summary():
    """Row count + amount totals."""
    rows = q("SELECT COUNT(*) AS rows, ROUND(SUM(amount), 2) AS total, ROUND(AVG(amount), 2) AS avg FROM records")
    return rows[0] if rows else {}
