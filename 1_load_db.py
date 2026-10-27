import os
import glob
import sqlite3
import pandas as pd

DB_PATH = "olist.db"
DATA_DIR = "data"

conn = sqlite3.connect(DB_PATH)
csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in '{DATA_DIR}'. Check folder path.")

print(f"Ingesting {len(csv_files)} CSV files into SQLite database '{DB_PATH}'...")

for file_path in csv_files:
    table_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f" - Loading table: {table_name}")
    df = pd.read_csv(file_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)

print("\nIngestion complete. Verifying record counts:")
cursor = conn.cursor()
sample_tables = [
    "olist_orders_dataset",
    "olist_order_items_dataset",
    "olist_customers_dataset",
    "olist_order_reviews_dataset"
]

for table in sample_tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  • {table}: {count:,} rows")

conn.close()