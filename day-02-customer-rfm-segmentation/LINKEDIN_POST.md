# LinkedIn post — Day 2
**30 Days. 30 Real-World Data Analytics Projects — Day 2**
How concentrated is customer revenue, and which customer groups might need a different retention approach?
Today I built a customer RFM segmentation and revenue concentration analysis using SQL and SQLite. I generated a reproducible synthetic order dataset, then used CTEs, NTILE, window functions, and a cumulative revenue calculation to score customers by recency, frequency, and monetary value.
**Sample results (synthetic data):**
- 180 customers and 1,367 completed orders
- $60,505.37 gross revenue
- The top 20% (36 customers) contributed 39.45% of revenue, so this sample does not follow an assumed 80/20 split
- Loyal Customers and Champions generated 63.75% of revenue across 73 customers
- Need Attention was the largest group (67 customers), while At Risk / High Frequency accounted for 9.15% of revenue
The business use is to focus retention and winback analysis by customer behavior. I would test retention ideas with Loyal Customers and Champions, and investigate high-frequency customers whose last purchase is getting stale. Segment labels are heuristics, so I would check margins and measure incremental impact before acting. These figures are generated for demonstration; they do not describe real customers or prove that any intervention will increase revenue.
Project code, assumptions, data checks, results, and reproducible instructions: https://github.com/Sanchay20Shukla/30days30projects/tree/main/day-02-customer-rfm-segmentation
**Attach these two charts to the post:**
1. `outputs/segment_revenue.png` — gross revenue and customer count by segment
2. `outputs/revenue_concentration.png` — customer-level cumulative revenue curve
Next: Day 3 — SaaS Customer Retention & Cohort Analysis.
#SQL #DataAnalytics #CustomerSegmentation #BusinessAnalytics #30Days30Projects
