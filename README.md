# 30 Days, 30 Projects

A portfolio challenge moving from advanced SQL and business analytics through Power BI, Python, machine learning, and AI powered analytics.

## Projects

| Day | Project | Focus |
|---|---|---|
| 2 | [Customer RFM Segmentation & Revenue Concentration](day-02-customer-rfm-segmentation/) | SQL CTEs, `NTILE`, window functions, Pareto analysis |
| 3 | [SaaS Customer Retention & Cohort Analysis](day-03-saas-retention-cohorts/) | SQL cohort matrices, product retention, subscription churn, MRR |
| 4 | [Banking Transaction Anomaly Investigation](day-04-banking-transaction-anomaly-investigation/) | SQL window functions, explainable risk scoring, alert review |
| 5 | [Retail Demand Forecasting & Inventory Replenishment](day-05-retail-demand-inventory/) | Time-based backtesting, forecast baselines, SQL summaries, reorder planning |
| 6 | [Customer Churn Analytics](day-06-customer-churn-analytics/) | SQL churn summaries, logistic regression, holdout evaluation, risk deciles |
| 7 | [Customer Support Operations & SLA Analytics](day-07-support-operations-analytics/) | SQL SLA summaries, channel performance, ticket volume, service metrics |
| 8 | [Marketing Campaign Performance Analytics](day-08-marketing-campaign-performance/) | SQL funnel reporting, campaign efficiency, channel and monthly KPIs |
| 9 | [Product A/B Experiment Analysis](day-09-product-ab-experiment-analysis/) | Conversion lift, confidence intervals, sample-ratio checks, guardrails |

Each project folder contains its source data (synthetic where noted), reproducible code, analysis outputs, and a project README covering assumptions, data checks, and limitations. See the [Day 2](day-02-customer-rfm-segmentation/LINKEDIN_POST.md), [Day 3](day-03-saas-retention-cohorts/LINKEDIN_POST.md), [Day 4](day-04-banking-transaction-anomaly-investigation/LINKEDIN_POST.md), [Day 5](day-05-retail-demand-inventory/LINKEDIN_POST.md), [Day 6](day-06-customer-churn-analytics/LINKEDIN_POST.md), [Day 7](day-07-support-operations-analytics/LINKEDIN_POST.md), [Day 8](day-08-marketing-campaign-performance/LINKEDIN_POST.md), and [Day 9](day-09-product-ab-experiment-analysis/LINKEDIN_POST.md) LinkedIn post drafts.

## Day 2 quick start

```bash
cd day-02-customer-rfm-segmentation
python generate_data.py
python analyze.py
```

## Day 3 quick start

```bash
cd day-03-saas-retention-cohorts
python generate_data.py
python analyze.py
python create_visuals.py
```

Day 2 and Day 3 use deterministic synthetic datasets. Their sample metrics are demonstrations and do not describe real customers.

## Day 4 quick start

```bash
cd day-04-banking-transaction-anomaly-investigation
python generate_data.py
python analyze.py
python create_visuals.py
```

Day 4 also uses deterministic synthetic data. Its screening metrics are educational examples, not estimates of real-world fraud detection performance.

## Day 5 quick start

```bash
cd day-05-retail-demand-inventory
python generate_data.py
python analyze.py
python create_visuals.py
```

Day 5 also uses deterministic synthetic data. Its holdout metrics and reorder quantities are educational examples, not real demand forecasts or purchase instructions.

## Day 6 quick start

```bash
cd day-06-customer-churn-analytics
python generate_data.py
python analyze.py
python create_visuals.py
```

Day 6 uses deterministic synthetic customer data. Churn scores and metrics are demonstrations, not estimates for real customers or production performance.

## Day 7 quick start

```bash
cd day-07-support-operations-analytics
python generate_data.py
python analyze.py
python create_visuals.py
```

Day 7 uses deterministic synthetic ticket data. Service levels and metrics are examples, not real operational benchmarks.

## Day 8 quick start

```bash
cd day-08-marketing-campaign-performance
python generate_data.py
python analyze.py
python create_visuals.py
```

Day 8 uses synthetic campaign data. Funnel metrics and channel returns are demonstrations, not real marketing benchmarks or budget recommendations.

## Day 9 quick start

```bash
cd day-09-product-ab-experiment-analysis
python generate_data.py
python analyze.py
python create_visuals.py
```

Day 9 uses simulated experiment data. Statistical outputs demonstrate the analysis workflow and are not findings about a real product.
