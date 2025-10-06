-- Migration: 001_initial_schema.sql
-- Description: Create initial database schema for tarball deduplication system
-- Date: 2025-10-06

BEGIN;

-- Create tables
\i ../schema.sql

-- Insert initial data or setup if needed
-- (None required for initial setup)

COMMIT;