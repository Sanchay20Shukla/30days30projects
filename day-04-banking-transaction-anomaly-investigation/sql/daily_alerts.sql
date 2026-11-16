SELECT substr(timestamp, 1, 10) AS transaction_date,
       COUNT(*) AS transaction_count,
       SUM(is_alert) AS alert_count,
       SUM(CASE WHEN scenario_label <> 'normal' THEN 1 ELSE 0 END) AS injected_anomaly_count,
       ROUND(100.0 * SUM(is_alert) / COUNT(*), 2) AS alert_rate_pct,
       ROUND(SUM(CASE WHEN is_alert = 1 THEN amount ELSE 0 END), 2) AS alert_amount
FROM transaction_risk
GROUP BY substr(timestamp, 1, 10)
ORDER BY transaction_date;
