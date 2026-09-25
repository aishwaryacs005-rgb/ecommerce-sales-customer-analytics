-- =============================================================
-- analysis_queries.sql
-- E-Commerce Sales & Customer Analytics
-- Phase 6 — 25 Business Analysis Queries
-- =============================================================
-- Database : SQLite  (ecommerce.db)
-- Run via  : python sql/run_analysis.py
-- Each query is numbered and explained in plain English.
-- =============================================================


-- ─────────────────────────────────────────────────────────
-- QUERY 1 — Total Revenue
-- Plain English: What is the total money earned from all orders?
-- ─────────────────────────────────────────────────────────
-- Q1
SELECT
    ROUND(SUM(od.Sales), 2)            AS Total_Revenue,
    ROUND(SUM(od.Cost), 2)             AS Total_Cost,
    ROUND(SUM(od.Profit), 2)           AS Total_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)          AS Profit_Margin_Pct
FROM order_details od
JOIN orders o ON od.Order_ID = o.Order_ID
WHERE o.Order_Status NOT IN ('Cancelled');


-- ─────────────────────────────────────────────────────────
-- QUERY 2 — Total Orders, Customers, Products
-- Plain English: How big is our business in terms of key counts?
-- ─────────────────────────────────────────────────────────
-- Q2
SELECT
    COUNT(DISTINCT o.Order_ID)      AS Total_Orders,
    COUNT(DISTINCT o.Customer_ID)   AS Total_Customers,
    COUNT(DISTINCT od.Product_ID)   AS Total_Products,
    SUM(od.Quantity)                AS Total_Units_Sold
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID;


-- ─────────────────────────────────────────────────────────
-- QUERY 3 — Average Order Value (AOV)
-- Plain English: On average, how much does each order earn?
-- AOV = Total Sales / Total Orders
-- ─────────────────────────────────────────────────────────
-- Q3
SELECT
    COUNT(DISTINCT o.Order_ID)                   AS Total_Orders,
    ROUND(SUM(od.Sales), 2)                      AS Total_Sales,
    ROUND(SUM(od.Sales) / COUNT(DISTINCT o.Order_ID), 2) AS Avg_Order_Value
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
WHERE o.Order_Status NOT IN ('Cancelled', 'Returned');


-- ─────────────────────────────────────────────────────────
-- QUERY 4 — Monthly Revenue
-- Plain English: How much did we earn each month?
-- STRFTIME extracts the year-month from a date string in SQLite.
-- ─────────────────────────────────────────────────────────
-- Q4
SELECT
    STRFTIME('%Y-%m', o.Order_Date)   AS Year_Month,
    COUNT(DISTINCT o.Order_ID)        AS Orders,
    ROUND(SUM(od.Sales), 2)           AS Monthly_Revenue,
    ROUND(SUM(od.Profit), 2)          AS Monthly_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)         AS Margin_Pct
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
GROUP BY STRFTIME('%Y-%m', o.Order_Date)
ORDER BY Year_Month;


-- ─────────────────────────────────────────────────────────
-- QUERY 5 — Yearly Revenue
-- Plain English: How did annual revenue change year over year?
-- ─────────────────────────────────────────────────────────
-- Q5
SELECT
    STRFTIME('%Y', o.Order_Date)    AS Year,
    COUNT(DISTINCT o.Order_ID)      AS Orders,
    ROUND(SUM(od.Sales), 2)         AS Yearly_Revenue,
    ROUND(SUM(od.Profit), 2)        AS Yearly_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)       AS Margin_Pct
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
GROUP BY STRFTIME('%Y', o.Order_Date)
ORDER BY Year;


-- ─────────────────────────────────────────────────────────
-- QUERY 6 — Top 10 Products by Revenue
-- Plain English: Which individual products earn the most money?
-- ─────────────────────────────────────────────────────────
-- Q6
SELECT
    p.Product_Name,
    p.Category,
    SUM(od.Quantity)                AS Units_Sold,
    ROUND(SUM(od.Sales), 2)         AS Total_Revenue,
    ROUND(SUM(od.Profit), 2)        AS Total_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)       AS Margin_Pct
