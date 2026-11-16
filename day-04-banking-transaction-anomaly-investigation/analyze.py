"""Load the synthetic transactions into SQLite, score explainable alerts, and summarize review outcomes."""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
SQL = ROOT / "sql"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise SystemExit(f"No rows to write: {path.name}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    accounts = read_csv(DATA / "accounts.csv")
    transactions = read_csv(DATA / "transactions.csv")
    if not accounts or not transactions:
        raise SystemExit("Run generate_data.py first.")
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE accounts(
            account_id TEXT PRIMARY KEY,
            home_country TEXT NOT NULL,
            customer_tier TEXT NOT NULL,
            typical_amount REAL NOT NULL CHECK (typical_amount > 0)
        );
        CREATE TABLE transactions(
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL REFERENCES accounts(account_id),
            timestamp TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount > 0),
            category TEXT NOT NULL,
            merchant_country TEXT NOT NULL,
            scenario_label TEXT NOT NULL CHECK (scenario_label IN
                ('normal','large_amount','foreign_country','overnight','velocity_burst'))
        );
    """)
    db.executemany("INSERT INTO accounts VALUES (:account_id,:home_country,:customer_tier,:typical_amount)",
                   [{**r, "typical_amount": float(r["typical_amount"])} for r in accounts])
    db.executemany("""INSERT INTO transactions VALUES
                   (:transaction_id,:account_id,:timestamp,:amount,:category,:merchant_country,:scenario_label)""",
                   [{**r, "amount": float(r["amount"])} for r in transactions])
    checks = {
        "unique_account_ids": db.execute("SELECT COUNT(*)=COUNT(DISTINCT account_id) FROM accounts").fetchone()[0],
        "unique_transaction_ids": db.execute("SELECT COUNT(*)=COUNT(DISTINCT transaction_id) FROM transactions").fetchone()[0],
        "all_transactions_link_to_account": db.execute("SELECT COUNT(*)=0 FROM transactions t LEFT JOIN accounts a USING(account_id) WHERE a.account_id IS NULL").fetchone()[0],
        "positive_transaction_amounts": db.execute("SELECT COUNT(*)=0 FROM transactions WHERE amount<=0").fetchone()[0],
        "valid_timestamp_text": db.execute("SELECT COUNT(*)=0 FROM transactions WHERE strftime('%s',timestamp) IS NULL").fetchone()[0],
        "expected_label_values": db.execute("SELECT COUNT(*)=0 FROM transactions WHERE scenario_label NOT IN ('normal','large_amount','foreign_country','overnight','velocity_burst')").fetchone()[0],
    }
    if not all(checks.values()):
        raise SystemExit(f"Input checks failed: {checks}")

    risk = [dict(r) for r in db.execute((SQL / "transaction_anomaly.sql").read_text(encoding="utf-8"))]
    db.execute("CREATE TABLE transaction_risk AS SELECT * FROM (" +
               (SQL / "transaction_anomaly.sql").read_text(encoding="utf-8").rstrip(";\n") + ")")
    daily = [dict(r) for r in db.execute((SQL / "daily_alerts.sql").read_text(encoding="utf-8"))]
    rule_rows = [dict(r) for r in db.execute((SQL / "rule_performance.sql").read_text(encoding="utf-8"))]
    OUT.mkdir(exist_ok=True)
    write_csv(OUT / "transaction_risk_scores.csv", risk)
    write_csv(OUT / "daily_alerts.csv", daily)
    write_csv(OUT / "rule_performance.csv", rule_rows)

    tp = sum(1 for r in risk if r["is_alert"] and r["scenario_label"] != "normal")
    fp = sum(1 for r in risk if r["is_alert"] and r["scenario_label"] == "normal")
    fn = sum(1 for r in risk if not r["is_alert"] and r["scenario_label"] != "normal")
    total_alerts = tp + fp
    precision = 100 * tp / total_alerts if total_alerts else 0
    recall = 100 * tp / (tp + fn) if tp + fn else 0
    anomalies = len(transactions) - sum(r["scenario_label"] == "normal" for r in transactions)
    print(f"Transactions: {len(transactions):,} | accounts: {len(accounts):,} | injected scenarios: {anomalies:,}")
    print(f"Alerts: {total_alerts:,} | injected anomalies among alerts: {tp:,} | other alerts: {fp:,}")
    print(f"Retrospective precision: {precision:.1f}% | recall: {recall:.1f}% (labels are synthetic scenario flags)")
    print("Data checks passed: " + ", ".join(checks))
    db.close()


if __name__ == "__main__":
    main()
