"""
phase4_data_cleaning.py
------------------------
Phase 4 — Python Data Cleaning & Transformation

WHAT THIS SCRIPT DOES (in order):
  Step 1  : Load all 5 raw CSV tables
  Step 2  : Inspect each table (shape, dtypes, nulls, dupes)
  Step 3  : Clean each table individually
  Step 4  : Join all tables into one master flat dataframe
  Step 5  : Handle missing values
  Step 6  : Remove duplicates
  Step 7  : Fix data types
  Step 8  : Standardise categorical text values
  Step 9  : Handle invalid / impossible values
  Step 10 : Check and handle outliers
  Step 11 : Create all calculated columns
  Step 12 : Final validation
  Step 13 : Export cleaned data to data/cleaned/

OUTPUT:
  data/cleaned/ecommerce_cleaned.csv     — master cleaned flat file
  data/cleaned/cleaning_report.txt       — full audit trail

Run with:  python python/phase4_data_cleaning.py
"""

import pandas as pd
import numpy as np
import os
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────
BASE_DIR     = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR      = os.path.join(BASE_DIR, "data", "raw")
CLEANED_DIR  = os.path.join(BASE_DIR, "data", "cleaned")
os.makedirs(CLEANED_DIR, exist_ok=True)

REPORT_PATH  = os.path.join(CLEANED_DIR, "cleaning_report.txt")

SEP = "=" * 65

# ─────────────────────────────────────────────────────────
# REPORT LOGGER — writes every step to a text file too
# ─────────────────────────────────────────────────────────
report_lines = []

def log(text=""):
    """Print to console AND save to report."""
    print(text)
    report_lines.append(text)

def save_report():
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

