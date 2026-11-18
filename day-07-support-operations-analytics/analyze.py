from pathlib import Path
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "support_tickets.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def main() -> None:
    frame = pd.read_csv(DATA, parse_dates=["created_at"])
    assert frame.ticket_id.is_unique
    assert frame.created_at.notna().all()
    assert set(frame.status.unique()) <= {"Open", "Resolved"}
    assert frame.loc[frame.status == "Open", "resolution_hours"].isna().all()
    assert frame.loc[frame.status == "Resolved", "resolution_hours"].notna().all()

    frame["response_sla_met"] = frame.first_response_hours <= frame.response_sla_hours
    frame["resolution_sla_met"] = frame.resolution_hours <= frame.resolution_sla_hours
    resolved = frame[frame.status == "Resolved"]
    summary = pd.DataFrame([{
        "tickets": len(frame), "resolved_tickets": len(resolved), "open_backlog": int((frame.status == "Open").sum()),
        "resolution_sla_met_pct": 100 * resolved.resolution_sla_met.mean(),
        "response_sla_met_pct": 100 * frame.response_sla_met.mean(),
        "median_resolution_hours": resolved.resolution_hours.median(),
        "average_customer_rating": frame.customer_rating.mean(),
        "rating_response_rate_pct": 100 * frame.customer_rating.notna().mean(),
    }])
    summary.to_csv(OUT / "overall_metrics.csv", index=False)

    with sqlite3.connect(":memory:") as connection:
        frame.to_sql("support_tickets", connection, index=False, if_exists="replace")
        for query_file, output_file in [
            ("sla_by_priority.sql", "sla_by_priority.csv"),
            ("monthly_support_trend.sql", "monthly_support_trend.csv"),
            ("channel_performance.sql", "channel_performance.csv"),
        ]:
            query = (ROOT / "sql" / query_file).read_text(encoding="utf-8")
            pd.read_sql_query(query, connection).to_csv(OUT / output_file, index=False)

    print(f"Validated {len(frame):,} tickets; open backlog={(frame.status == 'Open').sum():,}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
