"""Run account activity, subscription churn, and monthly SaaS metrics in SQLite."""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
AS_OF_MONTH = "2026-10-01"
SQL_DIR = ROOT / "sql"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise SystemExit(f"No rows to write to {path.name}.")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def month_age(cohort: str, as_of: str) -> int:
    cy, cm = (int(x) for x in cohort[:7].split("-"))
    ay, am = (int(x) for x in as_of[:7].split("-"))
    return (ay - cy) * 12 + am - cm


def main() -> None:
    accounts = read_csv(ROOT / "data" / "accounts.csv")
    activity = read_csv(ROOT / "data" / "monthly_activity.csv")
    if not accounts or not activity:
        raise SystemExit("Run generate_data.py first.")

    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE accounts(
            account_id TEXT PRIMARY KEY,
            signup_date TEXT NOT NULL,
            cohort_month TEXT NOT NULL,
            plan TEXT NOT NULL,
            monthly_mrr REAL NOT NULL CHECK (monthly_mrr > 0),
            cancel_month TEXT NOT NULL,
            cancel_age INTEGER
        );
        CREATE TABLE monthly_activity(
            account_id TEXT NOT NULL REFERENCES accounts(account_id),
            activity_month TEXT NOT NULL,
            month_age INTEGER NOT NULL CHECK (month_age >= 0),
            PRIMARY KEY(account_id, activity_month)
        );
    """)
    db.executemany(
        "INSERT INTO accounts VALUES (:account_id,:signup_date,:cohort_month,:plan,:monthly_mrr,:cancel_month,:cancel_age)",
        [{**a, "monthly_mrr": float(a["monthly_mrr"]),
          "cancel_age": int(a["cancel_age"]) if a["cancel_age"] else None} for a in accounts],
    )
    db.executemany(
        "INSERT INTO monthly_activity VALUES (:account_id,:activity_month,:month_age)",
        [{**x, "month_age": int(x["month_age"])} for x in activity],
    )

    checks = {
        "unique_account_ids": db.execute("SELECT COUNT(*) = COUNT(DISTINCT account_id) FROM accounts").fetchone()[0],
        "activity_account_references": db.execute("SELECT COUNT(*) = 0 FROM monthly_activity x LEFT JOIN accounts a USING(account_id) WHERE a.account_id IS NULL").fetchone()[0],
        "unique_account_month_activity": db.execute("SELECT COUNT(*) = COUNT(DISTINCT account_id || activity_month) FROM monthly_activity").fetchone()[0],
        "month_zero_for_every_account": db.execute("SELECT COUNT(*) = 0 FROM accounts a WHERE NOT EXISTS (SELECT 1 FROM monthly_activity x WHERE x.account_id=a.account_id AND x.month_age=0)").fetchone()[0],
        "cancellation_date_matches_age": db.execute("SELECT COUNT(*) = 0 FROM accounts WHERE (cancel_age IS NULL AND cancel_month <> '') OR (cancel_age IS NOT NULL AND cancel_month <> date(cohort_month, '+' || cancel_age || ' months'))").fetchone()[0],
        "no_activity_after_cancellation": db.execute("SELECT COUNT(*) = 0 FROM monthly_activity x JOIN accounts a USING(account_id) WHERE a.cancel_month <> '' AND x.activity_month >= a.cancel_month").fetchone()[0],
        "activity_within_observation_window": db.execute("SELECT COUNT(*) = 0 FROM monthly_activity WHERE activity_month > ?", (AS_OF_MONTH,)).fetchone()[0],
    }
    if not all(checks.values()):
        raise SystemExit(f"Data checks failed: {checks}")

    cohort_sql = (SQL_DIR / "cohort_retention.sql").read_text(encoding="utf-8")
    churn_sql = (SQL_DIR / "cohort_churn.sql").read_text(encoding="utf-8")
    monthly_sql = (SQL_DIR / "monthly_metrics.sql").read_text(encoding="utf-8")
    retention = [dict(r) for r in db.execute(cohort_sql).fetchall()]
    max_age = max(month_age(a["cohort_month"], AS_OF_MONTH) for a in accounts)
    params = {"as_of_month": AS_OF_MONTH, "max_age": max_age}
    churn = [dict(r) for r in db.execute(churn_sql, params).fetchall()]
    monthly = [dict(r) for r in db.execute(monthly_sql, {"as_of_month": AS_OF_MONTH}).fetchall()]

    OUT.mkdir(exist_ok=True)
    write_csv(OUT / "cohort_retention.csv", retention)
    write_csv(OUT / "cohort_churn.csv", churn)
    write_csv(OUT / "monthly_metrics.csv", monthly)

    cohorts = sorted({r["cohort_month"] for r in retention})
    ages = sorted({r["month_age"] for r in retention})
    sizes = {c: next(r["cohort_accounts"] for r in retention if r["cohort_month"] == c) for c in cohorts}
    retention_lookup = {(r["cohort_month"], r["month_age"]): r["retention_pct"] for r in retention}
    matrix_rows = []
    for cohort in cohorts:
        matrix_rows.append({"cohort_month": cohort, "cohort_accounts": sizes[cohort],
                            **{f"M{age}": retention_lookup.get((cohort, age), "") for age in ages}})
    write_csv(OUT / "cohort_retention_matrix.csv", matrix_rows)

    def mean_metric(rows: list[dict[str, object]], age: int, field: str) -> tuple[float | None, int]:
        vals = [float(r[field]) for r in rows if r["month_age"] == age and r[field] is not None]
        return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)

    averages = {age: mean_metric(retention, age, "retention_pct") for age in (0, 3, 6, 12)}
    cum_churn_12, cohorts_at_12 = mean_metric(churn, 12, "cumulative_churn_pct")
    last_month = monthly[-1]
    print(f"Accounts: {len(accounts):,} | activity account-months: {len(activity):,} | cohorts: {len(cohorts)}")
    for age, (value, count) in averages.items():
        if value is not None:
            print(f"Average active-account retention M{age}: {value:.1f}% across {count} cohorts")
    if cum_churn_12 is not None:
        print(f"Average cumulative subscription churn by M12: {cum_churn_12:.1f}% across {cohorts_at_12} cohorts")
    print(f"{last_month['calendar_month']} ending subscribers: {last_month['active_subscriptions']:,} | active MRR: ${last_month['active_mrr']:,.2f}")
    print("Data checks passed: " + ", ".join(checks))
    db.close()


if __name__ == "__main__":
    main()
