# LinkedIn draft — Day 6

📉 **Day 6 of my 30 Days, 30 Projects challenge: Customer Churn Analytics**

Today I explored how to summarize customer churn and evaluate an interpretable risk ranking using SQL and Python.

What I built:
• A reproducible synthetic customer dataset with 4,000 records
• SQL summaries for churn by contract type and tenure band
• A logistic regression pipeline with a stratified train/holdout split
• Holdout metrics, risk deciles, model coefficients, and visual summaries

📊 **On this simulated dataset:**
• Holdout ROC-AUC: **0.72**
• Average precision: **0.60**
• The highest-risk decile had a **75%** observed churn rate and contained **20.8%** of holdout churners
• At the illustrative 0.50 threshold, recall was **69.3%** and precision was **51.9%**

The exercise reinforced that a useful churn workflow needs more than a score: evaluate ranking and threshold behavior on held-out data, and connect intervention decisions to real costs and capacity.

All customer records and churn labels are synthetic, so these findings demonstrate the workflow and do not represent real customers or production performance.

Project and charts: https://github.com/Sanchay20Shukla/30days30projects/tree/main/day-06-customer-churn-analytics

#30Days30Projects #SQL #Python #DataAnalytics #CustomerChurn #MachineLearning #BusinessAnalytics
