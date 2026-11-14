# Day 2 — Customer RFM Segmentation & Revenue Concentration

**30 Days. 30 Real-World Data Analytics Projects.**

Segment customers by recency, purchase frequency, and monetary value (RFM), then quantify revenue concentration with a Pareto analysis. This project uses a deterministic, fully synthetic SQLite dataset so every result is reproducible and no simulated finding is presented as real business data.

## Business question

Which customer groups contribute the most revenue, and where should retention and reactivation effort go?

## Dataset and tools

- `data/transactions.csv`: 180 synthetic customers and 1,027 completed orders, dated between 2025-01-01 and 2026-10-31.
- SQLite 3 SQL: CTEs, `NTILE`, windowed running sums, and conditional aggregation.
- Reference date for recency: **2026-11-01**.

The generator uses a fixed random seed. Orders represent completed purchases; refunds, taxes, discounts, and costs are not modeled. Monetary value is gross order revenue.

## Run it

From this folder, using Python 3.10+:

```bash
python generate_data.py
python analyze.py
```

`analyze.py` loads the CSV into an in-memory SQLite database, runs `sql/analysis.sql`, prints segment and concentration summaries, and writes `outputs/customer_rfm.csv` and `outputs/segment_summary.csv`.

## Method

1. Aggregate completed orders to customer level: last purchase date, order count, and gross revenue.
2. Rank customers into four equal-sized bands using `NTILE(4)`: recency is reversed so a more recent purchase scores higher; frequency and monetary value score higher as they increase.
3. Combine the three scores into a 3–12 RFM score and assign readable segments.
4. Rank customers by revenue and compute cumulative revenue share to show how much revenue the top 20% contribute.

RFM labels are heuristic, not a predictive model. Ties can lead to adjacent customer rankings even where values match; the deterministic customer ID tie-breaker keeps results repeatable.

## Data quality checks

The analysis checks unique customer order attribution, positive order value, non-null order/customer/date fields, and a valid date range. The generated data has no duplicate order IDs, missing values, or non-positive order values by construction.

## Limitations

All data and findings are synthetic. No customer behavior, seasonality, refunds, acquisition cost, margin, or causal impact is inferred. Revenue concentration does not imply that high-value customers are at risk or that a retention action will be profitable. Validate segment cutoffs and unit economics against production data before making decisions.

## Project files

- `generate_data.py` — deterministic synthetic transaction generator
- `analyze.py` — SQLite runner and output writer
- `sql/analysis.sql` — RFM and Pareto queries
- `data/transactions.csv` — generated input data
- `outputs/` — generated customer and segment summaries
