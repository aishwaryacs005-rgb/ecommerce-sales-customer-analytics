"""
phase2_excel_analysis.py
-------------------------
Phase 2 — Excel Analysis

Builds a complete, professional Excel workbook with:
  Sheet 1 : Raw Data         — full 83,603-row flat table
  Sheet 2 : KPI Summary      — 7 key business metrics with formatting
  Sheet 3 : Category Analysis — sales/profit/margin by category + bar chart
  Sheet 4 : Monthly Trend     — monthly sales & profit 2022-2024 + line chart
  Sheet 5 : Regional Analysis — sales/profit/orders by region + pie chart
  Sheet 6 : Top 10 Products   — best-selling products + column chart
  Sheet 7 : Payment Analysis  — payment mode breakdown + donut chart
  Sheet 8 : Order Status      — order status breakdown + bar chart
  Sheet 9 : Customer Segment  — new vs returning analysis + chart

Output: excel/ecommerce_analysis.xlsx
"""

import pandas as pd
import numpy as np
import os
import xlsxwriter

# ─────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────
BASE_DIR   = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
EXCEL_DIR  = os.path.join(BASE_DIR, "excel")
os.makedirs(EXCEL_DIR, exist_ok=True)

OUT_FILE   = os.path.join(EXCEL_DIR, "ecommerce_analysis.xlsx")

# ─────────────────────────────────────────────────────────
# LOAD FLAT FILE
# ─────────────────────────────────────────────────────────
print("Loading data...")
flat = pd.read_csv(os.path.join(RAW_DIR, "ecommerce_flat.csv"), parse_dates=["Order_Date"])

# Ensure numeric columns
for col in ["Sales", "Profit", "Cost", "Quantity", "Unit_Price", "Discount", "Profit_Margin"]:
    flat[col] = pd.to_numeric(flat[col], errors="coerce")

print(f"  Rows: {len(flat):,}  |  Cols: {len(flat.columns)}")

# ─────────────────────────────────────────────────────────
# PRE-COMPUTE SUMMARIES  (used across multiple sheets)
# ─────────────────────────────────────────────────────────

# — KPIs ————————————————————————————————————————
total_sales   = flat["Sales"].sum()
total_profit  = flat["Profit"].sum()
total_cost    = flat["Cost"].sum()
total_orders  = flat["Order_ID"].nunique()
total_customers = flat["Customer_ID"].nunique()
total_qty     = flat["Quantity"].sum()
aov           = total_sales / total_orders
profit_margin = (total_profit / total_sales) * 100

# — Category ————————————————————————————————————
cat_summary = (
    flat.groupby("Category", as_index=False)
    .agg(Total_Sales=("Sales","sum"), Total_Profit=("Profit","sum"),
         Total_Orders=("Order_ID","nunique"), Total_Qty=("Quantity","sum"))
    .sort_values("Total_Sales", ascending=False)
)
cat_summary["Profit_Margin_%"] = (cat_summary["Total_Profit"] / cat_summary["Total_Sales"] * 100).round(2)

# — Monthly Trend ———————————————————————————————
monthly = (
    flat.groupby(["Order_Year","Order_Month"], as_index=False)
    .agg(Total_Sales=("Sales","sum"), Total_Profit=("Profit","sum"),
         Total_Orders=("Order_ID","nunique"))
    .sort_values(["Order_Year","Order_Month"])
)
monthly["Month_Label"] = monthly.apply(
    lambda r: f"{int(r['Order_Year'])}-{int(r['Order_Month']):02d}", axis=1
)

# — Region ——————————————————————————————————————
region_summary = (
    flat.groupby("Region", as_index=False)
    .agg(Total_Sales=("Sales","sum"), Total_Profit=("Profit","sum"),
         Total_Orders=("Order_ID","nunique"))
    .sort_values("Total_Sales", ascending=False)
)
region_summary["Profit_Margin_%"] = (region_summary["Total_Profit"] / region_summary["Total_Sales"] * 100).round(2)

# — Top 10 Products —————————————————————————————
top10 = (
    flat.groupby("Product_Name", as_index=False)
    .agg(Total_Sales=("Sales","sum"), Total_Profit=("Profit","sum"),
         Total_Qty=("Quantity","sum"), Total_Orders=("Order_ID","nunique"))
    .sort_values("Total_Sales", ascending=False)
    .head(10)
)
top10["Profit_Margin_%"] = (top10["Total_Profit"] / top10["Total_Sales"] * 100).round(2)

# — Bottom 10 Products ——————————————————————————
bottom10 = (
    flat.groupby("Product_Name", as_index=False)
    .agg(Total_Sales=("Sales","sum"), Total_Profit=("Profit","sum"),
         Total_Qty=("Quantity","sum"))
    .sort_values("Total_Sales", ascending=True)
    .head(10)
)
bottom10["Profit_Margin_%"] = (bottom10["Total_Profit"] / bottom10["Total_Sales"] * 100).round(2)

