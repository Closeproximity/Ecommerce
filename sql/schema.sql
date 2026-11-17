
-- =====================================================
-- E-commerce Delivery & Logistics Performance Analysis
-- File: schema.sql
-- Purpose: Create primary and foreign key constraints
-- Safe to rerun when the expected constraints exist
-- =====================================================

-- =====================================================
-- 1. PRIMARY KEY CONSTRAINTS
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.customers'::regclass
          AND conname = 'pk_customers'
          AND contype = 'p'
          AND pg_get_constraintdef(oid) = 'PRIMARY KEY (customer_id)'
    ) THEN
        ALTER TABLE customers
        ADD CONSTRAINT pk_customers PRIMARY KEY (customer_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.orders'::regclass
          AND conname = 'pk_orders'
          AND contype = 'p'
          AND pg_get_constraintdef(oid) = 'PRIMARY KEY (order_id)'
    ) THEN
        ALTER TABLE orders
        ADD CONSTRAINT pk_orders PRIMARY KEY (order_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.order_items'::regclass
          AND conname = 'pk_order_items'
          AND contype = 'p'
          AND pg_get_constraintdef(oid) =
              'PRIMARY KEY (order_id, order_item_id)'
    ) THEN
        ALTER TABLE order_items
        ADD CONSTRAINT pk_order_items
        PRIMARY KEY (order_id, order_item_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.payments'::regclass
          AND conname = 'pk_payments'
          AND contype = 'p'
          AND pg_get_constraintdef(oid) =
              'PRIMARY KEY (order_id, payment_sequential)'
    ) THEN
        ALTER TABLE payments
        ADD CONSTRAINT pk_payments
        PRIMARY KEY (order_id, payment_sequential);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.reviews'::regclass
          AND conname = 'pk_reviews'
          AND contype = 'p'
          AND pg_get_constraintdef(oid) =
              'PRIMARY KEY (review_id, order_id)'
    ) THEN
        ALTER TABLE reviews
        ADD CONSTRAINT pk_reviews
        PRIMARY KEY (review_id, order_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.products'::regclass
          AND conname = 'pk_products'
          AND contype = 'p'
          AND pg_get_constraintdef(oid) = 'PRIMARY KEY (product_id)'
    ) THEN
        ALTER TABLE products
        ADD CONSTRAINT pk_products PRIMARY KEY (product_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.sellers'::regclass
          AND conname = 'pk_sellers'
          AND contype = 'p'
          AND pg_get_constraintdef(oid) = 'PRIMARY KEY (seller_id)'
    ) THEN
        ALTER TABLE sellers
        ADD CONSTRAINT pk_sellers PRIMARY KEY (seller_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.category_translation'::regclass
          AND conname = 'pk_category_translation'
          AND contype = 'p'
          AND pg_get_constraintdef(oid) =
              'PRIMARY KEY (product_category_name)'
    ) THEN
        ALTER TABLE category_translation
        ADD CONSTRAINT pk_category_translation
        PRIMARY KEY (product_category_name);
    END IF;
END $$;


-- =====================================================
-- 2. FOREIGN KEY CONSTRAINTS
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.orders'::regclass
          AND conname = 'fk_orders_customers'
          AND contype = 'f'
          AND pg_get_constraintdef(oid) =
              'FOREIGN KEY (customer_id) REFERENCES customers(customer_id)'
    ) THEN
        ALTER TABLE orders
        ADD CONSTRAINT fk_orders_customers
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.order_items'::regclass
          AND conname = 'fk_order_items_orders'
          AND contype = 'f'
          AND pg_get_constraintdef(oid) =
              'FOREIGN KEY (order_id) REFERENCES orders(order_id)'
    ) THEN
        ALTER TABLE order_items
        ADD CONSTRAINT fk_order_items_orders
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.order_items'::regclass
          AND conname = 'fk_order_items_products'
          AND contype = 'f'
          AND pg_get_constraintdef(oid) =
              'FOREIGN KEY (product_id) REFERENCES products(product_id)'
    ) THEN
        ALTER TABLE order_items
        ADD CONSTRAINT fk_order_items_products
        FOREIGN KEY (product_id)
        REFERENCES products(product_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.order_items'::regclass
          AND conname = 'fk_order_items_sellers'
          AND contype = 'f'
          AND pg_get_constraintdef(oid) =
              'FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)'
    ) THEN
        ALTER TABLE order_items
        ADD CONSTRAINT fk_order_items_sellers
        FOREIGN KEY (seller_id)
        REFERENCES sellers(seller_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.payments'::regclass
          AND conname = 'fk_payments_orders'
          AND contype = 'f'
          AND pg_get_constraintdef(oid) =
              'FOREIGN KEY (order_id) REFERENCES orders(order_id)'
    ) THEN
        ALTER TABLE payments
        ADD CONSTRAINT fk_payments_orders
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.reviews'::regclass
          AND conname = 'fk_reviews_orders'
          AND contype = 'f'
          AND pg_get_constraintdef(oid) =
              'FOREIGN KEY (order_id) REFERENCES orders(order_id)'
    ) THEN
        ALTER TABLE reviews
        ADD CONSTRAINT fk_reviews_orders
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id);
    END IF;
END $$;
