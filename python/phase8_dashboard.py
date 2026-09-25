"""
phase8_dashboard.py  —  Professional Interactive Dashboard
Output: powerbi/ecommerce_dashboard.html
"""

import pandas as pd
import numpy as np
import os, json, warnings
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

BASE  = os.path.join(os.path.dirname(__file__), "..")
CLEAN = os.path.join(BASE, "data", "cleaned", "ecommerce_cleaned.csv")
RFM   = os.path.join(BASE, "data", "cleaned", "rfm_segments.csv")
RAW   = os.path.join(BASE, "data", "raw")
OUT   = os.path.join(BASE, "powerbi", "ecommerce_dashboard.html")

print("Loading data...")
df  = pd.read_csv(CLEAN, parse_dates=["Order_Date"])
rfm = pd.read_csv(RFM)
cust_raw = pd.read_csv(os.path.join(RAW, "customers.csv"))

# ── palette ─────────────────────────────────────────────
TEAL   = "#00D4AA"
BLUE   = "#4A9EFF"
ORANGE = "#FFB347"
RED    = "#FF6B6B"
PURPLE = "#A855F7"
YELLOW = "#F59E0B"
GREEN  = "#10B981"
PAL    = [TEAL, BLUE, ORANGE, RED, PURPLE, YELLOW, GREEN]

PAPER  = "rgba(0,0,0,0)"
PLOT   = "rgba(0,0,0,0)"
FONT_C = "#E8F0FE"
GRID_C = "rgba(136,153,170,0.12)"
CARD   = "#112233"

BASE_LAYOUT = dict(
    paper_bgcolor=PAPER, plot_bgcolor=PLOT,
    font=dict(family="Inter, Segoe UI, Arial", size=11, color=FONT_C),
    margin=dict(l=10, r=10, t=46, b=10),
    title_font=dict(size=13, color=FONT_C),
    legend=dict(font=dict(color=FONT_C), bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
               tickfont=dict(color="#8899AA"), title_font=dict(color="#8899AA")),
    yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
               tickfont=dict(color="#8899AA"), title_font=dict(color="#8899AA")),
)

MCFG = {"displayModeBar": False}

def fig2html(fig, div_id=""):
    return fig.to_html(full_html=False, include_plotlyjs=False,
                       div_id=div_id, config=MCFG)

def apply(fig, **extra):
    layout = {**BASE_LAYOUT, **extra}
    fig.update_layout(**layout)
    return fig

print("Computing aggregations...")

# ── KPIs ────────────────────────────────────────────────
ts   = df["Sales"].sum()
tp   = df["Profit"].sum()
tc   = df["Cost"].sum()
to   = df["Order_ID"].nunique()
tcu  = df["Customer_ID"].nunique()
tq   = df["Quantity"].sum()
aov  = ts / to
mgn  = tp / ts * 100
delr = df[df["Order_Status"]=="Delivered"]["Order_ID"].nunique() / to * 100
canr = df[df["Order_Status"]=="Cancelled"]["Order_ID"].nunique() / to * 100
retr = df[df["Customer_Type"]=="Returning"]["Customer_ID"].nunique() / tcu * 100

# ── Aggregations ────────────────────────────────────────
monthly = (df.groupby("Order_YearMonth", as_index=False)
           .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                Orders=("Order_ID","nunique"))
           .sort_values("Order_YearMonth"))
monthly["Margin"] = (monthly["Profit"]/monthly["Sales"]*100).round(1)

cat = (df.groupby("Category", as_index=False)
       .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
       .sort_values("Sales", ascending=False))
cat["Margin"] = (cat["Profit"]/cat["Sales"]*100).round(1)

region = (df.groupby("Region", as_index=False)
          .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
               Orders=("Order_ID","nunique"))
          .sort_values("Sales", ascending=False))

pay = (df.groupby("Payment_Mode")["Order_ID"].nunique()
       .reset_index().rename(columns={"Order_ID":"Count"})
       .sort_values("Count", ascending=False))

status = (df.groupby("Order_Status")["Order_ID"].nunique()
          .reset_index().rename(columns={"Order_ID":"Count"})
          .sort_values("Count", ascending=False))

top10 = (df.groupby("Product_Name", as_index=False)
         .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Qty=("Quantity","sum"))
         .nlargest(10,"Sales").sort_values("Sales"))
top10["Margin"] = (top10["Profit"]/top10["Sales"]*100).round(1)

bot10 = (df.groupby("Product_Name", as_index=False)
         .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
         .nsmallest(10,"Sales").sort_values("Sales", ascending=False))

sub = (df.groupby(["Category","Sub_Category"], as_index=False)
       .agg(Sales=("Sales","sum"))
       .sort_values("Sales", ascending=False).head(16))

prod_grp = (df.groupby(["Product_Name","Category"], as_index=False)
            .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Qty=("Quantity","sum")))

age_order = ["18–25","26–35","36–45","46–55","56+"]
age = (df.groupby("Age_Group", as_index=False)
       .agg(Sales=("Sales","sum"), Customers=("Customer_ID","nunique"))
       .assign(Age_Group=lambda x: pd.Categorical(
           x["Age_Group"], categories=age_order, ordered=True))
       .sort_values("Age_Group"))

ctype = (df.groupby("Customer_Type", as_index=False)
         .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"),
              Customers=("Customer_ID","nunique")))
ctype["AOV"] = (ctype["Sales"]/ctype["Orders"]).round(0)

seg_order = ["Champions","Loyal Customers","At Risk","Hibernating","Lost"]
SEG_C = {"Champions":TEAL,"Loyal Customers":BLUE,"At Risk":ORANGE,
          "Hibernating":RED,"Lost":"#8899AA"}
