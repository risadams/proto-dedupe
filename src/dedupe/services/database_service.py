"""Database service for dedupe-tarball.

This module provides database operations and CRUD functionality
for all model types in the dedupe-tarball application.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from ..models.tarball_record import TarballRecord
from ..models.file_record import FileRecord
from ..models.duplicate_group import DuplicateGroup
from ..models.processing_log import ProcessingLog

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations and model management."""
    
    def __init__(self):
        """Initialize the database service."""
        # In-memory storage for development/testing
        # In production, this would connect to PostgreSQL
        self._tarball_records: Dict[str, TarballRecord] = {}
        self._file_records: Dict[str, FileRecord] = {}
        self._duplicate_groups: Dict[str, DuplicateGroup] = {}
        self._processing_logs: Dict[str, ProcessingLog] = {}
        
        # Indexes for efficient queries
        self._tarball_by_hostname: Dict[str, List[str]] = {}
        self._files_by_tarball: Dict[str, List[str]] = {}
        self._files_by_hostname: Dict[str, List[str]] = {}
        self._duplicates_by_checksum: Dict[str, str] = {}
    
    # TarballRecord operations
    def save_tarball_record(self, record: TarballRecord) -> TarballRecord:
        """Save a tarball record to the database.
        
        Args:
            record: TarballRecord to save
            
        Returns:
            The saved record
        """
        self._tarball_records[record.id] = record
        
        # Update hostname index
        if record.hostname not in self._tarball_by_hostname:
            self._tarball_by_hostname[record.hostname] = []
        if record.id not in self._tarball_by_hostname[record.hostname]:
            self._tarball_by_hostname[record.hostname].append(record.id)
        
        logger.debug(f"Saved tarball record {record.id} for hostname {record.hostname}")
        return record
    
    def get_tarball_record(self, record_id: str) -> Optional[TarballRecord]:
        """Get a tarball record by ID.
        
        Args:
            record_id: ID of the record to retrieve
            
        Returns:
            TarballRecord or None if not found
        """
        return self._tarball_records.get(record_id)
    
    def get_tarball_records(self, hostname: Optional[str] = None) -> List[TarballRecord]:
        """Get tarball records, optionally filtered by hostname.
        
        Args:
            hostname: Optional hostname to filter by
            
        Returns:
            List of TarballRecord objects
        """
        if hostname:
            record_ids = self._tarball_by_hostname.get(hostname, [])
            return [self._tarball_records[rid] for rid in record_ids 
                   if rid in self._tarball_records]
        
        return list(self._tarball_records.values())
    
    def delete_tarball_record(self, record_id: str) -> bool:
        """Delete a tarball record.
        
        Args:
            record_id: ID of the record to delete
            
        Returns:
            True if record was deleted, False if not found
        """
        if record_id not in self._tarball_records:
            return False
        
        record = self._tarball_records[record_id]
        
        # Remove from hostname index
        if record.hostname in self._tarball_by_hostname:
            if record_id in self._tarball_by_hostname[record.hostname]:
                self._tarball_by_hostname[record.hostname].remove(record_id)
            if not self._tarball_by_hostname[record.hostname]:
                del self._tarball_by_hostname[record.hostname]
        
        # Delete the record
        del self._tarball_records[record_id]
        
        logger.info(f"Deleted tarball record {record_id}")
        return True
    
    # FileRecord operations
    def save_file_record(self, record: FileRecord) -> FileRecord:
        """Save a file record to the database.
        
        Args:
            record: FileRecord to save
            
        Returns:
            The saved record
        """
        self._file_records[record.id] = record
        
        # Update tarball index
        if record.tarball_id not in self._files_by_tarball:
            self._files_by_tarball[record.tarball_id] = []
        if record.id not in self._files_by_tarball[record.tarball_id]:
            self._files_by_tarball[record.tarball_id].append(record.id)
        
        # Update hostname index (need to look up tarball for hostname)
        tarball = self.get_tarball_record(record.tarball_id)
        if tarball:
            if tarball.hostname not in self._files_by_hostname:
                self._files_by_hostname[tarball.hostname] = []
            if record.id not in self._files_by_hostname[tarball.hostname]:
                self._files_by_hostname[tarball.hostname].append(record.id)
        
        logger.debug(f"Saved file record {record.id} for tarball {record.tarball_id}")
        return record
    
    def save_file_records(self, records: List[FileRecord]) -> List[FileRecord]:
        """Save multiple file records to the database.
        
        Args:
            records: List of FileRecord objects to save
            
        Returns:
            List of saved records
        """
        saved_records = []
        for record in records:
            saved_records.append(self.save_file_record(record))
        
        logger.info(f"Saved {len(saved_records)} file records")
        return saved_records
    
    def get_file_record(self, record_id: str) -> Optional[FileRecord]:
        """Get a file record by ID.
        
        Args:
            record_id: ID of the record to retrieve
            
        Returns:
            FileRecord or None if not found
        """
        return self._file_records.get(record_id)
    
    def get_file_records(self, tarball_id: str) -> List[FileRecord]:
        """Get file records for a specific tarball.
        
        Args:
            tarball_id: ID of the tarball
            
        Returns:
            List of FileRecord objects
        """
        record_ids = self._files_by_tarball.get(tarball_id, [])
        return [self._file_records[rid] for rid in record_ids 
               if rid in self._file_records]
    
    def get_file_records_by_hostname(self, hostname: str) -> List[FileRecord]:
        """Get file records for a specific hostname.
        
        Args:
            hostname: Hostname to filter by
            
        Returns:
            List of FileRecord objects
        """
        record_ids = self._files_by_hostname.get(hostname, [])
        return [self._file_records[rid] for rid in record_ids 
               if rid in self._file_records]
    
    def delete_file_record(self, record_id: str) -> bool:
        """Delete a file record.
        
        Args:
            record_id: ID of the record to delete
            
        Returns:
            True if record was deleted, False if not found
        """
        if record_id not in self._file_records:
            return False
        
        record = self._file_records[record_id]
        
        # Remove from tarball index
        if record.tarball_id in self._files_by_tarball:
            if record_id in self._files_by_tarball[record.tarball_id]:
                self._files_by_tarball[record.tarball_id].remove(record_id)
        
        # Remove from hostname index
        tarball = self.get_tarball_record(record.tarball_id)
        if tarball and tarball.hostname in self._files_by_hostname:
            if record_id in self._files_by_hostname[tarball.hostname]:
                self._files_by_hostname[tarball.hostname].remove(record_id)
        
        # Delete the record
        del self._file_records[record_id]
        
        logger.info(f"Deleted file record {record_id}")
        return True
    
    # DuplicateGroup operations
    def save_duplicate_group(self, group: DuplicateGroup) -> DuplicateGroup:
        """Save a duplicate group to the database.
        
        Args:
            group: DuplicateGroup to save
            
        Returns:
            The saved group
        """
        self._duplicate_groups[group.id] = group
        
        # Update checksum index
        self._duplicates_by_checksum[group.checksum] = group.id
        
        logger.debug(f"Saved duplicate group {group.id} for checksum {group.checksum[:16]}...")
        return group
    
    def get_duplicate_group(self, group_id: str) -> Optional[DuplicateGroup]:
        """Get a duplicate group by ID.
        
        Args:
            group_id: ID of the group to retrieve
            
        Returns:
            DuplicateGroup or None if not found
        """
        return self._duplicate_groups.get(group_id)
    
    def get_duplicate_group_by_checksum(self, checksum: str) -> Optional[DuplicateGroup]:
        """Get a duplicate group by checksum.
        
        Args:
            checksum: Checksum to search for
            
        Returns:
            DuplicateGroup or None if not found
        """
        group_id = self._duplicates_by_checksum.get(checksum)
        if group_id:
            return self._duplicate_groups.get(group_id)
        return None
    
    def get_duplicate_files(self) -> List[DuplicateGroup]:
        """Get all duplicate groups with more than one file.
        
        Returns:
            List of DuplicateGroup objects representing duplicates
        """
        return [group for group in self._duplicate_groups.values() 
               if group.file_count > 1]
    
    def get_all_duplicate_groups(self) -> List[DuplicateGroup]:
        """Get all duplicate groups.
        
        Returns:
            List of all DuplicateGroup objects
        """
        return list(self._duplicate_groups.values())
    
    def delete_duplicate_group(self, group_id: str) -> bool:
        """Delete a duplicate group.
        
        Args:
            group_id: ID of the group to delete
            
        Returns:
            True if group was deleted, False if not found
        """
        if group_id not in self._duplicate_groups:
            return False
        
        group = self._duplicate_groups[group_id]
        
        # Remove from checksum index
        if group.checksum in self._duplicates_by_checksum:
            del self._duplicates_by_checksum[group.checksum]
        
        # Delete the group
        del self._duplicate_groups[group_id]
        
        logger.info(f"Deleted duplicate group {group_id}")
        return True
    
    # ProcessingLog operations
    def save_processing_log(self, log: ProcessingLog) -> ProcessingLog:
        """Save a processing log to the database.
        
        Args:
            log: ProcessingLog to save
            
        Returns:
            The saved log
        """
        self._processing_logs[log.id] = log
        
        logger.debug(f"Saved processing log {log.id} with level {log.log_level}")
        return log
    
    def get_processing_log(self, log_id: str) -> Optional[ProcessingLog]:
        """Get a processing log by ID.
        
        Args:
            log_id: ID of the log to retrieve
            
        Returns:
            ProcessingLog or None if not found
        """
        return self._processing_logs.get(log_id)
    
    def get_processing_logs(self, 
                          hostname: Optional[str] = None,
                          level: Optional[str] = None) -> List[ProcessingLog]:
        """Get processing logs, optionally filtered.
        
        Args:
            hostname: Optional hostname to filter by
            level: Optional log level to filter by
            
        Returns:
            List of ProcessingLog objects
        """
        logs = list(self._processing_logs.values())
        
        if hostname:
            logs = [log for log in logs if log.hostname == hostname]
        
        if level:
            logs = [log for log in logs if log.log_level == level.upper()]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return logs
    
    def delete_processing_log(self, log_id: str) -> bool:
        """Delete a processing log.
        
        Args:
            log_id: ID of the log to delete
            
        Returns:
            True if log was deleted, False if not found
        """
        if log_id not in self._processing_logs:
            return False
        
        del self._processing_logs[log_id]
        
        logger.info(f"Deleted processing log {log_id}")
        return True
    
    # Utility methods
    def clear_all_data(self) -> None:
        """Clear all data from the database service.
        
        Warning: This will delete all records!
        """
        self._tarball_records.clear()
        self._file_records.clear()
        self._duplicate_groups.clear()
        self._processing_logs.clear()
        
        self._tarball_by_hostname.clear()
        self._files_by_tarball.clear()
        self._files_by_hostname.clear()
        self._duplicates_by_checksum.clear()
        
        logger.warning("Cleared all database data")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        return {
            'tarball_records': len(self._tarball_records),
            'file_records': len(self._file_records),
            'duplicate_groups': len(self._duplicate_groups),
            'processing_logs': len(self._processing_logs),
            'unique_hostnames': len(self._tarball_by_hostname),
            'duplicate_files': len([g for g in self._duplicate_groups.values() 
                                  if g.file_count > 1])
        }
    
    # Batch operations
    def process_tarball_with_files(self, 
                                 tarball_record: TarballRecord,
                                 file_records: List[FileRecord]) -> None:
        """Process a tarball and its files in a single transaction.
        
        Args:
            tarball_record: TarballRecord to save
            file_records: List of FileRecord objects to save
        """
        # Save tarball record first
        self.save_tarball_record(tarball_record)
        
        # Save all file records
        self.save_file_records(file_records)
        
        logger.info(f"Processed tarball {tarball_record.id} with {len(file_records)} files")
    
    def find_files_by_checksum(self, checksum: str) -> List[FileRecord]:
        """Find all files with a specific checksum.
        
        Args:
            checksum: Checksum to search for
            
        Returns:
            List of FileRecord objects with matching checksum
        """
        matching_files = []
        for file_record in self._file_records.values():
            if file_record.checksum and file_record.checksum.lower() == checksum.lower():
                matching_files.append(file_record)
        
        return matching_files