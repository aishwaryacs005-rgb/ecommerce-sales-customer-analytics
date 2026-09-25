# Data Dictionary — E-Commerce Sales & Customer Analytics

This document describes every column in every table of the dataset.
Use this as a reference throughout the project.

---

## Table Relationship Overview

```
regions ──────────────────────────────────────────────────────┐
                                                              │
customers (Region, State, City from regions) ─────────────── │
     │                                                        │
     │ Customer_ID                                            │
     ▼                                                        │
   orders ──────────────────────────────────────────────────  │
     │                                                        │
     │ Order_ID                                               │
     ▼                                                        │
  order_details ◄────── products
```

**Plain English:**
- One **customer** can place many **orders** (one-to-many).
- One **order** can contain many **products** via **order_details** (one-to-many).
- Each **product** belongs to one **category** and **sub-category**.
- Each **customer** lives in one **city**, which belongs to one **region**.

---

## Table 1 — regions.csv

| Column     | Data Type | Description                                                  | Example         |
|------------|-----------|--------------------------------------------------------------|-----------------|
| Region_ID  | String    | Unique identifier for each city/region row                   | RGN001          |
| Region     | String    | Broad geographic zone of India                               | North           |
| State      | String    | State name within the region                                 | Delhi           |
| City       | String    | City name where orders are delivered                         | New Delhi       |

**Primary Key:** Region_ID  
**Regions:** North, South, East, West, Central  
**Total rows:** 26 (one row per city)

---

## Table 2 — products.csv

| Column       | Data Type | Description                                                  | Example                   |
|--------------|-----------|--------------------------------------------------------------|---------------------------|
| Product_ID   | String    | Unique identifier for each product                           | PRD0001                   |
| Category     | String    | Top-level product group                                      | Electronics               |
| Sub_Category | String    | More specific product type within the category               | Smartphones               |
| Product_Name | String    | Full name of the product                                     | Samsung Galaxy A54        |
| Cost         | Integer   | Wholesale cost per unit (₹) — what the company paid          | 18000                     |
| Unit_Price   | Integer   | Selling price per unit (₹) — what the customer pays          | 39600                     |

**Primary Key:** Product_ID  
**Categories:** Electronics, Clothing, Home & Kitchen, Books, Sports, Beauty, Groceries  
**Total rows:** 61 products  
**Note:** Unit_Price > Cost always. The difference creates profit potential.

---

## Table 3 — customers.csv

| Column        | Data Type | Description                                                          | Example        |
|---------------|-----------|----------------------------------------------------------------------|----------------|
| Customer_ID   | String    | Unique identifier for each customer                                  | CUST00001      |
| Customer_Name | String    | Full name of the customer                                            | Arjun Sharma   |
| Gender        | String    | Customer gender (Male / Female)                                      | Male           |
| Age           | Integer   | Customer age in years at time of registration                        | 32             |
| City          | String    | City where the customer is located                                   | Mumbai         |
| State         | String    | State where the customer is located                                  | Maharashtra    |
| Region        | String    | Region of India where the customer is located                        | West           |
| Customer_Type | String    | Whether customer is New (first order) or Returning (repeat buyer)    | Returning      |

**Primary Key:** Customer_ID  
**Total rows:** 5,000 unique customers  
**Age Range:** 18 to 64 years  
**Note:** Customer_Type is a classification assigned at registration.

---

## Table 4 — orders.csv

| Column       | Data Type | Description                                                              | Example        |
|--------------|-----------|--------------------------------------------------------------------------|----------------|
| Order_ID     | String    | Unique identifier for each order                                         | ORD000001      |
| Order_Date   | Date      | Date when the order was placed (YYYY-MM-DD format)                       | 2022-03-15     |
| Customer_ID  | String    | Links this order to the customer who placed it (Foreign Key → customers) | CUST00142      |
| Payment_Mode | String    | How the customer paid for the order                                      | UPI            |
| Order_Status | String    | Current status of the order                                              | Delivered      |

