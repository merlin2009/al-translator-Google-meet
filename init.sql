-- Database initialization script
-- This script creates the necessary tables for the translation service

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS translation_service;

-- Use the database
\c translation_service;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create tables
CREATE TABLE IF NOT EXISTS translation_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    source_language VARCHAR(10) DEFAULT 'en',
    target_language VARCHAR(10) DEFAULT 'ru',
    platform VARCHAR(50),
    user_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS translation_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    original_text TEXT,
    translated_text TEXT,
    source_language VARCHAR(10),
    target_language VARCHAR(10),
    confidence INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    preferred_languages TEXT,
    auto_translate BOOLEAN DEFAULT TRUE,
    voice_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_translation_sessions_session_id ON translation_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_translation_sessions_user_id ON translation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_translation_sessions_platform ON translation_sessions(platform);
CREATE INDEX IF NOT EXISTS idx_translation_sessions_active ON translation_sessions(is_active);

CREATE INDEX IF NOT EXISTS idx_translation_history_session_id ON translation_history(session_id);
CREATE INDEX IF NOT EXISTS idx_translation_history_timestamp ON translation_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_translation_history_languages ON translation_history(source_language, target_language);

CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_translation_sessions_updated_at 
    BEFORE UPDATE ON translation_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at 
    BEFORE UPDATE ON user_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default data
INSERT INTO user_settings (user_id, preferred_languages, auto_translate, voice_enabled) 
VALUES ('default', '["en", "ru", "es", "fr", "de"]', TRUE, TRUE)
ON CONFLICT (user_id) DO NOTHING;

-- Create views for analytics
CREATE OR REPLACE VIEW translation_stats AS
SELECT 
    DATE(timestamp) as date,
    source_language,
    target_language,
    COUNT(*) as translation_count,
    AVG(confidence) as avg_confidence
FROM translation_history
GROUP BY DATE(timestamp), source_language, target_language
ORDER BY date DESC;

CREATE OR REPLACE VIEW active_sessions AS
SELECT 
    s.session_id,
    s.source_language,
    s.target_language,
    s.platform,
    s.user_id,
    s.created_at,
    COUNT(h.id) as translation_count
FROM translation_sessions s
LEFT JOIN translation_history h ON s.session_id = h.session_id
WHERE s.is_active = TRUE
GROUP BY s.session_id, s.source_language, s.target_language, s.platform, s.user_id, s.created_at;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE translation_service TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;