SELECT
    channel,
    COUNT(*) AS total_tickets,
    ROUND(AVG(first_response_hours), 2) AS avg_first_response_hours,
    ROUND(100.0 * AVG(CASE WHEN first_response_hours <= response_sla_hours THEN 1.0 ELSE 0.0 END), 2) AS response_sla_met_pct,
    ROUND(AVG(customer_rating), 2) AS avg_customer_rating
FROM support_tickets
GROUP BY channel
ORDER BY total_tickets DESC;
