-- V4__Add_Table_Management_Features.sql
-- Adds support for Change Table, Merge Table, and Split Bill features

-- Add table and order type columns to orders table
ALTER TABLE orders
ADD COLUMN table_id BIGINT NULL AFTER customer_id,
ADD COLUMN order_type VARCHAR(20) NULL AFTER table_id,
ADD COLUMN parent_order_id BIGINT NULL AFTER order_type,
ADD COLUMN is_split BOOLEAN DEFAULT FALSE AFTER parent_order_id,
ADD COLUMN split_number INT NULL AFTER is_split;

-- Add foreign key constraint for table
ALTER TABLE orders
ADD CONSTRAINT fk_orders_table
FOREIGN KEY (table_id) REFERENCES table_layouts(id) ON DELETE SET NULL;

-- Add foreign key constraint for parent order (self-referencing)
ALTER TABLE orders
ADD CONSTRAINT fk_orders_parent
FOREIGN KEY (parent_order_id) REFERENCES orders(id) ON DELETE SET NULL;

-- Create indexes for performance
CREATE INDEX idx_orders_table_id ON orders(table_id);
CREATE INDEX idx_orders_order_type ON orders(order_type);
CREATE INDEX idx_orders_parent_order_id ON orders(parent_order_id);
CREATE INDEX idx_orders_is_split ON orders(is_split);

-- Add current_order_id to table_layouts (if not exists)
-- This helps track which order is currently active on a table
SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'table_layouts'
    AND COLUMN_NAME = 'current_order_id'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE table_layouts ADD COLUMN current_order_id BIGINT NULL',
    'SELECT "Column current_order_id already exists"'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add foreign key for current_order (if column was just added)
SET @fk_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'table_layouts'
    AND CONSTRAINT_NAME = 'fk_table_current_order'
);

SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE table_layouts ADD CONSTRAINT fk_table_current_order FOREIGN KEY (current_order_id) REFERENCES orders(id) ON DELETE SET NULL',
    'SELECT "Foreign key fk_table_current_order already exists"'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Update existing orders to have default values
UPDATE orders
SET is_split = FALSE,
    order_type = 'DINE_IN'
WHERE is_split IS NULL;
