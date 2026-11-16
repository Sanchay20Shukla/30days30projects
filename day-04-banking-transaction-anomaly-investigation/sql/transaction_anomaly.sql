-- Explainable screening rules: transaction size, rolling velocity, foreign country, and overnight time.
WITH enriched AS (
    SELECT t.transaction_id, t.account_id, t.timestamp, t.amount, t.category,
           t.merchant_country, a.home_country, a.customer_tier, a.typical_amount,
           t.scenario_label,
           CAST(strftime('%s', t.timestamp) AS INTEGER) AS tx_epoch,
           CAST(strftime('%H', t.timestamp) AS INTEGER) AS transaction_hour
    FROM transactions t
    JOIN accounts a USING (account_id)
), velocity AS (
    SELECT *, COUNT(*) OVER (
        PARTITION BY account_id ORDER BY tx_epoch
        RANGE BETWEEN 600 PRECEDING AND CURRENT ROW
    ) AS transactions_in_10m
    FROM enriched
), scored AS (
    SELECT *,
           CASE WHEN amount >= 1800 AND amount >= 6 * typical_amount THEN 3 ELSE 0 END AS amount_points,
           CASE WHEN transactions_in_10m >= 4 THEN 3 ELSE 0 END AS velocity_points,
           CASE WHEN merchant_country <> home_country THEN 2 ELSE 0 END AS country_points,
           CASE WHEN transaction_hour BETWEEN 1 AND 4 THEN 1 ELSE 0 END AS hour_points
    FROM velocity
)
SELECT transaction_id, account_id, timestamp, amount, category, merchant_country,
       home_country, customer_tier, transactions_in_10m, transaction_hour,
       amount_points, velocity_points, country_points, hour_points,
       amount_points + velocity_points + country_points + hour_points AS risk_score,
       TRIM(
           CASE WHEN amount_points > 0 THEN 'large amount; ' ELSE '' END ||
           CASE WHEN velocity_points > 0 THEN 'rapid transaction burst; ' ELSE '' END ||
           CASE WHEN country_points > 0 THEN 'country differs from account home; ' ELSE '' END ||
           CASE WHEN hour_points > 0 THEN 'overnight transaction; ' ELSE '' END,
           '; '
       ) AS alert_reasons,
       CASE WHEN amount_points + velocity_points + country_points + hour_points >= 2 THEN 1 ELSE 0 END AS is_alert,
       scenario_label
FROM scored
ORDER BY timestamp, transaction_id;