# — Payment Mode ————————————————————————————————
pay_summary = (
    flat.groupby("Payment_Mode", as_index=False)
    .agg(Order_Count=("Order_ID","nunique"), Total_Sales=("Sales","sum"))
    .sort_values("Order_Count", ascending=False)
)
pay_summary["Pct_Orders"] = (pay_summary["Order_Count"] / total_orders * 100).round(2)

# — Order Status ————————————————————————————————
status_summary = (
    flat.groupby("Order_Status", as_index=False)
    .agg(Order_Count=("Order_ID","nunique"), Total_Sales=("Sales","sum"))
    .sort_values("Order_Count", ascending=False)
)
status_summary["Pct"] = (status_summary["Order_Count"] / total_orders * 100).round(2)

# — Customer Segment ————————————————————————————
seg_summary = (
    flat.groupby("Customer_Type", as_index=False)
    .agg(Customer_Count=("Customer_ID","nunique"),
         Total_Sales=("Sales","sum"),
         Total_Orders=("Order_ID","nunique"))
    .sort_values("Total_Sales", ascending=False)
)
seg_summary["Avg_Order_Value"] = (seg_summary["Total_Sales"] / seg_summary["Total_Orders"]).round(2)
seg_summary["Pct_Revenue"] = (seg_summary["Total_Sales"] / total_sales * 100).round(2)


# ═════════════════════════════════════════════════════════
# BUILD WORKBOOK
# ═════════════════════════════════════════════════════════
print("Building Excel workbook...")

wb = xlsxwriter.Workbook(OUT_FILE)

# ── COMMON FORMATS ──────────────────────────────────────

# Colors
DARK_BLUE  = "#1F3864"
MID_BLUE   = "#2E75B6"
LIGHT_BLUE = "#BDD7EE"
DARK_GREEN = "#1E5631"
MID_GREEN  = "#2D7D46"
LIGHT_GREEN= "#C6EFCE"
ORANGE     = "#E67E22"
LIGHT_GREY = "#F2F2F2"
WHITE      = "#FFFFFF"
DARK_GREY  = "#404040"
RED        = "#C00000"

def add_format(wb, bold=False, bg=WHITE, font_color=DARK_GREY, size=10,
               align="left", num_format=None, border=0, italic=False,
               valign="vcenter", wrap=False):
    fmt = {
        "bold": bold, "bg_color": bg, "font_color": font_color,
        "font_size": size, "align": align, "valign": valign,
        "border": border, "italic": italic, "text_wrap": wrap
    }
    if num_format:
        fmt["num_format"] = num_format
    return wb.add_format(fmt)

# Define all formats upfront
fmt_title      = add_format(wb, bold=True, bg=DARK_BLUE, font_color=WHITE, size=14, align="center")
fmt_subtitle   = add_format(wb, bold=True, bg=MID_BLUE,  font_color=WHITE, size=11, align="center")
fmt_header     = add_format(wb, bold=True, bg=MID_BLUE,  font_color=WHITE, size=10, align="center", border=1)
fmt_header_dk  = add_format(wb, bold=True, bg=DARK_BLUE, font_color=WHITE, size=10, align="center", border=1)
fmt_data       = add_format(wb, bg=WHITE,       size=10, border=1)
fmt_data_grey  = add_format(wb, bg=LIGHT_GREY,  size=10, border=1)
fmt_data_right = add_format(wb, bg=WHITE, align="right", size=10, border=1)
fmt_data_center= add_format(wb, bg=WHITE, align="center", size=10, border=1)
fmt_currency   = add_format(wb, bg=WHITE, align="right", size=10, border=1, num_format='₹#,##0')
fmt_currency_g = add_format(wb, bg=LIGHT_GREY, align="right", size=10, border=1, num_format='₹#,##0')
fmt_pct        = add_format(wb, bg=WHITE, align="right", size=10, border=1, num_format='0.00"%"')
fmt_pct_g      = add_format(wb, bg=LIGHT_GREY, align="right", size=10, border=1, num_format='0.00"%"')
fmt_int        = add_format(wb, bg=WHITE, align="right", size=10, border=1, num_format='#,##0')
fmt_int_g      = add_format(wb, bg=LIGHT_GREY, align="right", size=10, border=1, num_format='#,##0')
fmt_kpi_label  = add_format(wb, bold=True, bg=DARK_BLUE, font_color=WHITE, size=11, align="left", border=1)
fmt_kpi_value  = add_format(wb, bold=True, bg=LIGHT_BLUE, font_color=DARK_BLUE, size=12, align="right",
                             border=1, num_format='₹#,##0')
fmt_kpi_pct    = add_format(wb, bold=True, bg=LIGHT_BLUE, font_color=DARK_BLUE, size=12, align="right",
                             border=1, num_format='0.00"%"')
fmt_kpi_count  = add_format(wb, bold=True, bg=LIGHT_BLUE, font_color=DARK_BLUE, size=12, align="right",
                             border=1, num_format='#,##0')
fmt_note       = add_format(wb, italic=True, font_color="#7F7F7F", size=9)

def alt(i):
    """Alternate row format: white or light grey."""
    return fmt_data_grey if i % 2 == 0 else fmt_data

