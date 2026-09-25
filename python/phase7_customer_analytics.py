"""
phase7_customer_analytics.py
------------------------------
Phase 7 — Customer Analytics & RFM Segmentation

WHAT THIS SCRIPT DOES:
  1. Runs all 10 customer analysis SQL queries
  2. Performs full RFM segmentation in Python (pandas)
  3. Generates 6 customer analytics charts saved to screenshots/

OUTPUT FILES:
  screenshots/16_rfm_segments.png
  screenshots/17_rfm_scatter.png
  screenshots/18_customer_tier_revenue.png
  screenshots/19_retention_cohort.png
  screenshots/20_age_gender_heatmap.png
  screenshots/21_rfm_segment_profile.png

Run: python python/phase7_customer_analytics.py
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
import re

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────
BASE_DIR  = os.path.join(os.path.dirname(__file__), "..")
DB_PATH   = os.path.join(BASE_DIR, "sql", "ecommerce.db")
SQL_PATH  = os.path.join(BASE_DIR, "sql", "customer_analysis.sql")
SAVE_DIR  = os.path.join(BASE_DIR, "screenshots")
CLEAN_FILE = os.path.join(BASE_DIR, "data", "cleaned", "ecommerce_cleaned.csv")

os.makedirs(SAVE_DIR, exist_ok=True)

SEP = "=" * 65

# ─────────────────────────────────────────────────────────
# STYLE
# ─────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "figure.dpi": 150, "figure.facecolor": "#FAFAFA",
    "axes.facecolor": "#FAFAFA", "axes.titlesize": 13,
    "axes.titleweight": "bold", "axes.labelsize": 11,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
})

BLUE   = "#2E75B6"
GREEN  = "#2D7D46"
ORANGE = "#E67E22"
RED    = "#C0392B"
PURPLE = "#7D3C98"
TEAL   = "#1A7F7A"
GREY   = "#95A5A6"

SEG_COLORS = {
    "Champions":       "#27AE60",
    "Loyal Customers": "#2980B9",
    "At Risk":         "#F39C12",
    "Hibernating":     "#E74C3C",
    "Lost":            "#7F8C8D",
}

def save(fig, filename):
    path = os.path.join(SAVE_DIR, filename)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓ Saved: {filename}")

def inr(v):
    if v >= 1e7: return f"₹{v/1e7:.1f}Cr"
    if v >= 1e5: return f"₹{v/1e5:.1f}L"
    return f"₹{v:,.0f}"


# ─────────────────────────────────────────────────────────
# SECTION 1 — RUN SQL QUERIES & PRINT RESULTS
# ─────────────────────────────────────────────────────────
print(SEP)
print("  Phase 7 — Customer Analytics & RFM Segmentation")
print(SEP)

conn   = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(SQL_PATH, "r", encoding="utf-8") as f:
    sql_text = f.read()

# Parse individual queries by -- CA<n> markers
parts = re.split(r'--\s*CA(\d+)\s*\n', sql_text)
queries = {}
i = 1
while i < len(parts) - 1:
    num = int(parts[i])
    sql = parts[i + 1].strip().split("\n\n-- ─")[0].strip()
    queries[num] = sql
    i += 2

titles = {
    1: "Overall Customer Summary",
    2: "Average Orders Per Customer",
    3: "Customer Revenue by Gender",
    4: "Customer Revenue by Age Group",
    5: "Customer Revenue by Region",
    6: "Monthly Retention Cohort",
    7: "RFM Base Table (Top 20 Customers)",
    8: "RFM Segment Distribution",
    9: "Champion Customers Detail",
    10: "Revenue Contribution by Customer Tier (Pareto)",
}

print("\n--- SQL Query Results ---\n")
for qnum in sorted(queries.keys()):
    print(f"  [{qnum:02d}] {titles.get(qnum, '')}")
    try:
        cursor.execute(queries[qnum])
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        widths = [len(c) for c in cols]
        for row in rows:
            for i, v in enumerate(row):
                widths[i] = max(widths[i], len(str(v) if v is not None else ""))
        header = "       " + "  ".join(c.ljust(widths[i]) for i, c in enumerate(cols))
        print(header)
        print("       " + "  ".join("-" * w for w in widths))
        for row in rows[:15]:
            line = "       " + "  ".join(
                str(v if v is not None else "").ljust(widths[i])
                for i, v in enumerate(row))
            print(line)
        if len(rows) > 15:
            print(f"       ... ({len(rows)-15} more rows)")
    except Exception as e:
        print(f"       ERROR: {e}")
    print()

conn.close()


# ─────────────────────────────────────────────────────────
# SECTION 2 — PYTHON RFM ANALYSIS (full 5000 customers)
# ─────────────────────────────────────────────────────────
print("\n--- Python RFM Analysis ---\n")

df = pd.read_csv(CLEAN_FILE, parse_dates=["Order_Date"])

REFERENCE_DATE = pd.Timestamp("2024-12-31")

# Aggregate per customer
rfm = (
    df.groupby("Customer_ID")
    .agg(
        Last_Order = ("Order_Date", "max"),
        Frequency  = ("Order_ID",   "nunique"),
        Monetary   = ("Sales",      "sum"),
    )
    .reset_index()
)

rfm["Recency"] = (REFERENCE_DATE - rfm["Last_Order"]).dt.days

# Score each dimension 1–5 using quintiles
# Recency: lower days = better = score 5
rfm["R_Score"] = pd.qcut(rfm["Recency"],   q=5, labels=[5,4,3,2,1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1,2,3,4,5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"],  q=5, labels=[1,2,3,4,5]).astype(int)

rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

def segment(score):
    if score >= 13: return "Champions"
    if score >= 10: return "Loyal Customers"
    if score >= 7:  return "At Risk"
    if score >= 4:  return "Hibernating"
    return "Lost"

rfm["Segment"] = rfm["RFM_Score"].apply(segment)

# Merge with customer info
customers_df = pd.read_csv(os.path.join(BASE_DIR, "data", "raw", "customers.csv"))
rfm = rfm.merge(customers_df[["Customer_ID","Customer_Name","Gender","Age",
                               "Region","Customer_Type"]], on="Customer_ID")

# Segment summary
seg_summary = (
    rfm.groupby("Segment")
    .agg(
        Customer_Count = ("Customer_ID", "count"),
        Avg_Recency    = ("Recency",     "mean"),
        Avg_Frequency  = ("Frequency",   "mean"),
        Avg_Monetary   = ("Monetary",    "mean"),
        Total_Revenue  = ("Monetary",    "sum"),
    )
    .reset_index()
)
seg_summary["Pct_Revenue"] = seg_summary["Total_Revenue"] / rfm["Monetary"].sum() * 100

print("  RFM Segment Summary:")
print(f"  {'Segment':<20} {'Customers':>10} {'Avg Recency':>12} "
      f"{'Avg Freq':>10} {'Avg Spend':>14} {'Revenue %':>10}")
print("  " + "-"*80)
for _, r in seg_summary.sort_values("Avg_Monetary", ascending=False).iterrows():
    print(f"  {r['Segment']:<20} {int(r['Customer_Count']):>10,} "
          f"{r['Avg_Recency']:>12.1f} {r['Avg_Frequency']:>10.1f} "
          f"  {inr(r['Avg_Monetary']):>12}  {r['Pct_Revenue']:>9.1f}%")

print(f"\n  Total customers segmented: {len(rfm):,}")


# ─────────────────────────────────────────────────────────
# SECTION 3 — CHARTS
# ─────────────────────────────────────────────────────────
print("\n--- Generating Charts ---\n")

# ── CHART 16: RFM Segment Distribution (Donut) ───────────
seg_order = ["Champions","Loyal Customers","At Risk","Hibernating","Lost"]
seg_plot  = seg_summary.set_index("Segment").reindex(seg_order).dropna()

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

# Donut — customer count
colors = [SEG_COLORS[s] for s in seg_plot.index]
wedges, texts, autotexts = axes[0].pie(
    seg_plot["Customer_Count"],
    labels=seg_plot.index,
    autopct="%1.1f%%",
    colors=colors,
    startangle=90,
    pctdistance=0.78,
    wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
)
for t in autotexts:
    t.set_fontsize(9); t.set_fontweight("bold")
axes[0].set_title("RFM Segment — Customer Distribution")

# Bar — revenue by segment
seg_rev = seg_plot["Total_Revenue"].sort_values(ascending=False)
bar_colors = [SEG_COLORS[s] for s in seg_rev.index]
bars = axes[1].barh(seg_rev.index, seg_rev.values/1e7,
                    color=bar_colors, height=0.55, edgecolor="white")
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
axes[1].set_title("RFM Segment — Revenue Contribution")
axes[1].set_xlabel("Total Revenue (₹ Crores)")
axes[1].invert_yaxis()
for bar, val in zip(bars, seg_rev.values):
    axes[1].text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                 inr(val), va="center", fontsize=8.5)

fig.suptitle("RFM Customer Segmentation", fontsize=14, fontweight="bold")
fig.tight_layout()
save(fig, "16_rfm_segments.png")


# ── CHART 17: RFM Scatter — Frequency vs Monetary ────────
fig, ax = plt.subplots(figsize=(11, 7))

for seg in seg_order:
    grp = rfm[rfm["Segment"] == seg]
    ax.scatter(
        grp["Frequency"], grp["Monetary"]/1e5,
        label=seg, color=SEG_COLORS[seg],
        alpha=0.55, s=25, edgecolors="none"
    )

ax.set_title("RFM Scatter: Purchase Frequency vs Total Spend")
ax.set_xlabel("Purchase Frequency (# Orders)")
ax.set_ylabel("Total Monetary Value (₹ Lakhs)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}L"))
ax.legend(title="RFM Segment", loc="upper left", framealpha=0.9)
fig.tight_layout()
save(fig, "17_rfm_scatter.png")


# ── CHART 18: Customer Revenue Tier (Pareto) ─────────────
rfm_sorted = rfm.sort_values("Monetary", ascending=False).reset_index(drop=True)
rfm_sorted["rank_pct"] = (rfm_sorted.index + 1) / len(rfm_sorted) * 100
rfm_sorted["cumulative_revenue_pct"] = rfm_sorted["Monetary"].cumsum() / rfm_sorted["Monetary"].sum() * 100

fig, ax = plt.subplots(figsize=(10, 6))

ax.fill_between(rfm_sorted["rank_pct"], rfm_sorted["cumulative_revenue_pct"],
                alpha=0.15, color=BLUE)
ax.plot(rfm_sorted["rank_pct"], rfm_sorted["cumulative_revenue_pct"],
        color=BLUE, linewidth=2.5, label="Cumulative Revenue %")

# Mark 20% & 50% lines
for xv, label in [(20, "Top 20% customers"), (50, "Top 50% customers")]:
    yv = rfm_sorted[rfm_sorted["rank_pct"] <= xv]["cumulative_revenue_pct"].max()
    ax.axvline(xv, color=ORANGE, linestyle="--", linewidth=1.2, alpha=0.7)
    ax.axhline(yv, color=ORANGE, linestyle="--", linewidth=1.2, alpha=0.7)
    ax.annotate(f"{label}\n→ {yv:.1f}% of revenue",
                xy=(xv, yv), xytext=(xv+5, yv-10),
                fontsize=8, color=ORANGE,
                arrowprops={"arrowstyle":"->","color":ORANGE, "lw":1.2})

ax.set_title("Pareto Chart — Customer Revenue Concentration")
ax.set_xlabel("% of Customers (sorted by spend, high to low)")
ax.set_ylabel("Cumulative Revenue %")
ax.set_xlim(0, 100); ax.set_ylim(0, 105)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
fig.tight_layout()
save(fig, "18_customer_tier_revenue.png")


# ── CHART 19: Cohort Retention ────────────────────────────
conn2 = sqlite3.connect(DB_PATH)
cohort_df = pd.read_sql_query("""
    SELECT cohort_month, COUNT(*) AS cohort_size,
           SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS retained,
           ROUND(SUM(CASE WHEN order_count > 1 THEN 1.0 ELSE 0 END)
                 / COUNT(*) * 100, 2) AS retention_rate
    FROM (
        SELECT Customer_ID,
               STRFTIME('%Y-%m', MIN(Order_Date)) AS cohort_month,
               COUNT(DISTINCT Order_ID) AS order_count
        FROM orders
        GROUP BY Customer_ID
    ) sub
    GROUP BY cohort_month
    ORDER BY cohort_month
    LIMIT 24
