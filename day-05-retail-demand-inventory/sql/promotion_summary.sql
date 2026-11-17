SELECT p.category,
       s.promo_flag,
       COUNT(*) AS product_days,
       SUM(s.units_sold) AS units_sold,
       ROUND(AVG(s.units_sold), 2) AS avg_units_per_product_day
FROM daily_sales s
JOIN products p USING (product_id)
GROUP BY p.category, s.promo_flag
ORDER BY p.category, s.promo_flag;
