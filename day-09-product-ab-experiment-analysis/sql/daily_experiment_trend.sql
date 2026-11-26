SELECT
    date(assigned_at) AS experiment_date,
    variant,
    COUNT(*) AS assigned_users,
    SUM(converted) AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 3) AS conversion_rate_pct
FROM experiment_users
GROUP BY date(assigned_at), variant
ORDER BY experiment_date, variant;
