SELECT
    channel,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(conversions) AS conversions,
    ROUND(SUM(spend), 2) AS spend,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 2) AS ctr_pct,
    ROUND(100.0 * SUM(conversions) / NULLIF(SUM(clicks), 0), 2) AS conversion_rate_pct,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2) AS cost_per_acquisition,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas
FROM daily_campaign_performance
GROUP BY channel
ORDER BY roas DESC;
