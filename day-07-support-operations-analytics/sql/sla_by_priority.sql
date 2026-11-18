SELECT
    priority,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_tickets,
    ROUND(100.0 * SUM(CASE WHEN status = 'Resolved' AND resolution_hours <= resolution_sla_hours THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END), 0), 2) AS resolution_sla_met_pct,
    ROUND(AVG(CASE WHEN status = 'Resolved' THEN resolution_hours END), 2) AS avg_resolution_hours
FROM support_tickets
GROUP BY priority
ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;