FROM order_details od
JOIN products p ON od.Product_ID = p.Product_ID
GROUP BY p.Product_ID
ORDER BY Total_Revenue DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────
-- QUERY 7 — Top 10 Products by Profit
-- Plain English: Which products actually make the most profit?
-- (Different from revenue — a product can have high sales but low margin)
-- ─────────────────────────────────────────────────────────
-- Q7
SELECT
    p.Product_Name,
    p.Category,
    ROUND(SUM(od.Sales), 2)         AS Total_Revenue,
    ROUND(SUM(od.Profit), 2)        AS Total_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)       AS Margin_Pct
FROM order_details od
JOIN products p ON od.Product_ID = p.Product_ID
GROUP BY p.Product_ID
ORDER BY Total_Profit DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────
-- QUERY 8 — Bottom 10 Products (Lowest Revenue)
-- Plain English: Which products are barely selling?
-- These candidates for discontinuation or re-promotion.
-- ─────────────────────────────────────────────────────────
-- Q8
SELECT
    p.Product_Name,
    p.Category,
    SUM(od.Quantity)         AS Units_Sold,
    ROUND(SUM(od.Sales), 2)  AS Total_Revenue,
    ROUND(SUM(od.Profit), 2) AS Total_Profit
FROM order_details od
JOIN products p ON od.Product_ID = p.Product_ID
GROUP BY p.Product_ID
ORDER BY Total_Revenue ASC
LIMIT 10;


-- ─────────────────────────────────────────────────────────
-- QUERY 9 — Category Performance
-- Plain English: Which category is the strongest overall?
-- ─────────────────────────────────────────────────────────
-- Q9
SELECT
    p.Category,
    COUNT(DISTINCT od.Order_ID)     AS Orders,
    SUM(od.Quantity)                AS Units_Sold,
    ROUND(SUM(od.Sales), 2)         AS Total_Revenue,
    ROUND(SUM(od.Profit), 2)        AS Total_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)       AS Margin_Pct,
    ROUND(AVG(od.Discount) * 100, 2) AS Avg_Discount_Pct
FROM order_details od
JOIN products p ON od.Product_ID = p.Product_ID
GROUP BY p.Category
ORDER BY Total_Revenue DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 10 — Sub-Category Performance
-- Plain English: Drill one level deeper — which sub-categories perform best?
-- ─────────────────────────────────────────────────────────
-- Q10
SELECT
    p.Category,
    p.Sub_Category,
    ROUND(SUM(od.Sales), 2)   AS Total_Revenue,
    ROUND(SUM(od.Profit), 2)  AS Total_Profit,
    SUM(od.Quantity)          AS Units_Sold
FROM order_details od
JOIN products p ON od.Product_ID = p.Product_ID
GROUP BY p.Category, p.Sub_Category
ORDER BY Total_Revenue DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 11 — Regional Performance
-- Plain English: Which region brings the most revenue and profit?
-- ─────────────────────────────────────────────────────────
-- Q11
SELECT
    c.Region,
    COUNT(DISTINCT o.Order_ID)      AS Orders,
    COUNT(DISTINCT o.Customer_ID)   AS Customers,
    ROUND(SUM(od.Sales), 2)         AS Total_Revenue,
    ROUND(SUM(od.Profit), 2)        AS Total_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)       AS Margin_Pct
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
JOIN customers c      ON o.Customer_ID = c.Customer_ID
GROUP BY c.Region
ORDER BY Total_Revenue DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 12 — State-Level Performance (Top 10 States)
-- Plain English: Which states are our best markets?
-- ─────────────────────────────────────────────────────────
-- Q12
SELECT
    c.State,
    c.Region,
    COUNT(DISTINCT o.Order_ID)  AS Orders,
    ROUND(SUM(od.Sales), 2)     AS Total_Revenue,
    ROUND(SUM(od.Profit), 2)    AS Total_Profit
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
JOIN customers c      ON o.Customer_ID = c.Customer_ID
GROUP BY c.State
ORDER BY Total_Revenue DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────
-- QUERY 13 — Profit Margin by Category
-- Plain English: For every ₹100 of sales in each category, how much is profit?
-- ─────────────────────────────────────────────────────────
-- Q13
SELECT
    p.Category,
    ROUND(SUM(od.Sales), 2)             AS Total_Sales,
    ROUND(SUM(od.Cost), 2)              AS Total_Cost,
    ROUND(SUM(od.Profit), 2)            AS Total_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)           AS Profit_Margin_Pct,
    ROUND(AVG(od.Discount) * 100, 2)    AS Avg_Discount_Pct