seg = (rfm.groupby("Segment", as_index=False)
       .agg(Count=("Customer_ID","count"), Revenue=("Monetary","sum"),
            AvgSpend=("Monetary","mean"))
       .assign(Segment=lambda x: pd.Categorical(
           x["Segment"], categories=seg_order, ordered=True))
       .sort_values("Segment"))

top_cust = (df.groupby("Customer_ID", as_index=False)
            .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"))
            .nlargest(15,"Sales")
            .merge(cust_raw[["Customer_ID","Customer_Name","Region","Customer_Type"]],
                   on="Customer_ID")
            .sort_values("Sales"))

state_s = (df.groupby(["State","Region"], as_index=False)
           .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique"))
           .sort_values("Sales", ascending=False).head(15)
           .sort_values("Sales"))

cat_reg = (df.groupby(["Category","Region"])["Sales"]
           .sum().unstack(fill_value=0)/1e7)

season_order = ["Festive Season","New Year Sales","Summer","Monsoon"]
seas = (df.groupby("Season", as_index=False)
        .agg(Sales=("Sales","sum"), Orders=("Order_ID","nunique")))
seas["Pct"] = (seas["Sales"]/ts*100).round(1)

qtr = (df.groupby(["Order_Year","Order_Quarter"], as_index=False)
       .agg(Sales=("Sales","sum"), Profit=("Profit","sum")))
qtr["Label"] = qtr["Order_Year"].astype(str)+" Q"+qtr["Order_Quarter"].astype(str)

print("Building charts...")

# ════════════════════════════════════════════════════════
# PAGE 1 CHARTS
# ════════════════════════════════════════════════════════

