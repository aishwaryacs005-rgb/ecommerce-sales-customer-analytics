"""
phase8_powerbi_export.py
-------------------------
Phase 8 — Prepare data exports for Power BI

Creates 3 clean CSV files optimised for Power BI import:
  1. powerbi/fact_orders.csv        — Main fact table (one row per order line item)
  2. powerbi/dim_customers.csv      — Customer dimension with RFM segment
  3. powerbi/dim_products.csv       — Product dimension

Power BI will build relationships automatically between these tables.

Run: python python/phase8_powerbi_export.py
"""

import pandas as pd
import numpy as np
import os

BASE_DIR   = os.path.join(os.path.dirname(__file__), "..")
CLEAN_FILE = os.path.join(BASE_DIR, "data", "cleaned", "ecommerce_cleaned.csv")
RFM_FILE   = os.path.join(BASE_DIR, "data", "cleaned", "rfm_segments.csv")
RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR    = os.path.join(BASE_DIR, "powerbi")
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("  Phase 8 — Power BI Data Export")
print("=" * 60)

# ── Load data ────────────────────────────────────────────
print("\nLoading cleaned data...")
df  = pd.read_csv(CLEAN_FILE, parse_dates=["Order_Date"])
rfm = pd.read_csv(RFM_FILE)

# ── 1. FACT TABLE — fact_orders ──────────────────────────
# One row per order line item. This is the heart of the model.
# Keep all measures and foreign keys.
print("Building fact_orders...")

fact = df[[
    "Detail_ID", "Order_ID", "Customer_ID", "Product_ID",
    "Order_Date", "Order_Year", "Order_Month", "Order_Month_Name",
    "Order_Quarter", "Order_YearMonth", "Season",
    "Quantity", "Unit_Price", "Discount", "Discount_Amount",
    "Sales", "Cost", "Profit", "Profit_Margin_Pct",
    "Payment_Mode", "Order_Status",
    "Is_Profitable", "Is_High_Value",
]].copy()

# Power BI needs booleans as 0/1 integers
fact["Is_Profitable"] = fact["Is_Profitable"].astype(int)
fact["Is_High_Value"]  = fact["Is_High_Value"].astype(int)

fact.to_csv(os.path.join(OUT_DIR, "fact_orders.csv"), index=False)
print(f"  ✓ fact_orders.csv        : {len(fact):>8,} rows  × {fact.shape[1]} cols")

# ── 2. DIMENSION TABLE — dim_customers ───────────────────
# One row per customer. Includes RFM segment.
print("Building dim_customers...")

customers_raw = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))

# Merge RFM segment into customer dimension
rfm_seg = rfm[["Customer_ID", "Recency", "Frequency", "Monetary",
               "R_Score", "F_Score", "M_Score", "RFM_Score", "Segment"]].copy()
rfm_seg.rename(columns={"Segment": "RFM_Segment"}, inplace=True)

dim_customers = customers_raw.merge(rfm_seg, on="Customer_ID", how="left")

# Add Age_Group
def age_group(age):
    if age < 26: return "18-25"
    elif age < 36: return "26-35"
    elif age < 46: return "36-45"
    elif age < 56: return "46-55"
    return "56+"

dim_customers["Age_Group"] = dim_customers["Age"].apply(age_group)

dim_customers.to_csv(os.path.join(OUT_DIR, "dim_customers.csv"), index=False)
print(f"  ✓ dim_customers.csv      : {len(dim_customers):>8,} rows  × {dim_customers.shape[1]} cols")

# ── 3. DIMENSION TABLE — dim_products ────────────────────
# One row per product.
print("Building dim_products...")

dim_products = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
dim_products.to_csv(os.path.join(OUT_DIR, "dim_products.csv"), index=False)
print(f"  ✓ dim_products.csv       : {len(dim_products):>8,} rows  × {dim_products.shape[1]} cols")

# ── 4. SUMMARY TABLE for KPI Cards ───────────────────────
# Pre-aggregated monthly summary used for trend charts
print("Building monthly_summary...")

monthly = (
    df[df["Order_Status"] != "Cancelled"]
    .groupby("Order_YearMonth", as_index=False)
    .agg(
        Orders        = ("Order_ID",  "nunique"),
        Total_Sales   = ("Sales",     "sum"),
        Total_Profit  = ("Profit",    "sum"),
        Total_Cost    = ("Cost",      "sum"),
        Total_Qty     = ("Quantity",  "sum"),
        Customers     = ("Customer_ID","nunique"),
    )
)
monthly["Profit_Margin_Pct"] = (monthly["Total_Profit"] / monthly["Total_Sales"] * 100).round(2)
monthly["AOV"]               = (monthly["Total_Sales"] / monthly["Orders"]).round(2)
monthly.to_csv(os.path.join(OUT_DIR, "monthly_summary.csv"), index=False)
print(f"  ✓ monthly_summary.csv    : {len(monthly):>8,} rows  × {monthly.shape[1]} cols")

# ── Print summary ────────────────────────────────────────
print(f"\n  All files saved to: {os.path.abspath(OUT_DIR)}")
print("\n  Power BI Data Model:")
print("  ─────────────────────────────────────────────────")
print("  fact_orders  ──(Customer_ID)──►  dim_customers")
print("  fact_orders  ──(Product_ID) ──►  dim_products")
print("  ─────────────────────────────────────────────────")
print("  Relationship type: Many-to-One (Many orders → One customer/product)")

print(f"\n{'='*60}")
print("  Export COMPLETE — open Power BI Desktop and import these 3 files")
print(f"{'='*60}")
