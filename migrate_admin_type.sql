-- SQL Migration to add 'admin' to user_type enum
-- This migration adds the 'admin' value to the existing user_type enum

-- For PostgreSQL:
-- Add 'admin' to the user_type enum if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumlabel = 'admin'
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'usertype')
    ) THEN
        ALTER TYPE usertype ADD VALUE 'admin';
    END IF;
END$$;

-- For MySQL/MariaDB:
-- ALTER TABLE users MODIFY COLUMN user_type ENUM('employee', 'employer', 'admin') NOT NULL;

-- For SQLite (SQLite doesn't support ALTER TYPE, you may need to recreate the table or use check constraints)
-- This is handled automatically by SQLAlchemy for SQLite
