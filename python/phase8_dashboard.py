"""
phase8_dashboard.py  ·  Enterprise-Grade Interactive Dashboard
Output : powerbi/ecommerce_dashboard.html
"""

import pandas as pd, numpy as np, os, json, warnings
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
warnings.filterwarnings("ignore")

BASE  = os.path.join(os.path.dirname(__file__), "..")
CLEAN = os.path.join(BASE, "data", "cleaned", "ecommerce_cleaned.csv")
RFM_F = os.path.join(BASE, "data", "cleaned", "rfm_segments.csv")
RAW   = os.path.join(BASE, "data", "raw")
OUT   = os.path.join(BASE, "powerbi", "ecommerce_dashboard.html")

print("Loading data …")
df  = pd.read_csv(CLEAN, parse_dates=["Order_Date"])
rfm = pd.read_csv(RFM_F)
craw= pd.read_csv(os.path.join(RAW, "customers.csv"))

# ── palette ─────────────────────────────────────────────
T="#00E5CC"; B="#4F8EF7"; O="#FFA94D"; R="#FF6B6B"
PU="#B197FC"; YE="#FFD43B"; GR="#69DB7C"
PAL=[T,B,O,R,PU,YE,GR,"#F783AC","#63E6BE","#74C0FC"]

PP="rgba(0,0,0,0)"; FC="#E2E8F0"; GC="rgba(148,163,184,0.10)"
BL=dict(paper_bgcolor=PP,plot_bgcolor=PP,
        font=dict(family="'DM Sans',sans-serif",size=11,color=FC),
        margin=dict(l=8,r=8,t=42,b=8),
        title_font=dict(size=12.5,color=FC,family="'DM Sans',sans-serif"),
        legend=dict(font=dict(color=FC,size=10),bgcolor="rgba(0,0,0,0)",
                    bordercolor="rgba(255,255,255,0.06)",borderwidth=1),
        xaxis=dict(gridcolor=GC,zerolinecolor=GC,
                   tickfont=dict(color="#94A3B8",size=9.5),
                   title_font=dict(color="#94A3B8")),
        yaxis=dict(gridcolor=GC,zerolinecolor=GC,
                   tickfont=dict(color="#94A3B8",size=9.5),
                   title_font=dict(color="#94A3B8")))
CFG={"displayModeBar":False}

def fig2h(fig,did=""):
    return fig.to_html(full_html=False,include_plotlyjs=False,div_id=did,config=CFG)
def ap(fig,**kw):
    fig.update_layout(**{**BL,**kw}); return fig

# ── KPIs ────────────────────────────────────────────────
ts=df["Sales"].sum(); tp=df["Profit"].sum(); tc=df["Cost"].sum()
to_=df["Order_ID"].nunique(); tcu=df["Customer_ID"].nunique()
tq=df["Quantity"].sum(); aov=ts/to_; mgn=tp/ts*100
delr=df[df["Order_Status"]=="Delivered"]["Order_ID"].nunique()/to_*100
canr=df[df["Order_Status"]=="Cancelled"]["Order_ID"].nunique()/to_*100
retr=df[df["Customer_Type"]=="Returning"]["Customer_ID"].nunique()/tcu*100

# ── Aggregations ─────────────────────────────────────────
monthly=(df.groupby("Order_YearMonth",as_index=False)
         .agg(Sales=("Sales","sum"),Profit=("Profit","sum"),Orders=("Order_ID","nunique"))
         .sort_values("Order_YearMonth"))
monthly["Margin"]=(monthly["Profit"]/monthly["Sales"]*100).round(1)

cat=(df.groupby("Category",as_index=False)
     .agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
     .sort_values("Sales",ascending=False))
cat["Margin"]=(cat["Profit"]/cat["Sales"]*100).round(1)
cat["SalesCr"]=(cat["Sales"]/1e7).round(2)
cat["ProfCr"]=(cat["Profit"]/1e7).round(2)

reg=(df.groupby("Region",as_index=False)
     .agg(Sales=("Sales","sum"),Profit=("Profit","sum"),Orders=("Order_ID","nunique"))
     .sort_values("Sales",ascending=False))

pay=(df.groupby("Payment_Mode")["Order_ID"].nunique()
     .reset_index().rename(columns={"Order_ID":"Cnt"})
     .sort_values("Cnt",ascending=False))

status=(df.groupby("Order_Status")["Order_ID"].nunique()
        .reset_index().rename(columns={"Order_ID":"Cnt"})
        .sort_values("Cnt",ascending=False))

top10=(df.groupby("Product_Name",as_index=False)
       .agg(Sales=("Sales","sum"),Profit=("Profit","sum"),Qty=("Quantity","sum"))
       .nlargest(10,"Sales").sort_values("Sales"))
top10["Margin"]=(top10["Profit"]/top10["Sales"]*100).round(1)

bot10=(df.groupby("Product_Name",as_index=False)
       .agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
       .nsmallest(10,"Sales").sort_values("Sales",ascending=False))

sub=(df.groupby(["Category","Sub_Category"],as_index=False)
     .agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
     .sort_values("Sales",ascending=False).head(18))

pg=(df.groupby(["Product_Name","Category"],as_index=False)
    .agg(Sales=("Sales","sum"),Profit=("Profit","sum"),Qty=("Quantity","sum")))

AO=["18–25","26–35","36–45","46–55","56+"]
age=(df.groupby("Age_Group",as_index=False)
     .agg(Sales=("Sales","sum"),Customers=("Customer_ID","nunique"))
     .assign(Age_Group=lambda x:pd.Categorical(x["Age_Group"],categories=AO,ordered=True))
     .sort_values("Age_Group"))

ctype=(df.groupby("Customer_Type",as_index=False)
       .agg(Sales=("Sales","sum"),Orders=("Order_ID","nunique"),
            Customers=("Customer_ID","nunique")))

SO=["Champions","Loyal Customers","At Risk","Hibernating","Lost"]
SC={"Champions":T,"Loyal Customers":B,"At Risk":O,"Hibernating":R,"Lost":"#64748B"}
seg=(rfm.groupby("Segment",as_index=False)
     .agg(Count=("Customer_ID","count"),Revenue=("Monetary","sum"),Avg=("Monetary","mean"))
     .assign(Segment=lambda x:pd.Categorical(x["Segment"],categories=SO,ordered=True))
     .sort_values("Segment").dropna(subset=["Segment"]).reset_index(drop=True))

