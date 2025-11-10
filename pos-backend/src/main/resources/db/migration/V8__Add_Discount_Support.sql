-- V3__Add_Discount_Support.sql
-- Adds discount support for both invoice-level and line-item discounts

-- Add discount fields to orders table (invoice-level discount)
ALTER TABLE orders
ADD COLUMN subtotal DOUBLE NULL AFTER total_amount,
ADD COLUMN discount_type VARCHAR(20) NULL AFTER subtotal,
ADD COLUMN discount_value DOUBLE NULL AFTER discount_type,
ADD COLUMN discount_amount DOUBLE NULL AFTER discount_value,
ADD COLUMN discount_reason VARCHAR(500) NULL AFTER discount_amount,
ADD COLUMN tax_amount DOUBLE NULL AFTER discount_reason;

-- Add discount fields to order_items table (line-item discount)
ALTER TABLE order_items
ADD COLUMN discount_type VARCHAR(20) NULL AFTER price,
ADD COLUMN discount_value DOUBLE NULL AFTER discount_type,
ADD COLUMN discount_amount DOUBLE NULL AFTER discount_value,
ADD COLUMN discount_reason VARCHAR(500) NULL AFTER discount_amount;

-- Create index for discount queries
CREATE INDEX idx_orders_discount_type ON orders(discount_type);
CREATE INDEX idx_order_items_discount_type ON order_items(discount_type);

-- Update existing orders to have proper subtotal (migrate existing data)
UPDATE orders
SET subtotal = total_amount,
    discount_type = 'NONE',
    discount_value = 0,
    discount_amount = 0,
    tax_amount = 0
WHERE subtotal IS NULL;

-- Update existing order_items to have no discount by default
UPDATE order_items
SET discount_type = 'NONE',
    discount_value = 0,
    discount_amount = 0
WHERE discount_type IS NULL;
