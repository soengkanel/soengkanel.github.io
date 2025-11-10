# Flyway Database Migration Guide

## Overview

This project uses Flyway for database schema migrations. Flyway tracks which migrations have been applied to your database and applies new ones automatically when you start your application.

## Dependencies Added

```xml
<!-- Flyway for database migrations -->
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-mysql</artifactId>
</dependency>
```

## Configuration

### application.yml

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate  # Changed from 'update' to 'validate'
    show-sql: true

  flyway:
    enabled: true
    baseline-on-migrate: true
    baseline-version: 0
    locations: classpath:db/migration
    validate-on-migrate: true
    clean-disabled: true
```

### Key Configuration Explained

- **ddl-auto: validate** - Hibernate now validates the schema but doesn't create/modify it
- **baseline-on-migrate: true** - Creates a baseline for existing databases
- **baseline-version: 0** - Sets the baseline version number
- **locations** - Where Flyway looks for migration scripts
- **clean-disabled: true** - Prevents accidental deletion of all database objects

## Migration File Naming Convention

Flyway follows a strict naming convention:

```
V{version}__{description}.sql
```

Examples:
- `V1__Create_Reservations_Table.sql`
- `V2__Add_Customer_Loyalty_Program.sql`
- `V3__Update_Product_Pricing.sql`
- `V4__Add_Index_On_Orders.sql`

### Naming Rules:
1. Must start with `V` (uppercase)
2. Followed by version number (e.g., `1`, `2`, `3` or `1.1`, `1.2`)
3. Two underscores `__`
4. Description with underscores instead of spaces
5. `.sql` extension

## Directory Structure

```
pos-backend/
└── src/
    └── main/
        └── resources/
            └── db/
                └── migration/
                    ├── V1__Create_Reservations_Table.sql
                    ├── V2__Add_New_Feature.sql
                    └── V3__Update_Schema.sql
```

## Creating New Migrations

### Step 1: Create Migration File

Create a new SQL file in `src/main/resources/db/migration/` with the proper naming:

```sql
-- V2__Add_Customer_Loyalty_Points.sql
ALTER TABLE customer
ADD COLUMN loyalty_points INT DEFAULT 0;

CREATE INDEX idx_customer_loyalty ON customer(loyalty_points);
```

### Step 2: Test Migration

Start your application. Flyway will automatically:
1. Check the `flyway_schema_history` table
2. Identify new migrations
3. Apply them in order
4. Record the migration in the history table

### Step 3: Verify

Check the `flyway_schema_history` table:
```sql
SELECT * FROM flyway_schema_history ORDER BY installed_rank;
```

## Migration Types

### 1. Versioned Migrations (V)
Regular migrations that run once in order.

```sql
-- V1__Initial_Schema.sql
CREATE TABLE example (...);
```

### 2. Repeatable Migrations (R)
Re-run whenever their checksum changes (useful for views, procedures).

```sql
-- R__Create_Sales_Report_View.sql
CREATE OR REPLACE VIEW sales_report AS
SELECT ...;
```

### 3. Undo Migrations (U) - Enterprise Edition Only
Roll back migrations.

```sql
-- U1__Undo_Initial_Schema.sql
DROP TABLE example;
```

## Best Practices

### 1. Never Modify Existing Migrations
Once a migration is applied to any environment (dev, staging, production), **never modify it**.
Create a new migration instead:

```sql
-- WRONG: Modifying V1__Create_Users.sql
-- RIGHT: Create V2__Add_Email_To_Users.sql
ALTER TABLE users ADD COLUMN email VARCHAR(255);
```

### 2. Use Descriptive Names
Good:
- `V1__Create_Reservations_Table.sql`
- `V2__Add_Customer_Email_Index.sql`
- `V3__Update_Order_Status_Enum.sql`

Bad:
- `V1__update.sql`
- `V2__fix.sql`
- `V3__changes.sql`

### 3. One Logical Change Per Migration
Don't mix unrelated changes. Keep migrations focused:

```sql
-- Good: V5__Add_Product_Categories.sql
CREATE TABLE product_categories (...);
ALTER TABLE products ADD COLUMN category_id BIGINT;