# Monthly trend
f_monthly = go.Figure()
x_labels  = monthly["Order_YearMonth"].astype(str).tolist()
f_monthly.add_trace(go.Scatter(
    x=x_labels, y=monthly["Sales"]/1e7, name="Sales",
    line=dict(color=TEAL, width=2.5, shape="spline"),
    fill="tozeroy", fillcolor="rgba(0,212,170,0.07)",
    hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:.1f}Cr<extra></extra>"))
f_monthly.add_trace(go.Scatter(
    x=x_labels, y=monthly["Profit"]/1e7, name="Profit",
    line=dict(color=BLUE, width=2, shape="spline", dash="dot"),
    fill="tozeroy", fillcolor="rgba(74,158,255,0.05)",
    hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:.1f}Cr<extra></extra>"))
for yr in ["2023-01","2024-01"]:
    if yr in x_labels:
        i = x_labels.index(yr)
        f_monthly.add_shape(type="line", x0=i, x1=i, y0=0, y1=1,
            yref="paper", line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"))
        f_monthly.add_annotation(x=i, y=0.97, yref="paper",
            text=yr[:4], showarrow=False,
            font=dict(size=9, color="#8899AA"))
apply(f_monthly, title="Monthly Sales & Profit Trend (Jan 2022 – Dec 2024)",
      height=320, legend=dict(orientation="h", y=1.12, x=0),
      xaxis=dict(tickangle=-40, tickfont=dict(size=8, color="#8899AA"),
                 gridcolor=GRID_C, zerolinecolor=GRID_C),
      yaxis=dict(title="₹ Crores", tickprefix="₹",
                 gridcolor=GRID_C, zerolinecolor=GRID_C,
                 tickfont=dict(color="#8899AA")))

# Category bar
f_cat = go.Figure(go.Bar(
    x=cat["Sales"]/1e7, y=cat["Category"], orientation="h",
    marker=dict(
        color=cat["Sales"]/1e7,
        colorscale=[[0,"#112233"],[0.3,BLUE],[1,TEAL]],
        line=dict(width=0)),
    text=[f"₹{v/1e7:.1f}Cr" for v in cat["Sales"]],
    textposition="outside", textfont=dict(color="#8899AA", size=9),
    hovertemplate="<b>%{y}</b><br>₹%{x:.1f}Cr<extra></extra>"))
apply(f_cat, title="Sales by Category", height=280,
      xaxis=dict(title="₹ Crores", gridcolor=GRID_C, zerolinecolor=GRID_C,
                 tickfont=dict(color="#8899AA")),
      yaxis=dict(autorange="reversed", gridcolor=GRID_C,
                 tickfont=dict(color=FONT_C, size=10)))

# Region grouped bar
f_reg = go.Figure()
f_reg.add_trace(go.Bar(name="Sales", x=region["Region"],
    y=region["Sales"]/1e7, marker_color=TEAL, opacity=0.9,
    text=[f"₹{v/1e7:.0f}Cr" for v in region["Sales"]],
    textposition="outside", textfont=dict(size=8.5, color="#8899AA")))
f_reg.add_trace(go.Bar(name="Profit", x=region["Region"],
    y=region["Profit"]/1e7, marker_color=BLUE, opacity=0.9,
    text=[f"₹{v/1e7:.0f}Cr" for v in region["Profit"]],
    textposition="outside", textfont=dict(size=8.5, color="#8899AA")))
apply(f_reg, title="Sales & Profit by Region", barmode="group", height=280,
      legend=dict(orientation="h", y=1.12),
      yaxis=dict(title="₹ Crores", gridcolor=GRID_C, zerolinecolor=GRID_C,
                 tickfont=dict(color="#8899AA")),
      xaxis=dict(tickfont=dict(color=FONT_C)))

# Order status donut
st_colors = {"Delivered":TEAL,"Shipped":BLUE,"Cancelled":RED,
             "Returned":ORANGE,"Processing":PURPLE}
f_status = go.Figure(go.Pie(
    labels=status["Order_Status"], values=status["Count"], hole=0.6,
    marker=dict(colors=[st_colors.get(s,"#8899AA") for s in status["Order_Status"]],
                line=dict(color="#0D1B2A", width=2)),
    textinfo="percent", textfont=dict(size=10, color=FONT_C),
    hovertemplate="<b>%{label}</b><br>%{value:,} orders (%{percent})<extra></extra>"))
f_status.add_annotation(text=f"<b>{to:,}</b><br><span style='font-size:10px'>Orders</span>",
    x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=FONT_C))
apply(f_status, title="Order Status", height=300,
      legend=dict(orientation="v", x=1.01, y=0.5))

# Payment donut
f_pay = go.Figure(go.Pie(
    labels=pay["Payment_Mode"], values=pay["Count"], hole=0.6,
    marker=dict(colors=PAL[:len(pay)],
                line=dict(color="#0D1B2A", width=2)),
    textinfo="percent", textfont=dict(size=10, color=FONT_C),
    hovertemplate="<b>%{label}</b><br>%{value:,} orders (%{percent})<extra></extra>"))
f_pay.add_annotation(text=f"<b>{pay['Count'].iloc[0]:,}</b><br><span style='font-size:9px'>UPI (Top)</span>",
    x=0.5, y=0.5, showarrow=False, font=dict(size=13, color=FONT_C))
apply(f_pay, title="Payment Mode", height=300,
      legend=dict(orientation="v", x=1.01, y=0.5))

# ════════════════════════════════════════════════════════
# PAGE 2 CHARTS
# ════════════════════════════════════════════════════════

f_top10 = go.Figure(go.Bar(
    y=top10["Product_Name"], x=top10["Sales"]/1e5, orientation="h",
    marker=dict(color=top10["Sales"]/1e5,
                colorscale=[[0,BLUE],[1,TEAL]],
                line=dict(width=0)),
    text=[f"₹{v/1e5:.0f}L  {m:.0f}%" for v,m in zip(top10["Sales"],top10["Margin"])],
    textposition="outside", textfont=dict(size=8.5, color="#8899AA"),
    hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:.0f}L<extra></extra>"))
apply(f_top10, title="Top 10 Products by Revenue", height=380,
      xaxis=dict(title="₹ Lakhs", gridcolor=GRID_C, zerolinecolor=GRID_C,
                 tickfont=dict(color="#8899AA")),
      yaxis=dict(autorange="reversed", tickfont=dict(color=FONT_C, size=9.5)))

f_bot10 = go.Figure(go.Bar(
    y=bot10["Product_Name"], x=bot10["Sales"]/1e5, orientation="h",
    marker=dict(color=bot10["Sales"]/1e5,
                colorscale=[[0,RED],[1,ORANGE]],
                reversescale=True, line=dict(width=0)),
    text=[f"₹{v/1e5:.2f}L" for v in bot10["Sales"]],
    textposition="outside", textfont=dict(size=8.5, color="#8899AA"),
    hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:.2f}L<extra></extra>"))
apply(f_bot10, title="Bottom 10 Products (Lowest Revenue)", height=380,
      xaxis=dict(title="₹ Lakhs", gridcolor=GRID_C, zerolinecolor=GRID_C,
                 tickfont=dict(color="#8899AA")),
      yaxis=dict(tickfont=dict(color=FONT_C, size=9.5)))

f_sub = go.Figure()
cat_names = sub["Category"].unique()
for i, cn in enumerate(cat_names):
    g = sub[sub["Category"]==cn]
    f_sub.add_trace(go.Bar(
        x=g["Sub_Category"], y=g["Sales"]/1e7,
        name=cn, marker_color=PAL[i % len(PAL)], opacity=0.9))
apply(f_sub, title="Sub-Category Revenue Breakdown", barmode="group",
      height=340, xaxis=dict(tickangle=-30, tickfont=dict(color=FONT_C, size=8.5),
                             gridcolor=GRID_C),
      yaxis=dict(title="₹ Crores", gridcolor=GRID_C, tickfont=dict(color="#8899AA")),
      legend=dict(orientation="h", y=1.12))

f_scatter = px.scatter(prod_grp, x="Sales", y="Profit", size="Qty", color="Category",
    hover_name="Product_Name", color_discrete_sequence=PAL,
    labels={"Sales":"Total Sales (₹)","Profit":"Total Profit (₹)"},
    title="Sales vs Profit by Product  (bubble = units sold)")
f_scatter.update_traces(marker=dict(opacity=0.75, line=dict(width=0.5, color="#0D1B2A"),
                                    sizemin=4))
apply(f_scatter, height=400,
      xaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C, tickfont=dict(color="#8899AA")),
      yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C, tickfont=dict(color="#8899AA")))

# ════════════════════════════════════════════════════════
# PAGE 3 CHARTS
# ════════════════════════════════════════════════════════

seg_clean = seg.dropna(subset=["Segment"]).reset_index(drop=True)

f_rfm_donut = go.Figure(go.Pie(
    labels=seg_clean["Segment"], values=seg_clean["Count"], hole=0.58,
    marker=dict(colors=[SEG_C.get(s,BLUE) for s in seg_clean["Segment"]],
                line=dict(color="#0D1B2A", width=2)),
    textinfo="percent+label", textfont=dict(size=9.5, color=FONT_C),
    hovertemplate="<b>%{label}</b><br>%{value:,} customers (%{percent})<extra></extra>"))
f_rfm_donut.add_annotation(
    text=f"<b>{len(rfm):,}</b><br><span>Customers</span>",
    x=0.5, y=0.5, showarrow=False, font=dict(size=13, color=FONT_C))
apply(f_rfm_donut, title="RFM Customer Segments", height=340,
      legend=dict(orientation="v", x=1.02, y=0.5))

f_rfm_rev = go.Figure(go.Bar(
    y=seg_clean["Segment"], x=seg_clean["Revenue"]/1e7, orientation="h",
    marker=dict(color=[SEG_C.get(s,BLUE) for s in seg_clean["Segment"]],
                line=dict(width=0), opacity=0.9),
    text=[f"₹{v/1e7:.1f}Cr" for v in seg_clean["Revenue"]],
    textposition="outside", textfont=dict(size=9, color="#8899AA")))
apply(f_rfm_rev, title="Revenue by RFM Segment", height=340,
      xaxis=dict(title="₹ Crores", gridcolor=GRID_C, zerolinecolor=GRID_C,
                 tickfont=dict(color="#8899AA")),
      yaxis=dict(tickfont=dict(color=FONT_C), autorange="reversed"))

f_ctype = make_subplots(rows=1, cols=2,
    subplot_titles=["Revenue by Type","Orders by Type"])
for row in ctype.itertuples():
    clr = TEAL if row.Customer_Type == "Returning" else BLUE
    f_ctype.add_trace(go.Bar(
        x=[row.Customer_Type], y=[row.Sales/1e7], name=row.Customer_Type,
        marker_color=clr, showlegend=False,
        text=[f"₹{row.Sales/1e7:.1f}Cr"], textposition="outside",
        textfont=dict(size=10, color="#8899AA")), row=1, col=1)
    f_ctype.add_trace(go.Bar(
        x=[row.Customer_Type], y=[row.Orders], name=row.Customer_Type,
        marker_color=clr, showlegend=False,
        text=[f"{row.Orders:,}"], textposition="outside",
        textfont=dict(size=10, color="#8899AA")), row=1, col=2)
f_ctype.update_layout(**{**BASE_LAYOUT,
    "title":"New vs Returning Customer Comparison","height":300,
    "paper_bgcolor":PAPER,"plot_bgcolor":PLOT})
f_ctype.update_xaxes(tickfont=dict(color=FONT_C))
f_ctype.update_yaxes(gridcolor=GRID_C, zerolinecolor=GRID_C,
                     tickfont=dict(color="#8899AA"))
for ann in f_ctype.layout.annotations:
    ann.font = dict(color="#8899AA", size=10)

f_age = go.Figure(go.Bar(
    x=age["Age_Group"].astype(str), y=age["Sales"]/1e7,
    marker=dict(color=age["Sales"]/1e7,
                colorscale=[[0,BLUE],[1,TEAL]], line=dict(width=0)),
    text=[f"₹{v/1e7:.1f}Cr" for v in age["Sales"]],
    textposition="outside", textfont=dict(size=9, color="#8899AA")))
apply(f_age, title="Revenue by Customer Age Group", height=280,
      xaxis=dict(tickfont=dict(color=FONT_C)),
      yaxis=dict(title="₹ Crores", gridcolor=GRID_C, tickfont=dict(color="#8899AA")))

f_top_cust = go.Figure(go.Bar(
    y=top_cust["Customer_Name"]+" ("+top_cust["Region"]+")",
    x=top_cust["Sales"]/1e5, orientation="h",
    marker=dict(
        color=[TEAL if t=="Returning" else ORANGE for t in top_cust["Customer_Type"]],
        line=dict(width=0), opacity=0.9),
    text=[f"₹{v/1e5:.0f}L" for v in top_cust["Sales"]],
    textposition="outside", textfont=dict(size=8.5, color="#8899AA"),
    hovertemplate="<b>%{y}</b><br>₹%{x:.0f}L<extra></extra>"))
apply(f_top_cust, title="Top 15 Customers  (Teal=Returning · Orange=New)",
      height=480,
      xaxis=dict(title="₹ Lakhs", gridcolor=GRID_C, tickfont=dict(color="#8899AA")),
      yaxis=dict(autorange="reversed", tickfont=dict(color=FONT_C, size=9)))

# ════════════════════════════════════════════════════════
# PAGE 4 CHARTS
# ════════════════════════════════════════════════════════
REG_C = {"North":TEAL,"South":BLUE,"East":ORANGE,"West":PURPLE,"Central":YELLOW}

f_states = go.Figure(go.Bar(
    y=state_s["State"]+" ("+state_s["Region"]+")",
    x=state_s["Sales"]/1e7, orientation="h",
    marker=dict(color=[REG_C.get(r,BLUE) for r in state_s["Region"]],
                line=dict(width=0), opacity=0.9),
    text=[f"₹{v/1e7:.1f}Cr" for v in state_s["Sales"]],
    textposition="outside", textfont=dict(size=8.5, color="#8899AA")))
apply(f_states, title="Top 15 States by Revenue (color = region)", height=480,
      xaxis=dict(title="₹ Crores", gridcolor=GRID_C, tickfont=dict(color="#8899AA")),
      yaxis=dict(autorange="reversed", tickfont=dict(color=FONT_C, size=9.5)))

f_heat = go.Figure(go.Heatmap(
    z=cat_reg.values, x=cat_reg.columns.tolist(), y=cat_reg.index.tolist(),
    colorscale=[[0,"#0D1B2A"],[0.3,"#1A3A5C"],[0.7,BLUE],[1,TEAL]],
    text=[[f"₹{v:.1f}Cr" for v in row] for row in cat_reg.values],
    texttemplate="%{text}", textfont=dict(size=9, color=FONT_C),
    hovertemplate="<b>%{y} × %{x}</b><br>₹%{text}<extra></extra>",
    colorbar=dict(tickfont=dict(color="#8899AA"), title=dict(text="₹Cr",font=dict(color="#8899AA")))))
apply(f_heat, title="Sales Heatmap — Category × Region (₹ Crores)", height=320,
      xaxis=dict(tickfont=dict(color=FONT_C, size=10), side="bottom"),
      yaxis=dict(tickfont=dict(color=FONT_C, size=10)))

seas_c = {"Festive Season":ORANGE,"New Year Sales":TEAL,"Summer":RED,"Monsoon":BLUE}
f_seas = go.Figure(go.Bar(
    x=seas["Season"], y=seas["Sales"]/1e7,
    marker=dict(color=[seas_c.get(s,BLUE) for s in seas["Season"]],
                line=dict(width=0)),
    text=[f"₹{v/1e7:.1f}Cr<br>({p:.1f}%)" for v,p in zip(seas["Sales"],seas["Pct"])],
    textposition="outside", textfont=dict(size=9, color="#8899AA")))
apply(f_seas, title="Revenue by Season", height=320,
      xaxis=dict(tickfont=dict(color=FONT_C)),
      yaxis=dict(title="₹ Crores", gridcolor=GRID_C, tickfont=dict(color="#8899AA")))

f_qtr = go.Figure()
f_qtr.add_trace(go.Bar(x=qtr["Label"], y=qtr["Sales"]/1e7, name="Sales",
    marker_color=TEAL, opacity=0.85,
    text=[f"₹{v/1e7:.0f}Cr" for v in qtr["Sales"]],
    textposition="outside", textfont=dict(size=8, color="#8899AA")))
f_qtr.add_trace(go.Bar(x=qtr["Label"], y=qtr["Profit"]/1e7, name="Profit",
    marker_color=BLUE, opacity=0.85))
apply(f_qtr, title="Quarterly Revenue & Profit", barmode="group", height=320,
      xaxis=dict(tickangle=-30, tickfont=dict(color=FONT_C, size=8.5)),
      yaxis=dict(title="₹ Crores", gridcolor=GRID_C, tickfont=dict(color="#8899AA")),
      legend=dict(orientation="h", y=1.12))

print("All charts built. Assembling HTML...")

# ════════════════════════════════════════════════════════
# HTML HELPERS
# ════════════════════════════════════════════════════════

def kpi(icon, label, value, sub="", color=TEAL):
    return f"""
<div class="kpi-card" style="--accent:{color};">
  <div class="kpi-icon">{icon}</div>
  <div class="kpi-body">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
    <div class="kpi-sub">{sub}</div>
  </div>
</div>"""

def chart_box(fig, div_id, span=1):
    return f'<div class="chart-card span{span}">{fig2html(fig, div_id)}</div>'

def section(title):
    return f'<div class="section-header"><span>{title}</span></div>'

def nav_item(page_id, icon, label):
    active = 'class="nav-item active"' if page_id == "p1" else 'class="nav-item"'
    return f'<div {active} onclick="switchPage(\'{page_id}\',this)">{icon}<span>{label}</span></div>'

def cust_kpi(label, value, color=TEAL):
    return f'<div class="mini-kpi"><div class="mini-val" style="color:{color}">{value}</div><div class="mini-lbl">{label}</div></div>'

def insight_card(icon, title, obs, rec, color=TEAL):
    return f"""
<div class="ins-card" style="--ic:{color};">
  <div class="ins-head">{icon} {title}</div>
  <div class="ins-obs">{obs}</div>
  <div class="ins-rec">→ {rec}</div>
</div>"""

def badge(text, color):
    return f'<span class="badge" style="background:{color}22;color:{color};border:1px solid {color}44;">{text}</span>'

priority_rows = [
    (1, "Win-Back campaign — 1,606 At Risk customers", "+₹5–8 Cr", RED, "Critical"),
    (2, "No-cost EMI on Electronics >₹20K", "+15–20% AOV", RED, "Critical"),
    (3, "Reduce cancellation rate: 9% → 5%", "Recover ₹8–10 Cr", RED, "Critical"),
    (4, "Build July–August mid-year sale", "Reduce festive dependency", ORANGE, "High"),
    (5, "Reduce Groceries SKUs", "+1–2% overall margin", ORANGE, "High"),
    (6, "Expand Central India logistics", "₹20–30 Cr new market", ORANGE, "High"),
    (7, "Grow Clothing & Beauty categories", "Revenue diversification", YELLOW, "Medium"),
    (8, "Loyalty programme for Champions", "Protect ₹55 Cr base", TEAL, "Medium"),
]

pr_rows_html = ""
for i, (num, action, impact, color, prio) in enumerate(priority_rows):
    bg = "rgba(255,255,255,0.02)" if i % 2 == 0 else "transparent"
    pr_rows_html += f"""
<tr style="background:{bg};">
  <td style="color:{TEAL};font-weight:700;padding:11px 14px;">{num}</td>
  <td style="padding:11px 14px;color:#E8F0FE;">{action}</td>
  <td style="padding:11px 14px;color:{TEAL};">{impact}</td>
  <td style="padding:11px 14px;">{badge(prio, color)}</td>
</tr>"""

# ════════════════════════════════════════════════════════
# FINAL HTML
# ════════════════════════════════════════════════════════
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>E-Commerce Analytics Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
:root{{
  --bg:#0D1B2A; --card:#112233; --sidebar:#0A1628;
  --accent:{TEAL}; --blue:{BLUE}; --orange:{ORANGE}; --red:{RED};
  --text:#E8F0FE; --muted:#8899AA; --border:rgba(0,212,170,0.12);
}}
html,body{{height:100%;overflow:hidden;font-family:'Inter',sans-serif;
          background:var(--bg);color:var(--text);}}

/* scrollbar */
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:#0A1628;}}
::-webkit-scrollbar-thumb{{background:#1E3A5F;border-radius:3px;}}

/* layout */
.shell{{display:flex;height:100vh;}}

/* ── SIDEBAR ─────────────────────────────────── */
.sidebar{{
  width:220px;min-width:220px;
  background:var(--sidebar);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  padding:0;overflow:hidden;
}}
.sb-brand{{
  padding:22px 20px 18px;
  border-bottom:1px solid var(--border);
}}
.sb-brand .logo{{
  font-size:13px;font-weight:700;color:var(--accent);
  letter-spacing:0.5px;text-transform:uppercase;
}}
.sb-brand .tagline{{font-size:10px;color:var(--muted);margin-top:3px;}}
.sb-label{{
  font-size:9px;font-weight:600;color:var(--muted);
  letter-spacing:1.2px;text-transform:uppercase;
  padding:18px 20px 8px;
}}
.nav-item{{
  display:flex;align-items:center;gap:10px;
  padding:11px 20px;cursor:pointer;
  font-size:12.5px;font-weight:500;color:var(--muted);
  border-left:3px solid transparent;
  transition:all 0.18s ease;
  user-select:none;
}}
.nav-item:hover{{color:var(--text);background:rgba(255,255,255,0.03);}}
.nav-item.active{{
  color:var(--accent);
  background:rgba(0,212,170,0.07);
  border-left:3px solid var(--accent);
}}
.nav-item svg,.nav-item .ni{{width:16px;height:16px;flex-shrink:0;}}
.sb-footer{{
  margin-top:auto;padding:16px 20px;
  border-top:1px solid var(--border);
  font-size:10px;color:var(--muted);line-height:1.6;
}}
.sb-footer strong{{color:var(--accent);}}

/* ── MAIN ────────────────────────────────────── */
.main{{flex:1;overflow-y:auto;display:flex;flex-direction:column;}}

.topbar{{
  background:rgba(10,22,40,0.95);
  backdrop-filter:blur(8px);
  padding:14px 28px;
  border-bottom:1px solid var(--border);
  display:flex;justify-content:space-between;align-items:center;
  position:sticky;top:0;z-index:100;
}}
.topbar .page-title{{
  font-size:17px;font-weight:700;
  background:linear-gradient(90deg,var(--accent),var(--blue));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}}
.topbar .meta{{font-size:11px;color:var(--muted);}}
.topbar .badge-row{{display:flex;gap:8px;}}
.meta-badge{{
  background:rgba(0,212,170,0.1);color:var(--accent);
  border:1px solid rgba(0,212,170,0.25);
  border-radius:20px;padding:3px 10px;font-size:10px;font-weight:500;
}}

.content{{padding:22px 24px;flex:1;}}

/* ── PAGES ───────────────────────────────────── */
.page{{display:none;animation:fadeIn 0.22s ease;}}
.page.active{{display:block;}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(6px);}}to{{opacity:1;transform:none;}}}}

/* ── KPI CARDS ───────────────────────────────── */
.kpi-grid{{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:14px;margin-bottom:20px;
}}
.kpi-card{{
  background:var(--card);
  border:1px solid var(--border);
  border-top:3px solid var(--accent);
  border-radius:10px;
  padding:16px 18px;
  display:flex;align-items:flex-start;gap:12px;
  transition:transform 0.18s,box-shadow 0.18s;
}}
.kpi-card:hover{{
  transform:translateY(-2px);
  box-shadow:0 6px 28px rgba(0,0,0,0.35);
}}
.kpi-icon{{
  font-size:22px;line-height:1;
  background:rgba(255,255,255,0.04);
  border-radius:8px;padding:8px;
}}
.kpi-label{{font-size:10px;color:var(--muted);text-transform:uppercase;
            letter-spacing:0.6px;margin-bottom:5px;}}
.kpi-value{{font-size:21px;font-weight:700;color:var(--text);line-height:1;}}
.kpi-sub{{font-size:10px;color:var(--muted);margin-top:5px;}}

/* ── CHART GRID ──────────────────────────────── */
.chart-grid{{
  display:grid;gap:16px;margin-bottom:18px;
}}
.g1{{grid-template-columns:1fr;}}
.g2{{grid-template-columns:1fr 1fr;}}
.g2l{{grid-template-columns:3fr 2fr;}}
.g2r{{grid-template-columns:2fr 3fr;}}
.g3{{grid-template-columns:1fr 1fr 1fr;}}

.chart-card{{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:10px;padding:16px;
  box-shadow:0 4px 24px rgba(0,0,0,0.3);
  transition:box-shadow 0.18s;overflow:hidden;
}}
.chart-card:hover{{box-shadow:0 6px 32px rgba(0,212,170,0.07),0 4px 24px rgba(0,0,0,0.4);}}
.chart-card.span2{{grid-column:span 2;}}
.chart-card.span3{{grid-column:span 3;}}

/* ── SECTION HEADER ──────────────────────────── */
.section-header{{
  margin-bottom:14px;margin-top:6px;
  display:flex;align-items:center;gap:10px;
}}
.section-header span{{
  font-size:11px;font-weight:600;color:var(--muted);
  text-transform:uppercase;letter-spacing:1px;
}}
.section-header::before,.section-header::after{{
  content:'';flex:1;height:1px;
  background:linear-gradient(90deg,var(--border),transparent);
}}
.section-header::before{{background:linear-gradient(90deg,transparent,var(--border));}}

/* ── MINI KPI ROW (customer page) ────────────── */
.mini-kpi-row{{display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;}}
.mini-kpi{{
  background:var(--card);border:1px solid var(--border);
  border-radius:8px;padding:12px 18px;flex:1;min-width:120px;
  text-align:center;
}}
.mini-val{{font-size:20px;font-weight:700;}}
.mini-lbl{{font-size:10px;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;}}

/* ── INSIGHT CARDS ───────────────────────────── */
.ins-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:22px;}}
.ins-card{{
  background:var(--card);
  border:1px solid var(--border);
  border-left:3px solid var(--ic);
  border-radius:10px;padding:16px 18px;
  transition:transform 0.18s;
}}
.ins-card:hover{{transform:translateY(-2px);}}
.ins-head{{font-size:12px;font-weight:700;color:var(--text);margin-bottom:8px;}}
.ins-obs{{font-size:11px;color:var(--muted);line-height:1.6;margin-bottom:8px;}}
.ins-rec{{font-size:11px;color:var(--ic);font-style:italic;line-height:1.5;}}

