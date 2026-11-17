SELECT substr(s.date, 1, 7) AS month,
       p.category,
       COUNT(*) AS product_days,
       SUM(s.units_sold) AS units_sold,
       SUM(s.promo_flag) AS promo_product_days,
       ROUND(AVG(s.units_sold), 2) AS avg_units_per_product_day
FROM daily_sales s
JOIN products p USING (product_id)
GROUP BY substr(s.date, 1, 7), p.category
ORDER BY month, p.category;
