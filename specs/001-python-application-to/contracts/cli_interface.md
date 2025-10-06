# CLI Interface Contract

## Command Line Interface Specification

### Main Command Structure
```bash
dedupe-tarball [COMMAND] [OPTIONS] [ARGUMENTS]
```

### Available Commands

#### process
Process tarball files and detect duplicates
```bash
dedupe-tarball process [OPTIONS] TARBALL_PATH

Options:
  --hostname TEXT        Source hostname (required)
  --hash-algorithm TEXT  Hash algorithm: sha256, sha1, md5 [default: sha256]
  --batch-size INTEGER   Database batch size [default: 100]
  --progress            Show progress bar
  --dry-run             Analyze without writing to database
  --help                Show help message

Examples:
  dedupe-tarball process --hostname server01 /path/to/logs.tar.gz
  dedupe-tarball process --hostname server02 --hash-algorithm md5 --progress /logs/*.tar
```

#### query
Query duplicate files and generate reports
```bash
dedupe-tarball query [OPTIONS]

Options:
  --hostname TEXT       Filter by hostname
  --since DATE         Show files processed since date (YYYY-MM-DD)
  --duplicates-only    Show only duplicate files
  --format TEXT        Output format: table, json, csv [default: table]
  --output FILE        Write output to file
  --stats              Show summary statistics
  --help               Show help message

Examples:
  dedupe-tarball query --duplicates-only
  dedupe-tarball query --hostname server01 --since 2025-10-01
  dedupe-tarball query --stats --format json --output report.json
```

#### cleanup
Remove old records and optimize database
```bash
dedupe-tarball cleanup [OPTIONS]

Options:
  --older-than INTEGER  Remove records older than N days
  --dry-run            Show what would be deleted without deleting
  --vacuum             Run database vacuum after cleanup
  --help               Show help message

Examples:
  dedupe-tarball cleanup --older-than 365 --dry-run
  dedupe-tarball cleanup --older-than 90 --vacuum
```

### Global Options
```bash
Global Options:
  --config FILE         Configuration file path [default: ~/.dedupe/config.toml]
  --db-url TEXT         Database connection string
  --log-level TEXT      Logging level: debug, info, warning, error [default: info]
  --log-file FILE       Log file path
  --version             Show version and exit
  --help                Show help message
```

### Configuration File Format
```toml
[database]
url = "postgresql://user:password@localhost:5432/dedupe"
pool_size = 10
timeout = 30

[processing]
default_hash_algorithm = "sha256"
batch_size = 100
chunk_size = 8192

[logging]
level = "info"
file = "/var/log/dedupe-tarball.log"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Exit Codes
- 0: Success
- 1: General error
- 2: Command line usage error
- 3: Database connection error
- 4: File processing error
- 5: Configuration error

### Output Formats

#### Table Format (Default)
```
Hostname    | Tarball File    | Duplicates | Space Saved
server01    | logs-2025-10-06.tar.gz | 15 | 1.2 GB
server02    | logs-2025-10-06.tar.gz | 8  | 0.8 GB
```

#### JSON Format
```json
{
  "summary": {
    "total_files": 1234,
    "duplicate_files": 567,
    "space_saved_bytes": 1073741824
  },
  "duplicates": [
    {
      "checksum": "abc123...",
      "file_count": 3,
      "files": [
        {
          "hostname": "server01",
          "tarball": "logs-2025-10-06.tar.gz",
          "filename": "app.log",
          "size": 1024
        }
      ]
    }
  ]
}
```

#### CSV Format
```csv
hostname,tarball,filename,checksum,size,is_duplicate
server01,logs-2025-10-06.tar.gz,app.log,abc123...,1024,true
```

### Error Handling
- Invalid arguments: Show usage help and exit with code 2
- Database errors: Show detailed error message and exit with code 3
- File not found: Show file path and exit with code 4
- Permission errors: Show permission details and exit with code 4
- Interrupted processing: Clean up partial state and exit gracefully

### Progress Reporting
When --progress flag is used:
- Show progress bar with percentage completion
- Display current file being processed
- Show processing rate (files/second)
- Estimate time remaining
- Update every 100 files processed or every 5 seconds