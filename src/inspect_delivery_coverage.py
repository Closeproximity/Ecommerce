
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

orders = pd.read_csv(
    RAW / "olist_orders_dataset.csv",
    low_memory=False
)

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

print("\nORDER STATUS DISTRIBUTION")
print(orders["order_status"].value_counts(dropna=False))

print("\nDATE COVERAGE")
for column in date_columns:
    print(f"\n{column}")
    print("Available:", orders[column].notna().sum())
    print("Missing:", orders[column].isna().sum())

    if orders[column].notna().any():
        print("Earliest:", orders[column].min())
        print("Latest:", orders[column].max())

print("\nDELIVERY ANALYSIS ELIGIBILITY")

delivered = orders[
    orders["order_status"] == "delivered"
]

print("Delivered orders:", len(delivered))

print(
    "Delivered orders with actual delivery date:",
    delivered["order_delivered_customer_date"].notna().sum()
)

print(
    "Delivered orders with estimated delivery date:",
    delivered["order_estimated_delivery_date"].notna().sum()
)

eligible = delivered[
    delivered["order_delivered_customer_date"].notna()
    & delivered["order_estimated_delivery_date"].notna()
]

print(
    "Delivered orders with both dates available:",
    len(eligible)
)