FROM order_details od
JOIN products p ON od.Product_ID = p.Product_ID
GROUP BY p.Category
ORDER BY Profit_Margin_Pct DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 14 — Sales by Payment Method
-- Plain English: How do customers prefer to pay, and how much do they spend?
-- ─────────────────────────────────────────────────────────
-- Q14
SELECT
    o.Payment_Mode,
    COUNT(DISTINCT o.Order_ID)          AS Order_Count,
    ROUND(COUNT(DISTINCT o.Order_ID) * 100.0
          / (SELECT COUNT(*) FROM orders), 2) AS Pct_Of_Orders,
    ROUND(SUM(od.Sales), 2)             AS Total_Sales,
    ROUND(AVG(od.Sales), 2)             AS Avg_Sale_Per_Item
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
GROUP BY o.Payment_Mode
ORDER BY Order_Count DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 15 — Cancelled Orders Analysis
-- Plain English: How many orders were cancelled, and what revenue was lost?
-- ─────────────────────────────────────────────────────────
-- Q15
SELECT
    o.Order_Status,
    COUNT(DISTINCT o.Order_ID)   AS Order_Count,
    ROUND(SUM(od.Sales), 2)      AS Revenue_At_Risk,
    ROUND(AVG(od.Sales), 2)      AS Avg_Order_Item_Value
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
WHERE o.Order_Status IN ('Cancelled', 'Returned')
GROUP BY o.Order_Status
ORDER BY Revenue_At_Risk DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 16 — Average Quantity Per Order
-- Plain English: On average, how many items does a customer buy per order?
-- ─────────────────────────────────────────────────────────
-- Q16
SELECT
    ROUND(AVG(items_per_order), 2) AS Avg_Items_Per_Order,
    MIN(items_per_order)           AS Min_Items,
    MAX(items_per_order)           AS Max_Items
FROM (
    SELECT Order_ID, SUM(Quantity) AS items_per_order
    FROM order_details
    GROUP BY Order_ID
) sub;


-- ─────────────────────────────────────────────────────────
-- QUERY 17 — Repeat Customers (ordered more than once)
-- Plain English: How many customers have placed more than one order?
-- ─────────────────────────────────────────────────────────
-- Q17
SELECT
    order_count_group,
    COUNT(*) AS num_customers
