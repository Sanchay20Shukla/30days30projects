-- Subscription churn by signup cohort and tenure month.
WITH RECURSIVE ages(month_age) AS (
    SELECT 0
    UNION ALL
    SELECT month_age + 1 FROM ages WHERE month_age < :max_age
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_accounts
    FROM accounts
    GROUP BY cohort_month
),
cohort_age_grid AS (
    SELECT c.cohort_month, c.cohort_accounts, a.month_age
    FROM cohort_sizes c
    CROSS JOIN ages a
    WHERE date(c.cohort_month, '+' || a.month_age || ' months') <= :as_of_month
),
churn_by_age AS (
    SELECT cohort_month, CAST(cancel_age AS INTEGER) AS month_age,
           COUNT(*) AS churned_accounts,
           ROUND(SUM(monthly_mrr), 2) AS churned_mrr
    FROM accounts
    WHERE cancel_age <> ''
    GROUP BY cohort_month, CAST(cancel_age AS INTEGER)
),
base AS (
    SELECT g.cohort_month, g.cohort_accounts, g.month_age,
           COALESCE(c.churned_accounts, 0) AS churned_accounts,
           COALESCE(c.churned_mrr, 0) AS churned_mrr
    FROM cohort_age_grid g
    LEFT JOIN churn_by_age c USING (cohort_month, month_age)
),
with_opening AS (
    SELECT *,
           cohort_accounts - COALESCE(
               SUM(churned_accounts) OVER (
                   PARTITION BY cohort_month ORDER BY month_age
                   ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
               ), 0
           ) AS opening_accounts,
           SUM(churned_accounts) OVER (
               PARTITION BY cohort_month ORDER BY month_age
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS cumulative_churned_accounts
    FROM base
)
SELECT cohort_month, month_age, cohort_accounts, opening_accounts,
       churned_accounts, opening_accounts - churned_accounts AS ending_accounts,
       ROUND(100.0 * churned_accounts / NULLIF(opening_accounts, 0), 2) AS monthly_churn_pct,
       ROUND(100.0 * cumulative_churned_accounts / cohort_accounts, 2) AS cumulative_churn_pct
FROM with_opening
ORDER BY cohort_month, month_age;
