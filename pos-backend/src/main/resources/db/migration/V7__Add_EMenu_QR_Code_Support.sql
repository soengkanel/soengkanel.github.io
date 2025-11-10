-- Migration: Add eMenu QR Code Support
-- Description: Adds QR code token to table_layouts for eMenu access
-- Author: System
-- Date: 2025-10-14

-- Add QR code token column to table_layouts for eMenu
ALTER TABLE table_layouts
ADD COLUMN qr_code VARCHAR(255) NULL COMMENT 'Secure token for QR code eMenu access';

-- Create unique index on qr_code for quick lookups
CREATE UNIQUE INDEX idx_table_qr_code ON table_layouts(qr_code);

-- Add order_type column to orders if not exists (for tracking dine-in vs other types)
ALTER TABLE orders
ADD COLUMN order_type VARCHAR(20) NULL DEFAULT 'DINE_IN' COMMENT 'Type of order: DINE_IN, TAKEOUT, DELIVERY';

-- Add index for better performance
CREATE INDEX idx_orders_order_type ON orders(order_type);
