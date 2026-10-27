import sqlite3
import pandas as pd

conn = sqlite3.connect("olist.db")

audit_query = """
WITH UniqueOrderReviews AS (
    SELECT 
        order_id,
        AVG(review_score) AS avg_order_review_score,
        -- Check if any review was a 1-star
        MAX(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) AS has_one_star
    FROM olist_order_reviews_dataset
    GROUP BY order_id
),
DeliveryData AS (
    SELECT 
        o.order_id,
        r.avg_order_review_score,
        r.has_one_star,
        CASE 
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 
            ELSE 0 
        END AS is_late
    FROM olist_orders_dataset o
    LEFT JOIN UniqueOrderReviews r 
        ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT 
    CASE WHEN is_late = 1 THEN 'Late' ELSE 'On Time' END AS delivery_status,
    COUNT(order_id) AS total_orders,
    ROUND(COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM DeliveryData), 2) AS share_pct,
    ROUND(AVG(avg_order_review_score), 2) AS avg_review_score,
    ROUND(SUM(has_one_star) * 100.0 / COUNT(order_id), 2) AS pct_orders_with_1_star
FROM DeliveryData
GROUP BY is_late;
"""

df_audit = pd.read_sql(audit_query, conn)
print("\n=== BASELINE BUSINESS AUDIT (Deduplicated Orders) ===")
print(df_audit.to_string(index=False))

geo_query = """
WITH UniqueOrderReviews AS (
    SELECT 
        order_id,
        AVG(review_score) AS avg_order_review_score
    FROM olist_order_reviews_dataset
    GROUP BY order_id
)
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT o.order_id), 2) AS delay_rate_pct,
    ROUND(AVG(r.avg_order_review_score), 2) AS avg_score
FROM olist_orders_dataset o
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
LEFT JOIN UniqueOrderReviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY c.customer_state
HAVING total_orders > 500
ORDER BY delay_rate_pct DESC
LIMIT 5;
"""

df_geo = pd.read_sql(geo_query, conn)
print("\n=== TOP 5 HIGHEST RISK DESTINATIONS ===")
print(df_geo.to_string(index=False))

conn.close()