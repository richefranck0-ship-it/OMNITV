-- Migration 002: Live Streaming
CREATE TABLE IF NOT EXISTS live_streams (
    id VARCHAR(64) PRIMARY KEY,
    creator_name VARCHAR(255) NOT NULL,
    stream_title VARCHAR(255) NOT NULL,
    stream_url TEXT NOT NULL,
    is_vertical BOOLEAN DEFAULT TRUE,
    is_camera_feed BOOLEAN DEFAULT FALSE,
    viewer_count INTEGER DEFAULT 1500,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
