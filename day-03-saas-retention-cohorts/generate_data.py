"""Generate a reproducible synthetic SaaS account and activity dataset."""
from __future__ import annotations
import csv
import random
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 20261114
FIRST_COHORT = date(2025, 1, 1)
LAST_COHORT = date(2025, 12, 1)
AS_OF = date(2026, 10, 1)

def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month

def add_months(start: date, months: int) -> date:
    month_index = start.year * 12 + start.month - 1 + months
    return date(month_index // 12, month_index % 12 + 1, 1)

def main() -> None:
    rng = random.Random(SEED)
    accounts: list[dict[str, object]] = []
    activity: list[dict[str, object]] = []
    cohort = FIRST_COHORT
    while cohort <= LAST_COHORT:
        for _ in range(80):
            account_no = len(accounts) + 1
            account_id = f"A{account_no:05d}"
            plan = rng.choices(["Starter", "Growth", "Scale"], [0.48, 0.37, 0.15])[0]
            signup_day = rng.randint(1, 25)
            signup = date(cohort.year, cohort.month, signup_day)
            max_age = months_between(cohort, AS_OF)
            # Churn and product activity are separate: an account can remain
            # subscribed while skipping a month of tracked product activity.
            churn_hazard = {"Starter": 0.10, "Growth": 0.065, "Scale": 0.035}[plan]
            cancel_age = None
            for age in range(1, max_age + 1):
                if rng.random() < churn_hazard:
                    cancel_age = age
                    break
            plan_mrr = {"Starter": 29.0, "Growth": 79.0, "Scale": 199.0}[plan]
            mrr = round(plan_mrr * rng.uniform(0.9, 1.1), 2)
            cancel_month = add_months(cohort, cancel_age).isoformat() if cancel_age is not None else ""
            accounts.append({"account_id": account_id, "signup_date": signup.isoformat(),
                             "cohort_month": cohort.isoformat(), "plan": plan,
                             "monthly_mrr": mrr, "cancel_month": cancel_month,
                             "cancel_age": cancel_age if cancel_age is not None else ""})
            for age in range(max_age + 1):
                if cancel_age is not None and age >= cancel_age:
                    continue
                active_probability = max(0.40, 0.91 - 0.045 * age)
                if age == 0 or rng.random() < active_probability:
                    month_index = cohort.month - 1 + age
                    year = cohort.year + month_index // 12
                    month = month_index % 12 + 1
                    activity.append({"account_id": account_id,
                                     "activity_month": date(year, month, 1).isoformat(),
                                     "month_age": age})
        cohort = date(cohort.year + (cohort.month == 12), cohort.month % 12 + 1, 1)
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    for name, rows in [("accounts.csv", accounts), ("monthly_activity.csv", activity)]:
        with (data_dir / name).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    print(f"Generated {len(accounts):,} synthetic accounts and {len(activity):,} active account-months.")

if __name__ == "__main__":
    main()
