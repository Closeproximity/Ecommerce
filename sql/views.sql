
-- =====================================================
-- E-commerce Delivery & Logistics Performance Analysis
-- File: views.sql
-- Purpose: Analytical views for delivery performance
-- =====================================================

CREATE OR REPLACE VIEW vw_order_delivery_performance AS

SELECT
    order_id,
    customer_id,
    order_status,

    -- Original timestamps converted to TIMESTAMP
    NULLIF(order_purchase_timestamp, '')::TIMESTAMP
        AS purchase_timestamp,

    NULLIF(order_delivered_customer_date, '')::TIMESTAMP
        AS actual_delivery_timestamp,

    NULLIF(order_estimated_delivery_date, '')::TIMESTAMP
        AS estimated_delivery_timestamp,

    -- Actual delivery duration in days
    CASE
        WHEN order_status = 'delivered'
         AND order_delivered_customer_date IS NOT NULL
        THEN
            EXTRACT(
                EPOCH FROM (
                    NULLIF(order_delivered_customer_date, '')::TIMESTAMP
                    - NULLIF(order_purchase_timestamp, '')::TIMESTAMP
                )
            ) / 86400.0
        ELSE NULL
    END AS actual_delivery_duration_days,

    -- Difference between actual and estimated calendar dates
    CASE
        WHEN order_status = 'delivered'
         AND order_delivered_customer_date IS NOT NULL
         AND order_estimated_delivery_date IS NOT NULL
        THEN
            NULLIF(order_delivered_customer_date, '')::TIMESTAMP::DATE
            -
            NULLIF(order_estimated_delivery_date, '')::TIMESTAMP::DATE
        ELSE NULL
    END AS delivery_delay_days,

    -- Delivery classification
    CASE
        WHEN order_status <> 'delivered'
            THEN 'not_delivered'

        WHEN order_delivered_customer_date IS NULL
          OR order_estimated_delivery_date IS NULL
            THEN 'missing_delivery_date'

        WHEN NULLIF(order_delivered_customer_date, '')::TIMESTAMP::DATE
             < NULLIF(order_estimated_delivery_date, '')::TIMESTAMP::DATE
            THEN 'early'

        WHEN NULLIF(order_delivered_customer_date, '')::TIMESTAMP::DATE
             = NULLIF(order_estimated_delivery_date, '')::TIMESTAMP::DATE
            THEN 'on_date'

        ELSE 'late'
    END AS delivery_timing_category,

    -- Headline KPI: on-time includes early and same-day delivery
    CASE
        WHEN order_status = 'delivered'
         AND order_delivered_customer_date IS NOT NULL
         AND order_estimated_delivery_date IS NOT NULL
        THEN
            NULLIF(order_delivered_customer_date, '')::TIMESTAMP::DATE
            <=
            NULLIF(order_estimated_delivery_date, '')::TIMESTAMP::DATE
        ELSE NULL
    END AS is_on_time

FROM orders;


-- =====================================================
-- 2. Order Item Summary
-- One row per order
-- =====================================================

CREATE OR REPLACE VIEW vw_order_item_summary AS

SELECT
    order_id,

    COUNT(*) AS total_items,

    COUNT(DISTINCT product_id) AS unique_products,

    COUNT(DISTINCT seller_id) AS unique_sellers,

    ROUND(SUM(price)::NUMERIC, 2) AS total_product_value,

    ROUND(SUM(freight_value)::NUMERIC, 2) AS total_freight_value,

    ROUND(
        SUM(price + freight_value)::NUMERIC,
        2
    ) AS total_order_item_value

FROM order_items

GROUP BY order_id;



-- =====================================================
-- 3. Order Payment Summary
-- One row per order with payment records
-- =====================================================

CREATE OR REPLACE VIEW vw_order_payment_summary AS

