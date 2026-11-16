# LinkedIn post — Day 4

**30 Days. 30 Data Analytics Projects — Day 4**

How can a bank prioritize transactions for review without treating every unusual payment as fraud?

For Day 4, I built a small, explainable transaction-screening investigation with Python and SQLite. The synthetic dataset contains 600 customer accounts and 8,280 transactions over 90 days. I combined four signals: unusually large amounts, a rapid transaction burst, merchant-country mismatch, and overnight activity.

**What the sample showed:**
- 252 transactions (3.0%) entered the review queue.
- 145 alerts matched an injected scenario; 107 were routine records. Retrospective precision was 57.5%, with 51.8% recall across 280 injected examples.
- A country mismatch alone surfaced 152 transactions, but only 45 were injected country-mismatch scenarios. Context matters: a location difference is a reason to investigate, not a conclusion.
- The score threshold also left overnight-only transactions out of the queue. That trade-off makes alert volume and missed scenarios visible.

These are synthetic exercise results, not production fraud-detection performance. The labels and thresholds are constructed for learning, and a flagged transaction is not proof of fraud. In a real setting, I would validate against representative outcomes, review false-positive burden, and keep a trained analyst in the loop.

Project, SQL, assumptions, and reproducible outputs: https://github.com/Sanchay20Shukla/30days30projects/tree/main/day-04-banking-transaction-anomaly-investigation

**Attach these charts:**
1. `outputs/rule_flag_counts.png` — what each rule surfaced
2. `outputs/daily_alert_trend.png` — daily alerts and injected scenario records
3. `outputs/risk_score_distribution.png` — score distribution for routine records and injected scenarios

Next: Day 5 — Retail Inventory & Demand Forecasting.

#DataAnalytics #SQL #Python #BankingAnalytics #RiskAnalytics #FraudPrevention #30Days30Projects