/* ── PRIORITY TABLE ──────────────────────────── */
.table-card{{
  background:var(--card);border:1px solid var(--border);
  border-radius:10px;overflow:hidden;margin-top:4px;
}}
.table-card table{{width:100%;border-collapse:collapse;font-size:12px;}}
.table-card thead tr{{background:rgba(0,212,170,0.08);}}
.table-card thead th{{
  padding:12px 14px;text-align:left;
  color:var(--muted);font-weight:600;
  font-size:10px;text-transform:uppercase;letter-spacing:0.8px;
  border-bottom:1px solid var(--border);
}}
.table-card tbody tr{{border-bottom:1px solid rgba(255,255,255,0.03);transition:background 0.12s;}}
.table-card tbody tr:hover{{background:rgba(255,255,255,0.03);}}
.badge{{border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;}}

/* ── PAGE 4 specific ─────────────────────────── */
.legend-row{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px;}}
.leg{{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--muted);}}
.leg-dot{{width:10px;height:10px;border-radius:50%;}}
</style>
</head>
<body>
<div class="shell">

<!-- ══════════════ SIDEBAR ══════════════ -->
<div class="sidebar">
  <div class="sb-brand">
    <div class="logo">📊 EcomAnalytics</div>
    <div class="tagline">Sales &amp; Customer Intelligence</div>
  </div>
  <div class="sb-label">Navigation</div>
  {nav_item("p1","📈","Executive Overview")}
  {nav_item("p2","📦","Product Analytics")}
  {nav_item("p3","👥","Customer Analytics")}
  {nav_item("p4","🗺️","Regional Analytics")}
  {nav_item("p5","💡","Business Insights")}
  <div class="sb-footer">
    <strong>Data Analyst Portfolio</strong><br>
    50,000 Orders · 5,000 Customers<br>
    Jan 2022 – Dec 2024<br>
    Tools: Python · SQL · Plotly
  </div>
