-- Migration 003: Advertisements (HLS & MP4)
CREATE TABLE IF NOT EXISTS advertisements (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    advertiser_name VARCHAR(255) NOT NULL,
    media_type VARCHAR(20) NOT NULL DEFAULT 'video',
    video_url TEXT,
    destination_url TEXT NOT NULL,
    display_interval_seconds INTEGER DEFAULT 180,
    duration_seconds INTEGER DEFAULT 15,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