FROM (
    SELECT
        Customer_ID,
        COUNT(DISTINCT Order_ID) AS total_orders,
        CASE
            WHEN COUNT(DISTINCT Order_ID) = 1  THEN '1 Order (One-time)'
            WHEN COUNT(DISTINCT Order_ID) <= 3 THEN '2-3 Orders'
            WHEN COUNT(DISTINCT Order_ID) <= 6 THEN '4-6 Orders'
            WHEN COUNT(DISTINCT Order_ID) <= 10 THEN '7-10 Orders'
            ELSE '10+ Orders (Loyal)'
        END AS order_count_group
    FROM orders
    GROUP BY Customer_ID
) sub
GROUP BY order_count_group
ORDER BY num_customers DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 18 — New vs Returning Customer Revenue
-- Plain English: Do returning customers spend more than new ones?
-- ─────────────────────────────────────────────────────────
-- Q18
SELECT
    c.Customer_Type,
    COUNT(DISTINCT o.Customer_ID)           AS Customers,
    COUNT(DISTINCT o.Order_ID)              AS Total_Orders,
    ROUND(SUM(od.Sales), 2)                 AS Total_Revenue,
    ROUND(SUM(od.Sales)
          / COUNT(DISTINCT o.Customer_ID), 2) AS Revenue_Per_Customer,
    ROUND(SUM(od.Sales)
          / COUNT(DISTINCT o.Order_ID), 2)  AS Avg_Order_Value
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
JOIN customers c      ON o.Customer_ID = c.Customer_ID
GROUP BY c.Customer_Type
ORDER BY Total_Revenue DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 19 — Top 10 Customers by Total Spending
-- Plain English: Who are our most valuable customers?
-- ─────────────────────────────────────────────────────────
-- Q19
SELECT
    c.Customer_ID,
    c.Customer_Name,
    c.Customer_Type,
    c.Region,
    COUNT(DISTINCT o.Order_ID)   AS Orders_Placed,
    ROUND(SUM(od.Sales), 2)      AS Total_Spent,
    ROUND(AVG(od.Sales), 2)      AS Avg_Order_Item_Value
FROM orders o
JOIN order_details od ON o.Order_ID = od.Order_ID
JOIN customers c      ON o.Customer_ID = c.Customer_ID
GROUP BY c.Customer_ID
ORDER BY Total_Spent DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────
-- QUERY 20 — Customer Purchase Frequency
-- Plain English: On average, how often does a customer place an order?
-- ─────────────────────────────────────────────────────────
-- Q20
SELECT
    ROUND(AVG(order_count), 2)    AS Avg_Orders_Per_Customer,
    MIN(order_count)              AS Min_Orders,
    MAX(order_count)              AS Max_Orders,
    COUNT(CASE WHEN order_count = 1 THEN 1 END) AS One_Time_Buyers,
    COUNT(CASE WHEN order_count > 1 THEN 1 END) AS Repeat_Buyers
FROM (
    SELECT Customer_ID, COUNT(DISTINCT Order_ID) AS order_count
    FROM orders
    GROUP BY Customer_ID
) sub;


-- ─────────────────────────────────────────────────────────
-- QUERY 21 — Monthly Customer Acquisition (New Customers per Month)
-- Plain English: How many new customers joined each month?
-- We define a customer's "join month" as the month of their first order.
-- ─────────────────────────────────────────────────────────
-- Q21
SELECT
    STRFTIME('%Y-%m', first_order) AS Acquisition_Month,
    COUNT(*) AS New_Customers
FROM (
    SELECT Customer_ID, MIN(Order_Date) AS first_order
    FROM orders
    GROUP BY Customer_ID
) sub
GROUP BY STRFTIME('%Y-%m', first_order)
ORDER BY Acquisition_Month;


-- ─────────────────────────────────────────────────────────
-- QUERY 22 — Customer Lifetime Value (CLV) Approximation
-- Plain English: What is the total value each customer has brought since joining?
-- CLV here = total sales per customer (simplified, not predictive)
-- ─────────────────────────────────────────────────────────
-- Q22
SELECT
    c.Customer_Type,
    ROUND(AVG(customer_total), 2)  AS Avg_CLV,
    ROUND(MIN(customer_total), 2)  AS Min_CLV,
    ROUND(MAX(customer_total), 2)  AS Max_CLV,
    ROUND(SUM(customer_total), 2)  AS Total_CLV
FROM (
    SELECT o.Customer_ID, SUM(od.Sales) AS customer_total
    FROM orders o
    JOIN order_details od ON o.Order_ID = od.Order_ID
    GROUP BY o.Customer_ID
) sub
JOIN customers c ON sub.Customer_ID = c.Customer_ID
GROUP BY c.Customer_Type;


