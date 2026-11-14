# 30 Days, 30 Projects

A portfolio challenge moving from advanced SQL and business analytics through Power BI, Python, machine learning, and AI powered analytics.

## Projects

| Day | Project | Focus |
|---|---|---|
| 2 | [Customer RFM Segmentation & Revenue Concentration](day-02-customer-rfm-segmentation/) | SQL CTEs, `NTILE`, window functions, Pareto analysis |
| 3 | [SaaS Customer Retention & Cohort Analysis](day-03-saas-retention-cohorts/) | SQL cohort matrices, product retention, subscription churn, MRR |

Each project folder contains its source data (synthetic where noted), reproducible code, analysis outputs, and a project README covering assumptions, data checks, and limitations. See the [Day 2 LinkedIn draft](day-02-customer-rfm-segmentation/LINKEDIN_POST.md) and [Day 3 LinkedIn draft](day-03-saas-retention-cohorts/LINKEDIN_POST.md).

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
