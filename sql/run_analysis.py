"""
run_analysis.py
----------------
Phase 6 — Runs all 25 SQL analysis queries against ecommerce.db
and prints formatted results.

Run: python sql/run_analysis.py
"""

import sqlite3
import os
import re

BASE_DIR  = os.path.join(os.path.dirname(__file__), "..")
DB_PATH   = os.path.join(BASE_DIR, "sql", "ecommerce.db")
SQL_PATH  = os.path.join(BASE_DIR, "sql", "analysis_queries.sql")

SEP  = "=" * 65
SEP2 = "-" * 65

QUERY_TITLES = {
    1:  "Total Revenue, Cost & Profit",
    2:  "Total Orders, Customers, Products",
    3:  "Average Order Value (AOV)",
    4:  "Monthly Revenue Trend",
    5:  "Yearly Revenue Comparison",
    6:  "Top 10 Products by Revenue",
    7:  "Top 10 Products by Profit",
    8:  "Bottom 10 Products",
    9:  "Category Performance",
    10: "Sub-Category Performance",
    11: "Regional Performance",
    12: "Top 10 States by Revenue",
    13: "Profit Margin by Category",
    14: "Sales by Payment Method",
    15: "Cancelled & Returned Orders",
    16: "Average Quantity Per Order",
    17: "Customer Purchase Frequency Buckets",
    18: "New vs Returning Customer Revenue",
    19: "Top 10 Customers by Spending",
    20: "Customer Purchase Frequency Stats",
    21: "Monthly Customer Acquisition",
    22: "Customer Lifetime Value by Segment",
    23: "High Sales but Low Profit Products",
    24: "Quarterly Revenue with Growth %",
    25: "Customer Spending Segments",
}

def print_results(cursor, query_num):
    """Print query results in a readable table."""
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description] if cursor.description else []

    if not rows:
        print("  (no rows returned)")
        return

    # Calculate column widths
    widths = [len(c) for c in cols]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val) if val is not None else "NULL"))

    # Header
    header = "  " + "  ".join(c.ljust(widths[i]) for i, c in enumerate(cols))
    divider = "  " + "  ".join("-" * w for w in widths)
    print(header)
    print(divider)

    # Rows (limit display to 20 rows to avoid wall of text)
    display_rows = rows[:20]
    for row in display_rows:
        line = "  " + "  ".join(
            str(v if v is not None else "NULL").ljust(widths[i])
            for i, v in enumerate(row)
        )
        print(line)

    if len(rows) > 20:
        print(f"  ... ({len(rows) - 20} more rows not shown)")

    print(f"\n  Total rows returned: {len(rows)}")


def parse_queries(sql_text):
    """
    Split the SQL file into individual queries using -- Q<n> markers.
    Returns dict: {query_num: sql_string}
    """
    queries = {}
    # Split on -- Q<number> markers
    parts = re.split(r'--\s*Q(\d+)\s*\n', sql_text)
    # parts = [preamble, num, sql, num, sql, ...]
    i = 1
    while i < len(parts) - 1:
        num = int(parts[i])
        sql = parts[i + 1].strip()
        # Take only up to the next comment block or end
        sql_clean = sql.split("\n\n-- ─")[0].strip()
        queries[num] = sql_clean
        i += 2
    return queries


def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Run this first:  python sql/load_database.py")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read and parse query file
    with open(SQL_PATH, "r", encoding="utf-8") as f:
        sql_text = f.read()

    queries = parse_queries(sql_text)

    print(SEP)
    print("  Phase 6 — SQL Analysis Results")
    print(f"  Database: {DB_PATH}")
    print(SEP)

    for qnum in sorted(queries.keys()):
        title = QUERY_TITLES.get(qnum, f"Query {qnum}")
        print(f"\n{'─'*65}")
        print(f"  QUERY {qnum:02d}: {title}")
        print(f"{'─'*65}")

        sql = queries[qnum]
        try:
            cursor.execute(sql)
            print_results(cursor, qnum)
        except Exception as e:
            print(f"  ERROR: {e}")
            print(f"  SQL: {sql[:200]}...")

    conn.close()
    print(f"\n{SEP}")
    print("  All 25 queries executed successfully")
    print(SEP)


if __name__ == "__main__":
    main()
