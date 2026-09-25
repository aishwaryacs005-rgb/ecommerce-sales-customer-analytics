"""
phase5_eda.py
--------------
Phase 5 — Exploratory Data Analysis (EDA)

CHARTS PRODUCED (saved to screenshots/):
  01_monthly_sales_trend.png        — Line: Monthly Sales + Profit 2022-2024
  02_yearly_comparison.png          — Bar: Year-over-year Sales comparison
  03_category_sales.png             — Horizontal Bar: Sales by Category
  04_category_profit_margin.png     — Bar: Profit Margin % by Category
  05_top10_products.png             — Horizontal Bar: Top 10 Products by Sales
  06_bottom10_products.png          — Horizontal Bar: Bottom 10 Products
  07_regional_sales.png             — Bar: Sales by Region
  08_regional_heatmap.png           — Heatmap: Category vs Region Sales
  09_payment_mode.png               — Pie: Payment Mode Distribution
  10_order_status.png               — Bar: Order Status Breakdown
  11_age_group_sales.png            — Bar: Sales by Age Group
  12_customer_type_revenue.png      — Grouped bar: New vs Returning Revenue
  13_sales_vs_profit_scatter.png    — Scatter: Sales vs Profit by Category
  14_seasonal_trend.png             — Bar: Sales by Season
  15_day_of_week.png                — Bar: Orders by Day of Week

Run:  python python/phase5_eda.py
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — saves files without opening windows
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────
BASE_DIR    = os.path.join(os.path.dirname(__file__), "..")
CLEAN_FILE  = os.path.join(BASE_DIR, "data", "cleaned", "ecommerce_cleaned.csv")
SAVE_DIR    = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SAVE_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────
# GLOBAL STYLE
# ─────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "figure.dpi":       150,
    "figure.facecolor": "#FAFAFA",
    "axes.facecolor":   "#FAFAFA",
    "axes.edgecolor":   "#CCCCCC",
    "axes.labelsize":   11,
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
    "legend.fontsize":  9,
    "font.family":      "DejaVu Sans",
})

# Brand colors
BLUE    = "#2E75B6"
GREEN   = "#2D7D46"
ORANGE  = "#E67E22"
RED     = "#C0392B"
PURPLE  = "#7D3C98"
TEAL    = "#1A7F7A"
GREY    = "#7F8C8D"
PALETTE = [BLUE, GREEN, ORANGE, RED, PURPLE, TEAL, GREY, "#F39C12", "#1ABC9C", "#E74C3C"]

def inr(value):
    """Format large numbers as ₹ crores or lakhs."""
    if value >= 1e7:
        return f"₹{value/1e7:.1f}Cr"
    elif value >= 1e5:
        return f"₹{value/1e5:.1f}L"
    return f"₹{value:,.0f}"

def save(fig, filename):
    path = os.path.join(SAVE_DIR, filename)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓ Saved: {filename}")

# ─────────────────────────────────────────────────────────
# LOAD CLEANED DATA
# ─────────────────────────────────────────────────────────
print("=" * 60)
print("  Phase 5 — Exploratory Data Analysis")
print("=" * 60)
print("\nLoading cleaned data...")

df = pd.read_csv(CLEAN_FILE, parse_dates=["Order_Date"])
df["Order_YearMonth"] = df["Order_Date"].dt.to_period("M")
print(f"  {len(df):,} rows × {df.shape[1]} columns loaded\n")

# ─────────────────────────────────────────────────────────
# PRE-COMPUTE AGGREGATIONS
# ─────────────────────────────────────────────────────────

# Monthly
monthly = (
    df.groupby("Order_YearMonth", as_index=False)
    .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","nunique"))
    .sort_values("Order_YearMonth")
)
monthly["Month_Label"] = monthly["Order_YearMonth"].astype(str)

# Yearly
yearly = (
    df.groupby("Order_Year", as_index=False)
    .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","nunique"))
)

# Category
cat = (
    df.groupby("Category", as_index=False)
    .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","nunique"))
    .sort_values("Sales", ascending=False)
)
cat["Margin"] = (cat["Profit"] / cat["Sales"] * 100).round(1)

# Top / Bottom products
prod = (
    df.groupby("Product_Name", as_index=False)
    .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
)
top10  = prod.nlargest(10,  "Sales").reset_index(drop=True)
bot10  = prod.nsmallest(10, "Sales").reset_index(drop=True)

# Region
region = (
    df.groupby("Region", as_index=False)
    .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","nunique"))
    .sort_values("Sales", ascending=False)
)

# Category × Region heatmap
cat_reg = (
    df.groupby(["Category","Region"])["Sales"]
    .sum()
    .unstack(fill_value=0)
    / 1e7     # in crores
)

# Payment mode
pay = (
    df.groupby("Payment_Mode")["Order_ID"]
    .nunique()
    .reset_index()
    .rename(columns={"Order_ID":"Count"})
    .sort_values("Count", ascending=False)
)

# Order status
status = (
    df.groupby("Order_Status")["Order_ID"]
    .nunique()
    .reset_index()
    .rename(columns={"Order_ID":"Count"})
    .sort_values("Count", ascending=False)
)

# Age group
age_grp = (
    df.groupby("Age_Group", as_index=False)
    .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"))
    .sort_values("Age_Group")
)
age_order = ["18–25","26–35","36–45","46–55","56+"]
age_grp["Age_Group"] = pd.Categorical(age_grp["Age_Group"], categories=age_order, ordered=True)
age_grp = age_grp.sort_values("Age_Group")

# Customer type
ctype = (
    df.groupby("Customer_Type", as_index=False)
    .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"),
         Customers=("Customer_ID","nunique"))
)

# Season
season = (
    df.groupby("Season", as_index=False)
    .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"))
    .sort_values("Sales", ascending=False)
)

# Day of week
dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow = (
    df.groupby("Order_DayOfWeek")["Order_ID"]
    .nunique()
    .reset_index()
    .rename(columns={"Order_ID":"Count"})
)
dow["Order_DayOfWeek"] = pd.Categorical(dow["Order_DayOfWeek"], categories=dow_order, ordered=True)
dow = dow.sort_values("Order_DayOfWeek")

print("Generating charts...\n")

# ═════════════════════════════════════════════════════════
# CHART 1 — Monthly Sales & Profit Trend
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: How revenue and profit move month-by-month over 3 years.
# WHY USEFUL:    Reveals seasonality, growth trends, and impact of campaigns.
# INSIGHT HINT:  Spikes in Oct-Dec = festive season demand.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 5))

x = range(len(monthly))
ax.fill_between(x, monthly["Sales"]/1e7, alpha=0.15, color=BLUE)
ax.plot(x, monthly["Sales"]/1e7, color=BLUE, linewidth=2.5, label="Sales", marker="o", markersize=3)
ax.fill_between(x, monthly["Profit"]/1e7, alpha=0.15, color=GREEN)
ax.plot(x, monthly["Profit"]/1e7, color=GREEN, linewidth=2, label="Profit", marker="s", markersize=3)

# Year separators
for yr_start in ["2023-01", "2024-01"]:
    idx = monthly[monthly["Month_Label"] == yr_start].index
    if len(idx):
        pos = monthly["Month_Label"].tolist().index(yr_start)
        ax.axvline(pos, color=GREY, linestyle="--", linewidth=1, alpha=0.6)

# X-axis labels — show every 3rd month to avoid crowding
tick_positions = list(range(0, len(monthly), 3))
tick_labels    = [monthly["Month_Label"].iloc[i] for i in tick_positions]
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, rotation=30, ha="right", fontsize=8)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
ax.set_title("Monthly Sales & Profit Trend (Jan 2022 – Dec 2024)")
ax.set_xlabel("Month")
ax.set_ylabel("Amount (₹ Crores)")
ax.legend()
ax.text(0.99, 0.97, "Festive spikes visible Oct–Dec each year",
        transform=ax.transAxes, ha="right", va="top", fontsize=8, color=GREY, style="italic")
fig.tight_layout()
save(fig, "01_monthly_sales_trend.png")

# ═════════════════════════════════════════════════════════
# CHART 2 — Year-over-Year Comparison
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: How sales and profit changed year over year.
# WHY USEFUL:    Tells if business is growing, flat, or declining.
# ═════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(11, 5))

# Sales bars
bars = axes[0].bar(yearly["Order_Year"].astype(str), yearly["Sales"]/1e7,
                   color=[BLUE, GREEN, ORANGE], width=0.5, edgecolor="white", linewidth=0.8)
axes[0].set_title("Year-over-Year Sales")
axes[0].set_ylabel("Total Sales (₹ Crores)")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
for bar, val in zip(bars, yearly["Sales"]):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 inr(val), ha="center", va="bottom", fontsize=9, fontweight="bold")

# Profit bars
bars2 = axes[1].bar(yearly["Order_Year"].astype(str), yearly["Profit"]/1e7,
                    color=[BLUE, GREEN, ORANGE], width=0.5, edgecolor="white", linewidth=0.8)
axes[1].set_title("Year-over-Year Profit")
axes[1].set_ylabel("Total Profit (₹ Crores)")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
for bar, val in zip(bars2, yearly["Profit"]):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                 inr(val), ha="center", va="bottom", fontsize=9, fontweight="bold")

fig.suptitle("Year-over-Year Performance", fontsize=14, fontweight="bold")
fig.tight_layout()
save(fig, "02_yearly_comparison.png")

# ═════════════════════════════════════════════════════════
# CHART 3 — Sales by Category
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Which product category drives the most revenue.
# WHY USEFUL:    Helps prioritise inventory, marketing budget allocation.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))

colors = [BLUE if i == 0 else GREY for i in range(len(cat))]
bars = ax.barh(cat["Category"], cat["Sales"]/1e7, color=colors, edgecolor="white", height=0.6)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
ax.set_title("Total Sales by Product Category")
ax.set_xlabel("Total Sales (₹ Crores)")
ax.invert_yaxis()

for bar, val in zip(bars, cat["Sales"]):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
            inr(val), va="center", fontsize=9)

ax.text(0.99, 0.02, "Electronics dominates at ~79% of total revenue",
        transform=ax.transAxes, ha="right", fontsize=8, color=GREY, style="italic")
fig.tight_layout()
save(fig, "03_category_sales.png")

# ═════════════════════════════════════════════════════════
# CHART 4 — Profit Margin % by Category
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: How profitable each category is (not just revenue).
# WHY USEFUL:    A category can have high sales but thin margins.
# ═════════════════════════════════════════════════════════
cat_sorted = cat.sort_values("Margin", ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))

colors = [GREEN if m >= 45 else ORANGE if m >= 35 else RED for m in cat_sorted["Margin"]]
bars = ax.bar(cat_sorted["Category"], cat_sorted["Margin"], color=colors, width=0.5, edgecolor="white")
ax.axhline(cat_sorted["Margin"].mean(), color=GREY, linestyle="--", linewidth=1.2,
           label=f"Avg Margin: {cat_sorted['Margin'].mean():.1f}%")
ax.set_title("Profit Margin % by Category")
ax.set_ylabel("Profit Margin (%)")
ax.set_ylim(0, 65)

for bar, val in zip(bars, cat_sorted["Margin"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f"{val:.1f}%", ha="center", fontsize=9, fontweight="bold")

ax.legend()
plt.xticks(rotation=15, ha="right")
fig.tight_layout()
save(fig, "04_category_profit_margin.png")

# ═════════════════════════════════════════════════════════
# CHART 5 — Top 10 Products by Sales
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Your best-performing individual products.
# WHY USEFUL:    Informs stocking priorities and promotional focus.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))

top10_sorted = top10.sort_values("Sales")
colors = [BLUE]*8 + [GREEN]*2  # highlight top 2

bars = ax.barh(top10_sorted["Product_Name"], top10_sorted["Sales"]/1e5,
               color=BLUE, edgecolor="white", height=0.7)
ax.set_title("Top 10 Products by Total Sales")
ax.set_xlabel("Total Sales (₹ Lakhs)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}L"))

for bar, val in zip(bars, top10_sorted["Sales"]):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
            inr(val), va="center", fontsize=8)

fig.tight_layout()
save(fig, "05_top10_products.png")

# ═════════════════════════════════════════════════════════
# CHART 6 — Bottom 10 Products
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Lowest-performing products by revenue.
# WHY USEFUL:    Highlights products to discontinue or re-promote.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))

bot10_sorted = bot10.sort_values("Sales", ascending=False)
ax.barh(bot10_sorted["Product_Name"], bot10_sorted["Sales"]/1e5,
        color=RED, edgecolor="white", height=0.7, alpha=0.85)
ax.set_title("Bottom 10 Products by Total Sales (Lowest Performers)")
ax.set_xlabel("Total Sales (₹ Lakhs)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.1f}L"))

for i, (_, row) in enumerate(bot10_sorted.iterrows()):
    ax.text(row["Sales"]/1e5 + 0.02, i, inr(row["Sales"]), va="center", fontsize=8)

fig.tight_layout()
save(fig, "06_bottom10_products.png")

# ═════════════════════════════════════════════════════════
# CHART 7 — Regional Sales & Profit
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Which geographic region generates most revenue.
# WHY USEFUL:    Guides logistics investment and regional campaigns.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))

x = np.arange(len(region))
w = 0.38
b1 = ax.bar(x - w/2, region["Sales"]/1e7, width=w, label="Sales",
            color=BLUE, edgecolor="white")
b2 = ax.bar(x + w/2, region["Profit"]/1e7, width=w, label="Profit",
            color=GREEN, edgecolor="white")

ax.set_xticks(x)
ax.set_xticklabels(region["Region"])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
ax.set_title("Sales & Profit by Region")
ax.set_ylabel("Amount (₹ Crores)")
ax.legend()

for bar in b1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f"₹{bar.get_height():.0f}Cr", ha="center", fontsize=7.5)
for bar in b2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f"₹{bar.get_height():.0f}Cr", ha="center", fontsize=7.5)

fig.tight_layout()
save(fig, "07_regional_sales.png")

# ═════════════════════════════════════════════════════════
# CHART 8 — Category vs Region Heatmap
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Which categories sell best in which regions.
# WHY USEFUL:    Reveals regional product preferences for targeting.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))

sns.heatmap(cat_reg, annot=True, fmt=".1f", cmap="Blues",
            linewidths=0.5, linecolor="#EEEEEE",
            cbar_kws={"label": "Sales (₹ Crores)"}, ax=ax)
ax.set_title("Sales by Category × Region (₹ Crores)")
ax.set_xlabel("Region")
ax.set_ylabel("Category")
plt.xticks(rotation=0)
plt.yticks(rotation=0)
fig.tight_layout()
save(fig, "08_regional_heatmap.png")

# ═════════════════════════════════════════════════════════
# CHART 9 — Payment Mode Distribution
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: How customers prefer to pay.
# WHY USEFUL:    Guides checkout UX improvements and payment offers.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 6))

wedge_colors = [BLUE, GREEN, ORANGE, TEAL, PURPLE, RED]
explode = [0.05 if i == 0 else 0 for i in range(len(pay))]
wedges, texts, autotexts = ax.pie(
    pay["Count"], labels=pay["Payment_Mode"],
    autopct="%1.1f%%", colors=wedge_colors[:len(pay)],
    explode=explode, startangle=90,
    wedgeprops={"edgecolor": "white", "linewidth": 1.5}
)
for t in autotexts:
    t.set_fontsize(9)
    t.set_color("white")
    t.set_fontweight("bold")
ax.set_title("Payment Mode Distribution")
fig.tight_layout()
save(fig, "09_payment_mode.png")

# ═════════════════════════════════════════════════════════
# CHART 10 — Order Status Breakdown
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: How many orders are Delivered, Cancelled, Returned, etc.
# WHY USEFUL:    High cancellation/return rates signal operational issues.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

status_colors = {
    "Delivered":  GREEN,
    "Shipped":    BLUE,
    "Cancelled":  RED,
    "Returned":   ORANGE,
    "Processing": TEAL
}
colors_list = [status_colors.get(s, GREY) for s in status["Order_Status"]]
bars = ax.bar(status["Order_Status"], status["Count"], color=colors_list,
              width=0.5, edgecolor="white")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_title("Orders by Status")
ax.set_ylabel("Number of Orders")

for bar in bars:
    pct = bar.get_height() / status["Count"].sum() * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
            f"{bar.get_height():,.0f}\n({pct:.1f}%)", ha="center", fontsize=9)

ax.text(0.99, 0.97, "Cancelled + Returned = ~15% of orders",
        transform=ax.transAxes, ha="right", va="top", fontsize=8, color=RED, style="italic")
fig.tight_layout()
save(fig, "10_order_status.png")

# ═════════════════════════════════════════════════════════
# CHART 11 — Sales by Age Group
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Which customer age group drives the most revenue.
# WHY USEFUL:    Informs targeting strategy and product selection.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

bars = ax.bar(age_grp["Age_Group"].astype(str), age_grp["Sales"]/1e7,
              color=PALETTE[:5], width=0.5, edgecolor="white")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
ax.set_title("Total Sales by Customer Age Group")
ax.set_xlabel("Age Group")
ax.set_ylabel("Total Sales (₹ Crores)")

for bar, val in zip(bars, age_grp["Sales"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            inr(val), ha="center", fontsize=9, fontweight="bold")

fig.tight_layout()
save(fig, "11_age_group_sales.png")

# ═════════════════════════════════════════════════════════
# CHART 12 — New vs Returning Customer Revenue
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: How much revenue comes from new vs returning customers.
# WHY USEFUL:    Returning customers are cheaper to retain than acquiring new ones.
# ═════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(11, 5))

# Revenue comparison
bars1 = axes[0].bar(ctype["Customer_Type"], ctype["Sales"]/1e7,
                    color=[BLUE, GREEN], width=0.45, edgecolor="white")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
axes[0].set_title("Revenue: New vs Returning")
axes[0].set_ylabel("Total Sales (₹ Crores)")
for bar, val in zip(bars1, ctype["Sales"]):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 inr(val), ha="center", fontsize=10, fontweight="bold")

# Order count
bars2 = axes[1].bar(ctype["Customer_Type"], ctype["Orders"],
                    color=[BLUE, GREEN], width=0.45, edgecolor="white")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
axes[1].set_title("Orders: New vs Returning")
axes[1].set_ylabel("Total Orders")
for bar, val in zip(bars2, ctype["Orders"]):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                 f"{val:,}", ha="center", fontsize=10, fontweight="bold")

fig.suptitle("New vs Returning Customer Comparison", fontsize=13, fontweight="bold")
fig.tight_layout()
save(fig, "12_customer_type_revenue.png")

# ═════════════════════════════════════════════════════════
# CHART 13 — Sales vs Profit Scatter by Category
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Relationship between sales volume and profit at product level.
# WHY USEFUL:    Products with high sales but low profit are a warning sign.
# ═════════════════════════════════════════════════════════
prod_cat = (
    df.groupby(["Product_Name","Category"], as_index=False)
    .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Qty=("Quantity","sum"))
)
fig, ax = plt.subplots(figsize=(11, 7))

cat_palette = {c: PALETTE[i] for i, c in enumerate(prod_cat["Category"].unique())}
for cat_name, grp in prod_cat.groupby("Category"):
    ax.scatter(grp["Sales"]/1e5, grp["Profit"]/1e5,
               label=cat_name, color=cat_palette[cat_name],
               alpha=0.75, s=grp["Qty"]/5, edgecolors="white", linewidth=0.5)

ax.axhline(0, color=RED, linestyle="--", linewidth=1, alpha=0.5)
ax.set_title("Sales vs Profit by Product (bubble size = quantity sold)")
ax.set_xlabel("Total Sales (₹ Lakhs)")
ax.set_ylabel("Total Profit (₹ Lakhs)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}L"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}L"))
ax.legend(loc="upper left", framealpha=0.9)
fig.tight_layout()
save(fig, "13_sales_vs_profit_scatter.png")

# ═════════════════════════════════════════════════════════
# CHART 14 — Sales by Season
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Which season generates the most revenue.
# WHY USEFUL:    Helps plan inventory build-up before peak seasons.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

season_colors = {"Festive Season": ORANGE, "New Year Sales": BLUE,
                 "Summer": RED, "Monsoon": TEAL}
colors_s = [season_colors.get(s, GREY) for s in season["Season"]]
bars = ax.bar(season["Season"], season["Sales"]/1e7, color=colors_s,
              width=0.5, edgecolor="white")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
ax.set_title("Total Sales by Season")
ax.set_ylabel("Total Sales (₹ Crores)")

for bar, val in zip(bars, season["Sales"]):
    pct = val / season["Sales"].sum() * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{inr(val)}\n({pct:.1f}%)", ha="center", fontsize=9, fontweight="bold")

fig.tight_layout()
save(fig, "14_seasonal_trend.png")

# ═════════════════════════════════════════════════════════
# CHART 15 — Orders by Day of Week
# ─────────────────────────────────────────────────────────
# WHAT IT SHOWS: Which days of the week get the most orders.
# WHY USEFUL:    Schedule marketing pushes on high-traffic days.
# ═════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))

dow_colors = [ORANGE if d in ["Saturday","Sunday"] else BLUE for d in dow["Order_DayOfWeek"]]
bars = ax.bar(dow["Order_DayOfWeek"].astype(str), dow["Count"],
              color=dow_colors, width=0.55, edgecolor="white")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_title("Number of Orders by Day of Week")
ax.set_ylabel("Number of Orders")

for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
            f"{int(bar.get_height()):,}", ha="center", fontsize=8)

ax.text(0.99, 0.97, "Orange = Weekend", transform=ax.transAxes,
        ha="right", va="top", fontsize=8, color=ORANGE, style="italic")
fig.tight_layout()
save(fig, "15_day_of_week.png")


# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Phase 5 — EDA COMPLETE")
print(f"{'='*60}")
print(f"\n  15 charts saved to: {os.path.abspath(SAVE_DIR)}")
print("\n  Chart Index:")
chart_index = [
    ("01_monthly_sales_trend.png",    "Monthly Sales & Profit Trend"),
    ("02_yearly_comparison.png",      "Year-over-Year Sales & Profit"),
    ("03_category_sales.png",         "Sales by Category"),
    ("04_category_profit_margin.png", "Profit Margin % by Category"),
    ("05_top10_products.png",         "Top 10 Products"),
    ("06_bottom10_products.png",      "Bottom 10 Products"),
    ("07_regional_sales.png",         "Sales & Profit by Region"),
    ("08_regional_heatmap.png",       "Category × Region Heatmap"),
    ("09_payment_mode.png",           "Payment Mode Distribution"),
    ("10_order_status.png",           "Order Status Breakdown"),
    ("11_age_group_sales.png",        "Sales by Age Group"),
    ("12_customer_type_revenue.png",  "New vs Returning Customer Revenue"),
    ("13_sales_vs_profit_scatter.png","Sales vs Profit Scatter"),
    ("14_seasonal_trend.png",         "Sales by Season"),
    ("15_day_of_week.png",            "Orders by Day of Week"),
]
for fname, desc in chart_index:
    print(f"    {fname:<40}  {desc}")