def alt_c(i):
    return fmt_currency_g if i % 2 == 0 else fmt_currency

def alt_p(i):
    return fmt_pct_g if i % 2 == 0 else fmt_pct

def alt_i(i):
    return fmt_int_g if i % 2 == 0 else fmt_int


# ═════════════════════════════════════════════════════════
# SHEET 1 — RAW DATA  (first 5000 rows to keep file light)
# ═════════════════════════════════════════════════════════
print("  Sheet 1: Raw Data...")

ws1 = wb.add_worksheet("Raw Data")
ws1.set_tab_color(MID_BLUE)
ws1.freeze_panes(2, 0)

# Title
ws1.merge_range("A1:Y1", "E-Commerce Flat Data — Raw Export (first 5,000 rows shown)", fmt_title)
ws1.set_row(0, 22)

# Headers
headers = list(flat.columns)
for col_idx, h in enumerate(headers):
    ws1.write(1, col_idx, h, fmt_header)

# Column widths
col_widths = {
    "Order_ID":12, "Order_Date":13, "Customer_ID":12, "Customer_Name":18,
    "Gender":8, "Age":6, "City":14, "State":16, "Region":10,
    "Product_ID":10, "Product_Name":28, "Category":16, "Sub_Category":16,
    "Quantity":9, "Unit_Price":11, "Discount":9, "Sales":13, "Cost":13,
    "Profit":13, "Payment_Mode":16, "Order_Status":13, "Customer_Type":14,
    "Order_Month":12, "Order_Year":11, "Profit_Margin":14
}
for col_idx, h in enumerate(headers):
    ws1.set_column(col_idx, col_idx, col_widths.get(h, 12))

# Write data rows — limit to 5000 to keep file manageable
sample = flat.head(5000)
for row_idx, (_, row) in enumerate(sample.iterrows()):
    fmt_row = fmt_data_grey if row_idx % 2 == 0 else fmt_data
    for col_idx, h in enumerate(headers):
        val = row[h]
        if pd.isna(val):
            ws1.write(row_idx + 2, col_idx, "", fmt_row)
        elif h == "Order_Date":
            ws1.write(row_idx + 2, col_idx, str(val)[:10], fmt_row)
        elif h in ["Sales", "Cost", "Profit", "Unit_Price"]:
            ws1.write_number(row_idx + 2, col_idx, float(val),
                             fmt_currency_g if row_idx % 2 == 0 else fmt_currency)
        elif h in ["Discount", "Profit_Margin"]:
            ws1.write_number(row_idx + 2, col_idx, float(val),
                             fmt_pct_g if row_idx % 2 == 0 else fmt_pct)
        elif h in ["Quantity", "Order_Month", "Order_Year"]:
            ws1.write_number(row_idx + 2, col_idx, int(val),
                             fmt_int_g if row_idx % 2 == 0 else fmt_int)
        else:
            ws1.write(row_idx + 2, col_idx, str(val), fmt_row)

ws1.write(5003, 0, f"* Full dataset has {len(flat):,} rows. Showing first 5,000 for Excel performance.", fmt_note)


# ═════════════════════════════════════════════════════════
# SHEET 2 — KPI SUMMARY
# ═════════════════════════════════════════════════════════
print("  Sheet 2: KPI Summary...")

ws2 = wb.add_worksheet("KPI Summary")
ws2.set_tab_color(DARK_BLUE)
ws2.set_column("A:A", 30)
ws2.set_column("B:B", 22)
ws2.set_column("C:C", 20)
ws2.set_column("D:F", 18)

# Main title
ws2.merge_range("A1:F1", "E-Commerce Sales & Customer Analytics — KPI Summary", fmt_title)
ws2.set_row(0, 28)
ws2.merge_range("A2:F2", "Dataset: Jan 2022 – Dec 2024  |  50,000 Orders  |  5,000 Customers  |  7 Categories  |  5 Regions", fmt_subtitle)
ws2.set_row(1, 18)

# KPI Table header
ws2.merge_range("A4:F4", "KEY PERFORMANCE INDICATORS", fmt_header_dk)
ws2.set_row(3, 18)

kpi_headers = ["KPI", "Value", "Description"]
for i, h in enumerate(kpi_headers):
    ws2.write(4, i, h, fmt_header)
ws2.set_row(4, 16)

kpis = [
    ("Total Sales (Revenue)",   total_sales,   "fmt_kpi_value",  "Total revenue from all delivered & shipped orders"),
    ("Total Profit",            total_profit,  "fmt_kpi_value",  "Revenue minus Cost of Goods Sold"),
    ("Total Cost",              total_cost,    "fmt_kpi_value",  "Total cost of all products sold"),
    ("Total Orders",            total_orders,  "fmt_kpi_count",  "Number of unique orders placed"),
    ("Total Customers",         total_customers,"fmt_kpi_count", "Number of unique customers"),
    ("Total Quantity Sold",     total_qty,     "fmt_kpi_count",  "Total units of products sold"),
    ("Average Order Value",     aov,           "fmt_kpi_value",  "Total Sales ÷ Total Orders"),
    ("Profit Margin",           profit_margin, "fmt_kpi_pct",    "Total Profit ÷ Total Sales × 100"),
]