-- Bad: V5__Various_Updates.sql (mixing products, users, orders)
```

### 4. Always Use Transactions
Most migrations should be transactional:

```sql
-- MySQL uses transactions automatically for DDL in recent versions
START TRANSACTION;

ALTER TABLE products ADD COLUMN description TEXT;
UPDATE products SET description = name WHERE description IS NULL;

COMMIT;
```

### 5. Include Rollback Plans
Always have a strategy to undo changes (even if not automated):

```sql
-- V6__Add_User_Preferences.sql

-- Forward migration
ALTER TABLE users ADD COLUMN preferences JSON;

-- Rollback (document in comments):
-- To rollback: ALTER TABLE users DROP COLUMN preferences;
```

### 6. Test Migrations Locally First
Before committing:
1. Test on a copy of production data
2. Verify rollback procedure
3. Check performance on large datasets
4. Test with different MySQL versions if applicable

## Common Migration Scenarios

### Adding a Column

```sql
-- V3__Add_Phone_To_Customer.sql
ALTER TABLE customer
ADD COLUMN phone VARCHAR(20);
```

### Adding a Column with Default

```sql
-- V4__Add_Status_To_Orders.sql
ALTER TABLE orders
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'PENDING';
```

### Renaming a Column (Careful!)

```sql
-- V5__Rename_Customer_Full_Name.sql
ALTER TABLE customer
CHANGE COLUMN fullName full_name VARCHAR(255);
```

### Adding an Index

```sql
-- V6__Add_Index_Orders_Date.sql
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

### Creating a New Table with Foreign Keys

```sql
-- V7__Create_Order_Items_Table.sql
CREATE TABLE order_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders(id),
    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES products(id),

    INDEX idx_order_items_order (order_id),
    INDEX idx_order_items_product (product_id)
);
```

### Modifying Data

```sql
-- V8__Populate_Default_Categories.sql
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Food', 'Food and beverage products');

UPDATE products SET category_id = 1 WHERE category_id IS NULL;
```

### Dropping a Column (Dangerous!)

```sql
-- V9__Remove_Deprecated_Column.sql
-- Warning: This will permanently delete data

-- First, check if column is actually unused
-- SELECT COUNT(*) FROM users WHERE old_column IS NOT NULL;

ALTER TABLE users DROP COLUMN old_column;
```

## Working with Existing Databases

If you're adding Flyway to an existing database:

### Option 1: Baseline (Recommended)
1. Flyway creates a baseline at version 0
2. Your first migration becomes V1
3. Existing tables are preserved

```yaml
flyway:
  baseline-on-migrate: true
  baseline-version: 0
```

### Option 2: Initial Schema Migration
1. Create V1__Initial_Schema.sql with all existing tables
2. This won't work if tables already exist
3. Better for new projects

## Flyway Commands (Maven)

### Via Maven

```bash
# Apply migrations
mvn flyway:migrate

# Validate migrations
mvn flyway:validate

# Get migration info
mvn flyway:info

# Baseline existing database
mvn flyway:baseline

# Repair schema history (fix checksums)
mvn flyway:repair
```

### Via Spring Boot Application
Migrations run automatically when you start the application:

```bash
mvn spring-boot:run
```

## Troubleshooting

### Problem: Checksum Mismatch

**Error**: `Migration checksum mismatch`

**Solution**:
```bash
mvn flyway:repair
```

This recalculates checksums. Use carefully - only if you're sure the migration is correct.

### Problem: Failed Migration

**Error**: Migration fails halfway through

**Solution**:
1. Fix the issue in your migration script
2. Manually fix the database state
3. Delete the failed entry from `flyway_schema_history`:
   ```sql
   DELETE FROM flyway_schema_history WHERE success = 0;
   ```