tc15=(df.groupby("Customer_ID",as_index=False)
      .agg(Sales=("Sales","sum"),Orders=("Order_ID","nunique"))
      .nlargest(15,"Sales")
      .merge(craw[["Customer_ID","Customer_Name","Region","Customer_Type"]],on="Customer_ID")
      .sort_values("Sales"))

ss=(df.groupby(["State","Region"],as_index=False)
    .agg(Sales=("Sales","sum"),Orders=("Order_ID","nunique"))
    .sort_values("Sales",ascending=False).head(15).sort_values("Sales"))

cr=(df.groupby(["Category","Region"])["Sales"].sum().unstack(fill_value=0)/1e7)

seas=(df.groupby("Season",as_index=False)
      .agg(Sales=("Sales","sum"),Orders=("Order_ID","nunique")))
seas["Pct"]=(seas["Sales"]/ts*100).round(1)

qtr=(df.groupby(["Order_Year","Order_Quarter"],as_index=False)
     .agg(Sales=("Sales","sum"),Profit=("Profit","sum")))
qtr["Label"]=qtr["Order_Year"].astype(str)+" Q"+qtr["Order_Quarter"].astype(str)

# monthly sparkline data for KPI cards
yr24=monthly[monthly["Order_YearMonth"].astype(str).str.startswith("2024")]
spark_s=yr24["Sales"].tolist()
spark_p=yr24["Profit"].tolist()
spark_o=yr24["Orders"].tolist()

print("Building charts …")