</div>

<!-- ══════════════ MAIN ══════════════ -->
<div class="main">

<!-- topbar (dynamic title) -->
<div class="topbar">
  <div>
    <div class="page-title" id="page-title">Executive Overview</div>
    <div class="meta" id="page-meta">E-Commerce Sales &amp; Customer Analytics · ₹{ts/1e7:.1f} Crores Revenue · {mgn:.1f}% Margin</div>
  </div>
  <div class="badge-row">
    <span class="meta-badge">50K Orders</span>
    <span class="meta-badge">5K Customers</span>
    <span class="meta-badge">₹{ts/1e7:.0f}Cr Revenue</span>
    <span class="meta-badge">2022–2024</span>
  </div>
</div>

<div class="content">

<!-- ════════════ PAGE 1 ════════════ -->
<div id="p1" class="page active">
  {section("Key Performance Indicators")}
  <div class="kpi-grid">
    {kpi("💰","Total Sales",f"₹{ts/1e7:.1f}Cr","All orders",TEAL)}
    {kpi("📈","Total Profit",f"₹{tp/1e7:.1f}Cr",f"Margin {mgn:.1f}%",GREEN)}
    {kpi("🛒","Total Orders",f"{to:,}","Jan 2022–Dec 2024",BLUE)}
    {kpi("👤","Customers",f"{tcu:,}","Unique buyers",PURPLE)}
    {kpi("🎯","Avg Order Value",f"₹{aov:,.0f}","Per order",TEAL)}
    {kpi("📊","Profit Margin",f"{mgn:.1f}%","Overall",GREEN)}
    {kpi("✅","Delivery Rate",f"{delr:.1f}%","Successfully delivered",GREEN)}
    {kpi("❌","Cancellation",f"{canr:.1f}%","Orders cancelled",RED)}
  </div>
  {section("Revenue & Profit Trend")}
  <div class="chart-grid g1">
    {chart_box(f_monthly,"f_monthly")}
  </div>
  {section("Category & Regional Performance")}
  <div class="chart-grid g2">
    {chart_box(f_cat,"f_cat")}
    {chart_box(f_reg,"f_reg")}
  </div>
  {section("Order Status & Payment Distribution")}
  <div class="chart-grid g2">
    {chart_box(f_status,"f_status")}
    {chart_box(f_pay,"f_pay")}
  </div>
