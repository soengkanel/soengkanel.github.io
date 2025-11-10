# Database Migration Guide: Retail to Multi-Business Type POS

This guide helps you migrate from the existing single Product table to separate RetailProduct and MenuItem tables.

## Overview

**Old Structure:**
- Single `products` table for all products
- Direct foreign key relationship with `order_items`

**New Structure:**
- `retail_products` table for retail items
- `menu_items` table for F&B items
- `order_items` uses productId + productType (polymorphic reference)
- `stores` table has new `business_type` field

---

## Migration Steps

### Step 1: Backup Current Database

```sql
-- Backup existing data
CREATE TABLE products_backup AS SELECT * FROM products;
CREATE TABLE order_items_backup AS SELECT * FROM order_items;
CREATE TABLE stores_backup AS SELECT * FROM stores;
```

---

### Step 2: Add BusinessType to Stores Table

```sql
-- Add business_type column to stores
ALTER TABLE stores
ADD COLUMN business_type VARCHAR(20) NOT NULL DEFAULT 'RETAIL';

-- Update existing stores (all retail by default)
UPDATE stores SET business_type = 'RETAIL' WHERE business_type IS NULL;
```

---

### Step 3: Create New Tables

```sql
-- Create retail_products table
CREATE TABLE retail_products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    mrp DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    brand VARCHAR(255),
    barcode VARCHAR(255) UNIQUE,
    manufacturer VARCHAR(255),
    warranty VARCHAR(100),
    weight DOUBLE,
    dimensions VARCHAR(100),
    reorder_level INT,
    max_stock_level INT,
    hsn_code VARCHAR(50),
    tax_rate DECIMAL(5,2),
    model_number VARCHAR(100),
    color VARCHAR(50),
    size VARCHAR(50),
    material VARCHAR(100),
    has_expiry BOOLEAN DEFAULT FALSE,
    shelf_life_days INT,
    image VARCHAR(500),
    category_id BIGINT,
    store_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (store_id) REFERENCES stores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create menu_items table
CREATE TABLE menu_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    mrp DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    image VARCHAR(500),
    preparation_time INT,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    calories INT,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_vegan BOOLEAN DEFAULT FALSE,
    contains_nuts BOOLEAN DEFAULT FALSE,
    is_gluten_free BOOLEAN DEFAULT FALSE,
    spice_level VARCHAR(20),
    course_type VARCHAR(50),
    serves INT,
    kitchen_station VARCHAR(50),
    preparation_notes TEXT,
    portion_size VARCHAR(100),
    allows_modifiers BOOLEAN DEFAULT TRUE,
    category_id BIGINT,
    store_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (store_id) REFERENCES stores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create order_item_modifiers table
CREATE TABLE order_item_modifiers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    additional_price DECIMAL(10,2) NOT NULL,
    notes TEXT,
    order_item_id BIGINT NOT NULL,
    FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

### Step 4: Migrate Existing Product Data

```sql
-- Migrate all existing products to retail_products
INSERT INTO retail_products (
    id, name, sku, description, mrp, selling_price, brand, image,
    category_id, store_id, created_at, updated_at
)
SELECT
    id, name, sku, description, mrp, selling_price, brand, image,
    category_id, store_id, created_at, updated_at
FROM products;

-- Verify migration
SELECT COUNT(*) AS original_count FROM products;
SELECT COUNT(*) AS migrated_count FROM retail_products;
```

---

### Step 5: Update OrderItems Table

```sql
-- Add new columns to order_items
ALTER TABLE order_items
ADD COLUMN product_type VARCHAR(20) NOT NULL DEFAULT 'RETAIL';

ALTER TABLE order_items
ADD COLUMN product_name VARCHAR(255);

ALTER TABLE order_items
ADD COLUMN product_sku VARCHAR(255);

ALTER TABLE order_items
ADD COLUMN special_instructions TEXT;

-- Rename existing product_id column for clarity
ALTER TABLE order_items
CHANGE COLUMN product_id product_id BIGINT NOT NULL;

-- Update product_name and product_sku from existing products
UPDATE order_items oi
INNER JOIN products p ON oi.product_id = p.id
SET
    oi.product_name = p.name,
    oi.product_sku = p.sku,
    oi.product_type = 'RETAIL';

-- Remove foreign key constraint from order_items to products
-- (This allows flexibility for both retail_products and menu_items)
ALTER TABLE order_items DROP FOREIGN KEY order_items_ibfk_1;
-- Note: Constraint name may vary, check with:
-- SHOW CREATE TABLE order_items;
```

---

### Step 6: Update Inventory Table (if exists)

```sql
-- Check if inventory references products
SHOW CREATE TABLE inventory;

-- If inventory has product_id FK, update it to reference retail_products
-- Add product_type column
ALTER TABLE inventory
ADD COLUMN product_type VARCHAR(20) NOT NULL DEFAULT 'RETAIL';

-- Note: Menu items typically don't have inventory tracking
-- Only retail products have inventory
```

---

### Step 7: Create Indexes for Performance

```sql
-- Indexes for retail_products
CREATE INDEX idx_retail_products_store ON retail_products(store_id);
CREATE INDEX idx_retail_products_category ON retail_products(category_id);
CREATE INDEX idx_retail_products_barcode ON retail_products(barcode);
CREATE INDEX idx_retail_products_brand ON retail_products(brand);

