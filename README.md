# Dedupe Tarball

A command-line tool for detecting and managing duplicate files in tarball archives.

## Overview

This application processes tarball archives to identify duplicate files across different archives and time periods. It maintains a PostgreSQL database to track file metadata and provides efficient querying capabilities for system administrators managing large collections of archived data.

## Features

- **Process**: Analyze tarball files and extract metadata
- **Query**: Search for duplicate files across archives  
- **Cleanup**: Generate reports for space optimization
- **Memory Efficient**: Process large archives without excessive memory usage
- **Air-Gapped**: Designed for offline/isolated environments

## Requirements

- Python 3.12 or later
- PostgreSQL database
- RHEL8 compatible environment

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Process a tarball
dedupe-tarball process /path/to/archive.tar.gz

# Query for duplicates
dedupe-tarball query --hash abc123...

# Generate cleanup report
dedupe-tarball cleanup --dry-run
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src/ tests/
flake8 src/ tests/
mypy src/
```

## License

MIT License