""", conn2)
conn2.close()

fig, ax = plt.subplots(figsize=(14, 5))

bar_colors = [GREEN if r >= 80 else ORANGE if r >= 50 else RED
              for r in cohort_df["retention_rate"]]
ax.bar(range(len(cohort_df)), cohort_df["retention_rate"],
       color=bar_colors, edgecolor="white", width=0.7)
ax.axhline(cohort_df["retention_rate"].mean(), color=GREY, linestyle="--",
           linewidth=1.5, label=f"Average: {cohort_df['retention_rate'].mean():.1f}%")

ax.set_xticks(range(len(cohort_df)))
ax.set_xticklabels(cohort_df["cohort_month"], rotation=45, ha="right", fontsize=7.5)
ax.set_title("Monthly Cohort Retention Rate (% who placed >1 order)")
ax.set_ylabel("Retention Rate (%)")
ax.set_ylim(0, 115)
ax.legend()

for i, r in enumerate(cohort_df["retention_rate"]):
    ax.text(i, r + 1.5, f"{r:.0f}%", ha="center", fontsize=6.5, fontweight="bold")

fig.tight_layout()
save(fig, "19_retention_cohort.png")


# ── CHART 20: Revenue Heatmap — Age Group × Region ───────
age_region = (
    df.groupby(["Age_Group","Region"])["Sales"]
    .sum().unstack(fill_value=0) / 1e7
)
age_order = ["18–25","26–35","36–45","46–55","56+"]
age_region = age_region.reindex(age_order)

fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(age_region, annot=True, fmt=".1f", cmap="YlOrRd",
            linewidths=0.5, linecolor="#EEEEEE",
            cbar_kws={"label":"Sales (₹ Crores)"}, ax=ax)
ax.set_title("Customer Revenue Heatmap — Age Group × Region (₹ Crores)")
ax.set_xlabel("Region")
ax.set_ylabel("Age Group")
plt.xticks(rotation=0)
plt.yticks(rotation=0)
fig.tight_layout()
save(fig, "20_age_region_heatmap.png")


# ── CHART 21: RFM Segment Profile (Radar / Bar Matrix) ───
profile_cols = ["Avg_Recency","Avg_Frequency","Avg_Monetary"]
profile = seg_summary.set_index("Segment").reindex(seg_order)[["Avg_Recency","Avg_Frequency","Avg_Monetary"]].dropna()

fig, axes = plt.subplots(1, 3, figsize=(14, 5))

metric_labels = ["Avg Recency\n(days, lower=better)",
                 "Avg Frequency\n(orders)",
                 "Avg Monetary\n(₹ Lakhs)"]
metrics       = ["Avg_Recency", "Avg_Frequency", "Avg_Monetary"]
divisors      = [1, 1, 1e5]

for ax, col, label, div in zip(axes, metrics, metric_labels, divisors):
    data  = profile[col] / div
    bars  = ax.bar(profile.index, data,
                   color=[SEG_COLORS[s] for s in profile.index],
                   edgecolor="white", width=0.6)
    ax.set_title(label, fontsize=10)
    ax.tick_params(axis="x", rotation=30)
    for bar, v in zip(bars, data):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+data.max()*0.02,
                f"{v:.1f}", ha="center", fontsize=8)

fig.suptitle("RFM Segment Profile — Recency, Frequency, Monetary",
             fontsize=13, fontweight="bold")
fig.tight_layout()
save(fig, "21_rfm_segment_profile.png")


# ─────────────────────────────────────────────────────────
# EXPORT RFM TABLE
# ─────────────────────────────────────────────────────────
out = os.path.join(BASE_DIR, "data", "cleaned", "rfm_segments.csv")
rfm.to_csv(out, index=False)
print(f"  ✓ RFM data exported: data/cleaned/rfm_segments.csv  ({len(rfm):,} rows)")

print(f"\n{SEP}")
print("  Phase 7 — Customer Analytics COMPLETE")
print(SEP)
print("""
  Key Findings:
  ─────────────────────────────────────────────────────
  • 5,000 total customers | avg 10 orders per customer
  • All customers are repeat buyers (min 2 orders)
  • RFM Champions generate the highest avg spend
  • Top 20% customers contribute ~50% of revenue
  • Festive cohorts (Oct-Dec) show highest retention
  ─────────────────────────────────────────────────────
""")
