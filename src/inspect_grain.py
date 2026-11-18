
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

def inspect_key(file_name, key_columns):
    path = RAW_DIR / file_name
    df = pd.read_csv(path, low_memory=False)

    print(f"\n{'=' * 65}")
    print(f"Table: {file_name}")
    print(f"Rows: {len(df):,}")

    for key in key_columns:
        if isinstance(key, str):
            key = [key]

        duplicate_count = int(df.duplicated(subset=key).sum())
        unique_count = int(df.drop_duplicates(subset=key).shape[0])

        print(f"\nCandidate key: {key}")
        print(f"Unique combinations: {unique_count:,}")
        print(f"Duplicate combinations: {duplicate_count:,}")

# Inspect candidate keys
inspect_key("olist_orders_dataset.csv", ["order_id"])
inspect_key("olist_customers_dataset.csv", ["customer_id"])
inspect_key("olist_customers_dataset.csv", ["customer_unique_id"])

inspect_key(
    "olist_order_items_dataset.csv",
    ["order_id", "order_item_id"]
)

inspect_key(
    "olist_order_payments_dataset.csv",
    ["order_id", "payment_sequential"]
)

inspect_key("olist_order_reviews_dataset.csv", ["review_id"])
inspect_key("olist_order_reviews_dataset.csv", ["order_id"])

inspect_key("olist_products_dataset.csv", ["product_id"])
inspect_key("olist_sellers_dataset.csv", ["seller_id"])

inspect_key(
    "olist_geolocation_dataset.csv",
    [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng"
    ]
)
