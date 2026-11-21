
-- =====================================================
-- E-commerce Delivery & Logistics Performance Analysis
-- File: rebuild_views.sql
-- Purpose: Safely drop and recreate all analytical views
-- Run from the project root using psql
-- =====================================================

-- Drop dependent views first
DROP VIEW IF EXISTS vw_order_analytics;
DROP VIEW IF EXISTS vw_order_item_detail;

-- Drop supporting summary views
DROP VIEW IF EXISTS vw_order_review_summary;
DROP VIEW IF EXISTS vw_order_payment_summary;
DROP VIEW IF EXISTS vw_order_item_summary;
DROP VIEW IF EXISTS vw_order_delivery_performance;

-- Recreate all views using the main definitions file
\ir views.sql