# ══════════════════════════════════════════════════════
# P1 CHARTS
# ══════════════════════════════════════════════════════
xl=monthly["Order_YearMonth"].astype(str).tolist()
fm=go.Figure()
fm.add_trace(go.Scatter(x=xl,y=monthly["Sales"]/1e7,name="Sales",
    line=dict(color=T,width=2.5,shape="spline"),
    fill="tozeroy",fillcolor="rgba(0,229,204,0.06)",
    hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:.2f}Cr<extra></extra>"))
fm.add_trace(go.Scatter(x=xl,y=monthly["Profit"]/1e7,name="Profit",
    line=dict(color=B,width=2,shape="spline",dash="dot"),
    fill="tozeroy",fillcolor="rgba(79,142,247,0.04)",
    hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:.2f}Cr<extra></extra>"))
for yr in ["2023-01","2024-01"]:
    if yr in xl:
        i=xl.index(yr)
        fm.add_shape(type="line",x0=i,x1=i,y0=0,y1=1,yref="paper",
                     line=dict(color="rgba(255,255,255,0.1)",width=1,dash="dot"))
        fm.add_annotation(x=i,y=0.98,yref="paper",text=yr[:4],
                          showarrow=False,font=dict(size=9,color="#64748B"))
ap(fm,title="Monthly Revenue & Profit Trend",height=310,
   legend=dict(orientation="h",y=1.14,x=0,font=dict(size=10)),
   xaxis=dict(tickangle=-40,tickfont=dict(size=8.5,color="#64748B"),gridcolor=GC),
   yaxis=dict(title="₹ Crores",tickprefix="₹",gridcolor=GC,tickfont=dict(color="#64748B")))

# category horizontal
fc=go.Figure(go.Bar(
    x=cat["Sales"]/1e7,y=cat["Category"],orientation="h",
    marker=dict(color=cat["Sales"]/1e7,
                colorscale=[[0,"#1E3A5F"],[0.4,B],[1,T]],
                line=dict(width=0)),
    customdata=cat["Margin"],
    text=[f"₹{v:.1f}Cr · {m:.0f}%" for v,m in zip(cat["SalesCr"],cat["Margin"])],
    textposition="outside",textfont=dict(size=9,color="#94A3B8"),
    hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:.1f}Cr<br>Margin: %{customdata:.1f}%<extra></extra>"))
ap(fc,title="Revenue by Category",height=270,
   xaxis=dict(title="₹ Crores",gridcolor=GC,tickfont=dict(color="#64748B")),
   yaxis=dict(autorange="reversed",tickfont=dict(color=FC,size=10.5)))

# region
freg=go.Figure()
freg.add_trace(go.Bar(name="Sales",x=reg["Region"],y=reg["Sales"]/1e7,
    marker=dict(color=T,opacity=0.85,line=dict(width=0)),
    text=[f"₹{v/1e7:.0f}Cr" for v in reg["Sales"]],
    textposition="outside",textfont=dict(size=8.5,color="#64748B")))
freg.add_trace(go.Bar(name="Profit",x=reg["Region"],y=reg["Profit"]/1e7,
    marker=dict(color=B,opacity=0.85,line=dict(width=0)),
    text=[f"₹{v/1e7:.0f}Cr" for v in reg["Profit"]],
    textposition="outside",textfont=dict(size=8.5,color="#64748B")))
ap(freg,title="Sales & Profit by Region",barmode="group",height=270,
   legend=dict(orientation="h",y=1.14),
   yaxis=dict(title="₹ Crores",gridcolor=GC,tickfont=dict(color="#64748B")),
   xaxis=dict(tickfont=dict(color=FC)))

# status donut
stc={"Delivered":GR,"Shipped":B,"Cancelled":R,"Returned":O,"Processing":PU}
fst=go.Figure(go.Pie(
    labels=status["Order_Status"],values=status["Cnt"],hole=0.62,
    marker=dict(colors=[stc.get(s,"#64748B") for s in status["Order_Status"]],
                line=dict(color="#0B1526",width=2.5)),
    textinfo="percent",textfont=dict(size=10,color=FC),
    direction="clockwise",sort=False,
    hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>"))
fst.add_annotation(text=f"<b style='font-size:18px'>{to_:,}</b><br>Orders",
                   x=0.5,y=0.5,showarrow=False,font=dict(size=14,color=FC),
                   align="center")
ap(fst,title="Order Status",height=290,
   legend=dict(orientation="v",x=1.02,y=0.5,font=dict(size=9.5)))

# payment donut
fpy=go.Figure(go.Pie(
    labels=pay["Payment_Mode"],values=pay["Cnt"],hole=0.62,
    marker=dict(colors=PAL[:len(pay)],line=dict(color="#0B1526",width=2.5)),
    textinfo="percent",textfont=dict(size=10,color=FC),
    hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>"))
fpy.add_annotation(text=f"<b>UPI</b><br>{pay[pay['Payment_Mode']=='UPI']['Cnt'].values[0]/to_*100:.0f}%",
                   x=0.5,y=0.5,showarrow=False,font=dict(size=13,color=T),align="center")
ap(fpy,title="Payment Mode Split",height=290,
   legend=dict(orientation="v",x=1.02,y=0.5,font=dict(size=9.5)))

# ══════════════════════════════════════════════════════
# P2 CHARTS
# ══════════════════════════════════════════════════════
ft10=go.Figure(go.Bar(
    y=top10["Product_Name"],x=top10["Sales"]/1e5,orientation="h",
    marker=dict(color=top10["Sales"]/1e5,
                colorscale=[[0,"#1a3a5c"],[0.5,B],[1,T]],line=dict(width=0)),
    customdata=top10[["Margin","Qty"]].values,
    text=[f"₹{v/1e5:.0f}L" for v in top10["Sales"]],
    textposition="outside",textfont=dict(size=9,color="#94A3B8"),
    hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:.0f}L<br>Margin: %{customdata[0]:.1f}%<br>Units: %{customdata[1]:,}<extra></extra>"))
ap(ft10,title="Top 10 Products — Revenue",height=370,
   xaxis=dict(title="₹ Lakhs",gridcolor=GC,tickfont=dict(color="#64748B")),
   yaxis=dict(autorange="reversed",tickfont=dict(color=FC,size=9.5)))

fb10=go.Figure(go.Bar(
    y=bot10["Product_Name"],x=bot10["Sales"]/1e5,orientation="h",
    marker=dict(color=bot10["Sales"]/1e5,
                colorscale=[[0,R],[0.6,O],[1,"#FBBF24"]],reversescale=True,line=dict(width=0)),
    text=[f"₹{v/1e5:.2f}L" for v in bot10["Sales"]],
    textposition="outside",textfont=dict(size=9,color="#94A3B8"),
    hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:.2f}L<extra></extra>"))
ap(fb10,title="Bottom 10 Products — Lowest Revenue",height=370,
   xaxis=dict(title="₹ Lakhs",gridcolor=GC,tickfont=dict(color="#64748B")),
   yaxis=dict(tickfont=dict(color=FC,size=9.5)))

fsub=go.Figure()
for i,cn in enumerate(sub["Category"].unique()):
    g=sub[sub["Category"]==cn]
    fsub.add_trace(go.Bar(x=g["Sub_Category"],y=g["Sales"]/1e7,name=cn,
                          marker_color=PAL[i%len(PAL)],opacity=0.88))
ap(fsub,title="Revenue by Sub-Category",barmode="group",height=340,
   xaxis=dict(tickangle=-35,tickfont=dict(color=FC,size=8.5),gridcolor=GC),
   yaxis=dict(title="₹ Crores",gridcolor=GC,tickfont=dict(color="#64748B")),
   legend=dict(orientation="h",y=1.14,font=dict(size=9.5)))

fsc=px.scatter(pg,x="Sales",y="Profit",size="Qty",color="Category",
               hover_name="Product_Name",color_discrete_sequence=PAL,
               labels={"Sales":"Sales (₹)","Profit":"Profit (₹)"},
               title="Sales vs Profit · Bubble = Units Sold")
fsc.update_traces(marker=dict(opacity=0.72,line=dict(width=0.8,color="#0B1526"),sizemin=5))
ap(fsc,height=390,
   xaxis=dict(gridcolor=GC,zerolinecolor=GC,tickfont=dict(color="#64748B")),
   yaxis=dict(gridcolor=GC,zerolinecolor=GC,tickfont=dict(color="#64748B")))

# ══════════════════════════════════════════════════════
# P3 CHARTS
# ══════════════════════════════════════════════════════
frd=go.Figure(go.Pie(
    labels=seg["Segment"],values=seg["Count"],hole=0.60,
    marker=dict(colors=[SC.get(s,B) for s in seg["Segment"]],
                line=dict(color="#0B1526",width=2.5)),
    textinfo="label+percent",textfont=dict(size=9.5,color=FC),
    rotation=90,
    hovertemplate="<b>%{label}</b><br>%{value:,} customers (%{percent})<extra></extra>"))
frd.add_annotation(text=f"<b>{len(rfm):,}</b><br>Customers",
                   x=0.5,y=0.5,showarrow=False,font=dict(size=14,color=FC),align="center")
ap(frd,title="RFM Segment Distribution",height=330,
   legend=dict(orientation="v",x=1.02,y=0.5,font=dict(size=9.5)))

frr=go.Figure(go.Bar(
    y=seg["Segment"],x=seg["Revenue"]/1e7,orientation="h",
    marker=dict(color=[SC.get(s,B) for s in seg["Segment"]],
                opacity=0.88,line=dict(width=0)),
    text=[f"₹{v/1e7:.1f}Cr" for v in seg["Revenue"]],
    textposition="outside",textfont=dict(size=9,color="#94A3B8"),
    hovertemplate="<b>%{y}</b><br>₹%{x:.1f}Cr<extra></extra>"))
ap(frr,title="Revenue per RFM Segment",height=330,
   xaxis=dict(title="₹ Crores",gridcolor=GC,tickfont=dict(color="#64748B")),
   yaxis=dict(autorange="reversed",tickfont=dict(color=FC)))

fct=make_subplots(rows=1,cols=2,subplot_titles=["Revenue by Customer Type","Orders by Customer Type"])
for row in ctype.itertuples():
    c=T if row.Customer_Type=="Returning" else B
    fct.add_trace(go.Bar(x=[row.Customer_Type],y=[row.Sales/1e7],name=row.Customer_Type,
                         marker=dict(color=c,opacity=0.88,line=dict(width=0)),showlegend=False,
                         text=[f"₹{row.Sales/1e7:.1f}Cr"],textposition="outside",
                         textfont=dict(size=11,color="#94A3B8")),row=1,col=1)
    fct.add_trace(go.Bar(x=[row.Customer_Type],y=[row.Orders],name=row.Customer_Type,
                         marker=dict(color=c,opacity=0.88,line=dict(width=0)),showlegend=False,
                         text=[f"{row.Orders:,}"],textposition="outside",
                         textfont=dict(size=11,color="#94A3B8")),row=1,col=2)
fct.update_layout(**{**BL,"title":"New vs Returning Customers","height":295})
fct.update_xaxes(tickfont=dict(color=FC))
fct.update_yaxes(gridcolor=GC,zerolinecolor=GC,tickfont=dict(color="#64748B"))
for a in fct.layout.annotations: a.font=dict(color="#94A3B8",size=10)

fag=go.Figure(go.Bar(
    x=age["Age_Group"].astype(str),y=age["Sales"]/1e7,
    marker=dict(color=age["Sales"]/1e7,
                colorscale=[[0,"#1a3a5c"],[0.5,B],[1,T]],line=dict(width=0)),
    text=[f"₹{v/1e7:.1f}Cr" for v in age["Sales"]],
    textposition="outside",textfont=dict(size=9.5,color="#94A3B8")))
ap(fag,title="Revenue by Age Group",height=280,
   xaxis=dict(tickfont=dict(color=FC)),
   yaxis=dict(title="₹ Crores",gridcolor=GC,tickfont=dict(color="#64748B")))

ftc=go.Figure(go.Bar(
    y=tc15["Customer_Name"]+" · "+tc15["Region"],x=tc15["Sales"]/1e5,orientation="h",
    marker=dict(color=[T if t=="Returning" else O for t in tc15["Customer_Type"]],
                opacity=0.88,line=dict(width=0)),
    text=[f"₹{v/1e5:.0f}L" for v in tc15["Sales"]],
    textposition="outside",textfont=dict(size=8.5,color="#94A3B8"),
    hovertemplate="<b>%{y}</b><br>₹%{x:.0f}L<extra></extra>"))
ap(ftc,title="Top 15 Customers · Teal=Returning · Orange=New",height=460,
   xaxis=dict(title="₹ Lakhs",gridcolor=GC,tickfont=dict(color="#64748B")),
   yaxis=dict(autorange="reversed",tickfont=dict(color=FC,size=9)))

# ══════════════════════════════════════════════════════
# P4 CHARTS
# ══════════════════════════════════════════════════════
RC={"North":T,"South":B,"East":O,"West":PU,"Central":YE}
fst2=go.Figure(go.Bar(
    y=ss["State"]+" ("+ss["Region"]+")",x=ss["Sales"]/1e7,orientation="h",
    marker=dict(color=[RC.get(r,B) for r in ss["Region"]],
                opacity=0.88,line=dict(width=0)),
    text=[f"₹{v/1e7:.1f}Cr" for v in ss["Sales"]],
    textposition="outside",textfont=dict(size=8.5,color="#94A3B8"),
    hovertemplate="<b>%{y}</b><br>₹%{x:.1f}Cr<extra></extra>"))
ap(fst2,title="Top 15 States by Revenue  (colour = region)",height=470,
   xaxis=dict(title="₹ Crores",gridcolor=GC,tickfont=dict(color="#64748B")),
   yaxis=dict(autorange="reversed",tickfont=dict(color=FC,size=9.5)))

fhm=go.Figure(go.Heatmap(
    z=cr.values,x=cr.columns.tolist(),y=cr.index.tolist(),
    colorscale=[[0,"#0B1526"],[0.25,"#1E3A5F"],[0.6,B],[1,T]],
    text=[[f"₹{v:.1f}Cr" for v in row] for row in cr.values],
    texttemplate="%{text}",textfont=dict(size=9.5,color=FC),
    hovertemplate="<b>%{y} × %{x}</b><br>₹%{text}<extra></extra>",
    colorbar=dict(tickfont=dict(color="#94A3B8",size=9),
                  title=dict(text="₹ Crores",font=dict(color="#94A3B8",size=9)))))
ap(fhm,title="Category × Region Heatmap (₹ Crores)",height=310,
   xaxis=dict(tickfont=dict(color=FC,size=10),side="bottom"),
   yaxis=dict(tickfont=dict(color=FC,size=10)))

sc={"Festive Season":O,"New Year Sales":T,"Summer":R,"Monsoon":B}
fse=go.Figure(go.Bar(
    x=seas["Season"],y=seas["Sales"]/1e7,
    marker=dict(color=[sc.get(s,B) for s in seas["Season"]],
                opacity=0.88,line=dict(width=0)),
    text=[f"₹{v/1e7:.1f}Cr<br>{p:.1f}%" for v,p in zip(seas["Sales"],seas["Pct"])],
    textposition="outside",textfont=dict(size=9.5,color="#94A3B8")))
ap(fse,title="Revenue by Season",height=310,
   xaxis=dict(tickfont=dict(color=FC)),
   yaxis=dict(title="₹ Crores",gridcolor=GC,tickfont=dict(color="#64748B")))

fq=go.Figure()
fq.add_trace(go.Bar(x=qtr["Label"],y=qtr["Sales"]/1e7,name="Sales",
                    marker=dict(color=T,opacity=0.85,line=dict(width=0)),
                    text=[f"₹{v/1e7:.0f}Cr" for v in qtr["Sales"]],
                    textposition="outside",textfont=dict(size=8,color="#94A3B8")))
fq.add_trace(go.Bar(x=qtr["Label"],y=qtr["Profit"]/1e7,name="Profit",
                    marker=dict(color=B,opacity=0.85,line=dict(width=0))))
ap(fq,title="Quarterly Revenue & Profit",barmode="group",height=310,
   xaxis=dict(tickangle=-30,tickfont=dict(color=FC,size=8.5)),
   yaxis=dict(title="₹ Crores",gridcolor=GC,tickfont=dict(color="#64748B")),
   legend=dict(orientation="h",y=1.14))

print("Assembling HTML …")

# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════
def cb(fig,did,span=""):
    cls=f"chart-card{' '+span if span else ''}"
    return f'<div class="{cls}">{fig2h(fig,did)}</div>'

def sec(t):
    return f'<div class="sec-hdr"><div class="sec-line"></div><span>{t}</span><div class="sec-line r"></div></div>'

def kpi_card(icon,label,val,sub,acc,spark_data=None,is_bad=False):
    spark_html=""
    if spark_data:
        pts=spark_data
        mn,mx=min(pts),max(pts)
        rng=mx-mn if mx!=mn else 1
        w=80;h=32;pad=2
        coords=[]
        for i,v in enumerate(pts):
            x=pad+i*(w-2*pad)/(len(pts)-1)
            y=h-pad-(v-mn)/(rng)*(h-2*pad)
            coords.append(f"{x:.1f},{y:.1f}")
        poly=" ".join(coords)+f" {w-pad},{h} {pad},{h}"
        path=" ".join([f"{'M' if i==0 else 'L'}{c}" for i,c in enumerate(coords)])
        spark_html=f"""
        <svg width="{w}" height="{h}" style="margin-top:6px;overflow:visible">
          <defs>
            <linearGradient id="sg_{label[:3].replace(' ','')}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="{acc}" stop-opacity="0.35"/>
              <stop offset="100%" stop-color="{acc}" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <polygon points="{poly}" fill="url(#sg_{label[:3].replace(' ','')})" opacity="0.8"/>
          <path d="{path}" fill="none" stroke="{acc}" stroke-width="1.8" stroke-linejoin="round"/>
        </svg>"""
    trend="↑" if not is_bad else "↓"
    trend_clr=acc if not is_bad else R
    return f"""
<div class="kpi-card" onclick="void(0)">
  <div class="kpi-top">
    <div class="kpi-icon" style="background:linear-gradient(135deg,{acc}22,{acc}11);color:{acc};">{icon}</div>
    <div class="kpi-trend" style="color:{trend_clr};">{trend}</div>
  </div>
  <div class="kpi-val" data-target="{val}">{val}</div>
  <div class="kpi-lbl">{label}</div>
  <div class="kpi-sub">{sub}</div>
  {spark_html}
</div>"""

def ins(icon,title,obs,rec,col):
    return f"""
<div class="ins-card" style="--ic:{col};">
  <div class="ins-icon" style="background:{col}18;color:{col};">{icon}</div>
  <div class="ins-body">
    <div class="ins-title">{title}</div>
    <div class="ins-obs">{obs}</div>
    <div class="ins-rec">→ {rec}</div>
  </div>
</div>"""

def prog_row(label,val,maxv,col,sub=""):
    pct=val/maxv*100
    return f"""
<div class="prog-row">
  <div class="prog-hdr"><span>{label}</span><span style="color:{col};">₹{val/1e7:.1f}Cr</span></div>
  <div class="prog-track"><div class="prog-fill" style="width:{pct:.1f}%;background:linear-gradient(90deg,{col},{col}99);"></div></div>
  <div class="prog-sub">{sub}</div>
</div>"""

nav_items=[
    ("p1","📈","Executive Overview"),
    ("p2","📦","Product Analytics"),
    ("p3","👥","Customer Analytics"),
    ("p4","🗺️","Regional Analytics"),
    ("p5","💡","Business Insights"),
]
sidebar_nav="".join(
    f'<div class="nav-item{"  active" if pid=="p1" else ""}" onclick="go(\'{pid}\',this)" data-title="{ptitle}">'
    f'<span class="nav-ico">{pico}</span><span class="nav-lbl">{ptitle}</span>'
    f'</div>'
    for pid,pico,ptitle in nav_items)

# KPI card row
champ_n=int(seg[seg["Segment"]=="Champions"]["Count"].iloc[0]) if "Champions" in seg["Segment"].values else 0
atrisk_n=int(seg[seg["Segment"]=="At Risk"]["Count"].iloc[0]) if "At Risk" in seg["Segment"].values else 0

spark_s_norm=spark_s; spark_p_norm=spark_p

kpi_html="".join([
    kpi_card("💰","Total Revenue",f"₹{ts/1e7:.1f}Cr",f"3 years · 50,000 orders",T,spark_s_norm),
    kpi_card("📈","Total Profit",f"₹{tp/1e7:.1f}Cr",f"Margin {mgn:.1f}%",GR,spark_p_norm),
    kpi_card("🛒","Total Orders",f"{to_:,}","Jan 2022 – Dec 2024",B,spark_o),
    kpi_card("👥","Customers",f"{tcu:,}","Unique buyers",PU),
    kpi_card("🎯","Avg Order Value",f"₹{aov:,.0f}","Per order",T),
    kpi_card("✅","Delivery Rate",f"{delr:.1f}%","Orders delivered",GR),
    kpi_card("⚠️","Cancellation",f"{canr:.1f}%","Orders cancelled",O,None,True),
    kpi_card("🔁","Return Rate",f"{(df[df['Order_Status']=='Returned']['Order_ID'].nunique()/to_*100):.1f}%","Returned orders",R,None,True),
])

# category progress bars
maxcat=cat["Sales"].max()
prog_html="".join(prog_row(r["Category"],r["Sales"],maxcat,PAL[i],f"{r['Margin']:.1f}% margin · {r['Sales']/ts*100:.1f}% of revenue")
                  for i,(_, r) in enumerate(cat.iterrows()))

# RFM mini bar chart (inline SVG) — replaced with chart
seg_rows="".join(
    f'<div class="seg-row"><span class="seg-dot" style="background:{SC.get(r["Segment"],"#64748B")};"></span>'
    f'<span class="seg-name">{r["Segment"]}</span>'
    f'<span class="seg-cnt">{int(r["Count"]):,}</span>'
    f'<div class="seg-bar-wrap"><div class="seg-bar" style="width:{r["Count"]/len(rfm)*100:.1f}%;background:{SC.get(r["Segment"],"#64748B")};"></div></div>'
    f'<span class="seg-rev" style="color:{SC.get(r["Segment"],"#64748B")};">₹{r["Revenue"]/1e7:.1f}Cr</span>'
    f'</div>'
    for _,r in seg.iterrows())

# action table
pri_rows=""
rows_data=[
    (1,R,"Critical","Win-Back — 1,606 At Risk customers","Personalised 10% discount email + 60-day trigger","+₹5–8 Cr"),
    (2,R,"Critical","No-cost EMI for Electronics >₹20K","Bank partnerships · HDFC / ICICI / Axis","↑15–20% AOV"),
    (3,R,"Critical","Cut cancellation rate: 9% → 5%","Better product descriptions + Video return policy","Recover ₹8–10 Cr"),
    (4,O,"High","Mid-year sale event (July–August)","Reduce Q4 festive dependency","Stabilise revenue"),
    (5,O,"High","Reduce Groceries SKUs","Keep only high-margin items","↑1–2% margin"),
    (6,O,"High","Central India logistics expansion","Partner with regional couriers in MP & CG","₹20–30 Cr unlock"),
    (7,YE,"Medium","Grow Clothing & Beauty","Both >45% margin — run category-targeted campaigns","Revenue diversity"),
    (8,T,"Medium","Champions Loyalty Programme","Exclusive early access + milestone rewards","Protect ₹55Cr base"),
]
for num,col,prio,action,detail,impact in rows_data:
    pri_rows+=f"""
<tr>
  <td class="td-num">{num}</td>
  <td><div class="badge" style="background:{col}22;color:{col};border:1px solid {col}44;">{prio}</div></td>
  <td class="td-action"><strong>{action}</strong><div class="td-detail">{detail}</div></td>
  <td class="td-impact" style="color:{T};">{impact}</td>
</tr>"""

ins_html="".join([
    ins("⚠️","Electronics Concentration — 79.4% Revenue",
        f"Electronics = ₹162.6Cr revenue (79.4% share) at 47.7% margin. Single-category risk is high.",
        "Grow Clothing & Beauty (both 45%+ margin). Target Electronics below 65% within 2 years.",O),
    ins("🚨","Groceries: 20.4% Margin — Lowest Category",
        "Groceries produce only ₹1.6L profit on ₹7.9L sales. Real costs likely erode this further.",
        "Remove low-margin SKUs. Re-price staples 5–8%. Redirect marketing budget to higher-margin categories.",R),
    ins("📍","Central India Underperforms — 11% of Revenue",
        "Central region (₹22.5Cr) generates less than half of North (₹51.7Cr) despite large geography.",
        "Partner with regional couriers. Run Bhopal/Indore/Raipur campaigns. Offer COD incentives.",B),
    ins("🎉","Festive Season = 36.3% Annual Revenue",
        "Q4 (Oct–Dec) drives ₹74.3Cr. Q4 2022 grew 108% QoQ — extreme seasonal concentration.",
        "Build July–August sale event. Begin inventory 8–10 weeks pre-Diwali. Run post-festive retention.",T),
    ins("💳","UPI 30% · EMI Untapped at 7.2%",
        "UPI dominates payments. EMI customers are high-value Electronics buyers paying in instalments.",
        "No-cost EMI on Electronics >₹20K. UPI cashback during lean months for off-peak demand.",GR),
    ins("❌","₹31.1 Cr Lost — Cancellations & Returns",
        "Cancelled ₹18.8Cr + Returned ₹12.3Cr = 15.2% of total sales with logistics cost still incurred.",
        "Video unboxing return policy for Electronics. Improve product descriptions. Target <5% cancellation.",R),
    ins("🔄","Returning Customers: 51% More Orders",
        "Returning AOV (₹40,900) ≈ New AOV (₹41,083) but Returning placed 30,077 vs 19,923 orders.",
        "Loyalty programme: discount after every 5th order. Re-engagement email at 90 days inactivity.",T),
    ins("🎯","1,606 Customers 'At Risk' — Act Now",
        "RFM identifies 1,606 previously-active customers trending toward churn. Win-back is 5× cheaper than acquisition.",
        "Automated win-back flow: personalised email → push notification → 10% discount code.",O),
    ins("📉","10 Volume-Trap Products (High Sales · Low Margin)",
        "10 products exceed ₹10L sales but have margin below 35% — mainly Home & Kitchen and Sports items.",
        "Reduce discounts 5%. Bundle with high-margin items. De-list if margin stays below 25% for 2 quarters.",PU),
])

# ══════════════════════════════════════════════════════
# CSS + HTML
# ══════════════════════════════════════════════════════
CSS=f"""
*{{box-sizing:border-box;margin:0;padding:0;}}
:root{{--bg:#080F1A;--s1:#0B1526;--s2:#0F1E35;--card:#0E1C30;
      --brd:rgba(255,255,255,0.06);--acc:{T};--txt:#E2E8F0;--mt:#94A3B8;}}
html,body{{height:100%;overflow:hidden;
           font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--txt);}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:#080F1A;}}
::-webkit-scrollbar-thumb{{background:#1E3A5F;border-radius:4px;}}
::-webkit-scrollbar-thumb:hover{{background:{T}55;}}

/* layout */
.shell{{display:flex;height:100vh;}}

/* sidebar */
.sb{{width:230px;min-width:230px;background:var(--s1);
     border-right:1px solid var(--brd);display:flex;
     flex-direction:column;overflow:hidden;}}
.sb-top{{padding:22px 20px;border-bottom:1px solid var(--brd);}}
.sb-logo{{display:flex;align-items:center;gap:10px;margin-bottom:6px;}}
.sb-logo-icon{{width:34px;height:34px;border-radius:9px;
  background:linear-gradient(135deg,{T},{B});
  display:flex;align-items:center;justify-content:center;
  font-size:16px;flex-shrink:0;}}
.sb-name{{font-size:14px;font-weight:700;color:var(--txt);letter-spacing:0.2px;}}
.sb-tag{{font-size:10px;color:var(--mt);margin-top:2px;}}
.sb-section{{font-size:9px;font-weight:600;color:var(--mt);
             letter-spacing:1.4px;text-transform:uppercase;
             padding:18px 20px 7px;}}
.nav-item{{display:flex;align-items:center;gap:11px;padding:11px 20px;
           cursor:pointer;font-size:12.5px;font-weight:500;color:var(--mt);
           border-left:3px solid transparent;transition:all .15s ease;
           user-select:none;border-radius:0;}}
.nav-item:hover{{color:var(--txt);background:rgba(255,255,255,0.03);}}
.nav-item.active{{color:var(--acc);background:rgba(0,229,204,0.06);
                  border-left:3px solid var(--acc);}}
.nav-ico{{font-size:14px;width:20px;text-align:center;}}
.sb-foot{{margin-top:auto;padding:16px 20px;border-top:1px solid var(--brd);}}
.sb-foot-title{{font-size:11px;font-weight:600;color:var(--acc);margin-bottom:5px;}}
.sb-foot-line{{font-size:10px;color:var(--mt);line-height:1.7;}}

/* topbar */
.topbar{{background:rgba(8,15,26,.96);backdrop-filter:blur(10px);
         padding:13px 26px;border-bottom:1px solid var(--brd);
         display:flex;justify-content:space-between;align-items:center;
         position:sticky;top:0;z-index:200;flex-shrink:0;}}
.tb-title{{font-size:16px;font-weight:700;
           background:linear-gradient(90deg,{T},{B});
           -webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.tb-sub{{font-size:10.5px;color:var(--mt);margin-top:2px;}}
.badge-row{{display:flex;gap:7px;flex-wrap:wrap;}}
.mbadge{{background:rgba(0,229,204,.09);color:{T};
         border:1px solid rgba(0,229,204,.22);
         border-radius:20px;padding:3px 11px;
         font-size:10px;font-weight:500;}}

/* main */
.main{{flex:1;overflow:hidden;display:flex;flex-direction:column;}}
.content{{flex:1;overflow-y:auto;padding:22px 24px 30px;}}

/* pages */
.page{{display:none;animation:fi .2s ease;}}
.page.active{{display:block;}}
@keyframes fi{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:none}}}}

/* kpi grid */
.kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px;}}
.kpi-card{{background:var(--card);border:1px solid var(--brd);
           border-radius:12px;padding:17px 17px 13px;
           transition:transform .18s,box-shadow .18s;cursor:default;
           position:relative;overflow:hidden;}}
.kpi-card::after{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
                  background:linear-gradient(90deg,{T},{B});opacity:.6;}}
.kpi-card:hover{{transform:translateY(-3px);
                 box-shadow:0 8px 32px rgba(0,0,0,.45),0 0 0 1px rgba(0,229,204,.12);}}
.kpi-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;}}
.kpi-icon{{width:38px;height:38px;border-radius:10px;
           display:flex;align-items:center;justify-content:center;
           font-size:18px;flex-shrink:0;}}
.kpi-trend{{font-size:18px;font-weight:700;}}
.kpi-val{{font-size:24px;font-weight:700;color:var(--txt);
          letter-spacing:-.5px;line-height:1;margin-bottom:5px;}}
.kpi-lbl{{font-size:10px;color:var(--mt);text-transform:uppercase;
          letter-spacing:.8px;margin-bottom:3px;}}
.kpi-sub{{font-size:10px;color:#475569;}}

/* chart grid */
.cg{{display:grid;gap:16px;margin-bottom:18px;}}
.g1{{grid-template-columns:1fr;}}
.g2{{grid-template-columns:1fr 1fr;}}
.g3{{grid-template-columns:1fr 1fr 1fr;}}
.g21{{grid-template-columns:2fr 1fr;}}
.g12{{grid-template-columns:1fr 2fr;}}
.chart-card{{background:var(--card);border:1px solid var(--brd);
             border-radius:12px;padding:16px;
             box-shadow:0 4px 24px rgba(0,0,0,.28);
             transition:box-shadow .18s;overflow:hidden;}}
.chart-card:hover{{box-shadow:0 6px 32px rgba(0,229,204,.06),0 4px 24px rgba(0,0,0,.4);}}
.span2{{grid-column:span 2;}}
.span3{{grid-column:span 3;}}

/* section header */
.sec-hdr{{display:flex;align-items:center;gap:10px;margin:4px 0 14px;}}
.sec-hdr span{{font-size:10px;font-weight:600;color:var(--mt);
               text-transform:uppercase;letter-spacing:1.2px;white-space:nowrap;}}
.sec-line{{flex:1;height:1px;background:var(--brd);}}

/* progress bars (category panel) */
.prog-panel{{background:var(--card);border:1px solid var(--brd);border-radius:12px;padding:18px;}}
.prog-row{{margin-bottom:14px;}}
.prog-row:last-child{{margin-bottom:0;}}
.prog-hdr{{display:flex;justify-content:space-between;
           font-size:12px;font-weight:500;color:var(--txt);margin-bottom:5px;}}
.prog-track{{height:6px;background:rgba(255,255,255,.06);
             border-radius:3px;overflow:hidden;margin-bottom:3px;}}
.prog-fill{{height:100%;border-radius:3px;transition:width 1s ease;}}
.prog-sub{{font-size:10px;color:#475569;}}

/* mini-kpi row */
.mini-row{{display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;}}
.mini-kpi{{background:var(--card);border:1px solid var(--brd);
           border-radius:10px;padding:13px 17px;flex:1;min-width:110px;text-align:center;}}
.mini-v{{font-size:20px;font-weight:700;}}
.mini-l{{font-size:9.5px;color:var(--mt);text-transform:uppercase;
         letter-spacing:.6px;margin-top:4px;}}

/* seg table */
.seg-table{{background:var(--card);border:1px solid var(--brd);
            border-radius:12px;padding:18px;}}
.seg-row{{display:flex;align-items:center;gap:10px;margin-bottom:12px;}}
.seg-row:last-child{{margin-bottom:0;}}
.seg-dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0;}}
.seg-name{{font-size:12px;color:var(--txt);width:130px;flex-shrink:0;}}
.seg-cnt{{font-size:11px;color:var(--mt);width:50px;flex-shrink:0;text-align:right;}}
.seg-bar-wrap{{flex:1;height:8px;background:rgba(255,255,255,.05);
               border-radius:4px;overflow:hidden;}}
.seg-bar{{height:100%;border-radius:4px;opacity:.85;transition:width 1s ease;}}
.seg-rev{{font-size:11px;font-weight:600;width:60px;text-align:right;flex-shrink:0;}}

/* insight cards */
.ins-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:22px;}}
.ins-card{{background:var(--card);border:1px solid var(--brd);
           border-left:3px solid var(--ic);border-radius:12px;
           padding:16px 18px;display:flex;gap:13px;
           transition:transform .16s,box-shadow .16s;}}
.ins-card:hover{{transform:translateY(-2px);
                 box-shadow:0 6px 28px rgba(0,0,0,.35);}}
.ins-icon{{width:36px;height:36px;border-radius:9px;display:flex;
           align-items:center;justify-content:center;
           font-size:17px;flex-shrink:0;margin-top:2px;}}
.ins-title{{font-size:12px;font-weight:700;color:var(--txt);margin-bottom:6px;}}
.ins-obs{{font-size:11px;color:var(--mt);line-height:1.6;margin-bottom:7px;}}
.ins-rec{{font-size:11px;color:var(--ic);line-height:1.55;font-style:italic;}}

/* action table */
.act-table{{background:var(--card);border:1px solid var(--brd);
            border-radius:12px;overflow:hidden;}}
.act-table table{{width:100%;border-collapse:collapse;font-size:12px;}}
.act-table thead tr{{background:rgba(0,229,204,.06);}}
.act-table thead th{{padding:12px 16px;text-align:left;color:var(--mt);
                     font-weight:600;font-size:10px;text-transform:uppercase;
                     letter-spacing:.9px;border-bottom:1px solid var(--brd);}}
.act-table tbody tr{{border-bottom:1px solid rgba(255,255,255,.03);
                     transition:background .12s;}}
.act-table tbody tr:hover{{background:rgba(255,255,255,.025);}}
.td-num{{color:{T};font-weight:700;padding:12px 16px;width:40px;}}
.td-action{{padding:12px 16px;color:var(--txt);}}
.td-detail{{font-size:10.5px;color:var(--mt);margin-top:3px;}}
.td-impact{{padding:12px 16px;font-weight:600;font-size:12px;}}
.badge{{border-radius:20px;padding:3px 11px;font-size:10px;font-weight:600;}}

/* legend row */
.leg-row{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:12px;}}
.leg{{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--mt);}}
.leg-dot{{width:9px;height:9px;border-radius:50%;}}
"""

html=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>E-Commerce Analytics · Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div class="shell">

<!-- SIDEBAR -->
<div class="sb">
  <div class="sb-top">
    <div class="sb-logo">
      <div class="sb-logo-icon">📊</div>
      <div>
        <div class="sb-name">EcomAnalytics</div>
        <div class="sb-tag">Sales Intelligence Platform</div>
      </div>
    </div>
  </div>
  <div class="sb-section">Main Menu</div>
  {sidebar_nav}
  <div class="sb-foot">
    <div class="sb-foot-title">Dataset Overview</div>
    <div class="sb-foot-line">
      📦 50,000 Orders<br>
      👥 5,000 Customers<br>
      📅 Jan 2022 – Dec 2024<br>
      💰 ₹{ts/1e7:.0f} Crores Revenue<br>
      🏷️ 7 Categories · 5 Regions<br><br>
      <span style="color:#475569;">Python · SQL · Plotly</span>
    </div>
  </div>
</div>

<!-- MAIN -->
<div class="main">
<div class="topbar">
  <div>
    <div class="tb-title" id="pg-title">Executive Overview</div>
    <div class="tb-sub">E-Commerce Sales &amp; Customer Analytics · 3 Years · India</div>
  </div>
  <div class="badge-row">
    <span class="mbadge">₹{ts/1e7:.0f}Cr Revenue</span>
    <span class="mbadge">{mgn:.1f}% Margin</span>
    <span class="mbadge">AOV ₹{aov/1e3:.0f}K</span>
    <span class="mbadge">{delr:.0f}% Delivered</span>
  </div>
</div>

<div class="content">

<!-- PAGE 1 -->
<div id="p1" class="page active">
  {sec("Key Performance Indicators")}
  <div class="kpi-grid">{kpi_html}</div>

  {sec("Revenue & Profit Trend")}
  <div class="cg g1">{cb(fm,"fm")}</div>

  {sec("Category & Regional Breakdown")}
  <div class="cg g2">
    <div class="prog-panel">
      <div style="font-size:12.5px;font-weight:600;color:#E2E8F0;margin-bottom:16px;">Revenue by Category</div>
      {prog_html}
    </div>
    {cb(freg,"freg")}
  </div>

  {sec("Order Status & Payment Mode")}
  <div class="cg g2">
    {cb(fst,"fst")}
    {cb(fpy,"fpy")}
  </div>
</div>

<!-- PAGE 2 -->
<div id="p2" class="page">
  {sec("Product Revenue Leaders & Laggards")}
  <div class="cg g2">
    {cb(ft10,"ft10")}
    {cb(fb10,"fb10")}
  </div>
  {sec("Sub-Category Performance")}
  <div class="cg g1">{cb(fsub,"fsub")}</div>
  {sec("Profitability Scatter")}
  <div class="cg g1">{cb(fsc,"fsc")}</div>
</div>

<!-- PAGE 3 -->
<div id="p3" class="page">
  {sec("Customer KPIs")}
  <div class="mini-row">
    <div class="mini-kpi"><div class="mini-v" style="color:{T};">{tcu:,}</div><div class="mini-l">Total Customers</div></div>
    <div class="mini-kpi"><div class="mini-v" style="color:{GR};">{champ_n:,}</div><div class="mini-l">Champions</div></div>
    <div class="mini-kpi"><div class="mini-v" style="color:{O};">{atrisk_n:,}</div><div class="mini-l">At Risk</div></div>
    <div class="mini-kpi"><div class="mini-v" style="color:{B};">{df.groupby('Customer_ID')['Order_ID'].nunique().mean():.1f}</div><div class="mini-l">Avg Orders/Cust</div></div>
    <div class="mini-kpi"><div class="mini-v" style="color:{T};">{retr:.1f}%</div><div class="mini-l">Returning Rate</div></div>
    <div class="mini-kpi"><div class="mini-v" style="color:{PU};">₹{ts/tcu/1e3:.0f}K</div><div class="mini-l">Revenue/Customer</div></div>
  </div>

  {sec("RFM Segmentation")}
  <div class="cg g2">
    {cb(frd,"frd")}
    <div class="seg-table">
      <div style="font-size:12.5px;font-weight:600;color:#E2E8F0;margin-bottom:14px;">Segment Breakdown</div>
      {seg_rows}
    </div>
  </div>

  {sec("Revenue Distribution")}
  <div class="cg g1">{cb(frr,"frr")}</div>

  {sec("New vs Returning · Age Distribution")}
  <div class="cg g2">
    {cb(fct,"fct")}
    {cb(fag,"fag")}
  </div>

  {sec("Top 15 Customers by Lifetime Spend")}
  <div class="cg g1">{cb(ftc,"ftc")}</div>
</div>

<!-- PAGE 4 -->
<div id="p4" class="page">
  {sec("State & Regional Performance")}
  <div class="leg-row">
    {''.join(f'<div class="leg"><div class="leg-dot" style="background:{c};"></div>{r}</div>' for r,c in RC.items())}
  </div>
  <div class="cg g2">
    {cb(fst2,"fst2")}
    {cb(fhm,"fhm")}
  </div>
  {sec("Seasonal & Quarterly Trends")}
  <div class="cg g2">
    {cb(fse,"fse")}
    {cb(fq,"fq")}
  </div>
</div>

<!-- PAGE 5 -->
<div id="p5" class="page">
  {sec("Data-Driven Business Insights")}
  <div class="ins-grid">{ins_html}</div>

  {sec("Priority Action Plan")}
  <div class="act-table">
    <table>
      <thead><tr>
        <th>#</th><th>Priority</th><th>Recommended Action</th><th>Expected Impact</th>
      </tr></thead>
      <tbody>{pri_rows}</tbody>
    </table>
  </div>
</div>

</div><!-- /content -->
</div><!-- /main -->
</div><!-- /shell -->

<script>
function go(id,el){{
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  document.getElementById('pg-title').textContent=el.dataset.title;
  // re-trigger progress bar animation
  document.querySelectorAll('.prog-fill,.seg-bar').forEach(b=>{{
    const w=b.style.width; b.style.width='0'; setTimeout(()=>b.style.width=w,30);
  }});
}}
</script>
</body>
</html>"""

os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,"w",encoding="utf-8") as f:
    f.write(html)

mb=os.path.getsize(OUT)/1024/1024
print(f"\n{'='*55}")
print(f"  Saved: powerbi/ecommerce_dashboard.html")
print(f"  Size : {mb:.2f} MB")
print(f"{'='*55}")
