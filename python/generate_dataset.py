"""
generate_dataset.py
-------------------
Generates a realistic e-commerce dataset with 50,000 order records
split into 5 relational tables:

    1. customers.csv
    2. products.csv
    3. regions.csv
    4. orders.csv
    5. order_details.csv

Run this script once to produce the raw data files.
All files are saved to: data/raw/
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# Reproducibility — same seed = same dataset
# ─────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

# Output folder
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("  E-Commerce Dataset Generator")
print("=" * 60)


# ═══════════════════════════════════════════════════
# TABLE 1 — REGIONS
# ═══════════════════════════════════════════════════
# A small lookup table: Region → State → City
# Every order will link to one region record.

regions_data = [
    # Region,      State,              City
    ("North",      "Delhi",            "New Delhi"),
    ("North",      "Uttar Pradesh",    "Lucknow"),
    ("North",      "Uttar Pradesh",    "Agra"),
    ("North",      "Punjab",           "Amritsar"),
    ("North",      "Haryana",          "Gurugram"),
    ("North",      "Rajasthan",        "Jaipur"),
    ("North",      "Rajasthan",        "Udaipur"),
    ("South",      "Karnataka",        "Bengaluru"),
    ("South",      "Karnataka",        "Mysuru"),
    ("South",      "Tamil Nadu",       "Chennai"),
    ("South",      "Tamil Nadu",       "Coimbatore"),
    ("South",      "Andhra Pradesh",   "Hyderabad"),
    ("South",      "Kerala",           "Kochi"),
    ("East",       "West Bengal",      "Kolkata"),
    ("East",       "West Bengal",      "Siliguri"),
    ("East",       "Odisha",           "Bhubaneswar"),
    ("East",       "Bihar",            "Patna"),
    ("East",       "Jharkhand",        "Ranchi"),
    ("West",       "Maharashtra",      "Mumbai"),
    ("West",       "Maharashtra",      "Pune"),
    ("West",       "Gujarat",          "Ahmedabad"),
    ("West",       "Gujarat",          "Surat"),
    ("West",       "Goa",              "Panaji"),
    ("Central",    "Madhya Pradesh",   "Bhopal"),
    ("Central",    "Madhya Pradesh",   "Indore"),
    ("Central",    "Chhattisgarh",     "Raipur"),
]

regions_df = pd.DataFrame(regions_data, columns=["Region", "State", "City"])
regions_df.insert(0, "Region_ID", ["RGN" + str(i + 1).zfill(3) for i in range(len(regions_df))])

print(f"[1/5] Regions table       : {len(regions_df)} records")


# ═══════════════════════════════════════════════════
# TABLE 2 — PRODUCTS
# ═══════════════════════════════════════════════════
# Each product has a Category, Sub_Category, name, and base cost.
# Unit_Price = Cost * markup (1.3x to 2.5x depending on category).

products_data = [
    # Category,        Sub_Category,      Product_Name,                   Base_Cost
    ("Electronics",    "Smartphones",     "Samsung Galaxy A54",            18000),
    ("Electronics",    "Smartphones",     "Redmi Note 12",                 12000),
    ("Electronics",    "Smartphones",     "Apple iPhone 13",               55000),
    ("Electronics",    "Smartphones",     "OnePlus Nord CE 3",             22000),
    ("Electronics",    "Laptops",         "HP Pavilion 15",                42000),
    ("Electronics",    "Laptops",         "Dell Inspiron 14",              48000),
    ("Electronics",    "Laptops",         "Lenovo IdeaPad Slim 5",         38000),
    ("Electronics",    "Laptops",         "Acer Aspire 7",                 45000),
    ("Electronics",    "Accessories",     "boAt Rockerz 450 Headphones",   1500),
    ("Electronics",    "Accessories",     "Anker USB-C Charger",            800),
    ("Electronics",    "Accessories",     "JBL Clip 4 Speaker",            3500),
    ("Electronics",    "Accessories",     "MI Smart Band 7",               2500),
    ("Electronics",    "Tablets",         "Samsung Galaxy Tab A8",         18000),
    ("Electronics",    "Tablets",         "Lenovo Tab M10",                14000),
    ("Clothing",       "Men Wear",        "Levi's 511 Slim Jeans",          2800),
    ("Clothing",       "Men Wear",        "Allen Solly Formal Shirt",       1800),
    ("Clothing",       "Men Wear",        "Puma Running T-Shirt",            900),
    ("Clothing",       "Men Wear",        "US Polo Chinos",                 2200),
    ("Clothing",       "Women Wear",      "W Brand Kurta Set",              1600),
    ("Clothing",       "Women Wear",      "Biba Embroidered Suit",          2400),
    ("Clothing",       "Women Wear",      "Mango Floral Dress",             3200),
    ("Clothing",       "Women Wear",      "Zara Blazer",                    4500),
    ("Clothing",       "Kids Wear",       "H&M Kids Hoodie",                1200),
    ("Clothing",       "Kids Wear",       "Carter's Baby Onesie",            600),
    ("Clothing",       "Footwear",        "Nike Air Max 270",               8000),
    ("Clothing",       "Footwear",        "Adidas Ultraboost 22",          10000),
    ("Clothing",       "Footwear",        "Bata Casual Loafer",             2200),
    ("Home & Kitchen", "Furniture",       "IKEA KALLAX Shelf",             12000),
    ("Home & Kitchen", "Furniture",       "Wooden Study Table",             8500),
    ("Home & Kitchen", "Appliances",      "Prestige Induction Cooktop",     3500),
    ("Home & Kitchen", "Appliances",      "Butterfly Electric Kettle",      1200),
    ("Home & Kitchen", "Appliances",      "Bajaj Mixer Grinder",            2800),
    ("Home & Kitchen", "Kitchen Tools",   "Borosil Glass Set (6 pcs)",       900),
    ("Home & Kitchen", "Kitchen Tools",   "Hawkins Pressure Cooker 5L",     2200),
    ("Home & Kitchen", "Decor",           "IKEA Artificial Plant",           600),
    ("Home & Kitchen", "Decor",           "Wooden Photo Frame Set",          800),
    ("Books",          "Academic",        "Data Science from Scratch",      1200),
    ("Books",          "Academic",        "Python Crash Course",             950),
    ("Books",          "Academic",        "SQL in 10 Minutes",               750),
    ("Books",          "Fiction",         "Atomic Habits",                   499),
    ("Books",          "Fiction",         "The Alchemist",                   299),
    ("Books",          "Fiction",         "Rich Dad Poor Dad",               399),
    ("Books",          "Children",        "Panchatantra Stories",            250),
    ("Sports",         "Cricket",         "SG Cricket Bat",                 4500),
    ("Sports",         "Cricket",         "Kookaburra Cricket Ball (6pk)",   800),
    ("Sports",         "Fitness",         "Boldfit Resistance Bands Set",    650),
    ("Sports",         "Fitness",         "Strauss Yoga Mat",                899),
    ("Sports",         "Fitness",         "Nivia Basketball",               1200),
    ("Sports",         "Badminton",       "Yonex Badminton Racket",         2200),
    ("Beauty",         "Skincare",        "Neutrogena Face Wash",            450),
    ("Beauty",         "Skincare",        "Lakme Sunscreen SPF 50",          380),
    ("Beauty",         "Haircare",        "Dove Shampoo 650ml",              350),
    ("Beauty",         "Haircare",        "WOW Apple Cider Vinegar Shampoo", 550),
    ("Beauty",         "Makeup",          "Maybelline Fit Me Foundation",    600),
    ("Beauty",         "Makeup",          "L'Oreal Lipstick",                750),
    ("Groceries",      "Staples",         "Aashirvaad Atta 10kg",            430),
    ("Groceries",      "Staples",         "Fortune Basmati Rice 5kg",        380),
    ("Groceries",      "Snacks",          "Lay's Party Pack",                250),
    ("Groceries",      "Snacks",          "Cadbury Celebration Box",         450),
    ("Groceries",      "Beverages",       "Nescafe Classic 200g",            550),
    ("Groceries",      "Beverages",       "Tata Tea Premium 500g",           280),
]

products_df = pd.DataFrame(
    products_data,
    columns=["Category", "Sub_Category", "Product_Name", "Cost"]
)
products_df.insert(0, "Product_ID", ["PRD" + str(i + 1).zfill(4) for i in range(len(products_df))])

# Apply category-based markup to set Unit_Price
markup_map = {
    "Electronics":    2.2,
    "Clothing":       2.0,
    "Home & Kitchen": 1.8,
    "Books":          1.5,
    "Sports":         1.7,
    "Beauty":         2.0,
    "Groceries":      1.3,
}
products_df["Unit_Price"] = products_df.apply(
    lambda row: round(row["Cost"] * markup_map.get(row["Category"], 1.8), -1),
    axis=1
).astype(int)

print(f"[2/5] Products table      : {len(products_df)} records")


# ═══════════════════════════════════════════════════
# TABLE 3 — CUSTOMERS
# ═══════════════════════════════════════════════════
# 5,000 unique customers with demographic information.

NUM_CUSTOMERS = 5000

first_names_male   = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh",
                       "Ayaan","Krishna","Ishaan","Rohit","Amit","Suresh","Ramesh",
                       "Kiran","Nikhil","Rahul","Prateek","Deepak","Manish"]
first_names_female = ["Aadhya","Ananya","Pari","Anika","Navya","Diya","Mahi",
                       "Ishita","Pooja","Riya","Priya","Sneha","Anjali","Kavya",
                       "Lakshmi","Nisha","Sonal","Meera","Divya","Simran"]
last_names         = ["Sharma","Verma","Patel","Singh","Kumar","Gupta","Mehta",
                       "Joshi","Nair","Iyer","Reddy","Pillai","Yadav","Mishra",
                       "Chatterjee","Bose","Das","Shah","Agarwal","Jain"]

genders     = np.random.choice(["Male", "Female"], size=NUM_CUSTOMERS, p=[0.55, 0.45])
ages        = np.random.randint(18, 65, size=NUM_CUSTOMERS)

names = []
for g in genders:
    if g == "Male":
        names.append(random.choice(first_names_male) + " " + random.choice(last_names))
    else:
        names.append(random.choice(first_names_female) + " " + random.choice(last_names))

# Assign a random city to each customer
customer_cities = regions_df.sample(n=NUM_CUSTOMERS, replace=True).reset_index(drop=True)

customers_df = pd.DataFrame({
    "Customer_ID":   ["CUST" + str(i + 1).zfill(5) for i in range(NUM_CUSTOMERS)],
    "Customer_Name": names,
    "Gender":        genders,
    "Age":           ages,
    "City":          customer_cities["City"].values,
    "State":         customer_cities["State"].values,
    "Region":        customer_cities["Region"].values,
    "Customer_Type": np.random.choice(
                         ["New", "Returning"],
                         size=NUM_CUSTOMERS,
                         p=[0.40, 0.60]       # 60 % returning, realistic for e-commerce
                     ),
})

print(f"[3/5] Customers table     : {len(customers_df)} records")


# ═══════════════════════════════════════════════════
# TABLE 4 — ORDERS
# ═══════════════════════════════════════════════════
# 50,000 orders over Jan 2022 – Dec 2024 (3 full years).

NUM_ORDERS = 50000

start_date = datetime(2022, 1, 1)
end_date   = datetime(2024, 12, 31)
date_range = (end_date - start_date).days

# Simulate seasonal spikes: Oct–Dec (festive) and Jan–Feb (New Year sales)
def random_order_date():
    """Returns a date biased toward festive months."""
    while True:
        d = start_date + timedelta(days=random.randint(0, date_range))
        month = d.month
        # Higher probability in Oct, Nov, Dec, Jan
        if month in [10, 11, 12]:
            if random.random() < 0.7:
                return d
        elif month in [1, 2]:
            if random.random() < 0.55:
                return d
        else:
            if random.random() < 0.35:
                return d

order_dates = [random_order_date() for _ in range(NUM_ORDERS)]
order_dates.sort()

payment_modes   = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery", "EMI"]
payment_weights = [0.20, 0.18, 0.30, 0.10, 0.15, 0.07]

order_statuses   = ["Delivered", "Shipped", "Cancelled", "Returned", "Processing"]
status_weights   = [0.72, 0.10, 0.09, 0.06, 0.03]

orders_df = pd.DataFrame({
    "Order_ID":    ["ORD" + str(i + 1).zfill(6) for i in range(NUM_ORDERS)],
    "Order_Date":  [d.strftime("%Y-%m-%d") for d in order_dates],
    "Customer_ID": np.random.choice(customers_df["Customer_ID"], size=NUM_ORDERS),
    "Payment_Mode": np.random.choice(payment_modes, size=NUM_ORDERS, p=payment_weights),
    "Order_Status": np.random.choice(order_statuses, size=NUM_ORDERS, p=status_weights),
})

print(f"[4/5] Orders table        : {len(orders_df)} records")


# ═══════════════════════════════════════════════════
# TABLE 5 — ORDER_DETAILS
# ═══════════════════════════════════════════════════
# Each order can have 1–4 line items (products).
# Sales = Unit_Price * Quantity * (1 - Discount)
# Profit = Sales - (Cost * Quantity)

order_detail_rows = []
detail_id = 1

for _, order in orders_df.iterrows():
    num_items = np.random.choice([1, 2, 3, 4], p=[0.55, 0.28, 0.12, 0.05])
    # Pick 'num_items' distinct products for this order
    selected_products = products_df.sample(n=num_items)

    for _, prod in selected_products.iterrows():
        quantity = int(np.random.choice([1, 2, 3, 4, 5], p=[0.50, 0.25, 0.12, 0.08, 0.05]))

        # Discount: most items have 0–20% off; electronics sometimes up to 30%
        if prod["Category"] == "Electronics":
            discount = round(random.choice([0, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]), 2)
        elif prod["Category"] in ["Groceries", "Books"]:
            discount = round(random.choice([0, 0, 0, 0.05, 0.10]), 2)
        else:
            discount = round(random.choice([0, 0, 0.05, 0.10, 0.15, 0.20]), 2)

        unit_price = prod["Unit_Price"]
        cost       = prod["Cost"]
        sales      = round(unit_price * quantity * (1 - discount), 2)
        total_cost = round(cost * quantity, 2)
        profit     = round(sales - total_cost, 2)

        order_detail_rows.append({
            "Detail_ID":    "DTL" + str(detail_id).zfill(7),
            "Order_ID":     order["Order_ID"],
            "Product_ID":   prod["Product_ID"],
            "Quantity":     quantity,
            "Unit_Price":   unit_price,
            "Discount":     discount,
            "Sales":        sales,
            "Cost":         total_cost,
            "Profit":       profit,
        })
        detail_id += 1

order_details_df = pd.DataFrame(order_detail_rows)

print(f"[5/5] Order Details table : {len(order_details_df)} records")


# ═══════════════════════════════════════════════════
# SAVE ALL TABLES TO CSV
# ═══════════════════════════════════════════════════

regions_df.to_csv(      os.path.join(OUTPUT_DIR, "regions.csv"),       index=False)
products_df.to_csv(     os.path.join(OUTPUT_DIR, "products.csv"),      index=False)
customers_df.to_csv(    os.path.join(OUTPUT_DIR, "customers.csv"),     index=False)
orders_df.to_csv(       os.path.join(OUTPUT_DIR, "orders.csv"),        index=False)
order_details_df.to_csv(os.path.join(OUTPUT_DIR, "order_details.csv"), index=False)

print("\n✅ All 5 CSV files saved to:", os.path.abspath(OUTPUT_DIR))
print("\nSummary")
print("-" * 40)
print(f"  Regions        : {len(regions_df):>8,} rows")
print(f"  Products       : {len(products_df):>8,} rows")
print(f"  Customers      : {len(customers_df):>8,} rows")
print(f"  Orders         : {len(orders_df):>8,} rows")
print(f"  Order Details  : {len(order_details_df):>8,} rows")
print(f"  Total records  : {len(regions_df)+len(products_df)+len(customers_df)+len(orders_df)+len(order_details_df):>8,}")