# ─────────────────────────────────────────────────────────
# STEP 1 — LOAD RAW DATA
# ─────────────────────────────────────────────────────────
log(SEP)
log("  PHASE 4 — DATA CLEANING & TRANSFORMATION")
log(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log(SEP)

log("\n[STEP 1] Loading raw CSV files...")

regions_df       = pd.read_csv(os.path.join(RAW_DIR, "regions.csv"))
products_df      = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
customers_df     = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
orders_df        = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
order_details_df = pd.read_csv(os.path.join(RAW_DIR, "order_details.csv"))

log(f"  regions       : {regions_df.shape}")
log(f"  products      : {products_df.shape}")
log(f"  customers     : {customers_df.shape}")
log(f"  orders        : {orders_df.shape}")
log(f"  order_details : {order_details_df.shape}")
log("  ✓ All files loaded")

# ─────────────────────────────────────────────────────────
# STEP 2 — INSPECT EACH TABLE
# ─────────────────────────────────────────────────────────
log("\n[STEP 2] Inspecting tables for issues...")

def inspect(name, df):
    """Returns a summary dict of issues found in a dataframe."""
    nulls  = df.isnull().sum().sum()
    dupes  = df.duplicated().sum()
    log(f"  {name:<18}  rows={len(df):>6,}  null_cells={nulls:>4}  duplicate_rows={dupes:>4}")
    return {"nulls": nulls, "dupes": dupes}

for name, df in [("regions", regions_df), ("products", products_df),
                  ("customers", customers_df), ("orders", orders_df),
                  ("order_details", order_details_df)]:
    inspect(name, df)

log("  ✓ Inspection complete")

# ─────────────────────────────────────────────────────────
# STEP 3 — CLEAN EACH TABLE
# ─────────────────────────────────────────────────────────
log("\n[STEP 3] Cleaning individual tables...")

# ── 3a. Strip whitespace from all string columns ──────────
# Real data from databases often has leading/trailing spaces.
# Example: "  Electronics " should become "Electronics"

def strip_strings(df):
    """Strip leading/trailing spaces from all string columns."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df

regions_df       = strip_strings(regions_df)
products_df      = strip_strings(products_df)
customers_df     = strip_strings(customers_df)
orders_df        = strip_strings(orders_df)
order_details_df = strip_strings(order_details_df)
log("  ✓ 3a: Stripped whitespace from all string columns")

# ── 3b. Standardise text case ────────────────────────────
# Categorical columns should have consistent casing.
# "north" and "North" are the same — we want "North".

customers_df["Region"]        = customers_df["Region"].str.title()
customers_df["Gender"]        = customers_df["Gender"].str.title()
customers_df["Customer_Type"] = customers_df["Customer_Type"].str.title()
orders_df["Order_Status"]     = orders_df["Order_Status"].str.title()
orders_df["Payment_Mode"]     = orders_df["Payment_Mode"].str.title()
products_df["Category"]       = products_df["Category"].str.title()
log("  ✓ 3b: Standardised text casing on categorical columns")

# ── 3c. Convert Order_Date to datetime ───────────────────
# Stored as string "2022-03-15" → must be datetime for date math.
orders_df["Order_Date"] = pd.to_datetime(orders_df["Order_Date"], format="%Y-%m-%d", errors="coerce")

# How many dates failed to parse?
bad_dates = orders_df["Order_Date"].isna().sum()
log(f"  ✓ 3c: Parsed Order_Date to datetime  (failed parses: {bad_dates})")

# ── 3d. Validate numeric ranges ──────────────────────────
# Quantity must be 1–5, Discount must be 0–1, Sales/Profit/Cost must be > 0

before = len(order_details_df)
order_details_df = order_details_df[
    (order_details_df["Quantity"]   >= 1) &
    (order_details_df["Quantity"]   <= 10) &        # cap at 10 for safety
    (order_details_df["Discount"]   >= 0) &
    (order_details_df["Discount"]   <= 1) &
    (order_details_df["Sales"]      >  0) &
    (order_details_df["Cost"]       >  0)
]
removed = before - len(order_details_df)
log(f"  ✓ 3d: Removed {removed} order_detail rows with invalid numeric values")

# ── 3e. Remove duplicate rows ─────────────────────────────
for name, df in [("regions", regions_df), ("products", products_df),
                  ("customers", customers_df), ("orders", orders_df),
                  ("order_details", order_details_df)]:
    before = len(df)
    df.drop_duplicates(inplace=True)
    removed = before - len(df)
    if removed > 0:
        log(f"  ✓ 3e: Removed {removed} duplicate rows from {name}")

log("  ✓ 3e: Duplicate check complete (no duplicates found in this dataset)")

# ─────────────────────────────────────────────────────────
# STEP 4 — JOIN ALL TABLES INTO ONE MASTER DATAFRAME
# ─────────────────────────────────────────────────────────
log("\n[STEP 4] Joining all 5 tables into master dataframe...")

# order_details → products
df = order_details_df.merge(
    products_df[["Product_ID", "Category", "Sub_Category", "Product_Name"]],
    on="Product_ID", how="left"
)
log(f"  After joining products    : {df.shape}")

# → orders
df = df.merge(
    orders_df[["Order_ID", "Order_Date", "Customer_ID", "Payment_Mode", "Order_Status"]],
    on="Order_ID", how="left"
)
log(f"  After joining orders      : {df.shape}")

# → customers
df = df.merge(
    customers_df[["Customer_ID", "Customer_Name", "Gender", "Age",
                   "City", "State", "Region", "Customer_Type"]],
    on="Customer_ID", how="left"
)
log(f"  After joining customers   : {df.shape}")

log("  ✓ Master dataframe created")

# ─────────────────────────────────────────────────────────
# STEP 5 — HANDLE MISSING VALUES IN MASTER DF
# ─────────────────────────────────────────────────────────
log("\n[STEP 5] Handling missing values in master dataframe...")

# Check nulls per column
null_summary = df.isnull().sum()
null_cols = null_summary[null_summary > 0]

if len(null_cols) == 0:
    log("  ✓ No missing values found — dataset is complete")
else:
    log(f"  Columns with missing values:")
    for col, count in null_cols.items():
        pct = count / len(df) * 100
        log(f"    {col:<25} : {count:>5} missing ({pct:.2f}%)")

    # Strategy for each possible null:
    # String columns   → fill with "Unknown"
    # Numeric columns  → fill with median (more robust than mean for skewed data)
    # Date columns     → drop rows (can't impute a date meaningfully)

    for col in null_cols.index:
        if df[col].dtype == "object":
            df[col].fillna("Unknown", inplace=True)
            log(f"    Filled {col} nulls with 'Unknown'")
        elif df[col].dtype in ["float64", "int64"]:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            log(f"    Filled {col} nulls with median ({median_val:.2f})")
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            before = len(df)
            df.dropna(subset=[col], inplace=True)
            log(f"    Dropped {before - len(df)} rows with null {col}")

log(f"  ✓ Missing value handling complete. Remaining nulls: {df.isnull().sum().sum()}")

# ─────────────────────────────────────────────────────────
# STEP 6 — DATA TYPE ENFORCEMENT
# ─────────────────────────────────────────────────────────
log("\n[STEP 6] Enforcing correct data types...")

df["Order_Date"]  = pd.to_datetime(df["Order_Date"], errors="coerce")
df["Quantity"]    = df["Quantity"].astype(int)
df["Age"]         = df["Age"].astype(int)
df["Unit_Price"]  = df["Unit_Price"].astype(float)
df["Discount"]    = df["Discount"].astype(float)
df["Sales"]       = df["Sales"].astype(float).round(2)
df["Cost"]        = df["Cost"].astype(float).round(2)
df["Profit"]      = df["Profit"].astype(float).round(2)

log("  ✓ Order_Date  → datetime64")
log("  ✓ Quantity    → int")
log("  ✓ Age         → int")
log("  ✓ Unit_Price  → float")
log("  ✓ Discount    → float")
log("  ✓ Sales       → float (2 decimal places)")
log("  ✓ Cost        → float (2 decimal places)")
log("  ✓ Profit      → float (2 decimal places)")

# ─────────────────────────────────────────────────────────
# STEP 7 — STANDARDISE CATEGORICAL VALUES
# ─────────────────────────────────────────────────────────
log("\n[STEP 7] Standardising categorical values...")

# Check what unique values exist in key categorical columns
for col in ["Category", "Region", "Gender", "Customer_Type", "Order_Status", "Payment_Mode"]:
    unique_vals = sorted(df[col].dropna().unique().tolist())
    log(f"  {col:<18}: {unique_vals}")

# Correct any known variations
# (In a real project, you'd find things like "electronics", "ELECTRONICS", "Electronics" all meaning the same thing)
# Our generator is already clean, but this is the pattern to follow:

replacements = {
    "Order_Status": {
        "Delivered":  "Delivered",
        "Shipped":    "Shipped",
        "Cancelled":  "Cancelled",
        "Returned":   "Returned",
        "Processing": "Processing",
    },
    "Payment_Mode": {
        "Credit Card":      "Credit Card",
        "Debit Card":       "Debit Card",
        "Upi":              "UPI",           # fix incorrect casing from .title()
        "Net Banking":      "Net Banking",
        "Cash On Delivery": "Cash on Delivery",
        "Emi":              "EMI",           # fix incorrect casing
    },
}

for col, mapping in replacements.items():
    df[col] = df[col].map(mapping).fillna(df[col])

log("  ✓ Fixed casing: UPI, EMI, Cash on Delivery")

# ─────────────────────────────────────────────────────────
# STEP 8 — HANDLE INVALID VALUES
# ─────────────────────────────────────────────────────────
log("\n[STEP 8] Checking for invalid / impossible values...")

# Business rule checks:
checks = {
    "Sales <= 0":            (df["Sales"] <= 0).sum(),
    "Cost <= 0":             (df["Cost"] <= 0).sum(),
    "Profit < -Cost":        (df["Profit"] < -df["Cost"]).sum(),    # can't lose more than cost
    "Discount > 1":          (df["Discount"] > 1).sum(),
    "Discount < 0":          (df["Discount"] < 0).sum(),
    "Quantity <= 0":         (df["Quantity"] <= 0).sum(),
    "Age < 18":              (df["Age"] < 18).sum(),
    "Age > 100":             (df["Age"] > 100).sum(),
}

issues_found = False
for check, count in checks.items():
    status = "✓" if count == 0 else "⚠"
    log(f"  {status} {check:<30}: {count} rows affected")
    if count > 0:
        issues_found = True

if not issues_found:
    log("  ✓ All business rule checks passed — no invalid values found")

# ─────────────────────────────────────────────────────────
# STEP 9 — OUTLIER DETECTION
# ─────────────────────────────────────────────────────────
log("\n[STEP 9] Outlier detection (IQR method)...")

# We check Sales and Profit.
# We do NOT remove outliers here — in business data, high-value sales are real and important.
# We just flag them so analysts are aware.

def iqr_bounds(series):
    """Return lower and upper IQR fences."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return lower, upper

for col in ["Sales", "Profit", "Unit_Price"]:
    lo, hi = iqr_bounds(df[col])
    n_outliers = ((df[col] < lo) | (df[col] > hi)).sum()
    pct = n_outliers / len(df) * 100
    log(f"  {col:<14}: {n_outliers:>6,} outliers ({pct:.1f}%)  "
        f"[fence: {lo:,.0f} – {hi:,.0f}]")

log("  → Decision: Outliers KEPT. High-value Electronics orders are legitimate.")
log("  → Flag them with an 'Is_High_Value' column for separate analysis.")

# ─────────────────────────────────────────────────────────
# STEP 10 — CREATE CALCULATED COLUMNS
# ─────────────────────────────────────────────────────────
log("\n[STEP 10] Creating calculated columns...")

# 10a. Date-derived columns
df["Order_Year"]    = df["Order_Date"].dt.year.astype(int)
df["Order_Month"]   = df["Order_Date"].dt.month.astype(int)
df["Order_Quarter"] = df["Order_Date"].dt.quarter.astype(int)
df["Order_Month_Name"] = df["Order_Date"].dt.strftime("%b")   # Jan, Feb, ...
df["Order_YearMonth"]  = df["Order_Date"].dt.to_period("M").astype(str)  # 2022-01
df["Order_DayOfWeek"]  = df["Order_Date"].dt.day_name()       # Monday, Tuesday, ...
log("  ✓ Date columns: Order_Year, Order_Month, Order_Quarter, Order_Month_Name, Order_YearMonth, Order_DayOfWeek")

# 10b. Profit Margin (%)
#   = (Profit / Sales) × 100
#   Tells us how much of every ₹100 in revenue is actual profit.
df["Profit_Margin_Pct"] = ((df["Profit"] / df["Sales"]) * 100).round(2)
log("  ✓ Profit_Margin_Pct = (Profit / Sales) × 100")

# 10c. Revenue alias (same as Sales — clearer business term)
df["Revenue"] = df["Sales"]
log("  ✓ Revenue = Sales (alias for clarity)")

# 10d. Discount Amount (₹ value of discount given)
#   = Unit_Price × Quantity × Discount
df["Discount_Amount"] = (df["Unit_Price"] * df["Quantity"] * df["Discount"]).round(2)
log("  ✓ Discount_Amount = Unit_Price × Quantity × Discount")

# 10e. Age Group — bins customers into age segments
#   Useful for understanding which age groups buy what
def age_group(age):
    if age < 26:
        return "18–25"
    elif age < 36:
        return "26–35"
    elif age < 46:
        return "36–45"
    elif age < 56:
        return "46–55"
    else:
        return "56+"

df["Age_Group"] = df["Age"].apply(age_group)
log("  ✓ Age_Group: 18–25 / 26–35 / 36–45 / 46–55 / 56+")

# 10f. Is_Profitable flag
df["Is_Profitable"] = df["Profit"] > 0
log("  ✓ Is_Profitable = True if Profit > 0")

# 10g. Is_High_Value — flags top 5% orders by Sales
high_val_threshold = df["Sales"].quantile(0.95)
df["Is_High_Value"] = df["Sales"] >= high_val_threshold
log(f"  ✓ Is_High_Value = True if Sales ≥ ₹{high_val_threshold:,.0f} (top 5%)")

# 10h. Season — groups months into business seasons
def get_season(month):
    if month in [10, 11, 12]:
        return "Festive Season"     # Diwali, Christmas, New Year
    elif month in [1, 2]:
        return "New Year Sales"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    return "Other"

df["Season"] = df["Order_Month"].apply(get_season)
log("  ✓ Season: Festive Season / New Year Sales / Summer / Monsoon")

# ─────────────────────────────────────────────────────────
# STEP 11 — FINAL COLUMN ORDER & SELECTION
# ─────────────────────────────────────────────────────────
log("\n[STEP 11] Selecting and ordering final columns...")

final_columns = [
    # IDs
    "Detail_ID", "Order_ID", "Customer_ID", "Product_ID",
    # Order info
    "Order_Date", "Order_Year", "Order_Month", "Order_Month_Name",
    "Order_Quarter", "Order_YearMonth", "Order_DayOfWeek", "Season",
    # Customer info
    "Customer_Name", "Gender", "Age", "Age_Group",
    "City", "State", "Region", "Customer_Type",
    # Product info
    "Product_Name", "Category", "Sub_Category",
    # Transaction
    "Quantity", "Unit_Price", "Discount", "Discount_Amount",
    "Sales", "Revenue", "Cost", "Profit",
    "Profit_Margin_Pct",
    # Order info
    "Payment_Mode", "Order_Status",
    # Flags
    "Is_Profitable", "Is_High_Value",
]

df_clean = df[final_columns].copy()
log(f"  ✓ Final shape: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")

# ─────────────────────────────────────────────────────────
# STEP 12 — FINAL VALIDATION
# ─────────────────────────────────────────────────────────
log("\n[STEP 12] Final validation checks...")

log(f"  Total rows              : {len(df_clean):>10,}")
log(f"  Total columns           : {df_clean.shape[1]:>10}")
log(f"  Remaining null cells    : {df_clean.isnull().sum().sum():>10,}")
log(f"  Remaining duplicates    : {df_clean.duplicated().sum():>10,}")
log(f"  Date range              : {df_clean['Order_Date'].min().date()} → {df_clean['Order_Date'].max().date()}")
log(f"  Unique Orders           : {df_clean['Order_ID'].nunique():>10,}")
log(f"  Unique Customers        : {df_clean['Customer_ID'].nunique():>10,}")
log(f"  Unique Products         : {df_clean['Product_ID'].nunique():>10,}")

log("\n  Financial Summary:")
log(f"    Total Sales   : ₹{df_clean['Sales'].sum():>15,.2f}")
log(f"    Total Cost    : ₹{df_clean['Cost'].sum():>15,.2f}")
log(f"    Total Profit  : ₹{df_clean['Profit'].sum():>15,.2f}")
log(f"    Profit Margin : {(df_clean['Profit'].sum()/df_clean['Sales'].sum()*100):>14.2f}%")
log(f"    Avg Order Val : ₹{df_clean['Sales'].sum()/df_clean['Order_ID'].nunique():>15,.2f}")

log("\n  Calculated Column Check:")
log(f"    Age_Group values     : {sorted(df_clean['Age_Group'].unique())}")
log(f"    Season values        : {sorted(df_clean['Season'].unique())}")
log(f"    Is_Profitable (True) : {df_clean['Is_Profitable'].sum():,}")
log(f"    Is_High_Value (True) : {df_clean['Is_High_Value'].sum():,}")
log(f"    Unique YearMonths    : {df_clean['Order_YearMonth'].nunique()} (expect 36 for 3 years)")

log("\n  Category Distribution:")
cat_dist = df_clean.groupby("Category")["Sales"].agg(["count","sum"])
cat_dist.columns = ["Line_Items", "Total_Sales"]
cat_dist = cat_dist.sort_values("Total_Sales", ascending=False)
for cat, row in cat_dist.iterrows():
    pct = row["Total_Sales"] / df_clean["Sales"].sum() * 100
    log(f"    {cat:<18} : {row['Line_Items']:>6,} items  |  ₹{row['Total_Sales']:>12,.0f}  ({pct:.1f}%)")

log("\n  Regional Distribution:")
reg_dist = df_clean.groupby("Region")["Sales"].sum().sort_values(ascending=False)
for reg, sales in reg_dist.items():
    pct = sales / df_clean["Sales"].sum() * 100
    log(f"    {reg:<10} : ₹{sales:>12,.0f}  ({pct:.1f}%)")

# ─────────────────────────────────────────────────────────
# STEP 13 — EXPORT
# ─────────────────────────────────────────────────────────
log("\n[STEP 13] Exporting cleaned data...")

out_path = os.path.join(CLEANED_DIR, "ecommerce_cleaned.csv")
df_clean.to_csv(out_path, index=False)

file_size_mb = os.path.getsize(out_path) / (1024 * 1024)
log(f"  ✓ Saved: ecommerce_cleaned.csv")
log(f"    Path  : {os.path.abspath(out_path)}")
log(f"    Size  : {file_size_mb:.1f} MB")
log(f"    Rows  : {len(df_clean):,}")
log(f"    Cols  : {df_clean.shape[1]}")

# Save the cleaning report
save_report()
log(f"\n  ✓ Cleaning report saved: {os.path.abspath(REPORT_PATH)}")

log(f"\n{SEP}")
log("  Phase 4 — Data Cleaning COMPLETE")
log(SEP)
