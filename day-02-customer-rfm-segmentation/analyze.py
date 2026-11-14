"""Load the synthetic CSV into SQLite and produce RFM and Pareto summaries."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REFERENCE_DATE = "2026-11-01"


def main() -> None:
    with (ROOT / "data" / "transactions.csv").open(newline="", encoding="utf-8") as f:
        orders = list(csv.DictReader(f))
    if not orders:
        raise SystemExit("No orders found. Run generate_data.py first.")

    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE transactions (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        order_date TEXT NOT NULL,
        order_amount REAL NOT NULL CHECK (order_amount > 0)
    )""")
    db.executemany(
        "INSERT INTO transactions VALUES (:order_id, :customer_id, :order_date, :order_amount)",
        [{**row, "order_amount": float(row["order_amount"])} for row in orders],
    )
    checks = db.execute("""SELECT
        COUNT(*) AS order_count,
        COUNT(DISTINCT order_id) AS distinct_order_count,
        SUM(CASE WHEN customer_id IS NULL OR order_date IS NULL OR order_amount IS NULL THEN 1 ELSE 0 END) AS null_rows,
        SUM(CASE WHEN order_amount <= 0 THEN 1 ELSE 0 END) AS nonpositive_amounts
        FROM transactions""").fetchone()
    assert checks["order_count"] == checks["distinct_order_count"], "Duplicate order IDs found"
    assert checks["null_rows"] == 0, "Null required field found"
    assert checks["nonpositive_amounts"] == 0, "Non-positive order amount found"

    sql = (ROOT / "sql" / "analysis.sql").read_text(encoding="utf-8")
    rows = db.execute(sql, {"reference_date": REFERENCE_DATE}).fetchall()
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    customer_fields = list(rows[0].keys())
    with (out / "customer_rfm.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=customer_fields)
        writer.writeheader()
        writer.writerows([dict(row) for row in rows])

    # Summarize the query results in Python to keep the SQL file focused on customer-level logic.
    groups: dict[str, dict[str, float]] = {}
    total_revenue = sum(float(row["monetary"]) for row in rows)
    for row in rows:
        item = groups.setdefault(row["segment"], {"customers": 0, "revenue": 0.0})
        item["customers"] += 1
        item["revenue"] += float(row["monetary"])
    summary_rows = [
        {"segment": name, "customers": int(values["customers"]),
         "revenue": round(values["revenue"], 2),
         "revenue_share_pct": round(100 * values["revenue"] / total_revenue, 2)}
        for name, values in sorted(groups.items())
    ]
    with (out / "segment_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["segment", "customers", "revenue", "revenue_share_pct"])
        writer.writeheader()
        writer.writerows(summary_rows)

    top20_count = max(1, round(len(rows) * 0.20))
    top20 = sorted((float(row["monetary"]) for row in rows), reverse=True)[:top20_count]
    print(f"Reference date: {REFERENCE_DATE}")
    print(f"Data quality: {checks['order_count']} unique orders; no nulls or non-positive amounts")
    print(f"Customers: {len(rows)} | Orders: {len(orders)} | Gross revenue: ${total_revenue:,.2f}")
    print(f"Top {top20_count} customers ({100*top20_count/len(rows):.1f}%) revenue share: {100*sum(top20)/total_revenue:.1f}%")
    print("\nSegment summary")
    for item in summary_rows:
        print(f"{item['segment']}: {item['customers']} customers, ${item['revenue']:,.2f} ({item['revenue_share_pct']:.1f}%)")
    print(f"\nWrote outputs to {out}")
    db.close()


if __name__ == "__main__":
    main()
