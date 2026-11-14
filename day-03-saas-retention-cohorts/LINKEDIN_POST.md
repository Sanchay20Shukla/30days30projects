# LinkedIn post — Day 3

**30 Days. 30 Real-World Data Analytics Projects — Day 3**

For a SaaS product, signups are only the beginning. Which cohorts keep using the product, and how does subscription churn affect MRR?

Today I built a reproducible cohort analysis with Python and SQLite. The synthetic dataset has 960 accounts across 12 signup cohorts, monthly activity, explicit subscription cancellation, and plan-level MRR. The SQL separates product activity retention from subscription churn, then follows monthly subscriber and MRR movement.

**Sample findings (synthetic data):**
- Average active product retention: 59.9% at month 3, 40.5% at month 6, and 18.4% at month 12.
- Average cumulative subscription churn by month 12: 58.9% across 10 mature cohorts.
- MRR peaks at $52,636.90 in December 2025 and falls to $31,816.81 by October 2026. This sample has no new signup cohorts after December 2025, so the decline shows churn without replacement growth.

These measures have different definitions: a subscriber can miss a month of product activity without cancelling. The figures are simulated and do not represent a real SaaS business. In real data, I would investigate onboarding activation, churn reasons, and plan mix before proposing a retention action.

Project, SQL, assumptions, data checks, and reproducible outputs: https://github.com/Sanchay20Shukla/30days30projects/tree/main/day-03-saas-retention-cohorts

**Attach these three charts:**
1. `outputs/cohort_retention_heatmap.png` — active product retention by cohort and account age
2. `outputs/retention_curve.png` — average active product retention by age
3. `outputs/monthly_churn_mrr.png` — monthly subscription churn and ending MRR

Next: Day 4 — Banking Transaction Anomaly Investigation.

#SaaS #CustomerRetention #CohortAnalysis #DataAnalytics #SQL #Python #30Days30Projects
