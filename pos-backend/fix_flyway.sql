-- Fix Flyway schema history by removing failed migration
USE pos;

-- Show current flyway schema history
SELECT * FROM flyway_schema_history;

-- Delete the failed migration record
DELETE FROM flyway_schema_history WHERE success = 0;

-- Optionally, delete all migration records to start fresh
-- DELETE FROM flyway_schema_history;

-- Show updated flyway schema history
SELECT * FROM flyway_schema_history;
