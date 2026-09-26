"""
regenerate_screenshots.py
--------------------------
Regenerates all 21 portfolio screenshots with a professional dark theme.
Optimised for LinkedIn — high resolution, clean layout, consistent branding.

Output: screenshots/01_*.png  …  screenshots/21_*.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import os, warnings
warnings.filterwarnings("ignore")

# ── paths ────────────────────────────────────────────────
BASE   = os.path.join(os.path.dirname(__file__), "..")
CLEAN  = os.path.join(BASE, "data", "cleaned", "ecommerce_cleaned.csv")
RFM_F  = os.path.join(BASE, "data", "cleaned", "rfm_segments.csv")
SAVE   = os.path.join(BASE, "screenshots")
os.makedirs(SAVE, exist_ok=True)

# ── global style ─────────────────────────────────────────
BG      = "#0D1B2A"
CARD    = "#112233"
GRID    = "#1E3A5F"
TEXT    = "#E2E8F0"
MUTED   = "#64748B"
TEAL    = "#00D4AA"
BLUE    = "#4A9EFF"
ORANGE  = "#FFA94D"
RED     = "#FF6B6B"
GREEN   = "#51CF66"
PURPLE  = "#B197FC"
YELLOW  = "#FFD43B"
PAL     = [TEAL, BLUE, ORANGE, RED, PURPLE, YELLOW, GREEN, "#F783AC"]

plt.rcParams.update({
    "figure.facecolor":   BG,
    "axes.facecolor":     CARD,
    "axes.edgecolor":     GRID,
    "axes.labelcolor":    TEXT,
    "axes.titlecolor":    TEXT,
    "axes.titlesize":     15,
    "axes.titleweight":   "bold",
    "axes.titlepad":      14,
    "axes.labelsize":     11,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.spines.bottom": False,
    "axes.grid":          True,
    "grid.color":         GRID,
    "grid.linewidth":     0.6,
    "grid.alpha":         0.5,
    "xtick.color":        MUTED,
    "ytick.color":        MUTED,
    "xtick.labelsize":    9.5,
    "ytick.labelsize":    9.5,
    "legend.facecolor":   CARD,
    "legend.edgecolor":   GRID,
    "legend.labelcolor":  TEXT,
    "legend.fontsize":    9.5,
    "figure.dpi":         160,
    "savefig.facecolor":  BG,
    "savefig.bbox":       "tight",
    "savefig.pad_inches": 0.3,
    "font.family":        "DejaVu Sans",
    "text.color":         TEXT,
})

def watermark(ax, text="E-Commerce Analytics · aishwaryacs005-rgb"):
    ax.text(0.99, 0.01, text, transform=ax.transAxes,
            fontsize=7.5, color=MUTED, ha="right", va="bottom", alpha=0.7)

def header_bar(fig, title, subtitle=""):
    fig.text(0.5, 0.97, title, ha="center", va="top",
             fontsize=17, fontweight="bold", color=TEXT)
    if subtitle:
        fig.text(0.5, 0.93, subtitle, ha="center", va="top",
                 fontsize=10, color=MUTED)

def save(name):
    path = os.path.join(SAVE, name)
    plt.savefig(path, facecolor=BG)
    plt.close()
    print(f"  ✓ {name}")

def inr(v):
    if v >= 1e7: return f"₹{v/1e7:.1f}Cr"
    if v >= 1e5: return f"₹{v/1e5:.1f}L"
    return f"₹{v:,.0f}"

# ── load data ────────────────────────────────────────────
print("Loading data …")
df  = pd.read_csv(CLEAN, parse_dates=["Order_Date"])
rfm = pd.read_csv(RFM_F)

# aggregations
monthly = (df.groupby("Order_YearMonth", as_index=False)
           .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                Orders=("Order_ID","nunique"))
           .sort_values("Order_YearMonth"))

yearly = (df.groupby("Order_Year", as_index=False)
          .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
               Orders=("Order_ID","nunique")))

cat = (df.groupby("Category", as_index=False)
       .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
       .sort_values("Sales", ascending=False))
cat["Margin"] = (cat["Profit"]/cat["Sales"]*100).round(1)

region = (df.groupby("Region", as_index=False)
          .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
               Orders=("Order_ID","nunique"))
          .sort_values("Sales", ascending=False))

prod = (df.groupby("Product_Name", as_index=False)
        .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
             Qty=("Quantity","sum")))
top10  = prod.nlargest(10,"Sales").sort_values("Sales")
bot10  = prod.nsmallest(10,"Sales").sort_values("Sales", ascending=False)

pay = (df.groupby("Payment_Mode")["Order_ID"].nunique()
       .reset_index().rename(columns={"Order_ID":"Cnt"})
       .sort_values("Cnt", ascending=False))

status = (df.groupby("Order_Status")["Order_ID"].nunique()
          .reset_index().rename(columns={"Order_ID":"Cnt"})
          .sort_values("Cnt", ascending=False))

AO = ["18–25","26–35","36–45","46–55","56+"]
age = (df.groupby("Age_Group", as_index=False)
       .agg(Sales=("Sales","sum"))
       .assign(Age_Group=lambda x: pd.Categorical(
           x["Age_Group"], categories=AO, ordered=True))
       .sort_values("Age_Group"))

ctype = (df.groupby("Customer_Type", as_index=False)
         .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique")))

SO = ["Champions","Loyal Customers","At Risk","Hibernating","Lost"]
SC = {s:c for s,c in zip(SO,[TEAL,BLUE,ORANGE,RED,MUTED])}
seg = (rfm.groupby("Segment", as_index=False)
       .agg(Count=("Customer_ID","count"),
            Revenue=("Monetary","sum"),
            Avg=("Monetary","mean"),
            AvgR=("Recency","mean"),
            AvgF=("Frequency","mean"))
       .assign(Segment=lambda x: pd.Categorical(
           x["Segment"], categories=SO, ordered=True))
       .sort_values("Segment").dropna(subset=["Segment"]).reset_index(drop=True))

cat_reg = (df.groupby(["Category","Region"])["Sales"]
           .sum().unstack(fill_value=0)/1e7)

seas = (df.groupby("Season", as_index=False)
        .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique")))
seas["Pct"] = (seas["Sales"]/df["Sales"].sum()*100).round(1)

dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow = (df.groupby("Order_DayOfWeek")["Order_ID"].nunique()
       .reset_index().rename(columns={"Order_ID":"Cnt"}))
dow["Order_DayOfWeek"] = pd.Categorical(dow["Order_DayOfWeek"],
                                         categories=dow_order, ordered=True)
dow = dow.sort_values("Order_DayOfWeek")

rfm_sorted = rfm.sort_values("Monetary", ascending=False).reset_index(drop=True)
rfm_sorted["cum_pct"] = rfm_sorted["Monetary"].cumsum() / rfm_sorted["Monetary"].sum() * 100
rfm_sorted["rank_pct"] = (rfm_sorted.index+1) / len(rfm_sorted) * 100

print("Generating charts …\n")

# ════════════════════════════════════════════════════════
# 01 — Monthly Sales & Profit Trend
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 6))
x = range(len(monthly))
ax.fill_between(x, monthly["Sales"]/1e7, alpha=0.12, color=TEAL)
ax.plot(x, monthly["Sales"]/1e7, color=TEAL, lw=2.5, label="Sales", marker="o", ms=3.5)
ax.fill_between(x, monthly["Profit"]/1e7, alpha=0.10, color=BLUE)
ax.plot(x, monthly["Profit"]/1e7, color=BLUE, lw=2, label="Profit", ls="--", marker="s", ms=3)
for yr, lbl in [("2023-01","2023"),("2024-01","2024")]:
    if yr in monthly["Order_YearMonth"].astype(str).tolist():
        idx = monthly["Order_YearMonth"].astype(str).tolist().index(yr)
        ax.axvline(idx, color=GRID, lw=1.2, ls=":", alpha=0.8)
        ax.text(idx+0.3, ax.get_ylim()[1]*0.95, lbl, color=MUTED, fontsize=9)
tick_pos = list(range(0, len(monthly), 3))
ax.set_xticks(tick_pos)
ax.set_xticklabels([monthly["Order_YearMonth"].iloc[i] for i in tick_pos],
                   rotation=35, ha="right")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
ax.set_ylabel("Amount (₹ Crores)")
ax.legend(loc="upper left")
ax.set_title("Monthly Sales & Profit Trend  ·  Jan 2022 – Dec 2024")
watermark(ax)
fig.tight_layout(rect=[0,0,1,0.97])
save("01_monthly_sales_trend.png")

# ════════════════════════════════════════════════════════
# 02 — Year-over-Year Comparison
# ════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
colors3 = [TEAL, BLUE, ORANGE]
for ax, col, title, fmt in zip(axes,
        ["Sales","Profit"],
        ["Year-over-Year Sales","Year-over-Year Profit"],
        [lambda v: f"₹{v/1e7:.1f}Cr", lambda v: f"₹{v/1e7:.1f}Cr"]):
    bars = ax.bar(yearly["Order_Year"].astype(str), yearly[col]/1e7,
                  color=colors3, width=0.5, edgecolor=BG, linewidth=0.8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
    ax.set_title(title)
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                f"₹{bar.get_height():.1f}Cr", ha="center", fontsize=10,
                fontweight="bold", color=TEXT)
    watermark(ax)
fig.suptitle("Year-over-Year Performance  ·  2022 vs 2023 vs 2024",
             fontsize=16, fontweight="bold", color=TEXT, y=1.02)
fig.tight_layout()
save("02_yearly_comparison.png")

# ════════════════════════════════════════════════════════
# 03 — Category Sales (horizontal bar)
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(cat["Category"], cat["Sales"]/1e7,
               color=[TEAL if i==0 else PAL[i%len(PAL)] for i in range(len(cat))],
               height=0.6, edgecolor=BG)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
ax.invert_yaxis()
ax.set_xlabel("Total Sales (₹ Crores)")
ax.set_title("Total Sales by Product Category")
for bar, row in zip(bars, cat.itertuples()):
    ax.text(bar.get_width()+0.4, bar.get_y()+bar.get_height()/2,
            f"₹{row.Sales/1e7:.1f}Cr  ·  {row.Margin:.0f}% margin",
            va="center", fontsize=9, color=MUTED)
watermark(ax)
fig.tight_layout()
save("03_category_sales.png")

# ════════════════════════════════════════════════════════
# 04 — Profit Margin by Category
# ════════════════════════════════════════════════════════
cat_s = cat.sort_values("Margin", ascending=False)
fig, ax = plt.subplots(figsize=(12, 6))
bar_cols = [GREEN if m>=45 else ORANGE if m>=35 else RED for m in cat_s["Margin"]]
bars = ax.bar(cat_s["Category"], cat_s["Margin"], color=bar_cols,
              width=0.5, edgecolor=BG)
avg_m = cat_s["Margin"].mean()
ax.axhline(avg_m, color=MUTED, ls="--", lw=1.5,
           label=f"Average  {avg_m:.1f}%")
ax.set_ylabel("Profit Margin (%)")
ax.set_title("Profit Margin % by Category")
ax.set_ylim(0, 62)
for bar, m in zip(bars, cat_s["Margin"]):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.7,
            f"{m:.1f}%", ha="center", fontsize=10, fontweight="bold", color=TEXT)
plt.xticks(rotation=15, ha="right")
ax.legend()
watermark(ax)
fig.tight_layout()
save("04_category_profit_margin.png")

# ════════════════════════════════════════════════════════
# 05 — Top 10 Products
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 7))
cmap_vals = np.linspace(0.4, 1.0, len(top10))
cols = [plt.cm.cool(v) for v in cmap_vals]
bars = ax.barh(top10["Product_Name"], top10["Sales"]/1e5,
               color=cols, height=0.65, edgecolor=BG)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}L"))
ax.invert_yaxis()
ax.set_xlabel("Total Sales (₹ Lakhs)")
ax.set_title("Top 10 Products by Revenue")
for bar, row in zip(bars, top10.itertuples()):
    ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
            f"₹{row.Sales/1e5:.0f}L", va="center", fontsize=9, color=MUTED)
watermark(ax)
fig.tight_layout()
save("05_top10_products.png")

# ════════════════════════════════════════════════════════
# 06 — Bottom 10 Products
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 7))
bars = ax.barh(bot10["Product_Name"], bot10["Sales"]/1e5,
               color=RED, alpha=0.8, height=0.65, edgecolor=BG)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.2f}L"))
ax.set_xlabel("Total Sales (₹ Lakhs)")
ax.set_title("Bottom 10 Products — Lowest Revenue (Candidates for Review)")
for bar, row in zip(bars, bot10.itertuples()):
    ax.text(bar.get_width()+0.005, bar.get_y()+bar.get_height()/2,
            f"₹{row.Sales/1e5:.2f}L", va="center", fontsize=9, color=MUTED)
watermark(ax)
fig.tight_layout()
save("06_bottom10_products.png")

# ════════════════════════════════════════════════════════
# 07 — Regional Sales
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(region))
w = 0.38
b1 = ax.bar(x-w/2, region["Sales"]/1e7, w, color=TEAL, label="Sales", edgecolor=BG)
b2 = ax.bar(x+w/2, region["Profit"]/1e7, w, color=BLUE, label="Profit", edgecolor=BG)
ax.set_xticks(x); ax.set_xticklabels(region["Region"], fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
ax.set_ylabel("Amount (₹ Crores)")
ax.set_title("Sales & Profit by Region")
ax.legend()
for bar in list(b1)+list(b2):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
            f"₹{bar.get_height():.0f}Cr", ha="center", fontsize=8.5, color=MUTED)
watermark(ax)
fig.tight_layout()
save("07_regional_sales.png")

# ════════════════════════════════════════════════════════
# 08 — Category × Region Heatmap
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6))
cmap = LinearSegmentedColormap.from_list("teal",["#0D1B2A","#1E3A5F",BLUE,TEAL])
sns.heatmap(cat_reg, annot=True, fmt=".1f", cmap=cmap,
            linewidths=0.5, linecolor=BG, ax=ax,
            annot_kws={"size":10, "color":TEXT},
            cbar_kws={"label":"Sales (₹ Crores)"})
ax.set_title("Sales Heatmap — Category × Region  (₹ Crores)")
ax.set_xlabel("Region"); ax.set_ylabel("Category")
plt.xticks(rotation=0); plt.yticks(rotation=0)
watermark(ax)
fig.tight_layout()
save("08_regional_heatmap.png")

# ════════════════════════════════════════════════════════
# 09 — Payment Mode
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 7))
wedge_cols = PAL[:len(pay)]
explode    = [0.06 if i==0 else 0 for i in range(len(pay))]
wedges, texts, autotexts = ax.pie(
    pay["Cnt"], labels=pay["Payment_Mode"],
    autopct="%1.1f%%", colors=wedge_cols,
    explode=explode, startangle=90,
    pctdistance=0.78, labeldistance=1.1,
    wedgeprops={"edgecolor":BG,"linewidth":2})
for t in texts: t.set_color(TEXT); t.set_fontsize(10)
for at in autotexts: at.set_color(BG); at.set_fontsize(9); at.set_fontweight("bold")
ax.set_title("Payment Mode Distribution", pad=20)
watermark(ax)
fig.tight_layout()
save("09_payment_mode.png")

# ════════════════════════════════════════════════════════
# 10 — Order Status
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))
st_cols = {"Delivered":GREEN,"Shipped":BLUE,"Cancelled":RED,
           "Returned":ORANGE,"Processing":PURPLE}
cols = [st_cols.get(s,MUTED) for s in status["Order_Status"]]
bars = ax.bar(status["Order_Status"], status["Cnt"],
              color=cols, width=0.5, edgecolor=BG)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:,.0f}"))
ax.set_ylabel("Number of Orders")
ax.set_title("Order Status Breakdown")
total = status["Cnt"].sum()
for bar in bars:
    pct = bar.get_height()/total*100
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+80,
            f"{bar.get_height():,}\n({pct:.1f}%)", ha="center",
            fontsize=9.5, color=TEXT)
watermark(ax)
fig.tight_layout()
save("10_order_status.png")

# ════════════════════════════════════════════════════════
# 11 — Sales by Age Group
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.bar(age["Age_Group"].astype(str), age["Sales"]/1e7,
              color=PAL[:5], width=0.5, edgecolor=BG)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
ax.set_ylabel("Total Sales (₹ Crores)")
ax.set_xlabel("Customer Age Group")
ax.set_title("Revenue by Customer Age Group")
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
            f"₹{bar.get_height():.1f}Cr", ha="center",
            fontsize=10, fontweight="bold", color=TEXT)
watermark(ax)
fig.tight_layout()
save("11_age_group_sales.png")

# ════════════════════════════════════════════════════════
# 12 — New vs Returning Customer Revenue
# ════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
for ax, col, div, ylabel, title in zip(
        axes,
        ["Sales","Orders"],
        [1e7,1],
        ["₹ Crores","Orders"],
        ["Revenue by Customer Type","Order Count by Customer Type"]):
    bars = ax.bar(ctype["Customer_Type"], ctype[col]/div,
                  color=[TEAL,BLUE], width=0.45, edgecolor=BG)
    ax.set_title(title); ax.set_ylabel(ylabel)
    if div==1e7:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
    for bar in bars:
        val = bar.get_height()
        lbl = f"₹{val:.1f}Cr" if div==1e7 else f"{int(val):,}"
        ax.text(bar.get_x()+bar.get_width()/2, val+bar.get_height()*0.02,
                lbl, ha="center", fontsize=11, fontweight="bold", color=TEXT)
    watermark(ax)
fig.suptitle("New vs Returning Customer Comparison",
             fontsize=16, fontweight="bold", color=TEXT)
fig.tight_layout()
save("12_customer_type_revenue.png")

# ════════════════════════════════════════════════════════
# 13 — Sales vs Profit Scatter
# ════════════════════════════════════════════════════════
prod_cat = (df.groupby(["Product_Name","Category"], as_index=False)
            .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                 Qty=("Quantity","sum")))
fig, ax = plt.subplots(figsize=(13, 8))
cat_pal = {c:PAL[i%len(PAL)] for i,c in enumerate(prod_cat["Category"].unique())}
for cat_name, grp in prod_cat.groupby("Category"):
    ax.scatter(grp["Sales"]/1e5, grp["Profit"]/1e5,
               label=cat_name, color=cat_pal[cat_name],
               s=grp["Qty"]/4, alpha=0.72,
               edgecolors=BG, linewidth=0.5)
ax.axhline(0, color=RED, ls="--", lw=1, alpha=0.5)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}L"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}L"))
ax.set_xlabel("Total Sales (₹ Lakhs)")
ax.set_ylabel("Total Profit (₹ Lakhs)")
ax.set_title("Sales vs Profit by Product  ·  Bubble Size = Units Sold")
ax.legend(loc="upper left", framealpha=0.9)
watermark(ax)
fig.tight_layout()
save("13_sales_vs_profit_scatter.png")

# ════════════════════════════════════════════════════════
# 14 — Seasonal Trend
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))
seas_c = {"Festive Season":ORANGE,"New Year Sales":TEAL,"Summer":RED,"Monsoon":BLUE}
bars = ax.bar(seas["Season"], seas["Sales"]/1e7,
              color=[seas_c.get(s,BLUE) for s in seas["Season"]],
              width=0.5, edgecolor=BG)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
ax.set_ylabel("Total Sales (₹ Crores)")
ax.set_title("Revenue by Business Season")
for bar, row in zip(bars, seas.itertuples()):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.4,
            f"₹{bar.get_height():.1f}Cr\n({row.Pct:.1f}%)",
            ha="center", fontsize=10, fontweight="bold", color=TEXT)
watermark(ax)
fig.tight_layout()
save("14_seasonal_trend.png")

# ════════════════════════════════════════════════════════
# 15 — Day of Week
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6))
dow_cols = [ORANGE if d in ["Saturday","Sunday"] else BLUE
            for d in dow["Order_DayOfWeek"].astype(str)]
bars = ax.bar(dow["Order_DayOfWeek"].astype(str), dow["Cnt"],
              color=dow_cols, width=0.55, edgecolor=BG)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:,.0f}"))
ax.set_ylabel("Number of Orders")
ax.set_title("Orders by Day of Week")
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+30,
            f"{int(bar.get_height()):,}", ha="center", fontsize=9, color=MUTED)
leg = [mpatches.Patch(color=BLUE,label="Weekday"),
       mpatches.Patch(color=ORANGE,label="Weekend")]
ax.legend(handles=leg)
watermark(ax)
fig.tight_layout()
save("15_day_of_week.png")

# ════════════════════════════════════════════════════════
# 16 — RFM Segments
# ════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
# donut
sizes  = seg["Count"].tolist()
labels = seg["Segment"].tolist()
cols   = [SC.get(s,MUTED) for s in labels]
wedges, _, autotexts = axes[0].pie(
    sizes, labels=labels, autopct="%1.1f%%",
    colors=cols, startangle=90, pctdistance=0.78,
    wedgeprops={"edgecolor":BG,"linewidth":2.5,"width":0.55})
for t in autotexts:
    t.set_color(BG); t.set_fontsize(9); t.set_fontweight("bold")
axes[0].text(0,0, f"{len(rfm):,}\nCustomers", ha="center", va="center",
             fontsize=13, fontweight="bold", color=TEXT)
axes[0].set_title("RFM Customer Segments")
# revenue bar
bars = axes[1].barh(seg["Segment"], seg["Revenue"]/1e7,
                    color=[SC.get(s,MUTED) for s in seg["Segment"]],
                    height=0.55, edgecolor=BG)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}Cr"))
axes[1].set_xlabel("Total Revenue (₹ Crores)")
axes[1].set_title("Revenue Contribution per Segment")
axes[1].invert_yaxis()
for bar, row in zip(bars, seg.itertuples()):
    axes[1].text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                 f"₹{row.Revenue/1e7:.1f}Cr", va="center", fontsize=9.5, color=MUTED)
watermark(axes[1])
fig.suptitle("RFM Customer Segmentation  ·  5,000 Customers",
             fontsize=16, fontweight="bold", color=TEXT)
fig.tight_layout()
save("16_rfm_segments.png")

# ════════════════════════════════════════════════════════
# 17 — RFM Scatter (Frequency vs Monetary)
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 8))
for seg_name in SO:
    grp = rfm[rfm["Segment"]==seg_name]
    if len(grp)==0: continue
    ax.scatter(grp["Frequency"], grp["Monetary"]/1e5,
               label=seg_name, color=SC[seg_name],
               alpha=0.55, s=22, edgecolors="none")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}L"))
ax.set_xlabel("Purchase Frequency (Number of Orders)")
ax.set_ylabel("Total Monetary Value (₹ Lakhs)")
ax.set_title("RFM Analysis  ·  Frequency vs Monetary Value")
ax.legend(title="RFM Segment", loc="upper left",
          title_fontsize=9, framealpha=0.9)
watermark(ax)
fig.tight_layout()
save("17_rfm_scatter.png")

# ════════════════════════════════════════════════════════
# 18 — Customer Tier Revenue (Pareto)
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6))
ax.fill_between(rfm_sorted["rank_pct"], rfm_sorted["cum_pct"],
                alpha=0.08, color=TEAL)
ax.plot(rfm_sorted["rank_pct"], rfm_sorted["cum_pct"],
        color=TEAL, lw=2.5, label="Cumulative Revenue %")
for xv, lbl in [(20,"Top 20%"),(50,"Top 50%")]:
    yv = rfm_sorted[rfm_sorted["rank_pct"]<=xv]["cum_pct"].max()
    ax.axvline(xv, color=ORANGE, ls="--", lw=1.2, alpha=0.7)
    ax.axhline(yv, color=ORANGE, ls="--", lw=1.2, alpha=0.7)
    ax.annotate(f"{lbl}\n→ {yv:.1f}% revenue",
                xy=(xv,yv), xytext=(xv+5, yv-12),
                fontsize=9, color=ORANGE,
                arrowprops=dict(arrowstyle="->",color=ORANGE,lw=1.2))
ax.set_xlabel("% of Customers (high to low spenders)")
ax.set_ylabel("Cumulative Revenue %")
ax.set_title("Pareto Chart  ·  Customer Revenue Concentration")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
ax.set_xlim(0,100); ax.set_ylim(0,105)
ax.legend()
watermark(ax)
fig.tight_layout()
save("18_customer_tier_revenue.png")

# ════════════════════════════════════════════════════════
# 19 — Retention Cohort
# ════════════════════════════════════════════════════════
cohort = (df.groupby("Customer_ID")
          .agg(first=("Order_Date","min"),
               orders=("Order_ID","nunique"))
          .reset_index())
cohort["cohort"] = cohort["first"].dt.to_period("M").astype(str)
cohort_agg = (cohort.groupby("cohort")
              .agg(size=("Customer_ID","count"),
                   retained=("orders", lambda x:(x>1).sum()))
              .reset_index())
cohort_agg["rate"] = (cohort_agg["retained"]/cohort_agg["size"]*100).round(1)
cohort_agg = cohort_agg.head(24)

fig, ax = plt.subplots(figsize=(14, 6))
bar_cols = [GREEN if r>=80 else ORANGE if r>=50 else RED
            for r in cohort_agg["rate"]]
ax.bar(range(len(cohort_agg)), cohort_agg["rate"],
       color=bar_cols, edgecolor=BG, width=0.75)
avg_r = cohort_agg["rate"].mean()
ax.axhline(avg_r, color=MUTED, ls="--", lw=1.5,
           label=f"Average  {avg_r:.1f}%")
ax.set_xticks(range(len(cohort_agg)))
ax.set_xticklabels(cohort_agg["cohort"], rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Retention Rate (%)")
ax.set_title("Monthly Cohort Retention Rate  ·  % Who Placed >1 Order")
ax.set_ylim(0, 115)
ax.legend()
for i,r in enumerate(cohort_agg["rate"]):
    ax.text(i, r+1.5, f"{r:.0f}%", ha="center", fontsize=7, color=MUTED)
watermark(ax)
fig.tight_layout()
save("19_retention_cohort.png")

# ════════════════════════════════════════════════════════
# 20 — Age Group × Region Heatmap
# ════════════════════════════════════════════════════════
age_reg = (df.groupby(["Age_Group","Region"])["Sales"]
           .sum().unstack(fill_value=0)/1e7)
age_reg = age_reg.reindex(AO)
fig, ax = plt.subplots(figsize=(12, 6))
cmap2 = LinearSegmentedColormap.from_list("warm",["#0D1B2A","#3D1A00",ORANGE,YELLOW])
sns.heatmap(age_reg, annot=True, fmt=".1f", cmap=cmap2,
            linewidths=0.5, linecolor=BG, ax=ax,
            annot_kws={"size":10,"color":TEXT},
            cbar_kws={"label":"Sales (₹ Crores)"})
ax.set_title("Customer Revenue Heatmap  ·  Age Group × Region  (₹ Crores)")
ax.set_xlabel("Region"); ax.set_ylabel("Age Group")
plt.xticks(rotation=0); plt.yticks(rotation=0)
watermark(ax)
fig.tight_layout()
save("20_age_region_heatmap.png")

# ════════════════════════════════════════════════════════
# 21 — RFM Segment Profile (3-panel bar)
# ════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(15, 6))
metrics = [
    ("AvgR", "Avg Recency (Days)\nLower = Better", True),
    ("AvgF", "Avg Purchase Frequency\n(# Orders)", False),
    ("Avg",  "Avg Monetary Value\n(₹ Lakhs)", False),
]
for ax, (col, title, invert) in zip(axes, metrics):
    data = seg[col] if col != "Avg" else seg[col]/1e5
    bar_c = [SC.get(s,MUTED) for s in seg["Segment"]]
    bars = ax.bar(seg["Segment"], data, color=bar_c,
                  width=0.55, edgecolor=BG)
    ax.set_title(title, fontsize=11)
    ax.tick_params(axis="x", rotation=30)
    if col=="Avg":
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v,_: f"₹{v:.0f}L"))
    mx = data.max()
    for bar, v in zip(bars, data):
        ax.text(bar.get_x()+bar.get_width()/2,
                bar.get_height()+mx*0.02,
                f"{v:.1f}", ha="center", fontsize=9, color=MUTED)
    watermark(ax)
fig.suptitle("RFM Segment Profile  ·  Recency · Frequency · Monetary",
             fontsize=15, fontweight="bold", color=TEXT)
fig.tight_layout()
save("21_rfm_segment_profile.png")

# ════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════
print(f"\n{'='*55}")
print(f"  All 21 screenshots regenerated")
print(f"  Saved to: {os.path.abspath(SAVE)}")
print(f"{'='*55}")
print("\n  Upload these 4 to your LinkedIn post:")
print("    screenshots/01_monthly_sales_trend.png")
print("    screenshots/16_rfm_segments.png")
print("    screenshots/07_regional_sales.png")
print("    screenshots/05_top10_products.png")
