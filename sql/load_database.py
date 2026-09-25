"""
load_database.py
-----------------
Creates the SQLite database and loads all 5 CSV tables into it.

Run: python sql/load_database.py

Output: sql/ecommerce.db
"""

import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
SQL_DIR  = os.path.join(BASE_DIR, "sql")
DB_PATH  = os.path.join(SQL_DIR, "ecommerce.db")

# ── Load CSVs ────────────────────────────────────────────
print("Loading raw CSV files...")
regions_df       = pd.read_csv(os.path.join(RAW_DIR, "regions.csv"))
products_df      = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
customers_df     = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
orders_df        = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
order_details_df = pd.read_csv(os.path.join(RAW_DIR, "order_details.csv"))

# ── Connect / create DB ──────────────────────────────────
print(f"Creating database: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ── Run schema SQL ───────────────────────────────────────
schema_path = os.path.join(SQL_DIR, "schema.sql")
with open(schema_path, "r") as f:
    schema_sql = f.read()
cursor.executescript(schema_sql)
print("Schema created (5 tables + indexes)")

# ── Load tables ──────────────────────────────────────────
tables = [
    ("regions",       regions_df),
    ("products",      products_df),
    ("customers",     customers_df),
    ("orders",        orders_df),
    ("order_details", order_details_df),
]

for table_name, df in tables:
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  {table_name:<18}: {count:>8,} rows loaded")

conn.commit()
conn.close()

size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
print(f"\n✓ Database saved: {DB_PATH}  ({size_mb:.1f} MB)")
print("  Run SQL queries with: python sql/run_analysis.py")
