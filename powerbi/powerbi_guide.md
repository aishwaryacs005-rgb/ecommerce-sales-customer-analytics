# Power BI Dashboard Guide
## E-Commerce Sales & Customer Analytics

---

## Prerequisites

- Download **Power BI Desktop** (free): https://powerbi.microsoft.com/desktop
- Install and open it
- All 4 CSV files are ready in the `powerbi/` folder:
  - `fact_orders.csv`
  - `dim_customers.csv`
  - `dim_products.csv`
  - `monthly_summary.csv`

---

## STEP 1 — Import All 4 CSV Files

1. Open Power BI Desktop
2. Click **"Get data"** → **Text/CSV**
3. Navigate to your `powerbi/` folder
4. Select `fact_orders.csv` → Click **Load**
5. Repeat for `dim_customers.csv`, `dim_products.csv`, `monthly_summary.csv`

After loading, you will see 4 tables in the **Fields** panel on the right.

---

## STEP 2 — Build the Data Model (Relationships)

1. Click the **Model view** icon on the left sidebar (looks like 3 connected boxes)
2. You will see the 4 tables as boxes
3. Create relationships by dragging and dropping:

| From Table      | From Column  | To Table      | To Column   | Type         |
|-----------------|--------------|---------------|-------------|--------------|
| fact_orders     | Customer_ID  | dim_customers | Customer_ID | Many-to-One  |
| fact_orders     | Product_ID   | dim_products  | Product_ID  | Many-to-One  |

**How to create a relationship:**
- Drag `Customer_ID` from `fact_orders` and drop it onto `Customer_ID` in `dim_customers`
- Power BI will auto-detect it as Many-to-One
- Repeat for Product_ID

> **Why this matters:** Relationships allow slicers on one table to filter data across all connected tables. When you filter by Region in dim_customers, all charts using fact_orders automatically update.

---

## STEP 3 — Create All DAX Measures

DAX (Data Analysis Expressions) is Power BI's formula language.  
All measures go in a dedicated **Measures table** to keep things organised.

**Create the Measures table:**
1. Go to **Modeling** tab → **New Table**
2. Type: `_Measures = {""}`
3. Click the checkmark

Now create each measure by clicking **"New Measure"** in the Measures table:

---

### KPI Measures

```dax
Total Sales =
SUM(fact_orders[Sales])
```

```dax
Total Profit =
SUM(fact_orders[Profit])
```

```dax
Total Cost =
SUM(fact_orders[Cost])
```

```dax
Total Orders =
DISTINCTCOUNT(fact_orders[Order_ID])
```

```dax
Total Customers =
DISTINCTCOUNT(fact_orders[Customer_ID])
```

```dax
Total Quantity =
SUM(fact_orders[Quantity])
```

```dax
Average Order Value =
DIVIDE([Total Sales], [Total Orders], 0)
```

```dax
Profit Margin % =
DIVIDE([Total Profit], [Total Sales], 0) * 100
```

---

### Time Intelligence Measures

```dax
Sales LY =
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR(fact_orders[Order_Date])
)
```
> LY = Last Year. SAMEPERIODLASTYEAR shifts the date filter back 12 months.

```dax
Sales YoY Growth % =
DIVIDE(
    [Total Sales] - [Sales LY],
    [Sales LY],
    0
) * 100
```

```dax
Sales MTD =
TOTALMTD([Total Sales], fact_orders[Order_Date])
```
> MTD = Month to Date. Shows cumulative sales from the 1st of the current month.

```dax
Sales QTD =
TOTALQTD([Total Sales], fact_orders[Order_Date])
```

---

### Customer Measures

```dax
Returning Customer Revenue =
CALCULATE(
    [Total Sales],
    dim_customers[Customer_Type] = "Returning"
)
```

```dax
New Customer Revenue =
CALCULATE(
    [Total Sales],
    dim_customers[Customer_Type] = "New"
)
```

