-- =============================================================
-- customer_analysis.sql
-- Phase 7 — Customer Analytics & RFM Segmentation
-- =============================================================
-- All queries run on ecommerce.db (SQLite)
-- Run via: python sql/run_customer_analysis.py
-- =============================================================


-- ─────────────────────────────────────────────────────────
-- CA-01: Overall Customer Summary
-- ─────────────────────────────────────────────────────────
-- CA01
SELECT
    COUNT(DISTINCT Customer_ID)                       AS Total_Customers,
    SUM(CASE WHEN Customer_Type = 'New'       THEN 1 ELSE 0 END) AS New_Customers,
    SUM(CASE WHEN Customer_Type = 'Returning' THEN 1 ELSE 0 END) AS Returning_Customers,
    ROUND(
        SUM(CASE WHEN Customer_Type = 'Returning' THEN 1 ELSE 0 END) * 100.0
        / COUNT(*), 2)                                AS Returning_Pct
FROM customers;


-- ─────────────────────────────────────────────────────────
-- CA-02: Average Orders per Customer
-- ─────────────────────────────────────────────────────────
-- CA02
SELECT
    ROUND(AVG(order_count), 2)   AS Avg_Orders_Per_Customer,
    MIN(order_count)             AS Min_Orders,
    MAX(order_count)             AS Max_Orders
FROM (
    SELECT Customer_ID, COUNT(DISTINCT Order_ID) AS order_count
    FROM orders
    GROUP BY Customer_ID
);


-- ─────────────────────────────────────────────────────────
-- CA-03: Customer Revenue by Gender
-- ─────────────────────────────────────────────────────────
-- CA03
SELECT
    c.Gender,
    COUNT(DISTINCT c.Customer_ID)                AS Customers,
    COUNT(DISTINCT o.Order_ID)                   AS Orders,
    ROUND(SUM(od.Sales), 2)                      AS Total_Revenue,
    ROUND(SUM(od.Sales) /
          COUNT(DISTINCT c.Customer_ID), 2)      AS Revenue_Per_Customer,
    ROUND(AVG(od.Sales), 2)                      AS Avg_Order_Item_Value
FROM customers c
JOIN orders o       ON c.Customer_ID = o.Customer_ID
JOIN order_details od ON o.Order_ID  = od.Order_ID
GROUP BY c.Gender
ORDER BY Total_Revenue DESC;


-- ─────────────────────────────────────────────────────────
-- CA-04: Customer Revenue by Age Group
-- ─────────────────────────────────────────────────────────
-- CA04
SELECT
    CASE
        WHEN c.Age < 26 THEN '18-25'
        WHEN c.Age < 36 THEN '26-35'
        WHEN c.Age < 46 THEN '36-45'
        WHEN c.Age < 56 THEN '46-55'
        ELSE '56+'
    END                                          AS Age_Group,
    COUNT(DISTINCT c.Customer_ID)                AS Customers,
    COUNT(DISTINCT o.Order_ID)                   AS Orders,
    ROUND(SUM(od.Sales), 2)                      AS Total_Revenue,
    ROUND(SUM(od.Sales) /
          COUNT(DISTINCT c.Customer_ID), 2)      AS Revenue_Per_Customer
FROM customers c
JOIN orders o         ON c.Customer_ID = o.Customer_ID
JOIN order_details od ON o.Order_ID    = od.Order_ID
GROUP BY Age_Group
ORDER BY Age_Group;


-- ─────────────────────────────────────────────────────────
-- CA-05: Customer Revenue by Region
-- ─────────────────────────────────────────────────────────
-- CA05
SELECT
    c.Region,
    COUNT(DISTINCT c.Customer_ID)    AS Customers,
    COUNT(DISTINCT o.Order_ID)       AS Orders,
    ROUND(SUM(od.Sales), 2)          AS Total_Revenue,
    ROUND(SUM(od.Profit), 2)         AS Total_Profit,
    ROUND(SUM(od.Sales) /
          COUNT(DISTINCT c.Customer_ID), 2) AS Revenue_Per_Customer
FROM customers c
JOIN orders o         ON c.Customer_ID = o.Customer_ID
JOIN order_details od ON o.Order_ID    = od.Order_ID
GROUP BY c.Region
ORDER BY Total_Revenue DESC;


