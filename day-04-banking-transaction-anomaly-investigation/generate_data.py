"""Generate a deterministic synthetic banking transaction investigation dataset."""
from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 20261116
START = datetime(2026, 1, 1)
DAYS = 90
ACCOUNT_COUNT = 600
NORMAL_COUNT = 8_000


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    countries = ["US", "GB", "CA", "IN", "AU", "DE"]
    accounts: list[dict[str, object]] = []
    for i in range(1, ACCOUNT_COUNT + 1):
        accounts.append({
            "account_id": f"C{i:05d}",
            "home_country": rng.choices(countries, [48, 15, 12, 13, 7, 5])[0],
            "customer_tier": rng.choices(["Everyday", "Premium"], [0.78, 0.22])[0],
            "typical_amount": round(rng.uniform(35, 240), 2),
        })
    profile = {r["account_id"]: r for r in accounts}
    categories = ["Grocery", "Dining", "Fuel", "Shopping", "Travel", "Utilities", "Cash"]
    rows: list[dict[str, object]] = []
    next_id = 1

    def add(account_id: str, at: datetime, amount: float, category: str, country: str,
            label: str = "normal") -> None:
        nonlocal next_id
        rows.append({"transaction_id": f"T{next_id:07d}", "account_id": account_id,
                     "timestamp": at.strftime("%Y-%m-%d %H:%M:%S"), "amount": round(amount, 2),
                     "category": category, "merchant_country": country,
                     "scenario_label": label})
        next_id += 1

    for _ in range(NORMAL_COUNT):
        account = rng.choice(accounts)
        home = str(account["home_country"])
        at = START + timedelta(days=rng.randrange(DAYS), hours=rng.randrange(7, 23),
                               minutes=rng.randrange(60), seconds=rng.randrange(60))
        amount = min(1_200, rng.lognormvariate(3.4, 0.75) * float(account["typical_amount"]) / 100)
        country = home if rng.random() < 0.985 else rng.choice([c for c in countries if c != home])
        add(str(account["account_id"]), at, amount, rng.choice(categories), country)

    # Inject four interpretable scenarios with separate, auditable ground-truth labels.
    for _ in range(70):
        account = rng.choice(accounts)
        at = START + timedelta(days=rng.randrange(DAYS), hours=rng.randrange(8, 22), minutes=rng.randrange(60))
        add(str(account["account_id"]), at, rng.uniform(1_800, 8_500), rng.choice(categories),
            str(account["home_country"]), "large_amount")

    for _ in range(45):
        account = rng.choice(accounts)
        home = str(account["home_country"])
        foreign = rng.choice([c for c in countries if c != home])
        at = START + timedelta(days=rng.randrange(DAYS), hours=rng.randrange(7, 23), minutes=rng.randrange(60))
        add(str(account["account_id"]), at, rng.uniform(30, 650), rng.choice(categories), foreign, "foreign_country")

    for _ in range(45):
        account = rng.choice(accounts)
        at = START + timedelta(days=rng.randrange(DAYS), hours=rng.choice([1, 2, 3, 4]), minutes=rng.randrange(60))
        add(str(account["account_id"]), at, rng.uniform(25, 500), rng.choice(categories),
            str(account["home_country"]), "overnight")

    # 30 distinct account bursts, each with four transactions inside seven minutes.
    for _ in range(30):
        account = rng.choice(accounts)
        at = START + timedelta(days=rng.randrange(DAYS), hours=rng.randrange(8, 22), minutes=rng.randrange(50))
        for offset in (0, 2, 4, 6):
            add(str(account["account_id"]), at + timedelta(minutes=offset), rng.uniform(15, 180),
                rng.choice(categories), str(account["home_country"]), "velocity_burst")

    rows.sort(key=lambda r: (r["timestamp"], r["transaction_id"]))
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    write_csv(data_dir / "accounts.csv", accounts)
    write_csv(data_dir / "transactions.csv", rows)
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["scenario_label"])] = counts.get(str(row["scenario_label"]), 0) + 1
    print(f"Generated {len(accounts):,} accounts and {len(rows):,} transactions: {counts}")


if __name__ == "__main__":
    main()
