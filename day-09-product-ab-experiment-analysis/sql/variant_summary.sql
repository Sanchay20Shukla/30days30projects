SELECT
    variant,
    COUNT(*) AS users,
    SUM(converted) AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 3) AS conversion_rate_pct,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(AVG(revenue), 2) AS revenue_per_user,
    ROUND(AVG(CASE WHEN converted = 1 THEN revenue END), 2) AS revenue_per_order
FROM experiment_users
GROUP BY variant
ORDER BY CASE variant WHEN 'Control' THEN 1 ELSE 2 END;