SELECT
    order_id,

    COUNT(*) AS payment_records,

    COUNT(DISTINCT payment_type) AS payment_methods_used,

    ROUND(SUM(payment_value)::NUMERIC, 2)
        AS total_payment_value,

    ROUND(AVG(payment_value)::NUMERIC, 2)
        AS average_payment_value,

    MAX(payment_installments) AS max_installments,

    STRING_AGG(
        DISTINCT payment_type,
        ', ' ORDER BY payment_type
    ) AS payment_methods

FROM payments

GROUP BY order_id;


-- =========================================================
-- 5. Order Review Summary
-- One row per order
-- =========================================================

CREATE OR REPLACE VIEW vw_order_review_summary AS
SELECT
    order_id,
    COUNT(*) AS review_count,
    ROUND(AVG(review_score)::NUMERIC, 2) AS average_review_score,
    MIN(review_score) AS minimum_review_score,
    MAX(review_score) AS maximum_review_score,
    MIN(review_creation_date::TIMESTAMP) AS first_review_created_at,
    MAX(review_answer_timestamp::TIMESTAMP) AS last_review_answered_at
FROM reviews
GROUP BY order_id;

CREATE OR REPLACE VIEW vw_order_item_detail AS
SELECT
    oi.order_id,
    oi.order_item_id,
    o.order_status,
    o.order_purchase_timestamp::TIMESTAMP AS purchase_timestamp,

    oi.product_id,
    p.product_category_name,
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name
    ) AS product_category_english,

    oi.seller_id,
    s.seller_city,
    s.seller_state,

    c.customer_id,
    c.customer_city,
    c.customer_state,

    oi.price,
    oi.freight_value,
    oi.price + oi.freight_value AS total_item_value

FROM order_items oi
LEFT JOIN orders o
    ON oi.order_id = o.order_id
LEFT JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
LEFT JOIN sellers s
    ON oi.seller_id = s.seller_id
LEFT JOIN customers c
    ON o.customer_id = c.customer_id;


-- =========================================================
-- 6. Consolidated Order Analytics
-- One row per order
-- =========================================================

CREATE OR REPLACE VIEW vw_order_analytics AS
SELECT
    -- Order and customer information
    d.order_id,
    d.customer_id,
    d.order_status,
    d.purchase_timestamp,

    -- Delivery performance
    d.actual_delivery_timestamp,
    d.estimated_delivery_timestamp,
    d.actual_delivery_duration_days,
    d.delivery_delay_days,
    d.delivery_timing_category,
    d.is_on_time,

    -- Order item metrics
    COALESCE(i.total_items, 0) AS total_items,
    COALESCE(i.unique_products, 0) AS unique_products,
    COALESCE(i.unique_sellers, 0) AS unique_sellers,
    COALESCE(i.total_product_value, 0) AS total_product_value,
    COALESCE(i.total_freight_value, 0) AS total_freight_value,
    COALESCE(i.total_order_item_value, 0) AS total_order_item_value,

    -- Payment metrics
    COALESCE(p.payment_records, 0) AS payment_records,
    COALESCE(p.payment_methods_used, 0) AS payment_methods_used,
    p.total_payment_value,
    p.average_payment_value,
    p.max_installments,
    p.payment_methods,

    -- Existing data availability indicators
    (i.order_id IS NOT NULL) AS has_item_records,
    (p.order_id IS NOT NULL) AS has_payment_records,

    -- Review metrics
    COALESCE(r.review_count, 0::BIGINT) AS review_count,
    r.average_review_score,
    r.minimum_review_score,
    r.maximum_review_score,
    r.first_review_created_at,
    r.last_review_answered_at,

    -- Review availability indicator
    (r.order_id IS NOT NULL) AS has_review_records

FROM vw_order_delivery_performance d

LEFT JOIN vw_order_item_summary i
    ON d.order_id = i.order_id

LEFT JOIN vw_order_payment_summary p
    ON d.order_id = p.order_id

LEFT JOIN vw_order_review_summary r
    ON d.order_id = r.order_id;
