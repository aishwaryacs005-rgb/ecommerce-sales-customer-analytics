"""
phase8_dashboard.py
--------------------
Phase 8 — Interactive HTML Dashboard

Builds a fully self-contained interactive dashboard HTML file
that replicates the 4-page Power BI design using Plotly.

Output: powerbi/ecommerce_dashboard.html

Open in any browser — no server, no login, no install needed.
"""

import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────
BASE    = os.path.join(os.path.dirname(__file__), "..")
CLEAN   = os.path.join(BASE, "data", "cleaned", "ecommerce_cleaned.csv")
RFM     = os.path.join(BASE, "data", "cleaned", "rfm_segments.csv")
RAW     = os.path.join(BASE, "data", "raw")
OUT     = os.path.join(BASE, "powerbi", "ecommerce_dashboard.html")

print("=" * 60)
print("  Building Interactive HTML Dashboard")
print("=" * 60)

# ── Load data ────────────────────────────────────────────
df  = pd.read_csv(CLEAN, parse_dates=["Order_Date"])
rfm = pd.read_csv(RFM)
products_df = pd.read_csv(os.path.join(RAW, "products.csv"))

# ── Color palette ────────────────────────────────────────
C_BLUE    = "#2E75B6"
C_GREEN   = "#2D7D46"
C_ORANGE  = "#E67E22"
C_RED     = "#C0392B"
C_PURPLE  = "#7D3C98"
C_TEAL    = "#1A7F7A"
C_GREY    = "#95A5A6"
BG        = "#F5F7FA"
CARD_BG   = "#FFFFFF"
HDR_BG    = "#1F3864"

PALETTE   = [C_BLUE, C_GREEN, C_ORANGE, C_RED, C_PURPLE, C_TEAL, C_GREY]

SEG_COLORS = {
    "Champions":       "#27AE60",
    "Loyal Customers": "#2980B9",
    "At Risk":         "#F39C12",
    "Hibernating":     "#E74C3C",
    "Lost":            "#7F8C8D",
}

# ── KPIs ─────────────────────────────────────────────────
total_sales   = df["Sales"].sum()
total_profit  = df["Profit"].sum()
total_orders  = df["Order_ID"].nunique()
total_cust    = df["Customer_ID"].nunique()
aov           = total_sales / total_orders
margin        = total_profit / total_sales * 100
total_qty     = df["Quantity"].sum()
cancel_rate   = df[df["Order_Status"]=="Cancelled"]["Order_ID"].nunique() / total_orders * 100
deliver_rate  = df[df["Order_Status"]=="Delivered"]["Order_ID"].nunique() / total_orders * 100

# ── Aggregations ─────────────────────────────────────────
monthly = (df.groupby("Order_YearMonth", as_index=False)
           .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                Orders=("Order_ID","nunique"))
           .sort_values("Order_YearMonth"))

cat = (df.groupby("Category", as_index=False)
       .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
       .sort_values("Sales", ascending=False))
cat["Margin"] = (cat["Profit"]/cat["Sales"]*100).round(1)

region = (df.groupby("Region", as_index=False)
          .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
               Orders=("Order_ID","nunique"))
          .sort_values("Sales", ascending=False))

pay = (df.groupby("Payment_Mode")["Order_ID"]
       .nunique().reset_index()
       .rename(columns={"Order_ID":"Count"})
       .sort_values("Count", ascending=False))

status = (df.groupby("Order_Status")["Order_ID"]
          .nunique().reset_index()
          .rename(columns={"Order_ID":"Count"})
          .sort_values("Count", ascending=False))

top10 = (df.groupby("Product_Name", as_index=False)
         .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
              Qty=("Quantity","sum"))
         .nlargest(10,"Sales").sort_values("Sales"))
top10["Margin"] = (top10["Profit"]/top10["Sales"]*100).round(1)

bot10 = (df.groupby("Product_Name", as_index=False)
         .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
         .nsmallest(10,"Sales").sort_values("Sales", ascending=False))

sub_cat = (df.groupby(["Category","Sub_Category"], as_index=False)
           .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
           .sort_values("Sales", ascending=False).head(15))

age_grp_order = ["18–25","26–35","36–45","46–55","56+"]
age = (df.groupby("Age_Group", as_index=False)
       .agg(Sales=("Sales","sum"), Customers=("Customer_ID","nunique"))
       .assign(Age_Group=lambda x: pd.Categorical(
           x["Age_Group"], categories=age_grp_order, ordered=True))
       .sort_values("Age_Group"))

ctype = (df.groupby("Customer_Type", as_index=False)
         .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"),
              Customers=("Customer_ID","nunique")))
ctype["AOV"] = (ctype["Sales"]/ctype["Orders"]).round(0)

