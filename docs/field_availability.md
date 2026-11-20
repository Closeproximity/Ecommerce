# Field Availability Assessment

## 1. Purpose

This document identifies whether the fields required for the E-commerce Delivery & Logistics Performance Analysis are available in the Brazilian E-Commerce Public Dataset by Olist.

Availability classifications:

- **Available:** The required field exists and is sufficiently populated for analysis.
- **Partial:** The field exists, but some records have missing values or incomplete coverage.
- **Missing:** The dataset does not provide the required field.

## 2. Field Availability Table

| Required field | Availability | Source table | Source column | Notes |
|---|---|---|---|---|
| Order ID | Available | orders | `order_id` | Unique order identifier |
| Customer ID | Available | orders / customers | `customer_id` | Customer identifier |
| Order date | Available | orders | `order_purchase_timestamp` | Purchase timestamp is complete |
| Approval date | Partial | orders | `order_approved_at` | 160 missing values |
| Dispatch date | Partial | orders | `order_delivered_carrier_date` | 1,783 missing values |
| Promised delivery date | Available | orders | `order_estimated_delivery_date` | No missing values |
| Actual delivery date | Partial | orders | `order_delivered_customer_date` | 2,965 missing values |
| Order status | Available | orders | `order_status` | Includes delivered, canceled, shipped and other statuses |
| Cancellation reason | Missing | — | — | Not provided |
| Product category | Partial | products | `product_category_name` | Some product categories are missing |
| Carrier identity | Missing | — | — | No carrier name or identifier |
| Customer location — city | Available | customers | `customer_city` | Customer's recorded city |
| Customer location — state | Available | customers | `customer_state` | Customer's recorded state |
| Seller location — city | Available | sellers | `seller_city` | Seller's recorded city |
| Seller location — state | Available | sellers | `seller_state` | Seller's recorded state |
| Geographic coordinates for distance approximation | Partial | geolocation | `geolocation_lat`, `geolocation_lng` | ZIP-prefix-based coordinates only; multiple coordinates may exist for a prefix. These do not establish actual shipment routes or delivery distance |
| Actual delivery distance | Missing | — | — | No direct distance field or verified route information |
| Freight fee | Available | order_items | `freight_value` | Freight amount recorded per order item |
| Customer rating | Available | order_reviews | `review_score` | Multiple reviews may exist for an order |

## 3. Important Interpretation Notes

1. Customer and seller locations must be treated as separate geographical dimensions.
2. Customer location must not automatically be interpreted as a verified delivery destination.
3. Seller location must not automatically be interpreted as the dispatch warehouse location.
4. Geolocation data is associated with ZIP prefixes and may contain multiple coordinate records for a prefix. These coordinates provide partial geographic information only and must not be treated as verified shipment origin/destination points or actual route distances.
5. Carrier identity, cancellation reason and actual delivery distance must not be fabricated. Geographic information for distance approximation is partial at best because only ZIP-prefix-based coordinates are available.
6. Freight fee is recorded at order-item level. Aggregate it carefully when calculating order-level totals.
7. Product category availability is partial. Missing category values should be retained or explicitly grouped as unknown during analysis.
8. Customer ratings require a documented rule when multiple reviews are associated with an order.

## 4. Analytical Implications

The available fields support:

- Delivery duration and on-time performance analysis.
- Order status and cancellation analysis.
- Customer-state and seller-state comparisons.
- Product category performance analysis where category information exists.
- Freight cost analysis.
- Customer rating comparisons against delivery outcomes.

The dataset does not support direct carrier-level performance comparisons, cancellation-reason analysis or actual delivery-distance analysis. ZIP-prefix-based coordinates may support limited geographic exploration, but they are insufficient to establish actual delivery routes or calculate verified delivery distances.

## 5. Source

Brazilian E-Commerce Public Dataset by Olist

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

All availability classifications are based on the downloaded source files and their observed column coverage.