# Data Model: Tarball Deduplication System

## Entity Relationships

### Core Entities

#### TarballRecord
**Purpose**: Tracks each processed tarball file
**Attributes**:
- id (UUID, Primary Key)
- filename (VARCHAR(255), NOT NULL) - Original tarball filename
- hostname (VARCHAR(100), NOT NULL) - Source server hostname
- file_size (BIGINT) - Size of tarball in bytes
- processed_at (TIMESTAMP, NOT NULL) - When processing completed
- total_files_count (INTEGER) - Number of files extracted
- processing_duration (INTERVAL) - Time taken to process
- status (VARCHAR(20)) - SUCCESS, FAILED, PARTIAL
- error_message (TEXT) - Error details if processing failed

**Relationships**:
- One-to-Many with FileRecord (one tarball contains many files)

#### FileRecord
**Purpose**: Represents individual files found within tarballs
**Attributes**:
- id (UUID, Primary Key)
- tarball_id (UUID, Foreign Key → TarballRecord.id)
- filename (VARCHAR(500), NOT NULL) - Path within tarball
- file_size (BIGINT, NOT NULL) - Size in bytes
- checksum (VARCHAR(64), NOT NULL) - SHA256 hash (or other algorithm)
- hash_algorithm (VARCHAR(10), NOT NULL) - Algorithm used (sha256, md5, etc.)
- file_timestamp (TIMESTAMP) - Original file modification time
- created_at (TIMESTAMP, DEFAULT NOW()) - When record was created
- is_duplicate (BOOLEAN, DEFAULT FALSE) - Cached duplicate status

**Relationships**:
- Many-to-One with TarballRecord (many files belong to one tarball)
- Many-to-Many with DuplicateGroup through membership

#### DuplicateGroup
**Purpose**: Groups files with identical content (same checksum)
**Attributes**:
- id (UUID, Primary Key)
- checksum (VARCHAR(64), NOT NULL, UNIQUE) - Shared checksum of all files in group
- hash_algorithm (VARCHAR(10), NOT NULL) - Algorithm used
- file_count (INTEGER, DEFAULT 0) - Number of duplicate files
- first_seen_at (TIMESTAMP, NOT NULL) - When first file with this checksum was processed
- last_seen_at (TIMESTAMP, NOT NULL) - When most recent duplicate was found
- total_size_saved (BIGINT, DEFAULT 0) - Potential space savings

**Relationships**:
- One-to-Many with FileRecord (one group contains many duplicate files)

#### ProcessingLog
**Purpose**: Audit trail of system activities and errors
**Attributes**:
- id (UUID, Primary Key)
- operation_type (VARCHAR(50), NOT NULL) - PROCESS_TARBALL, DETECT_DUPLICATES, etc.
- tarball_id (UUID, Foreign Key → TarballRecord.id, NULLABLE)
- log_level (VARCHAR(10), NOT NULL) - INFO, WARNING, ERROR
- message (TEXT, NOT NULL) - Log message
- details (JSONB) - Additional structured data
- timestamp (TIMESTAMP, DEFAULT NOW())

**Relationships**:
- Many-to-One with TarballRecord (many logs can reference one tarball)

## Database Schema

### Indexes for Performance
```sql
-- Primary indexes for duplicate detection
CREATE INDEX idx_filerecord_checksum ON FileRecord(checksum, hash_algorithm);
CREATE INDEX idx_duplicategroup_checksum ON DuplicateGroup(checksum);

-- Indexes for common queries
CREATE INDEX idx_filerecord_tarball_id ON FileRecord(tarball_id);
CREATE INDEX idx_tarballrecord_hostname ON TarballRecord(hostname);
CREATE INDEX idx_tarballrecord_processed_at ON TarballRecord(processed_at);
CREATE INDEX idx_filerecord_filename ON FileRecord(filename);

-- Composite indexes for reporting
CREATE INDEX idx_filerecord_duplicate_lookup ON FileRecord(checksum, hash_algorithm, tarball_id);
CREATE INDEX idx_processinglog_operation_time ON ProcessingLog(operation_type, timestamp);
```

### Data Validation Rules
- Checksum format validation based on hash_algorithm
- File size must be non-negative
- Timestamps cannot be in the future
- Hash algorithm must be from approved list (sha256, sha1, md5)

### State Transitions

#### TarballRecord Status Flow
1. **PROCESSING** → Initial state when tarball processing starts
2. **SUCCESS** → All files processed successfully
3. **PARTIAL** → Some files processed, some failed
4. **FAILED** → Processing completely failed

#### Duplicate Detection Flow
1. New file processed → Check checksum against DuplicateGroup
2. If checksum exists → Add to existing group, mark as duplicate
3. If checksum new → Create new DuplicateGroup, mark as original
4. Update group statistics (file_count, last_seen_at, total_size_saved)

## Query Patterns

### Common Duplicate Queries
```sql
-- Find all duplicate files
SELECT f1.filename, f1.tarball_id, t1.hostname, f1.file_size
FROM FileRecord f1
JOIN DuplicateGroup dg ON f1.checksum = dg.checksum
JOIN TarballRecord t1 ON f1.tarball_id = t1.id
WHERE dg.file_count > 1;

-- Calculate space savings by hostname
SELECT t.hostname, 
       SUM(f.file_size * (dg.file_count - 1)) as space_savings
FROM FileRecord f
JOIN DuplicateGroup dg ON f.checksum = dg.checksum
JOIN TarballRecord t ON f.tarball_id = t.id
WHERE dg.file_count > 1
GROUP BY t.hostname;
```

### Performance Considerations
- Use EXPLAIN ANALYZE for query optimization
- Consider partitioning FileRecord by processed_at for large datasets
- Implement archive strategy for old ProcessingLog entries
- Monitor index usage and size growth