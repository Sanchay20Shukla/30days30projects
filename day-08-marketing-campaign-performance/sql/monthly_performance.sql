SELECT
    strftime('%Y-%m', date) AS month,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(conversions) AS conversions,
    ROUND(SUM(spend), 2) AS spend,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas
FROM daily_campaign_performance
GROUP BY strftime('%Y-%m', date)
ORDER BY month;