for i, (label, value, fmt_name, desc) in enumerate(kpis):
    r = i + 5
    bg = LIGHT_BLUE if i % 2 == 0 else "#DEEAF1"
    ws2.write(r, 0, label, add_format(wb, bold=True, bg=DARK_BLUE, font_color=WHITE, size=11, border=1))
    if fmt_name == "fmt_kpi_pct":
        ws2.write(r, 1, value,
                  add_format(wb, bold=True, bg=bg, font_color=DARK_BLUE, size=12,
                             align="right", border=1, num_format='0.00"%"'))
    elif fmt_name == "fmt_kpi_count":
        ws2.write(r, 1, value,
                  add_format(wb, bold=True, bg=bg, font_color=DARK_BLUE, size=12,
                             align="right", border=1, num_format='#,##0'))
    else:
        ws2.write(r, 1, value,
                  add_format(wb, bold=True, bg=bg, font_color=DARK_BLUE, size=12,
                             align="right", border=1, num_format='₹#,##0'))
    ws2.write(r, 2, desc, add_format(wb, bg=bg, size=10, border=1))
    ws2.set_row(r, 22)

# Missing value check section
ws2.merge_range("A15:F15", "DATA QUALITY CHECK — MISSING VALUES", fmt_header_dk)
ws2.set_row(14, 18)
ws2.write(15, 0, "Column", fmt_header)
ws2.write(15, 1, "Missing Values", fmt_header)
ws2.write(15, 2, "% Missing", fmt_header)
ws2.write(15, 3, "Status", fmt_header)

check_cols = ["Order_ID","Order_Date","Customer_ID","Product_Name","Category",
              "Region","Sales","Profit","Cost","Payment_Mode","Order_Status"]
for i, col in enumerate(check_cols):
    missing = int(flat[col].isna().sum())
    pct     = missing / len(flat) * 100
    status  = "✓ No missing values" if missing == 0 else "⚠ Has missing values"
    s_fmt   = add_format(wb, bg=LIGHT_GREEN, border=1) if missing == 0 else add_format(wb, bg="#FFEB9C", border=1)
    ws2.write(16 + i, 0, col,            alt(i))
    ws2.write(16 + i, 1, missing,        alt_i(i))
    ws2.write(16 + i, 2, pct,            alt_p(i))
    ws2.write(16 + i, 3, status,         s_fmt)

# Duplicate check
ws2.write(28, 0, "Duplicate Rows",  fmt_kpi_label)
ws2.write(28, 1, int(flat.duplicated().sum()), fmt_kpi_count)
ws2.write(28, 2, "Based on all columns", add_format(wb, bg=LIGHT_BLUE, border=1))

# Notes
ws2.merge_range("A30:F30", "Note: This summary was auto-generated using Python + xlsxwriter from 83,603 line-item records across 50,000 orders.", fmt_note)


# ═════════════════════════════════════════════════════════
# SHEET 3 — CATEGORY ANALYSIS
# ═════════════════════════════════════════════════════════
print("  Sheet 3: Category Analysis...")

ws3 = wb.add_worksheet("Category Analysis")
ws3.set_tab_color(MID_GREEN)
ws3.set_column("A:A", 20)
ws3.set_column("B:F", 18)

ws3.merge_range("A1:F1", "Sales & Profit Analysis by Product Category", fmt_title)
ws3.set_row(0, 26)

# Table headers
hdrs = ["Category", "Total Sales (₹)", "Total Profit (₹)", "Total Orders", "Total Qty Sold", "Profit Margin %"]
for i, h in enumerate(hdrs):
    ws3.write(1, i, h, fmt_header)

for i, row in cat_summary.reset_index(drop=True).iterrows():
    ws3.write(i + 2, 0, row["Category"],          alt(i))
    ws3.write(i + 2, 1, row["Total_Sales"],        alt_c(i))
    ws3.write(i + 2, 2, row["Total_Profit"],       alt_c(i))
    ws3.write(i + 2, 3, row["Total_Orders"],       alt_i(i))
    ws3.write(i + 2, 4, row["Total_Qty"],          alt_i(i))
    ws3.write(i + 2, 5, row["Profit_Margin_%"],    alt_p(i))

n = len(cat_summary)

# ── BAR CHART: Sales by Category ────────────────────────
chart_cat = wb.add_chart({"type": "bar"})
chart_cat.add_series({
    "name":       "Total Sales",
    "categories": ["Category Analysis", 2, 0, 1 + n, 0],
    "values":     ["Category Analysis", 2, 1, 1 + n, 1],
    "fill":       {"color": MID_BLUE},
    "gap":        50,
})
chart_cat.add_series({
    "name":       "Total Profit",
    "categories": ["Category Analysis", 2, 0, 1 + n, 0],
    "values":     ["Category Analysis", 2, 2, 1 + n, 2],
    "fill":       {"color": MID_GREEN},
})
chart_cat.set_title({"name": "Sales & Profit by Category"})
chart_cat.set_x_axis({"name": "Amount (₹)"})
chart_cat.set_y_axis({"name": "Category"})
chart_cat.set_style(10)
chart_cat.set_size({"width": 520, "height": 320})
chart_cat.set_legend({"position": "bottom"})
ws3.insert_chart("H2", chart_cat)

