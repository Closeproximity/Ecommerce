
# Table Grain and Candidate Key Analysis

## 1. Orders
- Rows: 99,441
- Grain: One row per order.
- Candidate key: `order_id`
- Validation: Unique.

## 2. Customers
- Rows: 99,441
- Grain: One customer-order record.
- Candidate key: `customer_id`
- Validation: Unique.
- Note: `customer_unique_id` is not unique because customers may have multiple orders.

## 3. Order Items
- Rows: 112,650
- Grain: One row per item within an order.
- Composite key: (`order_id`, `order_item_id`)
- Validation: No duplicate combinations.

## 4. Order Payments
- Rows: 103,886
- Grain: One row per payment record.
- Composite key: (`order_id`, `payment_sequential`)
- Validation: No duplicate combinations.

## 5. Order Reviews
- Rows: 99,224
- Grain: One review record associated with an order.
- Composite key: (`review_id`, `order_id`)
- Validation: No duplicate combinations.
- Note: Neither `review_id` nor `order_id` is independently unique.

## 6. Products
- Rows: 32,951
- Grain: One row per product.
- Candidate key: `product_id`
- Validation: Unique.

## 7. Sellers
- Rows: 3,095
- Grain: One row per seller.
- Candidate key: `seller_id`
- Validation: Unique.


## 8. Geolocation
- Rows: 1,000,163
- Grain: Multiple geographic coordinate records per ZIP-code prefix.
- Unique ZIP prefixes: 19,015
- ZIP prefixes with multiple latitude/longitude values: 17,781
- Candidate key: Not established.
- Note: A ZIP prefix does not uniquely identify one coordinate pair. Do not directly join this raw table to customers or sellers without handling multiple matches.

## 9. Product Category Translation
- Rows: 71
- Grain: One row per translated product category.
- Candidate key: `product_category_name`
- Validation: 71 unique values; zero duplicate records for this column.


## Data Integrity Precautions
1. Preserve all original raw records.
2. Do not assume order-level uniqueness in item, payment, or review tables.
3. Aggregate child tables before joining them to order-level data.
4. Never remove duplicate-looking records without investigating their meaning.
5. Document any missing or unavailable fields.


# Delivery Data Availability Analysis

## Dataset Coverage
- Total orders: 99,441
- Delivered orders: 96,478
- Dataset purchase date range: 2016-09-04 to 2018-10-17

## Timestamp Availability

| Timestamp | Available | Missing |
|---|---:|---:|
| order_purchase_timestamp | 99,441 | 0 |
| order_approved_at | 99,281 | 160 |
| order_delivered_carrier_date | 97,658 | 1,783 |
| order_delivered_customer_date | 96,476 | 2,965 |
| order_estimated_delivery_date | 99,441 | 0 |

## Delivery KPI Eligibility
- Delivered orders: 96,478
- Delivered orders with actual delivery date: 96,470
- Delivered orders with estimated delivery date: 96,478
- Delivered orders with both dates: 96,470

## Analysis Considerations
1. Use delivered orders with both actual and estimated delivery timestamps for actual-versus-estimated delivery analysis.
2. Exclude the eight delivered orders missing actual delivery timestamps from that specific calculation.
3. Do not treat non-delivered orders as late deliveries.
4. Report the eligible order count alongside delivery-performance percentages.
5. The dataset covers historical orders, not real-time delivery operations.
