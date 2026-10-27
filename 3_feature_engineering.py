import sqlite3
import pandas as pd
import time

DB_PATH = "olist.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("1. Creating indexes on join keys to speed up query execution...")
t0 = time.time()

cursor.executescript("""
CREATE INDEX IF NOT EXISTS idx_oi_order_id ON olist_order_items_dataset(order_id);
CREATE INDEX IF NOT EXISTS idx_oi_product_id ON olist_order_items_dataset(product_id);
CREATE INDEX IF NOT EXISTS idx_oi_seller_id ON olist_order_items_dataset(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON olist_orders_dataset(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON olist_orders_dataset(customer_id);
CREATE INDEX IF NOT EXISTS idx_customers_customer_id ON olist_customers_dataset(customer_id);
CREATE INDEX IF NOT EXISTS idx_products_product_id ON olist_products_dataset(product_id);
CREATE INDEX IF NOT EXISTS idx_sellers_seller_id ON olist_sellers_dataset(seller_id);
""")
conn.commit()
print(f"   Indexes created in {time.time() - t0:.2f}s.")

print("2. Executing SQL feature engineering query...")
t1 = time.time()

feature_query = """
WITH SellerItemCounts AS (
    SELECT 
        oi.order_id,
        s.seller_state,
        ROW_NUMBER() OVER (
            PARTITION BY oi.order_id 
            ORDER BY COUNT(oi.order_item_id) DESC, SUM(oi.price) DESC
        ) AS seller_rank
    FROM olist_order_items_dataset oi
    JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
    GROUP BY oi.order_id, s.seller_id, s.seller_state
),
PrimarySeller AS (
    SELECT 
        order_id, 
        seller_state 
    FROM SellerItemCounts 
    WHERE seller_rank = 1
),
OrderItemsAgg AS (
    SELECT 
        oi.order_id,
        COUNT(oi.order_item_id) AS total_items,
        COUNT(DISTINCT oi.seller_id) AS total_sellers,
        SUM(oi.price) AS total_order_value,
        SUM(oi.freight_value) AS total_freight,
        ROUND(SUM(oi.freight_value) * 1.0 / NULLIF(SUM(oi.price), 0), 4) AS freight_to_price_ratio,
        AVG(p.product_weight_g) AS avg_product_weight_g,
        AVG(p.product_length_cm * p.product_height_cm * p.product_width_cm) AS avg_product_volume_cm3
    FROM olist_order_items_dataset oi
    JOIN olist_products_dataset p ON oi.product_id = p.product_id
    GROUP BY oi.order_id
),
BaseOrders AS (
    SELECT 
        o.order_id,
        c.customer_state,
        o.order_purchase_timestamp,
        o.order_estimated_delivery_date,
        ROUND(JULIANDAY(o.order_estimated_delivery_date) - JULIANDAY(o.order_purchase_timestamp), 1) AS estimated_delivery_days,
        CASE 
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 
            ELSE 0 
        END AS is_late
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT 
    b.order_id,
    b.order_purchase_timestamp,
    b.customer_state,
    ps.seller_state,
    CASE 
        WHEN b.customer_state = ps.seller_state THEN 0 
        ELSE 1 
    END AS is_interstate,
    b.estimated_delivery_days,
    i.total_items,
    i.total_sellers,
    ROUND(i.total_order_value, 2) AS total_order_value,
    ROUND(i.total_freight, 2) AS total_freight,
    ROUND(i.freight_to_price_ratio, 4) AS freight_to_price_ratio,
    ROUND(i.avg_product_weight_g, 1) AS avg_product_weight_g,
    ROUND(i.avg_product_volume_cm3, 1) AS avg_product_volume_cm3,
    CAST(STRFTIME('%m', b.order_purchase_timestamp) AS INTEGER) AS purchase_month,
    CAST(STRFTIME('%w', b.order_purchase_timestamp) AS INTEGER) AS purchase_dayofweek,
    CAST(STRFTIME('%H', b.order_purchase_timestamp) AS INTEGER) AS purchase_hour,
    b.is_late
FROM BaseOrders b
JOIN OrderItemsAgg i ON b.order_id = i.order_id
JOIN PrimarySeller ps ON b.order_id = ps.order_id
WHERE i.avg_product_weight_g IS NOT NULL
  AND i.avg_product_volume_cm3 IS NOT NULL;
"""

df_features = pd.read_sql(feature_query, conn)
print(f"   Query finished in {time.time() - t1:.2f}s.")

print("3. Saving outputs...")
df_features.to_sql("ml_orders_features", conn, if_exists="replace", index=False)
conn.close()

df_features.to_csv("data/training_features.csv", index=False)

print(f"\nFeature pipeline complete!")
print(f"Dataset Shape: {df_features.shape[0]:,} rows, {df_features.shape[1]} columns")
print(f"Late orders count (target = 1): {df_features['is_late'].sum():,} ({df_features['is_late'].mean():.2%})")