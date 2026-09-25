"""
prepare_excel_data.py
----------------------
Joins all 5 relational tables into one flat CSV file
suitable for Excel analysis.

Output: data/raw/ecommerce_flat.csv
"""

import pandas as pd
import os

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

# ── Load all tables ──────────────────────────────────────
regions_df       = pd.read_csv(os.path.join(RAW_DIR, "regions.csv"))
products_df      = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
customers_df     = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
orders_df        = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
order_details_df = pd.read_csv(os.path.join(RAW_DIR, "order_details.csv"))

# ── Join step by step ────────────────────────────────────

# Step 1: order_details + products  →  adds Category, Sub_Category, Product_Name
flat = order_details_df.merge(
    products_df[["Product_ID", "Category", "Sub_Category", "Product_Name"]],
    on="Product_ID",
    how="left"
)

# Step 2: flat + orders  →  adds Order_Date, Customer_ID, Payment_Mode, Order_Status
flat = flat.merge(
    orders_df[["Order_ID", "Order_Date", "Customer_ID", "Payment_Mode", "Order_Status"]],
    on="Order_ID",
    how="left"
)

# Step 3: flat + customers  →  adds Customer_Name, Gender, Age, City, State, Region, Customer_Type
flat = flat.merge(
    customers_df[["Customer_ID", "Customer_Name", "Gender", "Age",
                  "City", "State", "Region", "Customer_Type"]],
    on="Customer_ID",
    how="left"
)

# ── Select and order final columns ───────────────────────
flat = flat[[
    "Order_ID",
    "Order_Date",
    "Customer_ID",
    "Customer_Name",
    "Gender",
    "Age",
    "City",
    "State",
    "Region",
    "Product_ID",
    "Product_Name",
    "Category",
    "Sub_Category",
    "Quantity",
    "Unit_Price",
    "Discount",
    "Sales",
    "Cost",
    "Profit",
    "Payment_Mode",
    "Order_Status",
    "Customer_Type",
]]

# ── Add a few calculated columns Excel will also use ────
flat["Order_Date"] = pd.to_datetime(flat["Order_Date"])
flat["Order_Month"] = flat["Order_Date"].dt.month
flat["Order_Year"]  = flat["Order_Date"].dt.year
flat["Profit_Margin"] = ((flat["Profit"] / flat["Sales"]) * 100).round(2)

# ── Save ─────────────────────────────────────────────────
out_path = os.path.join(RAW_DIR, "ecommerce_flat.csv")
flat.to_csv(out_path, index=False)

print("=" * 55)
print("  Flat file created for Excel analysis")
print("=" * 55)
print(f"\n  File   : ecommerce_flat.csv")
print(f"  Rows   : {len(flat):,}")
print(f"  Cols   : {len(flat.columns)}")
print(f"\n  Columns:")
for c in flat.columns:
    print(f"    {c}")
print(f"\n  Saved to: {os.path.abspath(out_path)}")
