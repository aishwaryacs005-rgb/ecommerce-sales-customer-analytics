"""
phase1_data_understanding.py
-----------------------------
Phase 1 — Data Understanding

This script inspects all 5 raw CSV files and prints a complete
summary so we understand the data BEFORE touching it.

A real Data Analyst always does this first.
"""

import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────
# Load all 5 tables
# ─────────────────────────────────────────
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

regions_df       = pd.read_csv(os.path.join(RAW_DIR, "regions.csv"))
products_df      = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
customers_df     = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
orders_df        = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"), parse_dates=["Order_Date"])
order_details_df = pd.read_csv(os.path.join(RAW_DIR, "order_details.csv"))

tables = {
    "regions":       regions_df,
    "products":      products_df,
    "customers":     customers_df,
    "orders":        orders_df,
    "order_details": order_details_df,
}

SEPARATOR = "=" * 65


# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────

def section(title):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def inspect_table(name, df):
    """Prints shape, dtypes, missing values, and duplicates for one table."""
    section(f"TABLE: {name.upper()}")

    print(f"\n  Rows    : {len(df):,}")
    print(f"  Columns : {len(df.columns)}")
    print(f"\n  Columns & Data Types:")
    for col in df.columns:
        dtype    = str(df[col].dtype)
        missing  = df[col].isna().sum()
        pct      = round(missing / len(df) * 100, 2)
        print(f"    {col:<25}  dtype={dtype:<12}  missing={missing} ({pct}%)")

    dupes = df.duplicated().sum()
    print(f"\n  Duplicate rows : {dupes}")


# ─────────────────────────────────────────
# 1. INSPECT EVERY TABLE
# ─────────────────────────────────────────
for table_name, df in tables.items():
    inspect_table(table_name, df)


# ─────────────────────────────────────────
# 2. KEY STATISTICS
# ─────────────────────────────────────────
section("KEY STATISTICS")

# Orders date range
print(f"\n  Date Range       : {orders_df['Order_Date'].min().date()} → {orders_df['Order_Date'].max().date()}")
print(f"  Total Orders     : {len(orders_df):,}")
print(f"  Unique Customers : {orders_df['Customer_ID'].nunique():,}")
print(f"  Unique Products  : {order_details_df['Product_ID'].nunique():,}")
print(f"  Total Line Items : {len(order_details_df):,}")

# Financial summary (from order_details)
total_sales  = order_details_df["Sales"].sum()
total_cost   = order_details_df["Cost"].sum()
total_profit = order_details_df["Profit"].sum()
total_qty    = order_details_df["Quantity"].sum()
aov          = total_sales / len(orders_df)    # Average Order Value
margin_pct   = (total_profit / total_sales) * 100

print(f"\n  Total Sales      : ₹{total_sales:>15,.2f}")
print(f"  Total Cost       : ₹{total_cost:>15,.2f}")
print(f"  Total Profit     : ₹{total_profit:>15,.2f}")
print(f"  Total Quantity   : {total_qty:>16,}")
print(f"  Avg Order Value  : ₹{aov:>15,.2f}")
print(f"  Profit Margin    : {margin_pct:>15.2f}%")


# ─────────────────────────────────────────
# 3. CATEGORIES
# ─────────────────────────────────────────
section("PRODUCT CATEGORIES")

cat_counts = products_df.groupby("Category")["Product_ID"].count().reset_index()
cat_counts.columns = ["Category", "Product Count"]
print(f"\n{cat_counts.to_string(index=False)}")

sub_counts = products_df.groupby(["Category", "Sub_Category"])["Product_ID"].count().reset_index()
sub_counts.columns = ["Category", "Sub_Category", "Products"]
print(f"\n  Sub-categories:\n{sub_counts.to_string(index=False)}")


# ─────────────────────────────────────────
# 4. REGIONS
# ─────────────────────────────────────────
section("REGIONS")

# Merge orders → customers → region to count orders per region
orders_with_customer = orders_df.merge(customers_df[["Customer_ID", "Region", "State", "City"]], on="Customer_ID")
region_order_counts  = orders_with_customer.groupby("Region")["Order_ID"].count().reset_index()
region_order_counts.columns = ["Region", "Order Count"]
print(f"\n{region_order_counts.to_string(index=False)}")

print(f"\n  States  : {customers_df['State'].nunique()}")
print(f"  Cities  : {customers_df['City'].nunique()}")


# ─────────────────────────────────────────
# 5. ORDER STATUSES
# ─────────────────────────────────────────
section("ORDER STATUSES")

status_counts = orders_df["Order_Status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]
status_counts["Percentage"] = (status_counts["Count"] / len(orders_df) * 100).round(2)
print(f"\n{status_counts.to_string(index=False)}")


# ─────────────────────────────────────────
# 6. PAYMENT METHODS
# ─────────────────────────────────────────
section("PAYMENT METHODS")

pay_counts = orders_df["Payment_Mode"].value_counts().reset_index()
pay_counts.columns = ["Payment_Mode", "Count"]
pay_counts["Percentage"] = (pay_counts["Count"] / len(orders_df) * 100).round(2)
print(f"\n{pay_counts.to_string(index=False)}")


# ─────────────────────────────────────────
# 7. CUSTOMER DEMOGRAPHICS
# ─────────────────────────────────────────
section("CUSTOMER DEMOGRAPHICS")

gender_counts = customers_df["Gender"].value_counts()
type_counts   = customers_df["Customer_Type"].value_counts()
age_stats     = customers_df["Age"].describe()

print(f"\n  Gender Distribution:")
for g, c in gender_counts.items():
    print(f"    {g:<10}: {c:,} ({c/len(customers_df)*100:.1f}%)")

print(f"\n  Customer Type:")
for t, c in type_counts.items():
    print(f"    {t:<12}: {c:,} ({c/len(customers_df)*100:.1f}%)")

print(f"\n  Age Statistics:")
print(f"    Min    : {int(age_stats['min'])}")
print(f"    Max    : {int(age_stats['max'])}")
print(f"    Mean   : {age_stats['mean']:.1f}")
print(f"    Median : {age_stats['50%']:.1f}")


# ─────────────────────────────────────────
# 8. YEARLY ORDER TREND
# ─────────────────────────────────────────
section("YEARLY ORDER TREND")

orders_df["Year"] = orders_df["Order_Date"].dt.year
yearly = orders_df.groupby("Year")["Order_ID"].count().reset_index()
yearly.columns = ["Year", "Orders"]
print(f"\n{yearly.to_string(index=False)}")


# ─────────────────────────────────────────
# 9. NUMERIC COLUMN RANGES (order_details)
# ─────────────────────────────────────────
section("NUMERIC RANGES — ORDER DETAILS")

for col in ["Quantity", "Unit_Price", "Discount", "Sales", "Cost", "Profit"]:
    mn  = order_details_df[col].min()
    mx  = order_details_df[col].max()
    avg = order_details_df[col].mean()
    print(f"  {col:<12}  min={mn:>10,.2f}  max={mx:>12,.2f}  avg={avg:>10,.2f}")


print(f"\n\n{'='*65}")
print("  Phase 1 — Data Understanding COMPLETE")
print(f"{'='*65}\n")