</div>

<!-- ════════════ PAGE 2 ════════════ -->
<div id="p2" class="page">
  {section("Top & Bottom Performing Products")}
  <div class="chart-grid g2">
    {chart_box(f_top10,"f_top10")}
    {chart_box(f_bot10,"f_bot10")}
  </div>
  {section("Sub-Category & Product Profitability")}
  <div class="chart-grid g1">
    {chart_box(f_sub,"f_sub")}
  </div>
  <div class="chart-grid g1">
    {chart_box(f_scatter,"f_scatter")}
  </div>
</div>

<!-- ════════════ PAGE 3 ════════════ -->
<div id="p3" class="page">
  {section("Customer KPIs")}
  <div class="mini-kpi-row">
    {cust_kpi("Total Customers",f"{tcu:,}",TEAL)}
    {cust_kpi("Champions",f"{int(seg_clean[seg_clean['Segment']=='Champions']['Count'].iloc[0]) if 'Champions' in seg_clean['Segment'].values else 0:,}",GREEN)}
    {cust_kpi("At Risk",f"{int(seg_clean[seg_clean['Segment']=='At Risk']['Count'].iloc[0]) if 'At Risk' in seg_clean['Segment'].values else 0:,}",ORANGE)}
    {cust_kpi("Avg Orders/Customer",f"{df.groupby('Customer_ID')['Order_ID'].nunique().mean():.1f}",BLUE)}
    {cust_kpi("Returning Rate",f"{retr:.1f}%",TEAL)}
    {cust_kpi("Revenue/Customer",f"₹{ts/tcu/1e3:.0f}K",PURPLE)}
  </div>
  {section("RFM Segmentation")}
  <div class="chart-grid g2">
    {chart_box(f_rfm_donut,"f_rfm_donut")}
    {chart_box(f_rfm_rev,"f_rfm_rev")}
  </div>
  {section("New vs Returning · Age Distribution")}
  <div class="chart-grid g2">
    {chart_box(f_ctype,"f_ctype")}
    {chart_box(f_age,"f_age")}
  </div>
  {section("Top 15 Customers by Lifetime Spend")}
  <div class="chart-grid g1">
    {chart_box(f_top_cust,"f_top_cust")}
  </div>
