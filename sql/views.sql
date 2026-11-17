
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

    -- Data availability indicators
    (i.order_id IS NOT NULL) AS has_item_records,
    (p.order_id IS NOT NULL) AS has_payment_records

FROM vw_order_delivery_performance d

LEFT JOIN vw_order_item_summary i
    ON d.order_id = i.order_id

LEFT JOIN vw_order_payment_summary p
    ON d.order_id = p.order_id;