**Primary Key:** Order_ID  
**Foreign Key:** Customer_ID → customers.Customer_ID  
**Total rows:** 50,000 orders  
**Date Range:** 2022-01-01 to 2024-12-31  

**Order_Status values:**
| Status     | Meaning                                          | Approx % |
|------------|--------------------------------------------------|----------|
| Delivered  | Order received by customer successfully           | 72%      |
| Shipped    | Order dispatched, not yet received                | 10%      |
| Cancelled  | Order was cancelled before delivery               | 9%       |
| Returned   | Customer returned the product after delivery      | 6%       |
| Processing | Order accepted but not yet dispatched             | 3%       |

**Payment_Mode values:** Credit Card, Debit Card, UPI, Net Banking, Cash on Delivery, EMI

---

## Table 5 — order_details.csv

This is the most important table — it contains the actual financial data.

| Column     | Data Type | Description                                                                    | Example    |
|------------|-----------|--------------------------------------------------------------------------------|------------|
| Detail_ID  | String    | Unique identifier for each line item                                           | DTL0000001 |
| Order_ID   | String    | Links this line item to the parent order (Foreign Key → orders)               | ORD000001  |
| Product_ID | String    | Links this line item to the product purchased (Foreign Key → products)        | PRD0015    |
| Quantity   | Integer   | Number of units purchased (1 to 5)                                            | 2          |
| Unit_Price | Integer   | Price per unit at time of purchase (₹) — copied from products at order time    | 39600      |
| Discount   | Float     | Discount applied as a decimal (0.10 = 10% off)                                | 0.10       |
| Sales      | Float     | Actual revenue from this line item: Unit_Price × Quantity × (1 − Discount)    | 71280.00   |
| Cost       | Integer   | Total cost of goods: products.Cost × Quantity                                 | 36000      |
| Profit     | Float     | Net profit from this line item: Sales − Cost                                   | 35280.00   |

**Primary Key:** Detail_ID  
**Foreign Keys:**
- Order_ID → orders.Order_ID
- Product_ID → products.Product_ID  
**Total rows:** 83,603 line items  

**Key Formula (memorize this):**
```
Sales  = Unit_Price × Quantity × (1 − Discount)
Cost   = Product_Cost × Quantity
Profit = Sales − Cost
Profit_Margin = (Profit / Sales) × 100
```

---

## Calculated Fields (Added in Phase 4 — Python Cleaning)

These columns do not exist in the raw data. We will create them in Python.

| Column          | Formula / Logic                                       | Why It Is Useful                        |
|-----------------|-------------------------------------------------------|-----------------------------------------|
| Revenue         | Same as Sales                                         | Clearer business terminology            |
| Profit_Margin   | (Profit / Sales) × 100                                | Tells us profitability as a percentage  |
| Order_Month     | Month extracted from Order_Date                       | Monthly trend analysis                  |
| Order_Year      | Year extracted from Order_Date                        | Year-over-year comparison               |
| Order_Quarter   | Quarter extracted from Order_Date                     | Quarterly performance                   |
| Age_Group       | Bin ages into: 18–25, 26–35, 36–45, 46–55, 55+       | Customer segment analysis               |
| Order_Value     | Total Sales value per order (sum of all line items)   | Average Order Value calculation         |
| Is_Profitable   | TRUE if Profit > 0, else FALSE                        | Quick profitability flag                |

---

## Summary Table

| Table         | Rows    | Purpose                                              |
|---------------|---------|------------------------------------------------------|
| regions       | 26      | Lookup table: Region → State → City                  |
| products      | 61      | Lookup table: Product details, cost, price           |
| customers     | 5,000   | Customer demographics and location                   |
| orders        | 50,000  | One row per order: date, customer, payment, status   |
| order_details | 83,603  | One row per product per order: sales, cost, profit   |

---

*Document created as part of Phase 1 — Data Understanding*  
*Project: E-Commerce Sales & Customer Analytics*
