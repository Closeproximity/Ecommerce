
# Data Dictionary
## E-commerce Delivery & Logistics Performance Analysis

## 1. Dataset Overview

**Dataset:** Brazilian E-Commerce Public Dataset by Olist

**Source:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

**Coverage:** Approximately 100,000 orders from 2016–2018.

**Source format:** CSV

**Database:** PostgreSQL

The dataset contains nine source tables covering customers, orders, products, sellers, payments, reviews, geolocation, and product category translations.

The original CSV files are preserved in `data/raw/`. No modifications are made to the raw source files.

---

## 2. Table Dictionary

### 2.1 customers

**Database table:** `customers`

**Grain:** One row per customer record (`customer_id`).

**Primary key:** `customer_id`

| Column | Description |
|---|---|
| customer_id | Unique identifier for a customer record associated with an order |
| customer_unique_id | Identifier representing the customer's unique identity across orders |
| customer_zip_code_prefix | First five digits of the customer's ZIP code |
| customer_city | Customer's city |
| customer_state | Customer's state |

**Foreign key relationship:**
- `orders.customer_id` references `customers.customer_id`.

**Important observation:** `customer_unique_id` is not unique. Multiple customer records can represent the same unique customer.

### 2.2 orders

**Database table:** `orders`

**Grain:** One row per order.

**Primary key:** `order_id`

| Column | Description |
|---|---|
| order_id | Unique identifier of an order |
| customer_id | Customer record associated with the order |
| order_status | Current or recorded status of the order |
| order_purchase_timestamp | Date and time when the order was purchased |
| order_approved_at | Date and time when payment approval occurred |
| order_delivered_carrier_date | Date and time when the order was handed to the carrier |
| order_delivered_customer_date | Date and time when the customer received the order |
| order_estimated_delivery_date | Estimated delivery date promised to the customer |

**Foreign key relationship:**
- `customer_id` references `customers.customer_id`.

**Important observation:** Some approval and delivery timestamps are missing. The estimated delivery date is available for all source records.

### 2.3 order_items

**Database table:** `order_items`

**Grain:** One row per item within an order.

**Composite primary key:** `(order_id, order_item_id)`

| Column | Description |
|---|---|
| order_id | Order to which the item belongs |
| order_item_id | Sequential item number within an order |
| product_id | Identifier of the purchased product |
| seller_id | Identifier of the seller supplying the item |
| shipping_limit_date | Seller's shipping deadline |
| price | Price of the individual item |
| freight_value | Freight charge associated with the item |

**Foreign key relationships:**
- `order_id` references `orders.order_id`.
- `product_id` references `products.product_id`.
- `seller_id` references `sellers.seller_id`.

**Important observation:** An order can contain multiple items and sellers. Do not assume one row per order.

### 2.4 payments

**Database table:** `payments`

**Grain:** One row per payment record within an order.

**Composite primary key:** `(order_id, payment_sequential)`

| Column | Description |
|---|---|
| order_id | Order associated with the payment |
| payment_sequential | Sequential number of the payment within an order |
| payment_type | Payment method used |
| payment_installments | Number of installments |
| payment_value | Value of the payment record |

**Foreign key relationship:**
- `order_id` references `orders.order_id`.

**Important observation:** An order can have multiple payment records. Aggregate payment data by order before joining it to other order-level summaries.

### 2.5 order_reviews

**Database table:** `reviews`

**Grain:** One review record associated with an order.

**Composite primary key:** `(review_id, order_id)`

| Column | Description |
|---|---|
| review_id | Identifier of the review |
| order_id | Order associated with the review |
| review_score | Customer's review score |
| review_comment_title | Review title |
| review_comment_message | Review text |
| review_creation_date | Date and time when the review survey was created |
| review_answer_timestamp | Date and time when the review was answered |

**Foreign key relationship:**
- `order_id` references `orders.order_id`.

**Important observation:** Review comment fields contain substantial missing data. `review_id` alone is not unique in the source dataset.

### 2.6 products

**Database table:** `products`

**Grain:** One row per product.

