# `orders_clean.csv` Schema

*Generated automatically by `python src/clean.py`. Do not edit by hand.*

- **File:** `data/interim/orders_clean.csv` (not committed; recreate with `python src/clean.py`)
- **Grain:** one row per order (99,441 rows, 33 columns)
- **Key:** `order_id` (unique)
- **Policy:** no rows removed; filter with the `flag_*` columns and state the exclusion in each KPI
- **Rules:** see `docs/data_quality_audit.md`

| # | Column | Type | Meaning | Rule | Orders where True |
|---:|---|---|---|---|---:|
| 1 | `order_id` | text | Unique order identifier (one row per order) |  |  |
| 2 | `customer_id` | text | Customer key for this order (links to customers) |  |  |
| 3 | `order_status` | text | Order status, lowercase (delivered, shipped, canceled, ...) |  |  |
| 4 | `order_purchase_timestamp` | datetime | (1) Customer placed the order |  |  |
| 5 | `order_approved_at` | datetime | (2) Payment approved; empty if never approved |  |  |
| 6 | `order_delivered_carrier_date` | datetime | (3) Handed to the courier; empty if never dispatched |  |  |
| 7 | `order_delivered_customer_date` | datetime | (4) Delivered to the customer; empty if never delivered |  |  |
| 8 | `order_estimated_delivery_date` | datetime | Delivery date promised to the customer |  |  |
| 9 | `flag_delivered_no_delivery_date` | bool | Delivered but no customer delivery date | DQ-01 | 8 |
| 10 | `flag_canceled_with_delivery_date` | bool | Canceled but has a customer delivery date | DQ-02 | 6 |
| 11 | `flag_delivered_no_carrier_date` | bool | Delivered but no carrier date | DQ-03 | 2 |
| 12 | `flag_delivered_no_approval_date` | bool | Delivered but no approval date | DQ-04 | 14 |
| 13 | `flag_carrier_before_purchase` | bool | Carrier date earlier than purchase date | DQ-05 | 166 |
| 14 | `flag_carrier_before_approval` | bool | Carrier date earlier than approval date | DQ-06 | 1,359 |
| 15 | `flag_delivered_before_carrier` | bool | Customer delivery earlier than carrier date | DQ-07 | 23 |
| 16 | `delivery_days` | float | Days from purchase to customer delivery (helper for EDA; KPI definition owned by M3/M6) |  |  |
| 17 | `processing_days` | float | Days from purchase to carrier handover (helper for EDA) |  |  |
| 18 | `flag_long_delivery` | bool | Delivered order with delivery_days above the IQR upper limit (kept) | DQ-08 | 4,896 |
| 19 | `item_count` | int | Number of items in the order (0 = no items) | DQ-09 |  |
| 20 | `items_unknown_category` | int | Items whose product has no category | DQ-11 |  |
| 21 | `items_untranslated_category` | int | Items whose category has no English name | DQ-12 |  |
| 22 | `items_zero_freight` | int | Items with freight_value = 0 | DQ-13 |  |
| 23 | `flag_no_items` | bool | Order has no items | DQ-09 | 775 |
| 24 | `flag_item_unknown_category` | bool | At least one item has no product category | DQ-11 | 1,451 |
| 25 | `flag_item_untranslated_category` | bool | At least one item's category has no English name | DQ-12 | 22 |
| 26 | `flag_item_zero_freight` | bool | At least one item has zero freight (kept) | DQ-13 | 339 |
| 27 | `review_count` | int | Number of reviews for the order (0 = no review) | DQ-10 |  |
| 28 | `review_score_latest` | float | Score of the latest review (PROPOSED rule, awaiting M3); empty if no review | DQ-10 |  |
| 29 | `review_score_mean` | float | Average review score (alternative rule); empty if no review | DQ-10 |  |
| 30 | `flag_multiple_reviews` | bool | Order has more than one review | DQ-10 | 547 |
| 31 | `customer_city` | text | Customer city, lowercase |  |  |
| 32 | `customer_state` | text | Customer state, 2-letter uppercase code |  |  |
| 33 | `flag_any_quality_issue` | bool | True if any data-error rule is True (DQ-01 to DQ-07, DQ-09) | summary | 2,186 |

## Suggested filters

| Use | Keep orders where |
|---|---|
| Delivery time, on-time, delay | `order_status == 'delivered'` and not `flag_delivered_no_delivery_date` (optionally exclude `flag_delivered_before_carrier`) |
| Processing time | `order_delivered_carrier_date` present, not `flag_carrier_before_purchase`; decide on `flag_carrier_before_approval` |
| Ratings | `review_count > 0`; use `review_score_latest` or `review_score_mean` once M3 confirms |
| Price / freight | `item_count > 0` |
| Category analysis | label orders with `flag_item_unknown_category` as `unknown`, never drop them |
