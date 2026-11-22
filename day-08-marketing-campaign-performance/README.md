# Day 8 — Marketing Campaign Performance Analytics

A reproducible campaign reporting project that turns daily channel metrics into comparable funnel, cost, and return measures using Python and SQL.

## Run it

Requires Python 3.10+ with `pandas`, `numpy`, and `matplotlib`.

```bash
python generate_data.py
python analyze.py
python create_visuals.py
```

`analyze.py` validates the generated records, runs the SQL summaries against an in-memory SQLite table, and writes campaign, channel, month, and overall KPI tables to `outputs/`.

## Data and metric definitions

- 12 synthetic campaigns across Search, Social, Email, Display, Affiliate, and Video.
- One record per campaign per day from January 1 through June 30, 2026 (2,172 rows).
- Funnel measures: impressions → clicks → conversions.
- CTR = clicks / impressions; conversion rate = conversions / clicks.
- CPA = modeled spend / conversions; ROAS = generated revenue / modeled spend.
- Spend uses assumed CPM and CPC rates; revenue is generated from conversions and a campaign-specific average order value.
- Random variation and a weekday uplift are included so the example has variation across campaigns and dates.

## Example findings

On the seeded synthetic data, the overall portfolio produced **8.54x ROAS**, **4.65% CTR**, and **5.01% click-to-conversion rate**. Email had the highest channel ROAS (**20.88x**) and Video the lowest (**1.25x**). Search generated the most revenue in aggregate (**2.98 million synthetic currency units**) while spending the most (**379 thousand**).

These comparisons are generated outcomes for this toy data, not channel benchmarks or budget recommendations.

## Outputs

- `outputs/overall_metrics.csv`: portfolio totals and rates.
- `outputs/channel_kpis.csv`: channel-level funnel and efficiency measures.
- `outputs/campaign_kpis.csv`: campaign-level measures, sorted by ROAS.
- `outputs/monthly_kpis.csv`: monthly rollup.
- `outputs/roas_by_channel.png`, `outputs/monthly_spend_revenue.png`, and `outputs/campaign_efficiency.png`: shareable visuals.

## SQL files

- `sql/campaign_performance.sql`
- `sql/channel_performance.sql`
- `sql/monthly_performance.sql`

## Limitations

All campaign activity, spend, conversions, and revenue are synthetic. The generated revenue is credited directly to the campaign row, so this dataset does not model real attribution paths, overlap between channels, returns, margin, or incrementality. The cost assumptions differ by channel and are illustrative. ROAS alone does not establish profitability or the effect of increasing spend. Real budget decisions require validated source data, consistent attribution windows, margins, and an incrementality design.