seg_summary = (rfm.groupby("Segment", as_index=False)
               .agg(Count=("Customer_ID","count"),
                    Revenue=("Monetary","sum"),
                    AvgSpend=("Monetary","mean"))
               .sort_values("Revenue", ascending=False))

top_cust = (df.groupby(["Customer_ID"], as_index=False)
            .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"))
            .nlargest(15,"Sales"))
top_cust = top_cust.merge(
    pd.read_csv(os.path.join(RAW,"customers.csv"))[["Customer_ID","Customer_Name","Region","Customer_Type"]],
    on="Customer_ID")

state_sales = (df.groupby(["State","Region"], as_index=False)
               .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"))
               .sort_values("Sales", ascending=False))

cat_reg = (df.groupby(["Category","Region"])["Sales"]
           .sum().unstack(fill_value=0)/1e7)

season = (df.groupby("Season", as_index=False)
          .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"))
          .sort_values("Sales", ascending=False))

quarterly = (df.groupby(["Order_Year","Order_Quarter"], as_index=False)
             .agg(Sales=("Sales","sum"), Profit=("Profit","sum")))
quarterly["Label"] = quarterly["Order_Year"].astype(str) + " Q" + quarterly["Order_Quarter"].astype(str)

print("  Data loaded and aggregated")

# ═════════════════════════════════════════════════════════
# BUILD FIGURES
# ═════════════════════════════════════════════════════════
print("  Building charts...")

def fmt_cr(v): return f"₹{v/1e7:.1f}Cr"
def fmt_l(v):  return f"₹{v/1e5:.1f}L"

layout_base = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(family="Segoe UI, Arial", size=11, color="#2C3E50"),
    margin=dict(l=40, r=20, t=50, b=40),
    title_font=dict(size=13, color=HDR_BG),
)

