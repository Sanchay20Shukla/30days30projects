# Day 4 — Banking Transaction Anomaly Investigation

**30 Days. 30 Data Analytics Projects.** This project builds an explainable first-pass review queue for synthetic bank card activity. It combines transaction-size context, rolling account velocity, merchant-country mismatch, and transaction hour into a simple rule score. The generated scenario labels are reserved for a retrospective exercise evaluation; they are not used by the scoring rules.

## Business question

Which transactions deserve analyst review, what signals raised them, and what does the current threshold miss?

## Dataset and tools

- 600 synthetic customer accounts and 8,280 transactions across a 90-day period in 2026.
- The dataset includes 8,000 routine records plus 280 injected examples: 70 large amounts, 120 records in 30 rapid-transaction bursts, 45 country mismatches, and 45 overnight transactions.
- Each account has a home country, tier, and typical transaction amount. Transactions include timestamp, amount, category, merchant country, and a synthetic scenario label for evaluation only.
- Python standard library, SQLite window functions, Matplotlib, and NumPy.
- Fixed random seed: `20261116`.

## Run it

From this folder with Python 3.10+:

```bash
python -m pip install matplotlib numpy
python generate_data.py
python analyze.py
python create_visuals.py
```

`analyze.py` validates the inputs, applies the SQL rules, and writes:

- `outputs/transaction_risk_scores.csv` — transaction-level rule points, risk score, reasons, and retrospective scenario label.
- `outputs/daily_alerts.csv` — daily transaction volume, alert counts, alert amount, and scenario count.
- `outputs/rule_performance.csv` — individual signal counts and synthetic examples each signal surfaced.
- Three PNG charts in `outputs/` for sharing.

## Screening logic

| Signal | Points | Rule |
|---|---:|---|
| Large amount | 3 | Amount is at least $1,800 and at least 6× the account's typical amount |
| Rapid transaction burst | 3 | Four or more transactions for the account in a rolling 10-minute window |
| Country mismatch | 2 | Merchant country differs from the account's home country |
| Overnight hour | 1 | Transaction occurs from 01:00 through 04:59 |

Scores of 2 or more enter the review queue. The score describes rule matches only; it is not a probability of fraud or a finding of wrongdoing.

## Sample findings

All figures below come from the generated synthetic sample and its injected scenario labels.

- The score sent 252 of 8,280 transactions to review (3.0% of records).
- 145 of those alerts matched an injected scenario; 107 were routine synthetic records. Retrospective precision was 57.5%, and recall was 51.8% (145 of 280 injected examples).
- The score intentionally requires at least 2 points: an overnight-hour signal alone is only 1 point. This leaves single-signal cases outside the queue and shows the trade-off between alert volume and coverage.
- Country mismatch surfaced 152 records, including 45 injected examples. The remaining mismatches illustrate why a location difference alone can create noise.
- Velocity scoring begins when the fourth transaction enters the rolling window, so it identifies the burst threshold crossing rather than labeling every transaction in the burst.

These precision and recall values are properties of this synthetic exercise, its injected scenarios, and chosen thresholds. They are not estimates of performance on real banking data.

## Data checks

The runner checks unique account and transaction IDs, valid account references, positive amounts, parseable timestamps, and allowed evaluation labels. All scenario types, amounts, and thresholds are simulated.

## Limitations and responsible use

This is an educational triage example, not a fraud model or production control. It omits authentication/device signals, account history beyond a fixed typical amount, customer travel, merchant risk, disputes, investigator outcomes, and regulatory requirements. A flagged transaction is not proof of fraud. In real operations, define the review objective, calibrate on representative and time-separated data, measure false-positive burden across customer groups, monitor drift, and keep a trained analyst in the decision loop.

## Shareable charts

- [Rule flags and injected examples](outputs/rule_flag_counts.png)
- [Daily alerts and injected scenario records](outputs/daily_alert_trend.png)
- [Synthetic risk-score distribution](outputs/risk_score_distribution.png)

## Project files

- `generate_data.py` — deterministic synthetic accounts and transaction generator
- `analyze.py` — SQLite loading, data checks, scoring outputs, retrospective metrics
- `sql/transaction_anomaly.sql` — explainable features and transaction risk score
- `sql/daily_alerts.sql` — daily review queue trend
- `sql/rule_performance.sql` — per-rule surfaced-record counts
- `create_visuals.py` — shareable charts
- `LINKEDIN_POST.md` — ready-to-copy post draft