</div>

<!-- ════════════ PAGE 4 ════════════ -->
<div id="p4" class="page">
  {section("State & Regional Performance")}
  <div class="legend-row">
    {''.join(f'<div class="leg"><div class="leg-dot" style="background:{c};"></div>{r}</div>' for r,c in REG_C.items())}
  </div>
  <div class="chart-grid g2l">
    {chart_box(f_states,"f_states")}
    {chart_box(f_heat,"f_heat")}
  </div>
  {section("Seasonal & Quarterly Trends")}
  <div class="chart-grid g2">
    {chart_box(f_seas,"f_seas")}
    {chart_box(f_qtr,"f_qtr")}
  </div>
</div>

<!-- ════════════ PAGE 5 ════════════ -->
<div id="p5" class="page">
  {section("Data-Driven Business Insights")}
  <div class="ins-grid">
    {insight_card("⚠️","Electronics Concentration Risk",
      f"Electronics = 79.4% of revenue (₹162.6Cr). Single-category dependency creates supply chain risk.",
      "Grow Clothing (45.5% margin) and Beauty (45.4%). Target Electronics below 65% in 2 years.",ORANGE)}
    {insight_card("🚨","Groceries: 20.4% Margin Alert",
      f"Groceries generate only ₹1.6L profit on ₹7.9L sales — far below every other category.",
      "Reduce SKUs. Stop marketing investment. Re-price staples upward by 5–8%.",RED)}
    {insight_card("📍","Central Region Underperformance",
      f"Central India = only 11% of revenue (₹22.5Cr) vs North's 25.3% (₹51.7Cr).",
      "Invest in Central logistics. Campaigns in Bhopal, Indore, Raipur. COD incentives.",BLUE)}
    {insight_card("🎉","Q4 Festive = 36.3% of Annual Revenue",
      f"Oct–Dec drives ₹74.3Cr annually. Q4 2022 grew 108% QoQ. One bad campaign = missed target.",
      "Build July–August mid-year sale. Begin inventory build 8 weeks before Diwali.",TEAL)}
    {insight_card("📱","UPI Leads · EMI is Untapped",
      f"UPI = 30% of orders. EMI = only 7.2% but likely the highest basket size (Electronics buyers).",
      "Partner with banks for no-cost EMI on Electronics >₹20K. UPI cashback in lean months.",GREEN)}
    {insight_card("❌","₹31.1 Cr Lost to Cancellations & Returns",
      f"Cancelled: ₹18.8Cr. Returned: ₹12.3Cr. Combined = 15.2% of total sales.",
      "Video unboxing return policy for Electronics. Target cancellation rate below 5%.",RED)}
    {insight_card("🔄","Returning Customers: Volume Advantage",
      f"Returning AOV ₹40,900 ≈ New AOV ₹41,083 but Returning = 30,077 orders vs 19,923.",
      "Loyalty programme: reward every 5th order. Re-engage customers inactive 90+ days.",TEAL)}
    {insight_card("🎯","1,606 At Risk Customers",
      f"RFM model identifies 1,606 customers who bought before but are now inactive.",
      "Personalised win-back email with 10% discount. Auto-trigger at 60 days inactivity.",ORANGE)}
    {insight_card("📉","Volume Trap Products",
      f"10 products have sales >₹10L but margins below 35% — mainly Home & Kitchen and Sports.",
      "Reduce discounts by 5%. Bundle with high-margin items. De-list if below 25% for 2 quarters.",PURPLE)}
  </div>
  {section("Priority Action Plan")}
  <div class="table-card">
    <table>
      <thead>
        <tr>
          <th>#</th><th>Recommended Action</th>
          <th>Expected Impact</th><th>Priority</th>
        </tr>
      </thead>
      <tbody>{pr_rows_html}</tbody>
    </table>
  </div>
</div>

</div><!-- /content -->
</div><!-- /main -->
</div><!-- /shell -->

<script>
const pageTitles = {{
  p1:"Executive Overview", p2:"Product Analytics",
  p3:"Customer Analytics", p4:"Regional Analytics",
  p5:"Business Insights"
}};
function switchPage(id, el) {{
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  document.getElementById('page-title').textContent = pageTitles[id];
}}
</script>
</body>
</html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = os.path.getsize(OUT) / 1024 / 1024
print(f"\n{'='*55}")
print(f"  Dashboard saved: powerbi/ecommerce_dashboard.html")
print(f"  File size      : {size_mb:.2f} MB")
print(f"{'='*55}")