# ── P1: Monthly trend ────────────────────────────────────
fig_monthly = go.Figure()
fig_monthly.add_trace(go.Scatter(
    x=monthly["Order_YearMonth"].astype(str), y=monthly["Sales"]/1e7,
    name="Sales", line=dict(color=C_BLUE, width=2.5),
    fill="tozeroy", fillcolor="rgba(46,117,182,0.08)",
    hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:.1f}Cr<extra></extra>"))
fig_monthly.add_trace(go.Scatter(
    x=monthly["Order_YearMonth"].astype(str), y=monthly["Profit"]/1e7,
    name="Profit", line=dict(color=C_GREEN, width=2),
    fill="tozeroy", fillcolor="rgba(45,125,70,0.08)",
    hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:.1f}Cr<extra></extra>"))
month_labels = monthly["Order_YearMonth"].astype(str).tolist()
for yr_start in ["2023-01","2024-01"]:
    if yr_start in month_labels:
        idx = month_labels.index(yr_start)
        fig_monthly.add_shape(type="line",
            x0=idx, x1=idx, y0=0, y1=1, yref="paper",
            line=dict(dash="dot", color=C_GREY, width=1.2))
        fig_monthly.add_annotation(x=idx, y=1, yref="paper",
            text=yr_start[:4], showarrow=False, font=dict(size=9, color=C_GREY))
fig_monthly.update_layout(**layout_base,
    title="Monthly Sales & Profit Trend (2022–2024)",
    xaxis=dict(tickangle=-45, tickfont_size=8),
    yaxis=dict(title="₹ Crores", tickprefix="₹", ticksuffix="Cr"),
    legend=dict(orientation="h", y=1.1),
    height=340)

# ── P1: Sales by Category ────────────────────────────────
fig_cat_bar = go.Figure(go.Bar(
    x=cat["Sales"]/1e7, y=cat["Category"],
    orientation="h",
    marker=dict(color=[C_BLUE if i==0 else PALETTE[i%len(PALETTE)]
                       for i in range(len(cat))],
                line=dict(color="white", width=0.5)),
    text=[fmt_cr(v) for v in cat["Sales"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:.1f}Cr<extra></extra>"))
fig_cat_bar.update_layout(**layout_base,
    title="Sales by Category",
    xaxis=dict(title="₹ Crores"), yaxis=dict(autorange="reversed"),
    height=300)

# ── P1: Sales by Region ──────────────────────────────────
fig_reg_col = go.Figure()
fig_reg_col.add_trace(go.Bar(
    x=region["Region"], y=region["Sales"]/1e7,
    name="Sales", marker_color=C_BLUE,
    text=[fmt_cr(v) for v in region["Sales"]], textposition="outside",
    hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:.1f}Cr<extra></extra>"))
fig_reg_col.add_trace(go.Bar(
    x=region["Region"], y=region["Profit"]/1e7,
    name="Profit", marker_color=C_GREEN,
    text=[fmt_cr(v) for v in region["Profit"]], textposition="outside",
    hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:.1f}Cr<extra></extra>"))
fig_reg_col.update_layout(**layout_base,
    title="Sales & Profit by Region", barmode="group",
    yaxis=dict(title="₹ Crores"), legend=dict(orientation="h", y=1.1),
    height=300)

# ── P1: Order Status ─────────────────────────────────────
status_colors = {"Delivered":C_GREEN,"Shipped":C_BLUE,
                 "Cancelled":C_RED,"Returned":C_ORANGE,"Processing":C_TEAL}
fig_status = go.Figure(go.Pie(
    labels=status["Order_Status"], values=status["Count"],
    hole=0.45,
    marker_colors=[status_colors.get(s,C_GREY) for s in status["Order_Status"]],
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>"))
fig_status.update_layout(**layout_base, title="Order Status Distribution",
    legend=dict(orientation="h", y=-0.15), height=300)

# ── P1: Payment Mode ─────────────────────────────────────
fig_pay = go.Figure(go.Pie(
    labels=pay["Payment_Mode"], values=pay["Count"],
    hole=0.45,
    marker_colors=PALETTE[:len(pay)],
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<extra></extra>"))
fig_pay.update_layout(**layout_base, title="Payment Mode Distribution",
    legend=dict(orientation="h", y=-0.2), height=300)

# ── P2: Top 10 Products ──────────────────────────────────
fig_top10 = go.Figure()
fig_top10.add_trace(go.Bar(
    y=top10["Product_Name"], x=top10["Sales"]/1e5,
    name="Sales", orientation="h", marker_color=C_BLUE,
    text=[fmt_l(v) for v in top10["Sales"]], textposition="outside",
    hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:.0f}L<br>Margin: "
                  + top10["Margin"].astype(str) + "%<extra></extra>"))
fig_top10.update_layout(**layout_base, title="Top 10 Products by Sales",
    xaxis=dict(title="₹ Lakhs"), yaxis=dict(autorange="reversed"),
    height=380)

# ── P2: Bottom 10 Products ───────────────────────────────
fig_bot10 = go.Figure(go.Bar(
    y=bot10["Product_Name"], x=bot10["Sales"]/1e5,
    orientation="h", marker_color=C_RED,
    text=[fmt_l(v) for v in bot10["Sales"]], textposition="outside"))
fig_bot10.update_layout(**layout_base,
    title="Bottom 10 Products (Lowest Revenue)",
    xaxis=dict(title="₹ Lakhs"), yaxis=dict(autorange="reversed"),
    height=380)

# ── P2: Sub-Category ────────────────────────────────────
fig_subcat = go.Figure()
for i, cat_name in enumerate(sub_cat["Category"].unique()):
    grp = sub_cat[sub_cat["Category"]==cat_name]
    fig_subcat.add_trace(go.Bar(
        x=grp["Sub_Category"], y=grp["Sales"]/1e7,
        name=cat_name, marker_color=PALETTE[i % len(PALETTE)]))
fig_subcat.update_layout(**layout_base,
    title="Sub-Category Sales Performance",
    barmode="stack", xaxis_tickangle=-30,
    yaxis=dict(title="₹ Crores"),
    legend=dict(orientation="h", y=1.1), height=360)

# ── P2: Sales vs Profit Scatter ──────────────────────────
prod_grp = (df.groupby(["Product_Name","Category"], as_index=False)
            .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                 Qty=("Quantity","sum")))
fig_scatter = px.scatter(
    prod_grp, x="Sales", y="Profit", size="Qty", color="Category",
    hover_name="Product_Name", color_discrete_sequence=PALETTE,
    labels={"Sales":"Total Sales (₹)","Profit":"Total Profit (₹)"},
    title="Sales vs Profit by Product (bubble = qty sold)")
fig_scatter.update_layout(**layout_base, height=400)
fig_scatter.update_traces(marker=dict(opacity=0.7, line=dict(width=0.3, color="white")))

# ── P3: RFM Segments ─────────────────────────────────────
seg_order = ["Champions","Loyal Customers","At Risk","Hibernating","Lost"]
seg_plot = seg_summary.set_index("Segment").reindex(seg_order).dropna().reset_index()

fig_rfm_donut = go.Figure(go.Pie(
    labels=seg_plot["Segment"], values=seg_plot["Count"],
    hole=0.5,
    marker_colors=[SEG_COLORS[s] for s in seg_plot["Segment"]],
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<extra></extra>"))
fig_rfm_donut.update_layout(**layout_base, title="RFM Customer Segments",
    legend=dict(orientation="h", y=-0.2), height=340)

fig_rfm_rev = go.Figure(go.Bar(
    y=seg_plot["Segment"], x=seg_plot["Revenue"]/1e7,
    orientation="h",
    marker_color=[SEG_COLORS[s] for s in seg_plot["Segment"]],
    text=[fmt_cr(v) for v in seg_plot["Revenue"]], textposition="outside",
    hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:.1f}Cr<extra></extra>"))
fig_rfm_rev.update_layout(**layout_base,
    title="Revenue by RFM Segment",
    xaxis=dict(title="₹ Crores"), height=340)

# ── P3: New vs Returning ─────────────────────────────────
fig_ctype = make_subplots(rows=1, cols=2,
    subplot_titles=("Revenue by Customer Type","Orders by Customer Type"))
for i, (col, div, label) in enumerate([("Sales",1e7,"₹ Crores"),("Orders",1,"Orders")]):
    fig_ctype.add_trace(go.Bar(
        x=ctype["Customer_Type"], y=ctype[col]/div,
        marker_color=[C_BLUE, C_GREEN],
        text=[f"₹{v/div:.1f}Cr" if col=="Sales" else f"{int(v/div):,}"
              for v in ctype[col]],
        textposition="outside", showlegend=False), row=1, col=i+1)
fig_ctype.update_layout(**layout_base, title="New vs Returning Customer Comparison",
    height=320)

# ── P3: Age Group ────────────────────────────────────────
fig_age = go.Figure(go.Bar(
    x=age["Age_Group"].astype(str), y=age["Sales"]/1e7,
    marker_color=PALETTE[:len(age)],
    text=[fmt_cr(v) for v in age["Sales"]], textposition="outside"))
fig_age.update_layout(**layout_base, title="Revenue by Customer Age Group",
    yaxis=dict(title="₹ Crores"), height=300)

# ── P3: Top 15 Customers ─────────────────────────────────
fig_top_cust = go.Figure(go.Bar(
    y=top_cust["Customer_Name"] + " (" + top_cust["Region"] + ")",
    x=top_cust["Sales"]/1e5,
    orientation="h",
    marker_color=[C_GREEN if t=="Returning" else C_ORANGE
                  for t in top_cust["Customer_Type"]],
    text=[fmt_l(v) for v in top_cust["Sales"]], textposition="outside",
    hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:.0f}L<extra></extra>"))
fig_top_cust.update_layout(**layout_base,
    title="Top 15 Customers by Spending (Green=Returning, Orange=New)",
    xaxis=dict(title="₹ Lakhs"), yaxis=dict(autorange="reversed"),
    height=480)

# ── P4: State performance ────────────────────────────────
top_states = state_sales.head(15).sort_values("Sales")
fig_states = go.Figure(go.Bar(
    y=top_states["State"] + " (" + top_states["Region"] + ")",
    x=top_states["Sales"]/1e7,
    orientation="h",
    marker_color=[{"North":C_BLUE,"South":C_GREEN,"East":C_ORANGE,
                   "West":C_PURPLE,"Central":C_TEAL}.get(r,C_GREY)
                  for r in top_states["Region"]],
    text=[fmt_cr(v) for v in top_states["Sales"]], textposition="outside"))
fig_states.update_layout(**layout_base,
    title="Top 15 States by Revenue (color = region)",
    xaxis=dict(title="₹ Crores"), height=460)

# ── P4: Category × Region Heatmap ───────────────────────
fig_heatmap = go.Figure(go.Heatmap(
    z=cat_reg.values,
    x=cat_reg.columns.tolist(),
    y=cat_reg.index.tolist(),
    colorscale="Blues",
    text=[[f"₹{v:.1f}Cr" for v in row] for row in cat_reg.values],
    texttemplate="%{text}",
    hovertemplate="<b>%{y} × %{x}</b><br>Sales: %{text}<extra></extra>",
    colorbar=dict(title="₹ Crores")))
fig_heatmap.update_layout(**layout_base,
    title="Sales by Category × Region (₹ Crores)",
    xaxis=dict(side="bottom"), height=320)

# ── P4: Seasonal trend ───────────────────────────────────
season_colors = {"Festive Season":C_ORANGE,"New Year Sales":C_BLUE,
                 "Summer":C_RED,"Monsoon":C_TEAL}
fig_season = go.Figure(go.Bar(
    x=season["Season"], y=season["Sales"]/1e7,
    marker_color=[season_colors.get(s,C_GREY) for s in season["Season"]],
    text=[f"{fmt_cr(v)}<br>({v/total_sales*100:.1f}%)"
          for v in season["Sales"]],
    textposition="outside"))
fig_season.update_layout(**layout_base,
    title="Revenue by Season",
    yaxis=dict(title="₹ Crores"), height=320)

# ── P4: Quarterly trend ──────────────────────────────────
fig_quarterly = go.Figure()
fig_quarterly.add_trace(go.Bar(
    x=quarterly["Label"], y=quarterly["Sales"]/1e7,
    name="Sales", marker_color=C_BLUE, opacity=0.85))
fig_quarterly.add_trace(go.Bar(
    x=quarterly["Label"], y=quarterly["Profit"]/1e7,
    name="Profit", marker_color=C_GREEN, opacity=0.85))
fig_quarterly.update_layout(**layout_base,
    title="Quarterly Sales & Profit Trend",
    barmode="group", xaxis_tickangle=-30,
    yaxis=dict(title="₹ Crores"),
    legend=dict(orientation="h", y=1.1), height=320)

print("  All charts built")

# ═════════════════════════════════════════════════════════
# CONVERT FIGURES TO HTML DIVS
# ═════════════════════════════════════════════════════════
print("  Converting to HTML...")

def fig_html(fig, div_id):
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id)

# ═════════════════════════════════════════════════════════
# ASSEMBLE FULL HTML
# ═════════════════════════════════════════════════════════

def kpi_card(label, value, subtitle="", color=C_BLUE):
    return f"""
    <div class="kpi-card" style="border-top: 4px solid {color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{subtitle}</div>
    </div>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>E-Commerce Sales & Customer Analytics Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: {BG}; color: #2C3E50; }}

  /* ── Header ── */
  .header {{
    background: {HDR_BG};
    color: white;
    padding: 18px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .header h1 {{ font-size: 20px; font-weight: 600; }}
  .header .subtitle {{ font-size: 12px; color: #BDD7EE; margin-top: 4px; }}
  .header .date {{ font-size: 11px; color: #BDD7EE; }}

  /* ── Tabs ── */
  .tab-bar {{
    background: #2C3E50;
    display: flex;
    padding: 0 32px;
  }}
  .tab {{
    padding: 12px 22px;
    cursor: pointer;
    color: #BDD7EE;
    font-size: 13px;
    font-weight: 500;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
  }}
  .tab:hover {{ color: white; }}
  .tab.active {{
    color: white;
    border-bottom: 3px solid #E67E22;
    background: rgba(255,255,255,0.05);
  }}

  /* ── Pages ── */
  .page {{ display: none; padding: 24px 28px; }}
  .page.active {{ display: block; }}

  /* ── KPI Cards ── */
  .kpi-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-bottom: 22px;
  }}
  .kpi-card {{
    background: white;
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
  }}
  .kpi-label {{ font-size: 11px; color: #7F8C8D; text-transform: uppercase;
                letter-spacing: 0.5px; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 22px; font-weight: 700; color: #1F3864; }}
  .kpi-sub {{ font-size: 10px; color: #95A5A6; margin-top: 4px; }}

  /* ── Chart grid ── */
  .chart-row {{
    display: grid;
    gap: 16px;
    margin-bottom: 18px;
  }}
  .col-1 {{ grid-template-columns: 1fr; }}
  .col-2 {{ grid-template-columns: 1fr 1fr; }}
  .col-3 {{ grid-template-columns: 1fr 1fr 1fr; }}
  .col-2-1 {{ grid-template-columns: 2fr 1fr; }}
  .col-1-2 {{ grid-template-columns: 1fr 2fr; }}

  .chart-box {{
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    overflow: hidden;
  }}

  /* ── Section titles ── */
  .section-title {{
    font-size: 13px; font-weight: 700; color: {HDR_BG};
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-bottom: 14px; padding-bottom: 6px;
    border-bottom: 2px solid #E8EEF4;
  }}

  /* ── Insight boxes ── */
  .insight-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 14px;
    margin-top: 20px;
  }}
  .insight-card {{
    background: white;
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border-left: 4px solid {C_BLUE};
  }}
  .insight-card.warn  {{ border-left-color: {C_ORANGE}; }}
  .insight-card.alert {{ border-left-color: {C_RED}; }}
  .insight-card.good  {{ border-left-color: {C_GREEN}; }}
  .insight-title {{ font-size: 12px; font-weight: 700; color: {HDR_BG};
                    margin-bottom: 6px; }}
  .insight-obs   {{ font-size: 11px; color: #555; margin-bottom: 5px; }}
  .insight-rec   {{ font-size: 11px; color: {C_GREEN}; font-style: italic; }}

  /* ── Footer ── */
  .footer {{
    background: #2C3E50; color: #7F8C8D;
    text-align: center; padding: 12px;
    font-size: 11px; margin-top: 28px;
  }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div>
    <h1>E-Commerce Sales &amp; Customer Analytics</h1>
    <div class="subtitle">50,000 Orders &bull; 5,000 Customers &bull; 7 Categories &bull; 5 Regions &bull; Jan 2022 – Dec 2024</div>
  </div>
  <div class="date">Total Revenue: ₹{total_sales/1e7:.1f} Crores &bull; Profit Margin: {margin:.1f}%</div>
</div>

<!-- TAB BAR -->
<div class="tab-bar">
  <div class="tab active" onclick="showPage('p1',this)">📊 Executive Overview</div>
  <div class="tab" onclick="showPage('p2',this)">📦 Product Analytics</div>
  <div class="tab" onclick="showPage('p3',this)">👥 Customer Analytics</div>
  <div class="tab" onclick="showPage('p4',this)">🗺️ Regional Analytics</div>
  <div class="tab" onclick="showPage('p5',this)">💡 Business Insights</div>
</div>

<!-- ═══════════════ PAGE 1: EXECUTIVE OVERVIEW ═══════════════ -->
<div id="p1" class="page active">
  <div class="section-title">Key Performance Indicators</div>
  <div class="kpi-row">
    {kpi_card("Total Sales", f"₹{total_sales/1e7:.1f} Cr", "All orders", C_BLUE)}
    {kpi_card("Total Profit", f"₹{total_profit/1e7:.1f} Cr", f"Margin: {margin:.1f}%", C_GREEN)}
    {kpi_card("Total Orders", f"{total_orders:,}", "Jan 2022–Dec 2024", C_ORANGE)}
    {kpi_card("Total Customers", f"{total_cust:,}", "Unique buyers", C_PURPLE)}
    {kpi_card("Avg Order Value", f"₹{aov:,.0f}", "Per order", C_TEAL)}
    {kpi_card("Profit Margin", f"{margin:.1f}%", "Overall", C_GREEN)}
    {kpi_card("Delivery Rate", f"{deliver_rate:.1f}%", "Successfully delivered", C_GREEN)}
    {kpi_card("Cancellation Rate", f"{cancel_rate:.1f}%", "Orders cancelled", C_RED)}
  </div>

  <div class="chart-row col-1">
    <div class="chart-box">{fig_html(fig_monthly, "fig_monthly")}</div>
  </div>
  <div class="chart-row col-2">
    <div class="chart-box">{fig_html(fig_cat_bar, "fig_cat_bar")}</div>
    <div class="chart-box">{fig_html(fig_reg_col, "fig_reg_col")}</div>
  </div>
  <div class="chart-row col-2">
    <div class="chart-box">{fig_html(fig_status, "fig_status")}</div>
    <div class="chart-box">{fig_html(fig_pay, "fig_pay")}</div>
  </div>
</div>

<!-- ═══════════════ PAGE 2: PRODUCT ANALYTICS ═══════════════ -->
<div id="p2" class="page">
  <div class="chart-row col-2">
    <div class="chart-box">{fig_html(fig_top10, "fig_top10")}</div>
    <div class="chart-box">{fig_html(fig_bot10, "fig_bot10")}</div>
  </div>
  <div class="chart-row col-1">
    <div class="chart-box">{fig_html(fig_subcat, "fig_subcat")}</div>
  </div>
  <div class="chart-row col-1">
    <div class="chart-box">{fig_html(fig_scatter, "fig_scatter")}</div>
  </div>
</div>

<!-- ═══════════════ PAGE 3: CUSTOMER ANALYTICS ═══════════════ -->
<div id="p3" class="page">
  <div class="kpi-row">
    {kpi_card("Total Customers", f"{total_cust:,}", "Unique", C_BLUE)}
    {kpi_card("Champions", f"{int(seg_plot[seg_plot['Segment']=='Champions']['Count'].values[0]):,}",
              "RFM top segment", "#27AE60")}
    {kpi_card("At Risk", f"{int(seg_plot[seg_plot['Segment']=='At Risk']['Count'].values[0]):,}",
              "Need win-back", C_ORANGE)}
    {kpi_card("Avg Orders/Customer",
              f"{df.groupby('Customer_ID')['Order_ID'].nunique().mean():.1f}",
              "Per customer", C_PURPLE)}
    {kpi_card("Repeat Customer Rate",
              f"{df[df['Customer_Type']=='Returning']['Customer_ID'].nunique()/total_cust*100:.1f}%",
              "Returning customers", C_GREEN)}
    {kpi_card("Revenue per Customer", f"₹{total_sales/total_cust/1e3:.0f}K",
              "Lifetime avg", C_TEAL)}
  </div>
  <div class="chart-row col-2">
    <div class="chart-box">{fig_html(fig_rfm_donut, "fig_rfm_donut")}</div>
    <div class="chart-box">{fig_html(fig_rfm_rev, "fig_rfm_rev")}</div>
  </div>
  <div class="chart-row col-2">
    <div class="chart-box">{fig_html(fig_ctype, "fig_ctype")}</div>
    <div class="chart-box">{fig_html(fig_age, "fig_age")}</div>
  </div>
  <div class="chart-row col-1">
    <div class="chart-box">{fig_html(fig_top_cust, "fig_top_cust")}</div>
  </div>
</div>

<!-- ═══════════════ PAGE 4: REGIONAL ANALYTICS ═══════════════ -->
<div id="p4" class="page">
  <div class="chart-row col-2">
    <div class="chart-box">{fig_html(fig_states, "fig_states")}</div>
    <div class="chart-box">{fig_html(fig_heatmap, "fig_heatmap")}</div>
  </div>
  <div class="chart-row col-2">
    <div class="chart-box">{fig_html(fig_season, "fig_season")}</div>
    <div class="chart-box">{fig_html(fig_quarterly, "fig_quarterly")}</div>
  </div>
</div>

<!-- ═══════════════ PAGE 5: BUSINESS INSIGHTS ═══════════════ -->
<div id="p5" class="page">
  <div class="section-title">Data-Driven Business Insights & Recommendations</div>

  <div class="insight-grid">
    <div class="insight-card warn">
      <div class="insight-title">⚠️ Insight 1 — Electronics Concentration Risk</div>
      <div class="insight-obs"><b>Observation:</b> Electronics = 79.4% of total revenue (₹162.6 Cr) with 47.7% margin.</div>
      <div class="insight-obs"><b>Insight:</b> High dependency on one category creates significant supply chain and market risk.</div>
      <div class="insight-rec">→ Grow Clothing (45.5%) and Beauty (45.4%) to diversify. Target Electronics below 65% in 2 years.</div>
    </div>
    <div class="insight-card alert">
      <div class="insight-title">🚨 Insight 2 — Groceries: 20.4% Margin</div>
      <div class="insight-obs"><b>Observation:</b> Groceries generate only ₹1.6L profit on ₹7.9L sales — lowest margin by far.</div>
      <div class="insight-obs"><b>Insight:</b> Storage, logistics, and handling costs likely erode this margin further in reality.</div>
      <div class="insight-rec">→ Reduce Groceries SKUs. Do not invest marketing budget here. Re-price staples.</div>
    </div>
    <div class="insight-card">
      <div class="insight-title">📍 Insight 3 — Central Region Underperformance</div>
      <div class="insight-obs"><b>Observation:</b> Central = only 11% of revenue (₹22.5 Cr) vs North's 25.3% (₹51.7 Cr).</div>
      <div class="insight-obs"><b>Insight:</b> Lower digital penetration, fewer logistics options, and limited brand awareness.</div>
      <div class="insight-rec">→ Invest in Central logistics. Run campaigns in Bhopal, Indore, Raipur. Offer COD incentives.</div>
    </div>
    <div class="insight-card warn">
      <div class="insight-title">🎉 Insight 4 — Festive Season = 36.3% of Revenue</div>
      <div class="insight-obs"><b>Observation:</b> Oct–Dec drives 36.3% of annual revenue. Q4 2022 grew 108% QoQ.</div>
      <div class="insight-obs"><b>Insight:</b> High seasonal dependency is a risk — one bad Diwali campaign = missed annual targets.</div>
      <div class="insight-rec">→ Build a July–August mid-year sale. Begin inventory build 8–10 weeks before Diwali.</div>
    </div>
    <div class="insight-card good">
      <div class="insight-title">📱 Insight 5 — UPI at 30%, EMI Opportunity</div>
      <div class="insight-obs"><b>Observation:</b> UPI = 30% of all orders. EMI = 7.2% but likely highest basket size.</div>
      <div class="insight-obs"><b>Insight:</b> EMI customers are buying expensive Electronics — high-value segment.</div>
      <div class="insight-rec">→ Partner with banks for no-cost EMI on Electronics >₹20K. UPI cashback for off-season months.</div>
    </div>
    <div class="insight-card alert">
      <div class="insight-title">❌ Insight 6 — ₹31.1 Cr Lost to Cancellations + Returns</div>
      <div class="insight-obs"><b>Observation:</b> Cancelled: ₹18.8 Cr. Returned: ₹12.3 Cr. Total = 15.2% of sales.</div>
      <div class="insight-obs"><b>Insight:</b> Logistics cost is incurred even for cancelled/returned orders — pure loss.</div>
      <div class="insight-rec">→ Video unboxing return policy for Electronics. Target cancellation rate below 5%.</div>
    </div>
    <div class="insight-card good">
      <div class="insight-title">🔄 Insight 7 — Returning Customers: Volume Advantage</div>
      <div class="insight-obs"><b>Observation:</b> Returning AOV ₹40,900 ≈ New AOV ₹41,083 but Returning = 30,077 orders vs 19,923.</div>
      <div class="insight-obs"><b>Insight:</b> Lifetime value driven by frequency, not basket size.</div>
      <div class="insight-rec">→ Loyalty programme: reward every 5th order. Re-engage customers inactive for 90+ days.</div>
    </div>
    <div class="insight-card warn">
      <div class="insight-title">🎯 Insight 8 — 1,606 At Risk Customers</div>
      <div class="insight-obs"><b>Observation:</b> RFM identifies 1,606 customers who previously bought but are now inactive.</div>
      <div class="insight-obs"><b>Insight:</b> Win-back cost is 5x cheaper than new customer acquisition.</div>
      <div class="insight-rec">→ Personalised win-back email with 10% discount. Auto-trigger at 60 days inactivity.</div>
    </div>
    <div class="insight-card">
      <div class="insight-title">📉 Insight 9 — Volume Traps (High Sales, Low Margin)</div>
      <div class="insight-obs"><b>Observation:</b> 10 products have sales >₹10L but margin &lt;35% (mainly Home & Kitchen, Sports).</div>
      <div class="insight-obs"><b>Insight:</b> These consume resources without proportional profit contribution.</div>
      <div class="insight-rec">→ Reduce discounts by 5%. Bundle with high-margin items. De-list if margin stays below 25%.</div>
    </div>
  </div>

  <div style="margin-top:24px; background:white; border-radius:8px; padding:20px;
              box-shadow: 0 1px 6px rgba(0,0,0,0.07);">
    <div class="section-title">Priority Action Plan</div>
    <table style="width:100%; border-collapse:collapse; font-size:12px;">
      <thead>
        <tr style="background:{HDR_BG}; color:white;">
          <th style="padding:10px; text-align:left;">#</th>
          <th style="padding:10px; text-align:left;">Action</th>
          <th style="padding:10px; text-align:left;">Expected Impact</th>
          <th style="padding:10px; text-align:center;">Priority</th>
        </tr>
      </thead>
      <tbody>
        {"".join(f'''<tr style="background:{'#F8F9FA' if i%2==0 else 'white'}; border-bottom:1px solid #EEE;">
          <td style="padding:9px 10px; font-weight:700; color:{HDR_BG};">{row[0]}</td>
          <td style="padding:9px 10px;">{row[1]}</td>
          <td style="padding:9px 10px; color:{C_GREEN};">{row[2]}</td>
          <td style="padding:9px 10px; text-align:center;">{row[3]}</td>
        </tr>''' for i, row in enumerate([
            (1, "Win-Back campaign for 1,606 At Risk customers", "+₹5–8 Cr recovery", "🔴 Critical"),
            (2, "No-cost EMI for Electronics orders >₹20K", "+15–20% Electronics AOV", "🔴 Critical"),
            (3, "Reduce cancellation rate from 9% to 5%", "Recover ₹8–10 Cr", "🔴 Critical"),
            (4, "Build July–August mid-year sale event", "Reduce festive dependency", "🟠 High"),
            (5, "Reduce Groceries SKUs to high-margin items", "+1–2% overall margin", "🟠 High"),
            (6, "Invest in Central India logistics", "Unlock ₹20–30 Cr market", "🟠 High"),
            (7, "Grow Clothing & Beauty categories", "Revenue diversification", "🟡 Medium"),
            (8, "Loyalty programme for 726 Champions", "Protect ₹55 Cr revenue base", "🟡 Medium"),
        ]))}
      </tbody>
    </table>
  </div>
</div>

<!-- FOOTER -->
<div class="footer">
  E-Commerce Sales & Customer Analytics | Built with Python + Plotly |
  Data: 50,000 orders · 5,000 customers · ₹204.9 Crores · Jan 2022 – Dec 2024
</div>

<script>
function showPage(pageId, tabEl) {{
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(pageId).classList.add('active');
  tabEl.classList.add('active');
}}
</script>

</body>
</html>"""

# ── Write file ───────────────────────────────────────────
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = os.path.getsize(OUT) / (1024*1024)
print(f"\n{'='*60}")
print("  Phase 8 — Interactive Dashboard COMPLETE")
print(f"{'='*60}")
print(f"\n  File : {os.path.abspath(OUT)}")
print(f"  Size : {size_mb:.1f} MB")
print(f"\n  Open in browser:")
print(f"  powerbi/ecommerce_dashboard.html")
print(f"\n  Pages:")
print("    1. Executive Overview — 8 KPIs + monthly trend + category + region")
print("    2. Product Analytics  — top/bottom 10 + sub-category + scatter")
print("    3. Customer Analytics — RFM segments + new vs returning + top 15")
print("    4. Regional Analytics — state bar + heatmap + seasonal + quarterly")
print("    5. Business Insights  — 9 insights + priority action table")
