# src/seed_data.py
"""
Robust CSV -> SQLite seeder (No SQLAlchemy).
Uses sqlite3 directly to avoid reflection recursion issues.
"""

import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = "data/sales.db"

COLUMN_MAP = {
    "date": "Date",
    "order_date": "Date",
    "orderdate": "Date",

    "product": "Product",
    "products": "Product",
    "item": "Product",

    "category": "Category",

    "quantity": "Quantity",
    "qty": "Quantity",
    "count": "Quantity",

    "price": "Price",
    "unit_price": "Price",
    "amount": "Price",

    "customer_id": "Customer_ID",
    "customer": "Customer_ID",
    "cust_id": "Customer_ID",

    "region": "Region",
    "area": "Region",

    "total_sales": "Total_Sales",
    "total": "Total_Sales",
    "revenue": "Total_Sales",
}

CANONICAL_COLS = [
    "Date",
    "Region",
    "Product",
    "Category",
    "Quantity",
    "Price",
    "Customer_ID",
    "Total_Sales",
]


def normalise_columns(df):
    new_cols = {}
    for col in df.columns:
        key = col.strip().replace("\ufeff", "").replace(" ", "_").lower()
        new_cols[col] = COLUMN_MAP.get(key, col.strip())
    return df.rename(columns=new_cols)


def ensure_types_and_totals(df):

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for col in ["Quantity", "Price", "Total_Sales"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Total_Sales" not in df.columns:
        if {"Quantity", "Price"}.issubset(df.columns):
            df["Total_Sales"] = df["Quantity"] * df["Price"]

    if "Customer_ID" not in df.columns:
        df["Customer_ID"] = None

    for col in CANONICAL_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    ordered_cols = CANONICAL_COLS + [
        c for c in df.columns if c not in CANONICAL_COLS
    ]

    return df[ordered_cols]


def seed_from_csv(csv_path="data/sales_data.csv", drop_existing=False):

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found.")

    df = pd.read_csv(csv_path)
    df = normalise_columns(df)
    df = ensure_types_and_totals(df)

    Path("data").mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    df.to_sql("sales", conn, if_exists="replace", index=False)

    conn.close()

    print(f"Seeded {len(df)} rows into {DB_PATH}")


if __name__ == "__main__":
    seed_from_csv("data/sales_data.csv")
