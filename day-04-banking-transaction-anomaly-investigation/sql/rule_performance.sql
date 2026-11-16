SELECT 'Large amount' AS rule_name,
       SUM(amount_points > 0) AS flagged_transactions,
       SUM(CASE WHEN amount_points > 0 AND scenario_label <> 'normal' THEN 1 ELSE 0 END) AS injected_anomalies_caught
FROM transaction_risk
UNION ALL
SELECT 'Velocity burst', SUM(velocity_points > 0),
       SUM(CASE WHEN velocity_points > 0 AND scenario_label <> 'normal' THEN 1 ELSE 0 END)
FROM transaction_risk
UNION ALL
SELECT 'Country mismatch', SUM(country_points > 0),
       SUM(CASE WHEN country_points > 0 AND scenario_label <> 'normal' THEN 1 ELSE 0 END)
FROM transaction_risk
UNION ALL
SELECT 'Overnight hour', SUM(hour_points > 0),
       SUM(CASE WHEN hour_points > 0 AND scenario_label <> 'normal' THEN 1 ELSE 0 END)
FROM transaction_risk;
