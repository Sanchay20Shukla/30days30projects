# Day 9 — Product A/B Experiment Analysis

A reproducible experiment analysis workflow for conversion lift, confidence intervals, sample-ratio checks, exploratory device segments, and a revenue-per-user guardrail.

## Run it

Requires Python 3.10+ with `pandas`, `numpy`, `scipy`, and `matplotlib`.

```bash
python generate_data.py
python analyze.py
python create_visuals.py
```

The analysis validates the assignment and outcomes, executes the SQL summaries against an in-memory SQLite table, and writes aggregate results and charts to `outputs/`.

## Experiment design

- 24,000 synthetic users assigned 1:1 to Control and Treatment across October 1–28, 2026.
- Device type is distributed across both arms. The generated treatment effect differs by device to make segmentation worth examining.
- Conversion is binary; revenue is zero for non-converters and drawn from a generated order-value distribution for converters.
- The generator deliberately encodes a treatment conversion effect and an 8% lower order value for treatment purchasers. These are simulation settings, not findings about a real product.

## Statistical approach

- Conversion lift is Treatment minus Control, reported in percentage points and relative percent.
- A two-sided two-proportion z-test uses the pooled standard error under the null; the 95% confidence interval uses the unpooled Wald standard error.
- A chi-square sample-ratio check compares the assignment counts with an expected 50/50 split.
- Revenue per user is compared using Welch's two-sample t-test and confidence interval, which do not assume equal variances.
- Device results are exploratory subgroup comparisons. No treatment-by-device interaction test or multiple-comparison adjustment is performed.

## Results from the seeded synthetic sample

The control conversion rate is **9.63%** and Treatment is **11.23%**, for **+1.61 percentage points** lift (95% CI: **+0.84 to +2.38 pp**, two-sided p = **0.000046**). Revenue per user is **8.0%** higher in Treatment, but its 95% interval for the absolute difference is **-0.05 to +1.21** synthetic currency units (p = **0.072**), so this guardrail is inconclusive in this run. The mobile subgroup's estimated conversion lift is +2.62 pp; treat segment results as exploratory.

## Outputs

- `outputs/conversion_test.csv`: overall conversion lift, interval, p-value, and sample-ratio check.
- `outputs/revenue_per_user_guardrail.csv`: revenue-per-user comparison and Welch interval/test.
- `outputs/device_segment_tests.csv`: device-level effect estimates and intervals.
- `outputs/variant_summary.csv`, `outputs/segment_summary.csv`, `outputs/daily_experiment_trend.csv`: SQL-generated summaries.
- `outputs/conversion_rate_comparison.png`, `outputs/device_segment_lift.png`, `outputs/revenue_per_user_guardrail.png`: shareable charts.

## SQL files

- `sql/variant_summary.sql`
- `sql/segment_summary.sql`
- `sql/daily_experiment_trend.sql`

## Limitations

The experiment and its effect sizes are synthetic and deliberately specified in the data generator, so statistical significance here only demonstrates the analysis pipeline. A real experiment also needs a pre-registered primary metric, validated exposure and assignment logs, power and duration planning, novelty and interference checks, multiple-testing controls, and decision thresholds tied to business impact. The simple Wald intervals are educational approximations.
