-- Monthly active-account retention by signup cohort and account age.
WITH cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_accounts
  FROM accounts
  GROUP BY cohort_month
),
retained AS (
  SELECT a.cohort_month,
         x.month_age,
         COUNT(DISTINCT x.account_id) AS active_accounts
  FROM monthly_activity AS x
  JOIN accounts AS a USING (account_id)
  GROUP BY a.cohort_month, x.month_age
)
SELECT r.cohort_month,
       r.month_age,
       c.cohort_accounts,
       r.active_accounts,
       ROUND(100.0 * r.active_accounts / c.cohort_accounts, 2) AS retention_pct
FROM retained AS r
JOIN cohort_sizes AS c USING (cohort_month)
ORDER BY r.cohort_month, r.month_age;
