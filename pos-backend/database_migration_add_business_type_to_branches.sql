-- ==========================================
-- Database Migration Script
-- Add business_type column to branches table
-- Date: 2025-10-15
-- ==========================================

-- Step 1: Add business_type column to branches table (allow NULL initially)
ALTER TABLE branches
ADD COLUMN business_type VARCHAR(20);

-- Step 2: Update existing branches to inherit business_type from their parent store
-- This ensures all existing branches get the correct business type
UPDATE branches b
INNER JOIN stores s ON b.store_id = s.id
SET b.business_type = s.business_type
WHERE b.store_id IS NOT NULL;

-- Step 3: For any branches without a store (shouldn't exist, but just in case)
-- Set them to RETAIL as a default
UPDATE branches
SET business_type = 'RETAIL'
WHERE business_type IS NULL;

-- Step 4: (OPTIONAL) Make the column NOT NULL now that all rows have values
-- Uncomment this line only if you want to enforce NOT NULL at database level
-- The application handles NULL values by defaulting to RETAIL
-- ALTER TABLE branches
-- MODIFY COLUMN business_type VARCHAR(20) NOT NULL;

-- Step 5: Add index for better query performance
CREATE INDEX idx_branches_business_type ON branches(business_type);

-- Step 6: Add foreign key constraint if not exists (ensures referential integrity)
-- Note: This assumes the foreign key constraint name; adjust if different
-- ALTER TABLE branches
-- ADD CONSTRAINT fk_branch_store
-- FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE;

-- Verification Queries
-- Run these to verify the migration was successful:

-- 1. Check all branches now have business_type
SELECT
    COUNT(*) as total_branches,
    COUNT(business_type) as branches_with_business_type
FROM branches;

-- 2. See business_type distribution
SELECT
    business_type,
    COUNT(*) as count
FROM branches
GROUP BY business_type;

-- 3. Verify branches match their store's business type
SELECT
    b.id as branch_id,
    b.name as branch_name,
    b.business_type as branch_business_type,
    s.business_type as store_business_type,
    CASE
        WHEN b.business_type = s.business_type THEN 'MATCH ✓'
        ELSE 'MISMATCH ✗'
    END as status
FROM branches b
INNER JOIN stores s ON b.store_id = s.id;

-- ==========================================
-- Rollback Script (if needed)
-- ==========================================

-- Uncomment these lines to rollback the changes:
-- ALTER TABLE branches DROP INDEX idx_branches_business_type;
-- ALTER TABLE branches DROP COLUMN business_type;
