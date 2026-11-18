WITH tenure_bands AS (
    SELECT
        customer_id,
        churned,
        CASE
            WHEN tenure_months < 6 THEN '00–05 months'
            WHEN tenure_months < 13 THEN '06–12 months'
            WHEN tenure_months < 25 THEN '13–24 months'
            WHEN tenure_months < 49 THEN '25–48 months'
            ELSE '49+ months'
        END AS tenure_band
    FROM customers
)
SELECT tenure_band, COUNT(*) AS customers,
       SUM(churned) AS churned_customers,
       ROUND(100.0 * SUM(churned) / COUNT(*), 2) AS churn_rate_pct
FROM tenure_bands
GROUP BY tenure_band
ORDER BY MIN(CASE tenure_band WHEN '00–05 months' THEN 1 WHEN '06–12 months' THEN 2 WHEN '13–24 months' THEN 3 WHEN '25–48 months' THEN 4 ELSE 5 END);
