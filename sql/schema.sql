-- =============================================================
-- schema.sql
-- E-Commerce Sales & Customer Analytics
-- Phase 6 — SQL Database Schema
-- =============================================================
-- Database : SQLite  (file: ecommerce.db)
-- Run via  : python sql/load_database.py   (creates DB + loads data)
-- =============================================================

-- Drop tables if they already exist (safe re-run)
DROP TABLE IF EXISTS order_details;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS regions;

-- =============================================================
-- TABLE 1: regions
-- Lookup table — one row per city
-- =============================================================
CREATE TABLE regions (
    Region_ID   TEXT PRIMARY KEY,
    Region      TEXT NOT NULL,
    State       TEXT NOT NULL,
    City        TEXT NOT NULL
);

-- =============================================================
-- TABLE 2: products
-- Master product catalogue
-- =============================================================
CREATE TABLE products (
    Product_ID   TEXT PRIMARY KEY,
    Category     TEXT NOT NULL,
    Sub_Category TEXT NOT NULL,
    Product_Name TEXT NOT NULL,
    Cost         REAL NOT NULL,         -- wholesale cost per unit (₹)
    Unit_Price   REAL NOT NULL          -- selling price per unit (₹)
);

-- =============================================================
-- TABLE 3: customers
-- Customer master data
-- =============================================================
CREATE TABLE customers (
    Customer_ID   TEXT PRIMARY KEY,
    Customer_Name TEXT NOT NULL,
    Gender        TEXT NOT NULL,        -- Male / Female
    Age           INTEGER NOT NULL,
    City          TEXT NOT NULL,
    State         TEXT NOT NULL,
    Region        TEXT NOT NULL,
    Customer_Type TEXT NOT NULL         -- New / Returning
);

-- =============================================================
-- TABLE 4: orders
-- One row per order (header)
-- =============================================================
CREATE TABLE orders (
    Order_ID     TEXT PRIMARY KEY,
    Order_Date   TEXT NOT NULL,         -- stored as YYYY-MM-DD text in SQLite
    Customer_ID  TEXT NOT NULL,
    Payment_Mode TEXT NOT NULL,
    Order_Status TEXT NOT NULL,
    FOREIGN KEY (Customer_ID) REFERENCES customers(Customer_ID)
);

-- =============================================================
-- TABLE 5: order_details
-- One row per product per order (line items)
-- This table holds all the financial data
-- =============================================================
CREATE TABLE order_details (
    Detail_ID    TEXT PRIMARY KEY,
    Order_ID     TEXT    NOT NULL,
    Product_ID   TEXT    NOT NULL,
    Quantity     INTEGER NOT NULL,
    Unit_Price   REAL    NOT NULL,      -- price at time of order
    Discount     REAL    NOT NULL,      -- 0.0 to 1.0
    Sales        REAL    NOT NULL,      -- Unit_Price × Qty × (1 - Discount)
    Cost         REAL    NOT NULL,      -- product cost × Qty
    Profit       REAL    NOT NULL,      -- Sales - Cost
    FOREIGN KEY (Order_ID)   REFERENCES orders(Order_ID),
    FOREIGN KEY (Product_ID) REFERENCES products(Product_ID)
);

-- =============================================================
-- INDEXES (speed up GROUP BY and JOIN queries)
-- =============================================================
CREATE INDEX IF NOT EXISTS idx_orders_date       ON orders(Order_Date);
CREATE INDEX IF NOT EXISTS idx_orders_customer   ON orders(Customer_ID);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(Order_Status);
CREATE INDEX IF NOT EXISTS idx_details_order     ON order_details(Order_ID);
CREATE INDEX IF NOT EXISTS idx_details_product   ON order_details(Product_ID);
CREATE INDEX IF NOT EXISTS idx_customers_region  ON customers(Region);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(Category);
