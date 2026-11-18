SELECT
    strftime('%Y-%m', created_at) AS month,
    COUNT(*) AS tickets_created,
    SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_tickets,
    ROUND(100.0 * SUM(CASE WHEN status = 'Resolved' AND resolution_hours <= resolution_sla_hours THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END), 0), 2) AS resolution_sla_met_pct,
    ROUND(AVG(customer_rating), 2) AS avg_customer_rating
FROM support_tickets
GROUP BY strftime('%Y-%m', created_at)
ORDER BY month;
