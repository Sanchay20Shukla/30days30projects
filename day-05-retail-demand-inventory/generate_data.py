"""Generate a deterministic daily retail demand and inventory snapshot dataset."""
from __future__ import annotations
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 20261117
START = date(2025, 1, 1)
DAYS = 365
PRODUCT_COUNT = 24
WEEKDAY_FACTOR = [0.80, 0.86, 0.93, 0.96, 1.04, 1.22, 1.19]
MONTH_FACTOR = [0.96, 0.94, 0.98, 1.00, 1.02, 1.03, 1.01, 1.00, 1.02, 1.04, 1.14, 1.30]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    categories = ["Pantry", "Household", "Personal Care", "Snacks"]
    products: list[dict[str, object]] = []
    sales: list[dict[str, object]] = []
    for i in range(1, PRODUCT_COUNT + 1):
        product_id = f"SKU{i:03d}"
        base = rng.uniform(7, 55)
        tier = rng.choices(["A", "B", "C"], [0.25, 0.40, 0.35])[0]
        lead_time = rng.randint(3, 14)
        products.append({
            "product_id": product_id,
            "category": categories[(i - 1) % len(categories)],
            "abc_tier": tier,
            "unit_cost": round(rng.uniform(2.5, 28), 2),
            "avg_daily_demand": round(base, 2),
            "lead_time_days": lead_time,
            "on_hand_units": rng.randint(max(2, int(base * 1.5)), int(base * 10 + 30)),
            "on_order_units": rng.choice([0, 0, 0, rng.randint(10, 120)]),
            "minimum_order_qty": rng.choice([6, 12, 24]),
        })
        sku_shift = rng.uniform(0.96, 1.04)
        trend = rng.uniform(-0.00015, 0.00035)
        for day_index in range(DAYS):
            current = START + timedelta(days=day_index)
            promo = 1 if rng.random() < 0.055 else 0
            promo_factor = 1.28 if promo else 1.0
            mean = base * sku_shift * WEEKDAY_FACTOR[current.weekday()] * MONTH_FACTOR[current.month - 1]
            mean *= (1 + trend * day_index) * promo_factor
            units = max(0, round(rng.gauss(mean, max(1.4, mean * 0.17))))
            sales.append({"date": current.isoformat(), "product_id": product_id,
                          "units_sold": units, "promo_flag": promo})

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    write_csv(data_dir / "products.csv", products)
    write_csv(data_dir / "daily_sales.csv", sales)
    promo_days = sum(int(r["promo_flag"]) for r in sales)
    print(f"Generated {len(products)} products and {len(sales):,} product-day records ({promo_days:,} promo days).")


if __name__ == "__main__":
    main()
