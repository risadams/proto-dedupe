"""Main CLI module for dedupe-tarball.

This module provides the command-line interface for the dedupe-tarball application.
It supports processing tarballs and querying for duplicates.
"""

import argparse
import sys
import json
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from ..services.tarball_service import TarballService
from ..services.duplicate_service import DuplicateService
from ..services.database_service import DatabaseService
from ..services.hash_service import HashService

# Global service instances
_tarball_service = None
_duplicate_service = None
_database_service = None
_hash_service = None

def get_services():
    """Get or initialize service instances."""
    global _tarball_service, _duplicate_service, _database_service, _hash_service
    
    if _hash_service is None:
        _hash_service = HashService()
    if _tarball_service is None:
        _tarball_service = TarballService(_hash_service)
    if _duplicate_service is None:
        _duplicate_service = DuplicateService()
    if _database_service is None:
        _database_service = DatabaseService()
    
    return _tarball_service, _duplicate_service, _database_service, _hash_service


def setup_logging(level: str = 'INFO'):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def process_command(args: argparse.Namespace) -> int:
    """Handle the 'process' command."""
    tarball_service, duplicate_service, database_service, _ = get_services()
    
    if not args.hostname:
        print("Error: --hostname is required for process command", file=sys.stderr)
        return 1
    
    if not args.files:
        print("Error: At least one tarball file is required", file=sys.stderr)
        return 1
    
    success_count = 0
    total_files = 0
    
    for tarball_path in args.files:
        if not os.path.exists(tarball_path):
            print(f"Error: File not found: {tarball_path}", file=sys.stderr)
            continue
        
        try:
            print(f"Processing {tarball_path}...")
            
            # Process the tarball
            tarball_record = tarball_service.process_tarball(tarball_path, args.hostname)
            file_records = tarball_service.get_extracted_files(tarball_record.id)
            
            if not args.dry_run:
                # Save to database
                database_service.save_tarball_record(tarball_record)
                database_service.save_file_records(file_records)
                
                # Process for duplicates
                duplicate_groups = duplicate_service.process_file_records(file_records)
                
                # Save duplicate groups
                for group in duplicate_groups:
                    database_service.save_duplicate_group(group)
            
            success_count += 1
            total_files += len(file_records)
            
            print(f"✅ Processed {tarball_record.filename}: {len(file_records)} files")
            
            if args.dry_run:
                print(f"   (Dry run - no data saved)")
            
            # Clean up memory
            tarball_service.clear_extracted_files(tarball_record.id)
            
        except Exception as e:
            print(f"❌ Error processing {tarball_path}: {e}", file=sys.stderr)
            continue
    
    print(f"\nProcessing complete: {success_count} tarballs, {total_files} files total")
    return 0 if success_count > 0 else 1


