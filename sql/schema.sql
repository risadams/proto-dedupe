-- Database Schema for Tarball Deduplication System
-- Version: 1.0.0
-- Date: 2025-10-06

-- TarballRecord table
CREATE TABLE TarballRecord (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    hostname VARCHAR(100) NOT NULL,
    file_size BIGINT,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_files_count INTEGER DEFAULT 0,
    processing_duration INTERVAL,
    status VARCHAR(20) NOT NULL DEFAULT 'PROCESSING' 
        CHECK (status IN ('PROCESSING', 'SUCCESS', 'PARTIAL', 'FAILED')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FileRecord table
CREATE TABLE FileRecord (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tarball_id UUID NOT NULL REFERENCES TarballRecord(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size >= 0),
    checksum VARCHAR(64) NOT NULL,
    hash_algorithm VARCHAR(10) NOT NULL 
        CHECK (hash_algorithm IN ('sha256', 'sha1', 'md5')),
    file_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_duplicate BOOLEAN DEFAULT FALSE
);

-- DuplicateGroup table
CREATE TABLE DuplicateGroup (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checksum VARCHAR(64) NOT NULL UNIQUE,
    hash_algorithm VARCHAR(10) NOT NULL,
    file_count INTEGER DEFAULT 0 CHECK (file_count >= 0),
    first_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_size_saved BIGINT DEFAULT 0 CHECK (total_size_saved >= 0)
);

-- ProcessingLog table
CREATE TABLE ProcessingLog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(50) NOT NULL,
    tarball_id UUID REFERENCES TarballRecord(id) ON DELETE SET NULL,
    log_level VARCHAR(10) NOT NULL CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR')),
    message TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX idx_filerecord_checksum ON FileRecord(checksum, hash_algorithm);
CREATE INDEX idx_duplicategroup_checksum ON DuplicateGroup(checksum);
CREATE INDEX idx_filerecord_tarball_id ON FileRecord(tarball_id);
CREATE INDEX idx_tarballrecord_hostname ON TarballRecord(hostname);
CREATE INDEX idx_tarballrecord_processed_at ON TarballRecord(processed_at);
CREATE INDEX idx_filerecord_filename ON FileRecord(filename);
CREATE INDEX idx_filerecord_duplicate_lookup ON FileRecord(checksum, hash_algorithm, tarball_id);
CREATE INDEX idx_processinglog_operation_time ON ProcessingLog(operation_type, timestamp);