-- PostgreSQL initialization script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS agent_wiki;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA agent_wiki TO agentwiki;

-- Note: Tables will be created by SQLAlchemy on application startup
-- This script is for initial database setup and extensions
