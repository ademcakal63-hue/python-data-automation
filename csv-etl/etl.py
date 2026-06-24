"""
Messy CSV -> clean, normalized rows -> SQLite.
Run:  python etl.py sample_messy.csv
Handles: trimming, casing, currency symbols, thousands separators,
mixed date formats, lowercased emails, and duplicate rows.
"""
import sys
import sqlite3
import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    for c in df.columns:
        if df[c].dtype == object or pd.api.types.is_string_dtype(df[c]):
            df[c] = df[c].astype(str).str.strip()

    if "name" in df.columns:
        df["name"] = df["name"].str.title()
    if "email" in df.columns:
        df["email"] = df["email"].str.lower()
    if "amount" in df.columns:
        s = df["amount"].astype(str)
        neg = s.str.contains(r"\(.*\d.*\)", regex=True)     # accounting negatives, e.g. (500)
        s = s.str.replace(r"[^0-9.\-]", "", regex=True)     # strip currency, commas, parens
        df["amount"] = pd.to_numeric(s, errors="coerce")
        df.loc[neg, "amount"] = -df.loc[neg, "amount"].abs()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed", dayfirst=False).dt.strftime("%Y-%m-%d")

    return df.drop_duplicates().reset_index(drop=True)


def run(csv_path: str, db_path: str = "data.db", table: str = "records"):
    raw = pd.read_csv(csv_path, skipinitialspace=True)
    cleaned = clean(raw)
    con = sqlite3.connect(db_path)
    cleaned.to_sql(table, con, if_exists="replace", index=False)
    con.close()
    return len(raw), len(cleaned)


if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else "sample_messy.csv"
    n_in, n_out = run(csv)
    print(f"Ingested {n_in} raw rows -> {n_out} clean rows into data.db (table: records)")
