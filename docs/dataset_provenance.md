# Dataset Provenance Note

## 1. Dataset Information

| Attribute | Details |
|---|---|
| Dataset name | Brazilian E-Commerce Public Dataset by Olist |
| Source | Kaggle |
| Source URL | https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce |
| Publisher | Olist |
| License | CC BY-NC-SA 4.0 |
| Download date | 15 November 2026 |
| Download time | 9:05:21 PM IST (UTC+05:30) |
| Format | CSV |
| Number of source files | 9 |

## 2. Dataset Description

The dataset contains anonymised Brazilian e-commerce transaction and delivery records. It includes information about orders, customers, sellers, products, payments, reviews, order items and geolocation.

The dataset is used to analyse delivery performance, order statuses, delivery delays, customer ratings and regional patterns.

## 3. Source File Inventory

The following nine CSV files were downloaded and preserved in `data/raw/`.

| File | Row count |
|---|---:|
| olist_customers_dataset.csv | 99,441 |
| olist_geolocation_dataset.csv | 1,000,163 |
| olist_order_items_dataset.csv | 112,650 |
| olist_order_payments_dataset.csv | 103,886 |
| olist_order_reviews_dataset.csv | 99,224 |
| olist_orders_dataset.csv | 99,441 |
| olist_products_dataset.csv | 32,951 |
| olist_sellers_dataset.csv | 3,095 |
| product_category_name_translation.csv | 71 |
| **Total** | **1,550,922** |

Row counts represent the original CSV records, including duplicate geolocation records.

## 4. Date Coverage

The purchase timestamp (`order_purchase_timestamp`) in the orders dataset covers:

- Earliest purchase: 4 September 2016, 21:15:19
- Latest purchase: 17 October 2018, 17:30:18

These values are reported as stored in the source dataset. No timezone conversion has been applied.

## 5. Data Storage and Preservation

- Original CSV files are stored in `data/raw/`.
- Raw files are preserved without modification.
- Raw datasets are excluded from Git because of their size.
- Database ingestion is performed using `src/ingest.py`.
- PostgreSQL stores the imported source tables.
- Database credentials are maintained in `.env`, which is excluded from Git.
- Dataset download instructions and source attribution are documented in `README.md`.

## 6. Known Dataset Limitations

The source dataset does not provide every operational field required for a complete logistics analysis.

| Field | Availability |
|---|---|
| Order ID | Available |
| Customer ID | Available |
| Order date | Available |
| Dispatch date | Partial |
| Promised delivery date | Available |
| Actual delivery date | Partial |
| Order status | Available |
| Cancellation reason | Missing |
| Product category | Partial |
| Carrier identity | Missing |
| Customer/seller region | Available through location fields |
| Actual delivery distance | Missing |
| Freight fee | Available |
| Customer rating | Available, with multiple-review considerations |

Missing or unavailable fields are treated as dataset limitations and are not fabricated.

## 7. Attribution and License

Dataset: Brazilian E-Commerce Public Dataset by Olist.

Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).

Any redistribution or reuse must comply with the dataset's applicable license terms.