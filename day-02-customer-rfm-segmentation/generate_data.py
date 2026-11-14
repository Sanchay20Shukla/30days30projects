"""Generate a deterministic synthetic order history for the Day 2 RFM project."""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "transactions.csv"
SEED = 20261114
START = date(2025, 1, 1)
END = date(2026, 10, 31)


def main() -> None:
    rng = random.Random(SEED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str | int | float]] = []
    order_number = 1
    for customer_num in range(1, 181):
        customer_id = f"C{customer_num:04d}"
        # Three intentionally mixed behavioral profiles create interpretable,
        # but not hard-coded, RFM variation.
        profile = (customer_num - 1) % 3
        count = rng.randint(2, 5) if profile == 0 else rng.randint(5, 9) if profile == 1 else rng.randint(9, 15)
        latest_offset = rng.randint(0, 45) if profile == 2 else rng.randint(20, 240) if profile == 1 else rng.randint(100, 500)
        latest = min(END, END - timedelta(days=latest_offset))
        span = (latest - START).days
        dates = sorted({START + timedelta(days=rng.randint(0, max(0, span))) for _ in range(count - 1)} | {latest})
        while len(dates) < count:
            dates.append(latest - timedelta(days=rng.randint(0, max(1, min(30, span)))))
        dates = sorted(dates[:count])
        for purchased in dates:
            amount = round(rng.lognormvariate(3.55 + (0.18 if profile == 2 else 0), 0.55), 2)
            rows.append({
                "order_id": f"O{order_number:06d}",
                "customer_id": customer_id,
                "order_date": purchased.isoformat(),
                "order_amount": amount,
            })
            order_number += 1
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["order_id", "customer_id", "order_date", "order_amount"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} orders for 180 customers to {OUT}")


if __name__ == "__main__":
    main()
