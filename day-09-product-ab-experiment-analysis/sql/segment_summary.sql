SELECT
    device_type,
    variant,
    COUNT(*) AS users,
    SUM(converted) AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 3) AS conversion_rate_pct,
    ROUND(AVG(revenue), 2) AS revenue_per_user
FROM experiment_users
GROUP BY device_type, variant
ORDER BY device_type, CASE variant WHEN 'Control' THEN 1 ELSE 2 END;
