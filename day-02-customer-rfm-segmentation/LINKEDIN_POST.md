# LinkedIn post — Day 2

**30 Days. 30 Real-World Data Analytics Projects — Day 2**

How concentrated is customer revenue, and which customers need a different retention approach?

Today I built a customer RFM segmentation and revenue concentration analysis using SQL and SQLite. I generated a reproducible synthetic order dataset, then used CTEs, `NTILE`, window functions, and a cumulative revenue calculation to score customers by recency, frequency, and monetary value.

**Sample results (synthetic data):**
- 180 customers and 1,367 completed orders
- $60,505.37 gross revenue
- The top 20% of customers contributed 39.4% of revenue
- RFM segments surfaced Champions, Loyal Customers, Recent Customers, At Risk / High Frequency, and customers needing attention

The business use case is to focus retention and winback analysis by customer behavior, then validate segment economics before choosing an action. These figures are generated for demonstration; they do not describe real customers or prove that any intervention will increase revenue.

The repo includes the generator, SQL, analysis runner, output tables, data quality checks, and assumptions: [GitHub repository link to add after publishing]

Next: Day 3 — SaaS Customer Retention & Cohort Analysis.

#SQL #DataAnalytics #CustomerSegmentation #BusinessAnalytics #30Days30Projects
