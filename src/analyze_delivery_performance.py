
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

orders = pd.read_csv(
    RAW / "olist_orders_dataset.csv",
    low_memory=False
)

# Convert timestamp columns
date_columns = [
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

# Keep delivered orders only
delivered = orders[
    orders["order_status"] == "delivered"
].copy()

# Keep orders with both actual and estimated delivery dates
eligible = delivered.dropna(
    subset=[
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
).copy()

# Calculate delivery metrics
eligible["actual_delivery_days"] = (
    eligible["order_delivered_customer_date"]
    - eligible["order_purchase_timestamp"]
).dt.total_seconds() / 86400

eligible["estimated_delivery_days"] = (
    eligible["order_estimated_delivery_date"]
    - eligible["order_purchase_timestamp"]
).dt.total_seconds() / 86400

eligible["delivery_delay_days"] = (
    eligible["order_delivered_customer_date"].dt.normalize()
    - eligible["order_estimated_delivery_date"].dt.normalize()
).dt.days

eligible["delivery_status"] = eligible[
    "delivery_delay_days"
].apply(
    lambda delay: "Late" if delay > 0
    else "Early" if delay < 0
    else "On Time"
)

# Calculate summary metrics
total_delivered = len(delivered)
eligible_count = len(eligible)

on_time_count = (
    eligible["delivery_status"] == "On Time"
).sum()

early_count = (
    eligible["delivery_status"] == "Early"
).sum()

late_count = (
    eligible["delivery_status"] == "Late"
).sum()

print("\nDELIVERY PERFORMANCE SUMMARY")
print("-" * 45)

print("Total delivered orders:", total_delivered)
print("Orders eligible for analysis:", eligible_count)

print(
    "Average actual delivery days:",
    round(eligible["actual_delivery_days"].mean(), 2)
)

print(
    "Average estimated delivery days:",
    round(eligible["estimated_delivery_days"].mean(), 2)
)

print(
    "Average delivery delay days:",
    round(eligible["delivery_delay_days"].mean(), 2)
)

print("\nDELIVERY CLASSIFICATION")
print("-" * 45)

print("Early deliveries:", early_count)
print("On-time deliveries:", on_time_count)
print("Late deliveries:", late_count)

print(
    "Early delivery percentage:",
    round(early_count / eligible_count * 100, 2), "%"
)

print(
    "On-time delivery percentage:",
    round(on_time_count / eligible_count * 100, 2), "%"
)

print(
    "Late delivery percentage:",
    round(late_count / eligible_count * 100, 2), "%"
)

# Save order-level delivery analysis
output_path = ROOT / "data" / "processed"
output_path.mkdir(parents=True, exist_ok=True)

eligible.to_csv(
    output_path / "delivery_performance.csv",
    index=False
)

print("\nSaved: data/processed/delivery_performance.csv")