def query_command(args: argparse.Namespace) -> int:
    """Handle the 'query' command."""
    _, duplicate_service, database_service, _ = get_services()
    
    try:
        if args.stats:
            # Show statistics
            stats = duplicate_service.get_duplicate_statistics()
            db_stats = database_service.get_statistics()
            
            combined_stats = {
                'duplicate_statistics': stats,
                'database_statistics': db_stats,
                'query_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            if args.format == 'json':
                print(json.dumps(combined_stats, indent=2))
            else:
                print("=== Duplicate Detection Statistics ===")
                print(f"Total groups: {stats['total_groups']}")
                print(f"Duplicate groups: {stats['duplicate_groups']}")
                print(f"Total files processed: {stats['total_files_processed']}")
                print(f"Total size saved: {stats['total_size_saved_bytes']} bytes")
                print(f"Average duplicates per group: {stats['average_duplicates_per_group']}")
                
                print("\n=== Database Statistics ===")
                print(f"Tarball records: {db_stats['tarball_records']}")
                print(f"File records: {db_stats['file_records']}")
                print(f"Duplicate files: {db_stats['duplicate_files']}")
                print(f"Unique hostnames: {db_stats['unique_hostnames']}")
            
            return 0
        
        # Query for duplicates
        duplicates = []
        
        if args.duplicates_only:
            duplicates = duplicate_service.find_all_duplicates()
        else:
            # Get all file records
            if args.hostname:
                file_records = database_service.get_file_records_by_hostname(args.hostname)
            else:
                # Get all tarballs and their files
                all_tarballs = database_service.get_tarball_records()
                file_records = []
                for tarball in all_tarballs:
                    file_records.extend(database_service.get_file_records(tarball.id))
            
            # Filter by date if specified
            if args.since:
                since_date = datetime.fromisoformat(args.since.replace('Z', '+00:00'))
                file_records = [f for f in file_records 
                              if f.created_at and f.created_at >= since_date]
            
            # Convert to output format
            if args.duplicates_only:
                # Only show duplicates
                duplicate_checksums = {g.checksum for g in duplicate_service.find_all_duplicates()}
                file_records = [f for f in file_records 
                              if f.checksum in duplicate_checksums]
        
        # Format output
        if args.format == 'json':
            if args.duplicates_only:
                output = []
                for group in duplicates:
                    output.append({
                        'checksum': group.checksum,
                        'file_count': group.file_count,
                        'total_size_saved': group.total_size_saved,
                        'hash_algorithm': group.hash_algorithm
                    })
                print(json.dumps(output, indent=2))
            else:
                output = []
                for record in file_records:
                    output.append({
                        'filename': record.filename,
                        'size': record.file_size,
                        'checksum': record.checksum,
                        'tarball_id': record.tarball_id
                    })
                print(json.dumps(output, indent=2))
        
        elif args.format == 'csv':
            if args.duplicates_only:
                print("checksum,file_count,total_size_saved,hash_algorithm")
                for group in duplicates:
                    print(f"{group.checksum},{group.file_count},{group.total_size_saved},{group.hash_algorithm}")
            else:
                print("filename,size,checksum,tarball_id")
                for record in file_records:
                    print(f"{record.filename},{record.file_size},{record.checksum},{record.tarball_id}")
        
        else:  # table format (default)
            if args.duplicates_only:
                if duplicates:
                    print("Found duplicate groups:")
                    print(f"{'Checksum':<16} {'Files':<6} {'Saved (bytes)':<12} {'Algorithm':<10}")
                    print("-" * 50)
                    for group in duplicates:
                        print(f"{group.checksum[:16]:<16} {group.file_count:<6} {group.total_size_saved:<12} {group.hash_algorithm:<10}")
                else:
                    print("No duplicate files found.")
            else:
                if file_records:
                    print(f"Found {len(file_records)} files:")
                    print(f"{'Filename':<30} {'Size':<10} {'Checksum':<16}")
                    print("-" * 60)
                    for record in file_records:
                        print(f"{record.filename[:30]:<30} {record.file_size:<10} {record.checksum[:16]:<16}")
                else:
                    print("No files found matching criteria.")
        
        return 0
        
    except Exception as e:
        print(f"Error querying data: {e}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog='dedupe-tarball',
        description='Dedupe-tarball: Detect duplicate files across tarball archives'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process tarball files')
    process_parser.add_argument(
        '--hostname',
        required=True,
        help='Hostname where tarballs originated'
    )
    process_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Analyze without saving to database'
    )
    process_parser.add_argument(
        'files',
        nargs='+',
        help='Tarball files to process'
    )
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query for duplicates')
    query_parser.add_argument(
        '--duplicates-only',
        action='store_true',
        help='Show only duplicate files'
    )
    query_parser.add_argument(
        '--hostname',
        help='Filter by hostname'
    )
    query_parser.add_argument(
        '--since',
        help='Show files processed since date (ISO format)'
    )
    query_parser.add_argument(
        '--format',
        choices=['table', 'json', 'csv'],
        default='table',
        help='Output format'
    )
    query_parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics instead of file listings'
    )
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    if argv is None:
        argv = sys.argv[1:]
    
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Set up logging
    setup_logging(args.log_level)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'process':
            return process_command(args)
        elif args.command == 'query':
            return query_command(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())