-- Indexes for menu_items
CREATE INDEX idx_menu_items_store ON menu_items(store_id);
CREATE INDEX idx_menu_items_category ON menu_items(category_id);
CREATE INDEX idx_menu_items_available ON menu_items(is_available);
CREATE INDEX idx_menu_items_course_type ON menu_items(course_type);
CREATE INDEX idx_menu_items_kitchen_station ON menu_items(kitchen_station);

-- Indexes for order_items
CREATE INDEX idx_order_items_product_type ON order_items(product_type);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
```

---

### Step 8: Verification Queries

```sql
-- Check data integrity
SELECT 'retail_products', COUNT(*) FROM retail_products
UNION ALL
SELECT 'menu_items', COUNT(*) FROM menu_items
UNION ALL
SELECT 'products (original)', COUNT(*) FROM products;

-- Verify order_items update
SELECT
    product_type,
    COUNT(*) as count,
    MIN(created_at) as earliest_order,
    MAX(created_at) as latest_order
FROM order_items
GROUP BY product_type;

-- Check for orphaned order_items
SELECT COUNT(*) as orphaned_retail_items
FROM order_items oi
LEFT JOIN retail_products rp ON oi.product_id = rp.id AND oi.product_type = 'RETAIL'
WHERE oi.product_type = 'RETAIL' AND rp.id IS NULL;

-- Check stores business_type
SELECT business_type, COUNT(*) as store_count
FROM stores
GROUP BY business_type;
```

---

### Step 9: Optional - Drop Old Products Table

**⚠️ WARNING: Only do this after thorough testing!**

```sql
-- Rename products table (keep as backup)
RENAME TABLE products TO products_old;

-- After 30 days of successful operation, you can drop it
-- DROP TABLE products_old;
```

---

## Rollback Plan

If migration fails, restore from backup:

```sql
-- Restore original tables
DROP TABLE retail_products;
DROP TABLE menu_items;
DROP TABLE order_item_modifiers;

-- Restore from backup
CREATE TABLE products AS SELECT * FROM products_backup;
CREATE TABLE order_items AS SELECT * FROM order_items_backup;
CREATE TABLE stores AS SELECT * FROM stores_backup;

-- Remove added columns from stores
ALTER TABLE stores DROP COLUMN business_type;
```

---

## Post-Migration Tasks

### 1. Update Application Configuration

**application.properties / application.yml:**
```properties
# Update JPA settings if needed
spring.jpa.hibernate.ddl-auto=none
spring.jpa.show-sql=false
```

### 2. Test Endpoints

```bash
# Test retail product endpoints
GET /api/retail-products?storeId=1
POST /api/retail-products
GET /api/retail-products/{id}

# Test menu item endpoints
GET /api/menu-items?storeId=1
POST /api/menu-items
GET /api/menu-items/{id}
```

### 3. Update Frontend

- Update Redux slices to handle retail vs F&B products
- Create separate forms for RetailProduct and MenuItem
- Update POS interface to show different product types

---

## Common Issues & Solutions

### Issue 1: Foreign Key Constraint Errors
**Solution:** Temporarily disable foreign key checks:
```sql
SET FOREIGN_KEY_CHECKS=0;
-- Run migration
SET FOREIGN_KEY_CHECKS=1;
```

### Issue 2: Duplicate SKU Errors
**Solution:** Update SKUs to be unique:
```sql
UPDATE products SET sku = CONCAT(sku, '-', id) WHERE sku IN (
    SELECT sku FROM (SELECT sku FROM products GROUP BY sku HAVING COUNT(*) > 1) as dupe
);
```

### Issue 3: NULL Category References
**Solution:** Create "Uncategorized" category:
```sql
INSERT INTO categories (name, store_id) VALUES ('Uncategorized', 1);
UPDATE retail_products SET category_id = LAST_INSERT_ID() WHERE category_id IS NULL;
```

---

## Migration Checklist

- [ ] Backup all tables
- [ ] Add business_type to stores
- [ ] Create retail_products table
- [ ] Create menu_items table
- [ ] Create order_item_modifiers table
- [ ] Migrate products to retail_products
- [ ] Update order_items structure
- [ ] Update inventory table (if applicable)
- [ ] Create indexes
- [ ] Run verification queries
- [ ] Test application with new structure
- [ ] Update frontend code
- [ ] Monitor for 7 days
- [ ] Archive old products table

---

## Next Steps

After successful migration:

1. **Implement Controllers**
   - RetailProductController
   - MenuItemController

2. **Create Frontend Components**
   - RetailProductForm
   - MenuItemForm
   - Unified POS interface

3. **Add F&B Specific Features**
   - Table management
   - Kitchen order system (KDS)
   - Menu modifiers UI

4. **Testing**
   - Unit tests for services
   - Integration tests for repositories
   - E2E tests for workflows

---

## Support

For questions or issues:
- Check application logs: `logs/spring-boot-app.log`
- Review database error logs
- Contact development team

**Migration Date:** _____________
**Performed By:** _____________
**Status:** [ ] Success [ ] Rollback Required