-- ─────────────────────────────────────────────────────────
-- QUERY 23 — Products with High Sales but Low Profit
-- Plain English: Which products look popular but barely make money?
-- These are "volume traps" — high revenue, thin margin.
-- HAVING filters groups AFTER aggregation (unlike WHERE which filters rows)
-- ─────────────────────────────────────────────────────────
-- Q23
SELECT
    p.Product_Name,
    p.Category,
    ROUND(SUM(od.Sales), 2)         AS Total_Sales,
    ROUND(SUM(od.Profit), 2)        AS Total_Profit,
    ROUND(SUM(od.Profit) * 100.0
          / SUM(od.Sales), 2)       AS Margin_Pct,
    SUM(od.Quantity)                AS Units_Sold
FROM order_details od
JOIN products p ON od.Product_ID = p.Product_ID
GROUP BY p.Product_ID
HAVING SUM(od.Sales) > 1000000     -- High sales: above ₹10 lakh
   AND (SUM(od.Profit) * 100.0
        / SUM(od.Sales)) < 40      -- Low margin: below 40%
ORDER BY Total_Sales DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 24 — Quarterly Revenue Trend (with Window Function)
-- Plain English: How does each quarter's revenue compare to the previous?
-- LAG() is a window function — it looks at the previous row's value.
-- ─────────────────────────────────────────────────────────
-- Q24
WITH quarterly AS (
    SELECT
        STRFTIME('%Y', o.Order_Date)    AS Year,
        CAST(
            CASE
                WHEN STRFTIME('%m', o.Order_Date) BETWEEN '01' AND '03' THEN 1
                WHEN STRFTIME('%m', o.Order_Date) BETWEEN '04' AND '06' THEN 2
                WHEN STRFTIME('%m', o.Order_Date) BETWEEN '07' AND '09' THEN 3
                ELSE 4
            END AS TEXT
        )                               AS Quarter,
        ROUND(SUM(od.Sales), 2)         AS Revenue,
        ROUND(SUM(od.Profit), 2)        AS Profit
    FROM orders o
    JOIN order_details od ON o.Order_ID = od.Order_ID
    GROUP BY Year, Quarter
)
SELECT
    Year,
    Quarter,
    Revenue,
    Profit,
    LAG(Revenue) OVER (ORDER BY Year, Quarter) AS Prev_Quarter_Revenue,
    ROUND(
        (Revenue - LAG(Revenue) OVER (ORDER BY Year, Quarter))
        * 100.0
        / LAG(Revenue) OVER (ORDER BY Year, Quarter),
    2) AS Revenue_Growth_Pct
FROM quarterly
ORDER BY Year, Quarter;


-- ─────────────────────────────────────────────────────────
-- QUERY 25 — Customer Spending Segments (using CASE + CTE)
-- Plain English: Group customers into High / Medium / Low value tiers.
-- CTE (Common Table Expression) = a temporary named result set.
-- ─────────────────────────────────────────────────────────
-- Q25
WITH customer_spend AS (
    -- Step 1: Calculate total spend per customer
    SELECT
        o.Customer_ID,
        ROUND(SUM(od.Sales), 2)         AS total_spend,
        COUNT(DISTINCT o.Order_ID)      AS order_count
    FROM orders o
    JOIN order_details od ON o.Order_ID = od.Order_ID
    GROUP BY o.Customer_ID
),
segmented AS (
    -- Step 2: Assign a segment label based on spend
    SELECT
        Customer_ID,
        total_spend,
        order_count,
        CASE
            WHEN total_spend >= 500000  THEN 'High Value   (₹5L+)'
            WHEN total_spend >= 200000  THEN 'Medium Value (₹2-5L)'
            WHEN total_spend >= 50000   THEN 'Low Value    (₹50K-2L)'
            ELSE                             'Minimal      (<₹50K)'
        END AS Spend_Segment
    FROM customer_spend
)
-- Step 3: Summarise each segment
SELECT
    Spend_Segment,
    COUNT(*)                           AS Customer_Count,
    ROUND(AVG(total_spend), 2)         AS Avg_Spend,
    ROUND(SUM(total_spend), 2)         AS Segment_Revenue,
    ROUND(AVG(order_count), 2)         AS Avg_Orders
FROM segmented
GROUP BY Spend_Segment
ORDER BY Avg_Spend DESC;