-- ─────────────────────────────────────────────────────────
-- CA-06: Retention — Monthly Cohort (first order month + repeat)
-- ─────────────────────────────────────────────────────────
-- CA06
SELECT
    cohort_month,
    COUNT(*)                          AS Cohort_Size,
    SUM(CASE WHEN order_count > 1
             THEN 1 ELSE 0 END)       AS Retained_Customers,
    ROUND(SUM(CASE WHEN order_count > 1
                   THEN 1 ELSE 0 END) * 100.0
          / COUNT(*), 2)              AS Retention_Rate_Pct
FROM (
    SELECT
        Customer_ID,
        STRFTIME('%Y-%m', MIN(Order_Date))   AS cohort_month,
        COUNT(DISTINCT Order_ID)             AS order_count
    FROM orders
    GROUP BY Customer_ID
) sub
GROUP BY cohort_month
ORDER BY cohort_month
LIMIT 24;


-- ─────────────────────────────────────────────────────────
-- CA-07: RFM BASE TABLE
-- RFM = Recency, Frequency, Monetary
--
-- Recency  : How recently did the customer last buy?
--            → Days since last order (lower = better)
-- Frequency: How many orders have they placed?
--            → Total distinct orders
-- Monetary : How much have they spent in total?
--            → Sum of Sales
--
-- We use '2024-12-31' as the reference "today" date.
-- ─────────────────────────────────────────────────────────
-- CA07
WITH rfm_base AS (
    SELECT
        o.Customer_ID,
        MAX(o.Order_Date)                           AS Last_Order_Date,
        CAST(
            JULIANDAY('2024-12-31') -
            JULIANDAY(MAX(o.Order_Date))
        AS INTEGER)                                 AS Recency_Days,
        COUNT(DISTINCT o.Order_ID)                  AS Frequency,
        ROUND(SUM(od.Sales), 2)                     AS Monetary
    FROM orders o
    JOIN order_details od ON o.Order_ID = od.Order_ID
    GROUP BY o.Customer_ID
),
rfm_scores AS (
    SELECT
        Customer_ID,
        Last_Order_Date,
        Recency_Days,
        Frequency,
        Monetary,
        -- Score 1-5: Recency (5 = most recent = best)
        NTILE(5) OVER (ORDER BY Recency_Days DESC)  AS R_Score,
        -- Score 1-5: Frequency (5 = most frequent = best)
        NTILE(5) OVER (ORDER BY Frequency ASC)      AS F_Score,
        -- Score 1-5: Monetary (5 = highest spender = best)
        NTILE(5) OVER (ORDER BY Monetary ASC)       AS M_Score
    FROM rfm_base
)
SELECT
    Customer_ID,
    Recency_Days,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    (R_Score + F_Score + M_Score)                   AS RFM_Total,
    ROUND((R_Score + F_Score + M_Score) / 3.0, 2)  AS RFM_Avg
FROM rfm_scores
ORDER BY RFM_Total DESC
LIMIT 20;


-- ─────────────────────────────────────────────────────────
-- CA-08: RFM SEGMENTS — Label each customer
-- RFM Total Score 13-15 = Champions
-- RFM Total Score 10-12 = Loyal Customers
-- RFM Total Score 7-9   = At Risk
-- RFM Total Score 4-6   = Hibernating
-- RFM Total Score 0-3   = Lost
-- ─────────────────────────────────────────────────────────
-- CA08
WITH rfm_base AS (
    SELECT
        o.Customer_ID,
        CAST(
            JULIANDAY('2024-12-31') -
            JULIANDAY(MAX(o.Order_Date))
        AS INTEGER)                                  AS Recency_Days,
        COUNT(DISTINCT o.Order_ID)                   AS Frequency,
        ROUND(SUM(od.Sales), 2)                      AS Monetary
    FROM orders o
    JOIN order_details od ON o.Order_ID = od.Order_ID
    GROUP BY o.Customer_ID
),
rfm_scored AS (
    SELECT
        Customer_ID,
        Recency_Days,
        Frequency,
        Monetary,
        NTILE(5) OVER (ORDER BY Recency_Days DESC) AS R,
        NTILE(5) OVER (ORDER BY Frequency ASC)    AS F,
        NTILE(5) OVER (ORDER BY Monetary ASC)     AS M
    FROM rfm_base
),
rfm_segmented AS (
    SELECT
        Customer_ID,
        Recency_Days,
        Frequency,
        Monetary,
        (R + F + M)   AS RFM_Score,
        CASE
            WHEN (R + F + M) >= 13 THEN 'Champions'
            WHEN (R + F + M) >= 10 THEN 'Loyal Customers'
            WHEN (R + F + M) >= 7  THEN 'At Risk'
            WHEN (R + F + M) >= 4  THEN 'Hibernating'
            ELSE                        'Lost'
        END           AS RFM_Segment
    FROM rfm_scored
)
SELECT
    RFM_Segment,
    COUNT(*)                              AS Customer_Count,
    ROUND(COUNT(*) * 100.0 / 5000, 2)    AS Pct_Of_Customers,
    ROUND(AVG(Recency_Days), 1)           AS Avg_Recency_Days,
    ROUND(AVG(Frequency), 1)              AS Avg_Frequency,
    ROUND(AVG(Monetary), 2)               AS Avg_Monetary,
    ROUND(SUM(Monetary), 2)               AS Segment_Revenue