4. Re-run migration

### Problem: Need to Skip a Version

**Error**: Can't skip V3 and jump to V4

**Solution**: Flyway requires sequential versions. Create an empty V3:
```sql
-- V3__Placeholder.sql
-- This version intentionally left empty
SELECT 1;
```

### Problem: Baseline Not Created

**Error**: `flyway_schema_history` table doesn't exist

**Solution**: Ensure baseline settings are correct:
```yaml
spring:
  flyway:
    baseline-on-migrate: true
```

## Monitoring Migrations

### Check Applied Migrations

```sql
SELECT
    installed_rank,
    version,
    description,
    type,
    script,
    installed_on,
    execution_time,
    success
FROM flyway_schema_history
ORDER BY installed_rank;
```

### Check Pending Migrations

Run `mvn flyway:info` to see:
- Applied migrations (✓)
- Pending migrations (⚠)
- Failed migrations (✗)

## Team Workflow

### Developer Workflow

1. **Pull latest code**
   ```bash
   git pull origin main
   ```

2. **Start application** (migrations run automatically)
   ```bash
   mvn spring-boot:run
   ```

3. **Create new migration if needed**
   ```bash
   # Get next version number
   # Check flyway_schema_history or existing files
   # Create V{next}__Description.sql
   ```

4. **Test migration locally**

5. **Commit and push**
   ```bash
   git add src/main/resources/db/migration/V*
   git commit -m "Add migration for feature X"
   git push
   ```

### Deployment Workflow

1. **Staging**: Automatic migrations on deployment
2. **Production**:
   - Review migrations carefully
   - Backup database first
   - Deploy during maintenance window
   - Monitor migration execution

## CI/CD Integration

In your CI/CD pipeline:

```yaml
# Example GitLab CI
test:
  script:
    - mvn clean test
    - mvn flyway:validate  # Validate migrations

deploy:
  script:
    - mvn flyway:info  # Show pending migrations
    - mvn spring-boot:run  # Migrations run automatically
```

## Rollback Strategy

Flyway Community Edition doesn't support automatic rollback. Plan manually:

1. **Document rollback in comments**:
   ```sql
   -- V5__Add_New_Feature.sql
   -- Rollback: Run R__Rollback_V5.sql
   ```

2. **Create rollback scripts** (not run automatically):
   ```sql
   -- rollback/R5__Rollback_V5.sql
   ALTER TABLE users DROP COLUMN new_column;
   ```

3. **Test rollback procedures** in staging

## Performance Considerations

### Large Datasets

For tables with millions of rows:

```sql
-- Bad: Locks entire table
ALTER TABLE large_table ADD COLUMN new_col INT;

-- Better: Add nullable first, then populate
ALTER TABLE large_table ADD COLUMN new_col INT NULL;

-- Then create data migration
UPDATE large_table
SET new_col = 0
WHERE new_col IS NULL
LIMIT 10000;  -- Run in batches
```

### Indexes on Large Tables

```sql
-- Create index with less locking
CREATE INDEX CONCURRENTLY idx_name ON table(column);
-- Note: MySQL doesn't support CONCURRENTLY, but uses online DDL in 5.6+
```

## Resources

- [Flyway Documentation](https://flywaydb.org/documentation/)
- [Flyway MySQL Documentation](https://flywaydb.org/documentation/database/mysql)
- [Spring Boot Flyway Integration](https://docs.spring.io/spring-boot/docs/current/reference/html/howto.html#howto.data-initialization.migration-tool.flyway)

## Summary

✅ **DO**:
- Use sequential version numbers
- Test migrations locally first
- Keep migrations focused and small
- Document rollback procedures
- Never modify applied migrations
- Use descriptive names

❌ **DON'T**:
- Modify existing migrations
- Skip version numbers
- Mix unrelated changes
- Forget to test on real data
- Deploy without backup
- Use Flyway clean in production

---

**Remember**: Migrations are code. Treat them with the same care as your application code!