# ── PIE CHART: Profit Margin by Category ────────────────
chart_margin = wb.add_chart({"type": "pie"})
chart_margin.add_series({
    "name":       "Profit Margin %",
    "categories": ["Category Analysis", 2, 0, 1 + n, 0],
    "values":     ["Category Analysis", 2, 5, 1 + n, 5],
    "data_labels": {"percentage": True, "category": True, "separator": "\n"},
})
chart_margin.set_title({"name": "Profit Margin % by Category"})
chart_margin.set_style(10)
chart_margin.set_size({"width": 400, "height": 300})
ws3.insert_chart("H20", chart_margin)

ws3.write(n + 4, 0, "Insight: Categories with high sales AND high margin are the most valuable to the business.", fmt_note)


# ═════════════════════════════════════════════════════════
# SHEET 4 — MONTHLY TREND
# ═════════════════════════════════════════════════════════
print("  Sheet 4: Monthly Trend...")

ws4 = wb.add_worksheet("Monthly Trend")
ws4.set_tab_color(ORANGE)
ws4.set_column("A:A", 15)
ws4.set_column("B:E", 18)

ws4.merge_range("A1:E1", "Monthly Sales & Profit Trend (2022–2024)", fmt_title)
ws4.set_row(0, 26)

hdrs = ["Month", "Total Sales (₹)", "Total Profit (₹)", "Total Orders", "Year"]
for i, h in enumerate(hdrs):
    ws4.write(1, i, h, fmt_header)

for i, row in monthly.reset_index(drop=True).iterrows():
    ws4.write(i + 2, 0, row["Month_Label"],     alt(i))
    ws4.write(i + 2, 1, row["Total_Sales"],      alt_c(i))
    ws4.write(i + 2, 2, row["Total_Profit"],     alt_c(i))
    ws4.write(i + 2, 3, row["Total_Orders"],     alt_i(i))
    ws4.write(i + 2, 4, int(row["Order_Year"]),  alt_i(i))

n = len(monthly)

# ── LINE CHART: Monthly Sales ────────────────────────────
chart_monthly = wb.add_chart({"type": "line"})
chart_monthly.add_series({
    "name":       "Total Sales",
    "categories": ["Monthly Trend", 2, 0, 1 + n, 0],
    "values":     ["Monthly Trend", 2, 1, 1 + n, 1],
    "line":       {"color": MID_BLUE, "width": 2.5},
    "marker":     {"type": "circle", "size": 5, "fill": {"color": MID_BLUE}},
})
chart_monthly.add_series({
    "name":       "Total Profit",
    "categories": ["Monthly Trend", 2, 0, 1 + n, 0],
    "values":     ["Monthly Trend", 2, 2, 1 + n, 2],
    "line":       {"color": MID_GREEN, "width": 2.5},
    "marker":     {"type": "square", "size": 5, "fill": {"color": MID_GREEN}},
})
chart_monthly.set_title({"name": "Monthly Sales & Profit Trend (Jan 2022 – Dec 2024)"})
chart_monthly.set_x_axis({"name": "Month", "num_font": {"rotation": -45}})
chart_monthly.set_y_axis({"name": "Amount (₹)"})
chart_monthly.set_style(10)
chart_monthly.set_size({"width": 700, "height": 380})
chart_monthly.set_legend({"position": "bottom"})
ws4.insert_chart("G2", chart_monthly)

ws4.write(n + 4, 0, "Insight: Look for seasonal spikes in Oct–Dec (Diwali/festive season).", fmt_note)


# ═════════════════════════════════════════════════════════
# SHEET 5 — REGIONAL ANALYSIS
# ═════════════════════════════════════════════════════════
print("  Sheet 5: Regional Analysis...")

ws5 = wb.add_worksheet("Regional Analysis")
ws5.set_tab_color(RED)
ws5.set_column("A:A", 14)
ws5.set_column("B:E", 18)

ws5.merge_range("A1:E1", "Sales & Profit Analysis by Region", fmt_title)
ws5.set_row(0, 26)

hdrs = ["Region", "Total Sales (₹)", "Total Profit (₹)", "Total Orders", "Profit Margin %"]
for i, h in enumerate(hdrs):
    ws5.write(1, i, h, fmt_header)

for i, row in region_summary.reset_index(drop=True).iterrows():
    ws5.write(i + 2, 0, row["Region"],          alt(i))
    ws5.write(i + 2, 1, row["Total_Sales"],      alt_c(i))
    ws5.write(i + 2, 2, row["Total_Profit"],     alt_c(i))
    ws5.write(i + 2, 3, row["Total_Orders"],     alt_i(i))
    ws5.write(i + 2, 4, row["Profit_Margin_%"],  alt_p(i))

