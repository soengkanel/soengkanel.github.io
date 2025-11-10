-- Repair Flyway Schema History
-- This script removes the failed migration record from the flyway_schema_history table

USE pos;

-- Check current state
SELECT * FROM flyway_schema_history;

-- Delete the failed migration (version 1)
DELETE FROM flyway_schema_history WHERE version = '1' AND success = 0;

-- Verify cleanup
SELECT * FROM flyway_schema_history;

-- If you want to completely reset Flyway (use with caution):
-- DELETE FROM flyway_schema_history;
