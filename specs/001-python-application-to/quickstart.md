# Quickstart Guide: Tarball Deduplication System

## Prerequisites
- RHEL8 server with Python 3.12+ installed
- PostgreSQL 13+ database running
- Write access to tarball files directory
- Database connection privileges

## Quick Setup

### 1. Database Setup
```sql
-- Connect to PostgreSQL as admin user
CREATE DATABASE dedupe_db;
CREATE USER dedupe_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE dedupe_db TO dedupe_user;

-- Connect to dedupe_db and run schema
\c dedupe_db
-- (Run schema from contracts/database_schema.md)
```

### 2. Install Application
```bash
# In air-gapped environment, transfer files first
cd /opt/dedupe-tarball
pip install -r requirements.txt
python setup.py install

# Create configuration directory
mkdir -p ~/.dedupe
```

### 3. Configure Application
```bash
# Create config file
cat > ~/.dedupe/config.toml << EOF
[database]
url = "postgresql://dedupe_user:secure_password@localhost:5432/dedupe_db"
pool_size = 10

[processing]
default_hash_algorithm = "sha256"
batch_size = 100

[logging]
level = "info"
file = "/var/log/dedupe-tarball.log"
EOF
```

## Basic Usage Scenarios

### Scenario 1: Process Single Tarball
```bash
# Process a single tarball from server01
dedupe-tarball process --hostname server01 /logs/server01-2025-10-06.tar.gz

# Expected output:
# Processing /logs/server01-2025-10-06.tar.gz from server01...
# Extracted 1,234 files
# Found 45 duplicates
# Processing completed in 2m 15s
```

### Scenario 2: Process Multiple Tarballs with Progress
```bash
# Process all tarballs for server02 with progress bar
dedupe-tarball process --hostname server02 --progress /logs/server02-*.tar.gz

# Expected output:
# Processing server02-2025-10-01.tar.gz: 100% |████████| 1234/1234 [01:30<00:00, 13.7files/s]
# Processing server02-2025-10-02.tar.gz: 100% |████████| 1156/1156 [01:25<00:00, 13.5files/s]
# ...
# Total duplicates found: 156
# Total space savings: 2.3 GB
```

### Scenario 3: Query Duplicate Files
```bash
# Find all duplicate files
dedupe-tarball query --duplicates-only

# Expected output:
# Hostname | Tarball File           | Filename    | Duplicates | Size
# server01 | logs-2025-10-06.tar.gz | app.log     | 3          | 1.2 MB
# server01 | logs-2025-10-06.tar.gz | error.log   | 2          | 0.8 MB
# server02 | logs-2025-10-06.tar.gz | app.log     | 3          | 1.2 MB
```

### Scenario 4: Generate Space Savings Report
```bash
# Get space savings report in JSON format
dedupe-tarball query --stats --format json --output savings_report.json

# Expected JSON structure:
# {
#   "summary": {
#     "total_files": 12450,
#     "duplicate_files": 3456,
#     "space_saved_bytes": 5368709120,
#     "space_saved_human": "5.0 GB"
#   },
#   "by_hostname": {
#     "server01": {"duplicates": 1200, "saved_bytes": 2147483648},
#     "server02": {"duplicates": 1100, "saved_bytes": 1879048192}
#   }
# }
```

### Scenario 5: Analyze Without Database Changes
```bash
# Dry run to see what duplicates would be found
dedupe-tarball process --hostname server03 --dry-run /logs/server03-latest.tar.gz

# Expected output:
# DRY RUN: Processing /logs/server03-latest.tar.gz from server03...
# Would extract 987 files
# Would find 23 potential duplicates
# Estimated space savings: 0.5 GB
# No database changes made
```

## Integration Test Scenarios

### Test 1: Duplicate Detection Across Tarballs
```bash
# Process tarball A
dedupe-tarball process --hostname test-server logs-day1.tar.gz

# Process tarball B (contains some same files)
dedupe-tarball process --hostname test-server logs-day2.tar.gz

# Query duplicates
dedupe-tarball query --hostname test-server --duplicates-only

# Verify: Files present in both tarballs are marked as duplicates
```

### Test 2: Error Handling
```bash
# Test corrupted tarball
dedupe-tarball process --hostname test-server corrupted.tar.gz

# Expected: Error message, no partial database entries
# Exit code: 4
```

### Test 3: Performance Validation
```bash
# Test large tarball processing
time dedupe-tarball process --hostname perf-test --progress large-tarball.tar.gz

# Verify: Completes within reasonable time, memory usage stays reasonable
```

## Acceptance Criteria Validation

### Criterion 1: Extract and Calculate Checksums
```bash
# Verify files are extracted and checksums calculated
dedupe-tarball process --hostname acceptance-test sample.tar.gz
psql -d dedupe_db -c "SELECT filename, checksum FROM FileRecord WHERE tarball_id IN (SELECT id FROM TarballRecord WHERE hostname='acceptance-test');"
```

### Criterion 2: Duplicate Detection
```bash
# Process same tarball twice with different names
cp sample.tar.gz sample-copy.tar.gz
dedupe-tarball process --hostname acceptance-test sample-copy.tar.gz
dedupe-tarball query --hostname acceptance-test --duplicates-only
# Verify: All files marked as duplicates in second processing
```

### Criterion 3: Cross-Server Duplicate Tracking
```bash
# Process same files from different servers
dedupe-tarball process --hostname server-a shared-logs.tar.gz
dedupe-tarball process --hostname server-b shared-logs.tar.gz
dedupe-tarball query --duplicates-only
# Verify: Duplicates shown across both servers
```

### Criterion 4: Metadata Storage
```bash
# Verify all required metadata is stored
psql -d dedupe_db -c "SELECT tarball_id, filename, file_size, checksum, hash_algorithm, file_timestamp FROM FileRecord LIMIT 5;"
# Verify: All columns populated correctly
```

## Troubleshooting

### Database Connection Issues
```bash
# Test database connectivity
dedupe-tarball query --stats
# If fails: Check config.toml, PostgreSQL service, network connectivity
```

### Performance Issues
```bash
# Check database indexes
psql -d dedupe_db -c "\d+ FileRecord"
# Verify indexes exist on checksum, tarball_id columns
```

### Large File Processing
```bash
# Monitor memory usage during processing
dedupe-tarball process --hostname test --progress large-file.tar.gz &
PID=$!
while kill -0 $PID 2>/dev/null; do
    ps -o pid,vsz,rss,comm $PID
    sleep 5
done
# Verify: Memory usage stays within reasonable bounds
```