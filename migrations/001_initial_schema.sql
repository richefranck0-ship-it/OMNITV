-- Migration 001: Initial Schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS channels (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL DEFAULT 'Généraliste',
    stream_url TEXT NOT NULL,
    logo_url TEXT NOT NULL,
    description TEXT,
    viewer_count INTEGER DEFAULT 1200,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS videos (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    video_url TEXT NOT NULL,
    poster_url TEXT NOT NULL,
    duration_minutes INTEGER DEFAULT 90,
    release_year INTEGER DEFAULT 2024,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS schedules (
    id VARCHAR(64) PRIMARY KEY,
    channel_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    starts_at VARCHAR(10) NOT NULL,
    ends_at VARCHAR(10) NOT NULL,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