```dax
Repeat Customer Rate % =
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(fact_orders[Customer_ID]),
        dim_customers[Customer_Type] = "Returning"
    ),
    [Total Customers],
    0
) * 100
```

```dax
Revenue Per Customer =
DIVIDE([Total Sales], [Total Customers], 0)
```

---

### Order Quality Measures

```dax
Cancelled Orders =
CALCULATE(
    DISTINCTCOUNT(fact_orders[Order_ID]),
    fact_orders[Order_Status] = "Cancelled"
)
```

```dax
Cancellation Rate % =
DIVIDE([Cancelled Orders], [Total Orders], 0) * 100
```

```dax
Delivered Orders =
CALCULATE(
    DISTINCTCOUNT(fact_orders[Order_ID]),
    fact_orders[Order_Status] = "Delivered"
)
```

```dax
Delivery Rate % =
DIVIDE([Delivered Orders], [Total Orders], 0) * 100
```

---

## STEP 4 — Build the Dashboard (4 Pages)

---

### PAGE 1 — Executive Overview

**Rename the tab:** Double-click the page tab at the bottom → type `Executive Overview`

**Background color:** Canvas background → Light grey (#F5F5F5)

---

#### Row 1 — KPI Cards (6 cards across the top)

For each card:
1. Click **Visualizations** panel → Select **Card** visual
2. Drag the measure into the **Fields** well

| Card # | Measure              | Format           |
|--------|----------------------|------------------|
| 1      | Total Sales          | ₹ Currency, 0 dp |
| 2      | Total Profit         | ₹ Currency, 0 dp |
| 3      | Total Orders         | Number, 0 dp     |
| 4      | Total Customers      | Number, 0 dp     |
| 5      | Average Order Value  | ₹ Currency, 0 dp |
| 6      | Profit Margin %      | Decimal, 2 dp    |

**Format each card:**
- Visual → Background → Light blue (#BDD7EE)
- Data label → Font size 20, Bold, Dark blue (#1F3864)
- Category label → Font size 10, Grey

---

#### Row 2 — Monthly Sales Trend (Line Chart)

1. Insert → **Line chart**
2. Fields:
   - X-axis: `fact_orders[Order_YearMonth]`
   - Y-axis: `[Total Sales]`
   - Secondary Y-axis: `[Total Profit]`
3. Format:
   - Total Sales line: Blue, width 2.5
   - Total Profit line: Green, width 2
   - Title: "Monthly Sales & Profit Trend"
   - X-axis: rotate labels 45°

---

#### Row 2 — Sales by Category (Clustered Bar Chart)

1. Insert → **Clustered bar chart**
2. Fields:
   - Y-axis: `dim_products[Category]`
   - X-axis: `[Total Sales]`
   - Legend: _(leave empty)_
3. Format:
   - Sort by Total Sales descending
   - Data labels: On
   - Title: "Sales by Category"

---

#### Row 3 — Sales by Region (Column Chart) + Order Status (Donut Chart)

**Column chart:**
- X-axis: `dim_customers[Region]`
- Y-axis: `[Total Sales]`
- Title: "Sales by Region"

**Donut chart:**
- Legend: `fact_orders[Order_Status]`
- Values: `[Total Orders]`
- Title: "Order Status Distribution"

---

### PAGE 2 — Product Analytics

**Tab name:** `Product Analytics`

---

#### Visuals:

**1. Top 10 Products Table**
- Insert → **Table**
- Columns: `dim_products[Product_Name]`, `dim_products[Category]`, `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]`, `[Total Quantity]`
- Sort by Total Sales descending
- Apply **Top N filter**: Visual-level filter → Product_Name → Top 10 by Total Sales
- Format: Alternate row shading

**2. Category vs Sub-Category Matrix**
- Insert → **Matrix**
- Rows: `dim_products[Category]` → `dim_products[Sub_Category]`
- Values: `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]`
- Format: Enable row subtotals, conditional formatting on Profit Margin %
  - Go to Format → Conditional formatting → Background color
  - Set: Low = Red, Mid = Yellow, High = Green

**3. Sales vs Profit Scatter Chart**
- Insert → **Scatter chart**
- X-axis: `[Total Sales]`
- Y-axis: `[Total Profit]`
- Details: `dim_products[Product_Name]`
- Size: `[Total Quantity]`
- Legend: `dim_products[Category]`
- Title: "Sales vs Profit by Product"

**4. Bottom 10 Products Bar Chart**
- Same as Top 10 but apply Bottom N filter (bottom 10 by Total Sales)
- Use Red color scheme
- Title: "Bottom 10 Products (Lowest Revenue)"

---

### PAGE 3 — Customer Analytics

**Tab name:** `Customer Analytics`

---

#### Visuals:

**1. Customer Segment Donut Chart**
- Legend: `dim_customers[RFM_Segment]`
- Values: `[Total Customers]`
- Title: "Customer RFM Segments"
- Colors: Champions=Green, Loyal=Blue, At Risk=Orange, Hibernating=Red, Lost=Grey

**2. New vs Returning Revenue Bar Chart**
- X-axis: `dim_customers[Customer_Type]`
- Y-axis: `[Total Sales]`
- Secondary Y-axis: `[Total Orders]`
- Title: "New vs Returning Customer Revenue"
- Add data labels

**3. Revenue by Age Group Column Chart**
- X-axis: `dim_customers[Age_Group]`
- Y-axis: `[Total Sales]`
- Title: "Revenue by Customer Age Group"

**4. Top 15 Customers Table**
- Columns: `dim_customers[Customer_Name]`, `dim_customers[Region]`, `dim_customers[RFM_Segment]`, `[Total Sales]`, `[Total Orders]`, `[Revenue Per Customer]`
- Sort by Total Sales desc
- Apply Top N filter: Top 15

**5. Customer Revenue KPI Cards (row)**
- `[Total Customers]`
- `[Repeat Customer Rate %]`
- `[Revenue Per Customer]`
- `[Returning Customer Revenue]`

---

### PAGE 4 — Regional Analytics

**Tab name:** `Regional Analytics`

---

#### Visuals:

**1. Map Visual — Sales by State**
- Insert → **Map** (or Filled Map)
- Location: `dim_customers[State]`
- Bubble size / Color saturation: `[Total Sales]`
- Title: "Sales Intensity by State"
- > Note: If map does not work, use a Treemap instead.

**2. Region Performance Table**
- Columns: `dim_customers[Region]`, `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]`, `[Total Orders]`, `[Total Customers]`
- Sort by Total Sales descending
- Conditional formatting on Profit Margin %

**3. Region vs Category Heatmap (Matrix)**
- Rows: `dim_customers[Region]`
- Columns: `dim_products[Category]`
- Values: `[Total Sales]`
- Format: Conditional formatting → Color scale (white to dark blue)
- Title: "Sales by Region × Category"

**4. State Performance Bar Chart (Top 10)**
- Y-axis: `dim_customers[State]`
- X-axis: `[Total Sales]`
- Top N filter: 10
- Title: "Top 10 States by Revenue"

---

## STEP 5 — Add Slicers (All Pages)

Slicers let users filter the entire dashboard interactively.

Add these slicers on **every page** (copy-paste them after creating on Page 1):

| Slicer          | Field                             | Style              |
|-----------------|-----------------------------------|--------------------|
| Date Range      | `fact_orders[Order_Date]`         | Between (date range picker) |
| Year            | `fact_orders[Order_Year]`         | Dropdown           |
| Region          | `dim_customers[Region]`           | Dropdown           |
| Category        | `dim_products[Category]`          | Tile/Checkbox      |
| Order Status    | `fact_orders[Order_Status]`       | Dropdown           |
| Customer Type   | `dim_customers[Customer_Type]`    | Tile               |
| Payment Mode    | `fact_orders[Payment_Mode]`       | Dropdown           |
| RFM Segment     | `dim_customers[RFM_Segment]`      | Dropdown           |

**How to create a slicer:**
1. Insert → **Slicer**
2. Drag the field into the **Field** well
3. Format → Slicer settings → choose style (Tile, Dropdown, Between)
4. Format → Title → type the column name

**How to copy slicers to other pages:**
1. Select all slicers (hold Ctrl, click each one)
2. Right-click → **Copy**
3. Go to Page 2 → Right-click canvas → **Paste**

---

## STEP 6 — Format the Dashboard Professionally

### Color Theme
Go to **View** tab → **Themes** → **Customize current theme**

| Element           | Color      |
|-------------------|------------|
| Name              | ECom Blue  |
| First data color  | #2E75B6    |
| Second data color | #2D7D46    |
| Third data color  | #E67E22    |
| Fourth data color | #C0392B    |
| Background        | #FAFAFA    |

### Typography
- Title font: Segoe UI, 14pt, Bold
- Axis labels: Segoe UI, 10pt
- Data labels: Segoe UI, 9pt

### Page Navigation Buttons
1. Go to **Insert** → **Buttons** → **Navigator** → **Page navigator**
2. This adds clickable tabs at the top so viewers can jump between pages
3. Format → Background → Match your theme color

---

## STEP 7 — Publish to Power BI Service (Optional)

If you have a Power BI account (free with a work/school email):

1. Click **File** → **Publish** → **Publish to Power BI**
2. Sign in with your account
3. Choose **My workspace**
4. After publishing, share the link on LinkedIn

---

## STEP 8 — Take Screenshots for Portfolio

After building the dashboard:

1. Press **Print Screen** or use Windows Snipping Tool (Win + Shift + S)
2. Capture each of the 4 pages
3. Save them to: `screenshots/powerbi_page1.png`, etc.
4. Add them to your GitHub README

---

## DAX Measures — Complete Reference

| Measure               | Formula Summary                                 | Used On       |
|-----------------------|-------------------------------------------------|---------------|
| Total Sales           | SUM(Sales)                                      | All pages     |
| Total Profit          | SUM(Profit)                                     | All pages     |
| Total Cost            | SUM(Cost)                                       | All pages     |
| Total Orders          | DISTINCTCOUNT(Order_ID)                         | All pages     |
| Total Customers       | DISTINCTCOUNT(Customer_ID)                      | All pages     |
| Total Quantity        | SUM(Quantity)                                   | Product page  |
| Average Order Value   | DIVIDE(Total Sales, Total Orders)               | All pages     |
| Profit Margin %       | DIVIDE(Total Profit, Total Sales) × 100         | All pages     |
| Sales LY              | SAMEPERIODLASTYEAR of Total Sales               | Exec page     |
| Sales YoY Growth %    | (Sales - Sales LY) / Sales LY × 100            | Exec page     |
| Sales MTD             | TOTALMTD(Total Sales)                           | Exec page     |
| Sales QTD             | TOTALQTD(Total Sales)                           | Exec page     |
| Returning Revenue     | CALCULATE(Sales, Customer_Type = "Returning")   | Customer page |
| New Revenue           | CALCULATE(Sales, Customer_Type = "New")         | Customer page |
| Repeat Customer Rate  | Returning Customers / Total Customers × 100     | Customer page |
| Revenue Per Customer  | Total Sales / Total Customers                   | Customer page |
| Cancelled Orders      | CALCULATE(Orders, Status = "Cancelled")         | Exec page     |
| Cancellation Rate %   | Cancelled / Total Orders × 100                  | Exec page     |
| Delivery Rate %       | Delivered Orders / Total Orders × 100           | Exec page     |

---

*Phase 8 — Power BI Dashboard Guide*
*Project: E-Commerce Sales & Customer Analytics*