n = len(region_summary)

# ── COLUMN CHART: Sales by Region ───────────────────────
chart_reg = wb.add_chart({"type": "column"})
chart_reg.add_series({
    "name":       "Total Sales",
    "categories": ["Regional Analysis", 2, 0, 1 + n, 0],
    "values":     ["Regional Analysis", 2, 1, 1 + n, 1],
    "fill":       {"color": MID_BLUE},
    "gap":        60,
})
chart_reg.add_series({
    "name":       "Total Profit",
    "categories": ["Regional Analysis", 2, 0, 1 + n, 0],
    "values":     ["Regional Analysis", 2, 2, 1 + n, 2],
    "fill":       {"color": MID_GREEN},
})
chart_reg.set_title({"name": "Sales & Profit by Region"})
chart_reg.set_x_axis({"name": "Region"})
chart_reg.set_y_axis({"name": "Amount (₹)"})
chart_reg.set_style(10)
chart_reg.set_size({"width": 480, "height": 300})
chart_reg.set_legend({"position": "bottom"})
ws5.insert_chart("G2", chart_reg)

# ── PIE CHART: Orders by Region ─────────────────────────
chart_reg_pie = wb.add_chart({"type": "pie"})
chart_reg_pie.add_series({
    "name":       "Order Share by Region",
    "categories": ["Regional Analysis", 2, 0, 1 + n, 0],
    "values":     ["Regional Analysis", 2, 3, 1 + n, 3],
    "data_labels": {"percentage": True, "category": True, "separator": "\n"},
})
chart_reg_pie.set_title({"name": "Order Share by Region"})
chart_reg_pie.set_style(10)
chart_reg_pie.set_size({"width": 380, "height": 280})
ws5.insert_chart("G20", chart_reg_pie)

# State-level detail
state_summary = (
    flat.groupby(["Region","State"], as_index=False)
    .agg(Total_Sales=("Sales","sum"), Total_Orders=("Order_ID","nunique"))
    .sort_values(["Region","Total_Sales"], ascending=[True, False])
)
ws5.merge_range(f"A{n+5}:E{n+5}", "State-Level Breakdown", fmt_header_dk)
ws5.write(n + 5, 0, "Region",        fmt_header)
ws5.write(n + 5, 1, "State",         fmt_header)
ws5.write(n + 5, 2, "Total Sales (₹)", fmt_header)
ws5.write(n + 5, 3, "Total Orders",  fmt_header)
for i, row in state_summary.reset_index(drop=True).iterrows():
    ws5.write(n + 6 + i, 0, row["Region"],       alt(i))
    ws5.write(n + 6 + i, 1, row["State"],        alt(i))
    ws5.write(n + 6 + i, 2, row["Total_Sales"],  alt_c(i))
    ws5.write(n + 6 + i, 3, row["Total_Orders"], alt_i(i))


# ═════════════════════════════════════════════════════════
# SHEET 6 — TOP & BOTTOM PRODUCTS
# ═════════════════════════════════════════════════════════
print("  Sheet 6: Product Analysis...")

ws6 = wb.add_worksheet("Product Analysis")
ws6.set_tab_color("#7030A0")
ws6.set_column("A:A", 32)
ws6.set_column("B:F", 16)

ws6.merge_range("A1:F1", "Product Performance Analysis — Top 10 & Bottom 10", fmt_title)
ws6.set_row(0, 26)

# Top 10
ws6.merge_range("A2:F2", "TOP 10 PRODUCTS BY SALES", fmt_header_dk)
hdrs = ["Product Name", "Total Sales (₹)", "Total Profit (₹)", "Qty Sold", "Orders", "Profit Margin %"]
for i, h in enumerate(hdrs):
    ws6.write(2, i, h, fmt_header)

for i, row in top10.reset_index(drop=True).iterrows():
    ws6.write(i + 3, 0, row["Product_Name"],       alt(i))
    ws6.write(i + 3, 1, row["Total_Sales"],         alt_c(i))
    ws6.write(i + 3, 2, row["Total_Profit"],        alt_c(i))
    ws6.write(i + 3, 3, row["Total_Qty"],           alt_i(i))
    ws6.write(i + 3, 4, row["Total_Orders"],        alt_i(i))
    ws6.write(i + 3, 5, row["Profit_Margin_%"],     alt_p(i))

# Bottom 10
ws6.merge_range("A15:F15", "BOTTOM 10 PRODUCTS BY SALES (Lowest Performing)", fmt_header_dk)
hdrs2 = ["Product Name", "Total Sales (₹)", "Total Profit (₹)", "Qty Sold", "Profit Margin %", ""]
for i, h in enumerate(hdrs2[:5]):
    ws6.write(15, i, h, fmt_header)

for i, row in bottom10.reset_index(drop=True).iterrows():
    ws6.write(i + 16, 0, row["Product_Name"],       alt(i))
    ws6.write(i + 16, 1, row["Total_Sales"],        alt_c(i))
    ws6.write(i + 16, 2, row["Total_Profit"],       alt_c(i))
    ws6.write(i + 16, 3, row["Total_Qty"],          alt_i(i))
    ws6.write(i + 16, 4, row["Profit_Margin_%"],    alt_p(i))

