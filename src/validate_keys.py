
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"


def check_composite_key(file_name, key_columns):
    df = pd.read_csv(RAW / file_name, low_memory=False)

    duplicate_mask = df.duplicated(
        subset=key_columns,
        keep=False
    )

    duplicate_records = df[duplicate_mask]

    print("\n" + "=" * 70)
    print(f"File: {file_name}")
    print(f"Tested columns: {key_columns}")
    print(f"Total rows: {len(df):,}")
    print(f"Duplicate records involved: {len(duplicate_records):,}")
    print(
        "Unique key combinations:",
        df.drop_duplicates(subset=key_columns).shape[0]
    )

    if not duplicate_records.empty:
        print("\nExample repeated records:")
        print(
            duplicate_records
            .sort_values(key_columns)
            .head(10)
            .to_string(index=False)
        )


check_composite_key(
    "olist_order_items_dataset.csv",
    ["order_id", "order_item_id"]
)

check_composite_key(
    "olist_order_payments_dataset.csv",
    ["order_id", "payment_sequential"]
)

check_composite_key(
    "olist_order_reviews_dataset.csv",
    ["review_id", "order_id"]
)

check_composite_key(
    "olist_order_reviews_dataset.csv",
    ["review_id"]
)

check_composite_key(
    "olist_order_reviews_dataset.csv",
    ["order_id"]
)
