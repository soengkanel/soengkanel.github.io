-- V5__Add_Void_Invoice_Feature.sql
-- Adds support for voiding invoices/orders

-- Add void-related columns to orders table
ALTER TABLE orders
ADD COLUMN is_voided BOOLEAN DEFAULT FALSE AFTER status,
ADD COLUMN void_reason VARCHAR(50) NULL AFTER is_voided,
ADD COLUMN void_notes VARCHAR(1000) NULL AFTER void_reason,
ADD COLUMN voided_by BIGINT NULL AFTER void_notes,
ADD COLUMN voided_at DATETIME NULL AFTER voided_by,
ADD COLUMN void_approved_by BIGINT NULL AFTER voided_at;

-- Add foreign key constraints
ALTER TABLE orders
ADD CONSTRAINT fk_orders_voided_by
FOREIGN KEY (voided_by) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE orders
ADD CONSTRAINT fk_orders_void_approved_by
FOREIGN KEY (void_approved_by) REFERENCES users(id) ON DELETE SET NULL;

-- Create indexes for performance
CREATE INDEX idx_orders_is_voided ON orders(is_voided);
CREATE INDEX idx_orders_void_reason ON orders(void_reason);
CREATE INDEX idx_orders_voided_at ON orders(voided_at);
CREATE INDEX idx_orders_voided_by ON orders(voided_by);

-- Update existing orders to have is_voided = false
UPDATE orders
SET is_voided = FALSE
WHERE is_voided IS NULL;