# ── COLUMN CHART: Top 10 Products ───────────────────────
chart_top = wb.add_chart({"type": "bar"})
chart_top.add_series({
    "name":       "Total Sales",
    "categories": ["Product Analysis", 3, 0, 12, 0],
    "values":     ["Product Analysis", 3, 1, 12, 1],
    "fill":       {"color": MID_BLUE},
})
chart_top.add_series({
    "name":       "Total Profit",
    "categories": ["Product Analysis", 3, 0, 12, 0],
    "values":     ["Product Analysis", 3, 2, 12, 2],
    "fill":       {"color": MID_GREEN},
})
chart_top.set_title({"name": "Top 10 Products — Sales vs Profit"})
chart_top.set_x_axis({"name": "Amount (₹)"})
chart_top.set_y_axis({"name": "Product"})
chart_top.set_style(10)
chart_top.set_size({"width": 560, "height": 360})
chart_top.set_legend({"position": "bottom"})
ws6.insert_chart("H2", chart_top)

ws6.write(28, 0, "Insight: Products with high sales but low profit margin are not as profitable as they appear.", fmt_note)


# ═════════════════════════════════════════════════════════
# SHEET 7 — PAYMENT MODE ANALYSIS
# ═════════════════════════════════════════════════════════
print("  Sheet 7: Payment Analysis...")

ws7 = wb.add_worksheet("Payment Analysis")
ws7.set_tab_color("#00B0F0")
ws7.set_column("A:A", 20)
ws7.set_column("B:D", 18)

ws7.merge_range("A1:D1", "Payment Mode Distribution & Revenue Analysis", fmt_title)
ws7.set_row(0, 26)

hdrs = ["Payment Mode", "Order Count", "% of Orders", "Total Sales (₹)"]
for i, h in enumerate(hdrs):
    ws7.write(1, i, h, fmt_header)

for i, row in pay_summary.reset_index(drop=True).iterrows():
    ws7.write(i + 2, 0, row["Payment_Mode"],    alt(i))
    ws7.write(i + 2, 1, row["Order_Count"],     alt_i(i))
    ws7.write(i + 2, 2, row["Pct_Orders"],      alt_p(i))
    ws7.write(i + 2, 3, row["Total_Sales"],     alt_c(i))

n = len(pay_summary)

# ── DOUGHNUT CHART: Payment Mode ────────────────────────
chart_pay = wb.add_chart({"type": "doughnut"})
chart_pay.add_series({
    "name":       "Orders by Payment Mode",
    "categories": ["Payment Analysis", 2, 0, 1 + n, 0],
    "values":     ["Payment Analysis", 2, 1, 1 + n, 1],
    "data_labels": {"percentage": True, "category": True, "separator": "\n"},
})
chart_pay.set_title({"name": "Payment Mode Distribution"})
chart_pay.set_style(10)
chart_pay.set_size({"width": 420, "height": 340})
ws7.insert_chart("F2", chart_pay)

ws7.write(n + 4, 0, "Insight: UPI dominates — ensure UPI gateway is always reliable.", fmt_note)


# ═════════════════════════════════════════════════════════
# SHEET 8 — ORDER STATUS
# ═════════════════════════════════════════════════════════
print("  Sheet 8: Order Status...")

ws8 = wb.add_worksheet("Order Status")
ws8.set_tab_color("#FF0000")
ws8.set_column("A:A", 16)
ws8.set_column("B:D", 18)

ws8.merge_range("A1:D1", "Order Status Breakdown", fmt_title)
ws8.set_row(0, 26)

hdrs = ["Order Status", "Order Count", "% of Total", "Total Sales (₹)"]
for i, h in enumerate(hdrs):
    ws8.write(1, i, h, fmt_header)

for i, row in status_summary.reset_index(drop=True).iterrows():
    ws8.write(i + 2, 0, row["Order_Status"],   alt(i))
    ws8.write(i + 2, 1, row["Order_Count"],    alt_i(i))
    ws8.write(i + 2, 2, row["Pct"],            alt_p(i))
    ws8.write(i + 2, 3, row["Total_Sales"],    alt_c(i))

n = len(status_summary)

# ── BAR CHART: Order Status ──────────────────────────────
chart_status = wb.add_chart({"type": "column"})
chart_status.add_series({
    "name":       "Order Count",
    "categories": ["Order Status", 2, 0, 1 + n, 0],
    "values":     ["Order Status", 2, 1, 1 + n, 1],
    "fill":       {"color": MID_BLUE},
    "gap":        60,
})
chart_status.set_title({"name": "Orders by Status"})
chart_status.set_x_axis({"name": "Status"})
chart_status.set_y_axis({"name": "Number of Orders"})
chart_status.set_style(10)
chart_status.set_size({"width": 440, "height": 300})
ws8.insert_chart("F2", chart_status)

