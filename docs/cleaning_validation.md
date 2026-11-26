# Cleaning Validation Report

*Generated automatically by `python src/clean.py`. Do not edit by hand; re-run the script instead.*

## 1. Raw data integrity (`python src/verify_raw.py`)

Cleaning only runs when all 9 expected files are listed once in the manifest and match it.

| File | Status |
|---|---|
| `data/raw/olist_customers_dataset.csv` | OK |
| `data/raw/olist_geolocation_dataset.csv` | OK |
| `data/raw/olist_order_items_dataset.csv` | OK |
| `data/raw/olist_order_payments_dataset.csv` | OK |
| `data/raw/olist_order_reviews_dataset.csv` | OK |
| `data/raw/olist_orders_dataset.csv` | OK |
| `data/raw/olist_products_dataset.csv` | OK |
| `data/raw/olist_sellers_dataset.csv` | OK |
| `data/raw/product_category_name_translation.csv` | OK |

## 2. Row reconciliation (no order lost or duplicated)

| Check | Value | Result |
|---|---:|---|
| Raw order rows | 99,441 |  |
| Raw unique order_id | 99,441 |  |
| Output rows (re-read from disk) | 99,441 | PASS |
| Output unique order_id | 99,441 | PASS |
| Order IDs lost (in raw, not in output) | 0 | PASS |
| Order IDs added (in output, not in raw) | 0 | PASS |
| Duplicate order_id in output | 0 | PASS |

Joins use `validate="m:1"` (customers, products) and per-order counts use `.map()`, so no step can multiply order rows. The script stops with an error if any check fails.

## 3. Rule counts (order level)

| Rule | Flag column | Orders | % of orders | Counts as quality issue |
|---|---|---:|---:|---|
| DQ-01 | `flag_delivered_no_delivery_date` | 8 | 0.01% | Yes |
| DQ-02 | `flag_canceled_with_delivery_date` | 6 | 0.01% | Yes |
| DQ-03 | `flag_delivered_no_carrier_date` | 2 | 0.00% | Yes |
| DQ-04 | `flag_delivered_no_approval_date` | 14 | 0.01% | Yes |
| DQ-05 | `flag_carrier_before_purchase` | 166 | 0.17% | Yes |
| DQ-06 | `flag_carrier_before_approval` | 1,359 | 1.37% | Yes |
| DQ-07 | `flag_delivered_before_carrier` | 23 | 0.02% | Yes |
| DQ-08 | `flag_long_delivery` | 4,896 | 4.92% | No |
| DQ-09 | `flag_no_items` | 775 | 0.78% | Yes |
| DQ-10 | `flag_multiple_reviews` | 547 | 0.55% | No |
| DQ-11 | `flag_item_unknown_category` | 1,451 | 1.46% | No |
| DQ-12 | `flag_item_untranslated_category` | 22 | 0.02% | No |
| DQ-13 | `flag_item_zero_freight` | 339 | 0.34% | No |
| **Any** | `flag_any_quality_issue` | **2,186** | **2.20%** | DQ-01 to DQ-07, DQ-09 |

Source-level counts behind the item/product rules:

- DQ-11: 610 of 32,951 products have no category
- DQ-12: 13 products in categories without an English name: `pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`
- DQ-13: 383 of 112,650 items have freight = 0

## 4. DQ-08 long-delivery threshold (exact calculation)

- Population: orders with status `delivered` **and** a customer delivery date (n = 96,470)
- `delivery_days` = (order_delivered_customer_date − order_purchase_timestamp) in seconds ÷ 86,400
- Quartiles: `pandas.Series.quantile` with its default linear interpolation

| Step | Value (days) |
|---|---:|
| Q1 (25th percentile) | 6.7662 |
| Q3 (75th percentile) | 15.7202 |
| IQR = Q3 − Q1 | 8.9540 |
| 1.5 × IQR | 13.4310 |
| **Upper limit = Q3 + 1.5 × IQR** | **29.1512** |
| Orders above the limit | 4,896 |

## 5. Reviews per order (DQ-10)

| Reviews per order | Orders |
|---|---:|
| 0 | 768 |
| 1 | 98,126 |
| 2 | 543 |
| 3 or more | 4 |

Orders with several reviews whose scores disagree: 202

Latest-review ordering (rule confirmed by M3): `review_answer_timestamp`, falling back to `review_creation_date` when it is missing; reviews with neither date sort as oldest.

- Reviews with missing `review_answer_timestamp` (fallback used): 0
- Reviews with neither date (treated as oldest): 0

Columns provided: `review_count`, `review_score_latest` (proposed rule), `review_score_mean` (alternative). See `docs/data_quality_audit.md`, section 6.
