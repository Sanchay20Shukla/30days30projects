-- Monthly subscription movement, product activity, and recurring revenue.
WITH RECURSIVE calendar(month_start) AS (
    SELECT MIN(cohort_month) FROM accounts
    UNION ALL
    SELECT date(month_start, '+1 month') FROM calendar
    WHERE month_start < :as_of_month
),
movement AS (
    SELECT month_start,
           (SELECT COUNT(*) FROM accounts a WHERE a.cohort_month = c.month_start) AS new_subscriptions,
           (SELECT COUNT(*) FROM accounts a WHERE a.cancel_month = c.month_start) AS churned_subscriptions,
           (SELECT ROUND(SUM(monthly_mrr), 2) FROM accounts a WHERE a.cohort_month = c.month_start) AS new_mrr,
           (SELECT ROUND(SUM(monthly_mrr), 2) FROM accounts a WHERE a.cancel_month = c.month_start) AS churned_mrr,
           (SELECT COUNT(*) FROM accounts a
             WHERE a.cohort_month <= c.month_start
               AND (a.cancel_month = '' OR a.cancel_month > c.month_start)) AS active_subscriptions,
           (SELECT ROUND(SUM(monthly_mrr), 2) FROM accounts a
             WHERE a.cohort_month <= c.month_start
               AND (a.cancel_month = '' OR a.cancel_month > c.month_start)) AS ending_mrr,
           (SELECT COUNT(DISTINCT x.account_id) FROM monthly_activity x
             WHERE x.activity_month = c.month_start) AS active_accounts
    FROM calendar c
),
with_opening AS (
    SELECT *,
           LAG(active_subscriptions) OVER (ORDER BY month_start) AS opening_subscriptions,
           LAG(ending_mrr) OVER (ORDER BY month_start) AS opening_mrr
    FROM movement
)
SELECT month_start AS calendar_month, new_subscriptions, churned_subscriptions,
       opening_subscriptions, active_subscriptions,
       CASE WHEN opening_subscriptions IS NULL OR opening_subscriptions = 0 THEN NULL
            ELSE ROUND(100.0 * churned_subscriptions / opening_subscriptions, 2) END AS monthly_churn_pct,
       active_accounts, new_mrr, churned_mrr, ending_mrr AS active_mrr,
       CASE WHEN opening_mrr IS NULL OR opening_mrr = 0 THEN NULL
            ELSE ROUND(100.0 * churned_mrr / opening_mrr, 2) END AS monthly_mrr_churn_pct
FROM with_opening
ORDER BY calendar_month;
