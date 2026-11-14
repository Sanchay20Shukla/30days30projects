WITH customer_orders AS (
    SELECT
        customer_id,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(order_amount), 2) AS monetary
    FROM transactions
    GROUP BY customer_id
),
rfm_bands AS (
    SELECT
        customer_id,
        last_order_date,
        CAST(julianday(:reference_date) - julianday(last_order_date) AS INTEGER) AS recency_days,
        frequency,
        monetary,
        5 - NTILE(4) OVER (ORDER BY julianday(last_order_date) DESC, customer_id) AS r_score,
        NTILE(4) OVER (ORDER BY frequency, customer_id) AS f_score,
        NTILE(4) OVER (ORDER BY monetary, customer_id) AS m_score
    FROM customer_orders
),
scored AS (
    SELECT *, r_score + f_score + m_score AS rfm_score
    FROM rfm_bands
),
segmented AS (
    SELECT *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score <= 2 THEN 'Recent Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / High Frequency'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'High Value — Needs Winback'
            ELSE 'Need Attention'
        END AS segment
    FROM scored
),
pareto AS (
    SELECT *,
        ROW_NUMBER() OVER (ORDER BY monetary DESC, customer_id) AS revenue_rank,
        COUNT(*) OVER () AS customer_count,
        SUM(monetary) OVER (
            ORDER BY monetary DESC, customer_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue
    FROM segmented
)
SELECT
    customer_id, last_order_date, recency_days, frequency, monetary,
    r_score, f_score, m_score, rfm_score, segment,
    revenue_rank, customer_count,
    ROUND(cumulative_revenue / SUM(monetary) OVER (), 6) AS cumulative_revenue_share,
    ROUND(100.0 * revenue_rank / customer_count, 2) AS customer_percentile
FROM pareto
ORDER BY customer_id;