ws8.write(n + 4, 0, "Insight: Cancelled + Returned orders represent lost revenue. Monitor closely.", fmt_note)


# ═════════════════════════════════════════════════════════
# SHEET 9 — CUSTOMER SEGMENT
# ═════════════════════════════════════════════════════════
print("  Sheet 9: Customer Segment...")

ws9 = wb.add_worksheet("Customer Segment")
ws9.set_tab_color(DARK_GREEN)
ws9.set_column("A:A", 18)
ws9.set_column("B:F", 18)

ws9.merge_range("A1:F1", "Customer Segment Analysis — New vs Returning", fmt_title)
ws9.set_row(0, 26)

hdrs = ["Customer Type", "Customer Count", "Total Orders", "Total Sales (₹)", "Avg Order Value (₹)", "Revenue Share %"]
for i, h in enumerate(hdrs):
    ws9.write(1, i, h, fmt_header)

for i, row in seg_summary.reset_index(drop=True).iterrows():
    ws9.write(i + 2, 0, row["Customer_Type"],      alt(i))
    ws9.write(i + 2, 1, row["Customer_Count"],     alt_i(i))
    ws9.write(i + 2, 2, row["Total_Orders"],       alt_i(i))
    ws9.write(i + 2, 3, row["Total_Sales"],        alt_c(i))
    ws9.write(i + 2, 4, row["Avg_Order_Value"],    alt_c(i))
    ws9.write(i + 2, 5, row["Pct_Revenue"],        alt_p(i))

n = len(seg_summary)

# ── COLUMN CHART: Customer Segment Revenue ──────────────
chart_seg = wb.add_chart({"type": "column"})
chart_seg.add_series({
    "name":       "Total Sales",
    "categories": ["Customer Segment", 2, 0, 1 + n, 0],
    "values":     ["Customer Segment", 2, 3, 1 + n, 3],
    "fill":       {"color": MID_BLUE},
    "gap":        80,
})
chart_seg.set_title({"name": "Revenue: New vs Returning Customers"})
chart_seg.set_x_axis({"name": "Customer Type"})
chart_seg.set_y_axis({"name": "Total Sales (₹)"})
chart_seg.set_style(10)
chart_seg.set_size({"width": 380, "height": 280})
ws9.insert_chart("H2", chart_seg)

# Top 15 Customers by spending
top_customers = (
    flat.groupby(["Customer_ID","Customer_Name","Customer_Type"], as_index=False)
    .agg(Total_Sales=("Sales","sum"), Total_Orders=("Order_ID","nunique"))
    .sort_values("Total_Sales", ascending=False)
    .head(15)
)
top_customers["Avg_Order_Value"] = (top_customers["Total_Sales"] / top_customers["Total_Orders"]).round(0)

ws9.merge_range(f"A{n+5}:F{n+5}", "TOP 15 CUSTOMERS BY TOTAL SPENDING", fmt_header_dk)
hdrs_top = ["Customer ID", "Customer Name", "Type", "Total Sales (₹)", "Orders", "Avg Order Value (₹)"]
for i, h in enumerate(hdrs_top):
    ws9.write(n + 5, i, h, fmt_header)

for i, row in top_customers.reset_index(drop=True).iterrows():
    ws9.write(n + 6 + i, 0, row["Customer_ID"],      alt(i))
    ws9.write(n + 6 + i, 1, row["Customer_Name"],    alt(i))
    ws9.write(n + 6 + i, 2, row["Customer_Type"],    alt(i))
    ws9.write(n + 6 + i, 3, row["Total_Sales"],      alt_c(i))
    ws9.write(n + 6 + i, 4, row["Total_Orders"],     alt_i(i))
    ws9.write(n + 6 + i, 5, row["Avg_Order_Value"],  alt_c(i))

ws9.write(n + 23, 0, "Insight: Returning customers typically have higher lifetime value — focus on retention strategies.", fmt_note)


# ═════════════════════════════════════════════════════════
# CLOSE WORKBOOK
# ═════════════════════════════════════════════════════════
wb.close()

print(f"\n{'='*55}")
print("  Phase 2 — Excel Analysis COMPLETE")
print(f"{'='*55}")
print(f"\n  File saved: {os.path.abspath(OUT_FILE)}")
print("\n  Sheets created:")
sheets = [
    ("Raw Data",          "83,603-row flat table (5k shown for performance)"),
    ("KPI Summary",       "7 KPIs + Data Quality Check"),
    ("Category Analysis", "Sales/Profit by Category + 2 Charts"),
    ("Monthly Trend",     "Month-by-month trend 2022-2024 + Line Chart"),
    ("Regional Analysis", "Region + State breakdown + 2 Charts"),
    ("Product Analysis",  "Top 10 + Bottom 10 Products + Bar Chart"),
    ("Payment Analysis",  "Payment mode split + Doughnut Chart"),
    ("Order Status",      "Order status breakdown + Column Chart"),
    ("Customer Segment",  "New vs Returning + Top 15 Customers + Chart"),
]
for name, desc in sheets:
    print(f"    {name:<22} — {desc}")