FROM rfm_segmented
GROUP BY RFM_Segment
ORDER BY Avg_Monetary DESC;


-- ─────────────────────────────────────────────────────────
-- CA-09: High Value Customers detail (RFM Champions)
-- ─────────────────────────────────────────────────────────
-- CA09
WITH rfm_base AS (
    SELECT
        o.Customer_ID,
        CAST(JULIANDAY('2024-12-31') -
             JULIANDAY(MAX(o.Order_Date)) AS INTEGER)  AS Recency_Days,
        COUNT(DISTINCT o.Order_ID)                      AS Frequency,
        ROUND(SUM(od.Sales), 2)                         AS Monetary
    FROM orders o
    JOIN order_details od ON o.Order_ID = od.Order_ID
    GROUP BY o.Customer_ID
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY Recency_Days DESC) AS R,
        NTILE(5) OVER (ORDER BY Frequency ASC)    AS F,
        NTILE(5) OVER (ORDER BY Monetary ASC)     AS M
    FROM rfm_base
)
SELECT
    rs.Customer_ID,
    c.Customer_Name,
    c.Gender,
    c.Age,
    c.Region,
    c.Customer_Type,
    rs.Recency_Days,
    rs.Frequency,
    rs.Monetary,
    (rs.R + rs.F + rs.M) AS RFM_Score
FROM rfm_scored rs
JOIN customers c ON rs.Customer_ID = c.Customer_ID
WHERE (rs.R + rs.F + rs.M) >= 13
ORDER BY rs.Monetary DESC
LIMIT 15;


-- ─────────────────────────────────────────────────────────
-- CA-10: Revenue Contribution by Segment (Pareto Check)
-- How much of total revenue comes from the top 20% of customers?
-- ─────────────────────────────────────────────────────────
-- CA10
WITH customer_revenue AS (
    SELECT
        o.Customer_ID,
        ROUND(SUM(od.Sales), 2) AS total_spent
    FROM orders o
    JOIN order_details od ON o.Order_ID = od.Order_ID
    GROUP BY o.Customer_ID
    ORDER BY total_spent DESC
),
ranked AS (
    SELECT
        Customer_ID,
        total_spent,
        ROW_NUMBER() OVER (ORDER BY total_spent DESC) AS rank_num
    FROM customer_revenue
),
total AS (SELECT SUM(total_spent) AS grand_total FROM customer_revenue)
SELECT
    CASE
        WHEN rank_num <= 500  THEN 'Top 10% (500 customers)'
        WHEN rank_num <= 1000 THEN 'Next 10% (501-1000)'
        WHEN rank_num <= 2500 THEN 'Middle 30% (1001-2500)'
        ELSE                       'Bottom 50% (2501-5000)'
    END                                               AS Customer_Tier,
    COUNT(*)                                          AS Customer_Count,
    ROUND(SUM(total_spent), 2)                        AS Tier_Revenue,
    ROUND(SUM(total_spent) * 100.0
          / (SELECT grand_total FROM total), 2)       AS Revenue_Share_Pct
FROM ranked
GROUP BY Customer_Tier
ORDER BY Revenue_Share_Pct DESC;
