from pathlib import Path
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "daily_campaign_performance.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def main() -> None:
    frame = pd.read_csv(DATA, parse_dates=["date"])
    assert not frame.isna().any().any()
    assert frame.groupby(["date", "campaign"]).size().eq(1).all()
    assert (frame[["impressions", "clicks", "conversions", "spend", "revenue"]] >= 0).all().all()
    assert (frame.clicks <= frame.impressions).all()
    assert (frame.conversions <= frame.clicks).all()

    with sqlite3.connect(":memory:") as connection:
        frame.to_sql("daily_campaign_performance", connection, index=False, if_exists="replace")
        queries = [
            ("campaign_performance.sql", "campaign_kpis.csv"),
            ("channel_performance.sql", "channel_kpis.csv"),
            ("monthly_performance.sql", "monthly_kpis.csv"),
        ]
        for sql_file, csv_file in queries:
            query = (ROOT / "sql" / sql_file).read_text(encoding="utf-8")
            pd.read_sql_query(query, connection).to_csv(OUT / csv_file, index=False)

    channel = pd.read_csv(OUT / "channel_kpis.csv")
    totals = frame[["impressions", "clicks", "conversions", "spend", "revenue"]].sum()
    overall = pd.DataFrame([{
        "campaigns": frame.campaign.nunique(), "campaign_days": len(frame),
        "impressions": int(totals.impressions), "clicks": int(totals.clicks), "conversions": int(totals.conversions),
        "spend": totals.spend, "revenue": totals.revenue,
        "overall_ctr_pct": 100 * totals.clicks / totals.impressions,
        "overall_conversion_rate_pct": 100 * totals.conversions / totals.clicks,
        "overall_cpa": totals.spend / totals.conversions, "overall_roas": totals.revenue / totals.spend,
        "top_roas_channel": channel.iloc[0].channel, "top_roas_channel_value": channel.iloc[0].roas,
    }])
    overall.to_csv(OUT / "overall_metrics.csv", index=False)
    print(f"Validated {len(frame):,} records from {frame.date.min().date()} through {frame.date.max().date()}")
    print(overall.to_string(index=False))


if __name__ == "__main__":
    main()