**Primary key:** `product_id`

| Column | Description |
|---|---|
| product_id | Unique product identifier |
| product_category_name | Product category in Portuguese |
| product_name_lenght | Length of the product name |
| product_description_lenght | Length of the product description |
| product_photos_qty | Number of product photos |
| product_weight_g | Product weight in grams |
| product_length_cm | Product length in centimeters |
| product_height_cm | Product height in centimeters |
| product_width_cm | Product width in centimeters |

**Important observation:** Some product attributes and category values are missing. Original source column spellings are preserved.

### 2.7 sellers

**Database table:** `sellers`

**Grain:** One row per seller.

**Primary key:** `seller_id`

| Column | Description |
|---|---|
| seller_id | Unique seller identifier |
| seller_zip_code_prefix | First five digits of the seller's ZIP code |
| seller_city | Seller's city |
| seller_state | Seller's state |

**Important observation:** Seller information can be linked to individual order items through `seller_id`.

### 2.8 geolocation

**Database table:** `geolocation`

**Grain:** One row per geolocation record.

**Primary key:** No primary key defined.

| Column | Description |
|---|---|
| geolocation_zip_code_prefix | ZIP code prefix |
| geolocation_lat | Latitude |
| geolocation_lng | Longitude |
| geolocation_city | City |
| geolocation_state | State |

**Important observation:**
- The table contains duplicate full rows.
- ZIP code prefixes are not unique.
- Multiple coordinates can exist for the same ZIP code prefix.
- Direct joins can multiply rows unless geolocation records are first deduplicated or aggregated using a documented method.

### 2.9 category_translation

**Database table:** `category_translation`

**Grain:** One row per translated product category.

**Primary key:** `product_category_name`

| Column | Description |
|---|---|
| product_category_name | Original product category in Portuguese |
| product_category_name_english | English translation of the category |

**Important observation:** Two product categories in the products table do not have corresponding translations. No translations have been invented.

---

## 3. Database Relationships

The following primary and foreign key relationships are defined in PostgreSQL:

| Child table | Foreign key | Parent table | Referenced key |
|---|---|---|---|
| orders | customer_id | customers | customer_id |
| order_items | order_id | orders | order_id |
| order_items | product_id | products | product_id |
| order_items | seller_id | sellers | seller_id |
| payments | order_id | orders | order_id |
| reviews | order_id | orders | order_id |

The `geolocation` table has no defined primary key or foreign key.

The category translation relationship is not enforced as a foreign key because two product categories have no matching translation records.

---

## 4. Table Grain Summary

| Table | Grain | Primary key |
|---|---|---|
| customers | One customer record | customer_id |
| orders | One order | order_id |
| order_items | One item per order | order_id + order_item_id |
| payments | One payment record per order | order_id + payment_sequential |
| reviews | One review/order record | review_id + order_id |
| products | One product | product_id |
| sellers | One seller | seller_id |
| geolocation | One geolocation record | None |
| category_translation | One category translation | product_category_name |

---

## 5. Important Data Handling Rules

1. Preserve all original CSV files in `data/raw/`.
2. Do not modify or overwrite raw source data.
3. Do not assume that every table has one row per order.
4. Aggregate `order_items` and `payments` separately before joining them to order-level data.
5. Do not directly join geolocation using ZIP code prefixes without addressing multiple matches.
6. Preserve missing values and document exclusions in KPI calculations.
7. Do not invent missing product category translations or other source information.
8. Keep source column names unchanged in the raw database tables.

---

## 6. Related Analytical Views

The following SQL views are created for downstream analysis:

| View | Purpose |
|---|---|
| vw_order_delivery_performance | Order delivery duration, delay, timing category, and on-time indicator |
| vw_order_item_summary | Order-level item counts and product/freight totals |
| vw_order_payment_summary | Order-level payment counts, methods, and payment totals |
| vw_order_analytics | Consolidated order-level analytical dataset |

The consolidated view preserves all 99,441 orders and uses pre-aggregated item and payment summaries to avoid row multiplication.
