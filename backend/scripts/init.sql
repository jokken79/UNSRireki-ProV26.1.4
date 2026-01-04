-- UNS Rirekisho Pro - Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create default admin user (password: admin123 - CHANGE IN PRODUCTION)
-- This will be inserted by the application on first run

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE uns_rirekisho TO postgres;

-- Create indexes for performance
-- These are defined in SQLAlchemy models but we can add custom ones here

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'UNS Rirekisho Pro database initialized successfully';
END $$;
