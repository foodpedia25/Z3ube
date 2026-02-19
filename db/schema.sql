-- Z3ube Database Schema
-- Run this in your Supabase SQL Editor if automation fails

-- Enable pgvector extension for AI embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Interactions Table
CREATE TABLE IF NOT EXISTS interactions (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    feedback TEXT,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc'),
    tags JSONB DEFAULT '[]'::jsonb,
    embedding VECTOR(384) -- Dimension for all-MiniLM-L6-v2
);

-- Patterns Table (Self-Learning)
CREATE TABLE IF NOT EXISTS patterns (
    id SERIAL PRIMARY KEY,
    pattern_type TEXT NOT NULL,
    description TEXT NOT NULL,
    occurrences INTEGER DEFAULT 1,
    success_rate FLOAT DEFAULT 0.0,
    examples JSONB DEFAULT '[]'::jsonb,
    confidence FLOAT DEFAULT 0.0
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
