"""Duplicate detection service for dedupe-tarball.

This module provides duplicate file detection functionality using checksums
and manages duplicate group tracking.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict

from ..models.duplicate_group import DuplicateGroup
from ..models.file_record import FileRecord

logger = logging.getLogger(__name__)


class DuplicateService:
    """Service for detecting and managing duplicate files."""
    
    def __init__(self):
        """Initialize the duplicate detection service."""
        self._duplicate_groups: Dict[str, DuplicateGroup] = {}
        self._checksum_to_group: Dict[str, str] = {}
        
    def process_file_for_duplicates(self, 
                                  checksum: str, 
                                  hash_algorithm: str, 
                                  file_size: int) -> DuplicateGroup:
        """Process a file for duplicate detection.
        
        Args:
            checksum: File checksum
            hash_algorithm: Algorithm used for checksum
            file_size: Size of the file in bytes
            
        Returns:
            DuplicateGroup that the file belongs to
        """
        if not checksum or not checksum.strip():
            raise ValueError("checksum cannot be empty")
        
        if not hash_algorithm or not hash_algorithm.strip():
            raise ValueError("hash_algorithm cannot be empty")
        
        if file_size < 0:
            raise ValueError("file_size cannot be negative")
        
        checksum = checksum.strip().lower()
        hash_algorithm = hash_algorithm.strip().lower()
        
        # Check if we already have a group for this checksum
        if checksum in self._checksum_to_group:
            group_id = self._checksum_to_group[checksum]
            group = self._duplicate_groups[group_id]
            
            # Update group statistics
            group.file_count += 1
            group.total_size_saved = (group.file_count - 1) * file_size
            
            logger.debug(f"Added duplicate to existing group {group_id}: "
                        f"file_count={group.file_count}, "
                        f"total_size_saved={group.total_size_saved}")
            
            return group
        
        # Create new duplicate group
        group = DuplicateGroup(
            checksum=checksum,
            hash_algorithm=hash_algorithm,
            file_count=1,
            total_size_saved=0
        )
        
        # Store in our tracking dictionaries
        self._duplicate_groups[group.id] = group
        self._checksum_to_group[checksum] = group.id
        
        logger.debug(f"Created new duplicate group {group.id} for checksum {checksum[:16]}...")
        
        return group
    
    def find_duplicates_by_checksum(self, checksum: str) -> List[DuplicateGroup]:
        """Find duplicate groups by checksum.
        
        Args:
            checksum: Checksum to search for
            
        Returns:
            List of DuplicateGroup objects (empty if no duplicates found)
        """
        if not checksum or not checksum.strip():
            return []
        
        checksum = checksum.strip().lower()
        
        if checksum in self._checksum_to_group:
            group_id = self._checksum_to_group[checksum]
            group = self._duplicate_groups[group_id]
            
            # Only return if it's actually a duplicate (more than 1 file)
            if group.file_count > 1:
                return [group]
        
        return []
    
    def find_all_duplicates(self) -> List[DuplicateGroup]:
        """Find all duplicate groups with more than one file.
        
        Returns:
            List of DuplicateGroup objects with file_count > 1
        """
        duplicates = []
        for group in self._duplicate_groups.values():
            if group.file_count > 1:
                duplicates.append(group)
        
        return duplicates
    
    def get_duplicate_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected duplicates.
        
        Returns:
            Dictionary with duplicate statistics
        """
        total_groups = len(self._duplicate_groups)
        duplicate_groups = len([g for g in self._duplicate_groups.values() 
                              if g.file_count > 1])
        total_files = sum(g.file_count for g in self._duplicate_groups.values())
        total_size_saved = sum(g.total_size_saved for g in self._duplicate_groups.values())
        
        # Calculate average duplicates per group
        avg_duplicates = 0
        if duplicate_groups > 0:
            duplicate_files = sum(g.file_count for g in self._duplicate_groups.values() 
                                if g.file_count > 1)
            avg_duplicates = duplicate_files / duplicate_groups
        
        return {
            'total_groups': total_groups,
            'duplicate_groups': duplicate_groups,
            'unique_groups': total_groups - duplicate_groups,
            'total_files_processed': total_files,
            'total_size_saved_bytes': total_size_saved,
            'average_duplicates_per_group': round(avg_duplicates, 2)
        }
    
    def process_file_records(self, file_records: List[FileRecord]) -> List[DuplicateGroup]:
        """Process multiple file records for duplicate detection.
        
        Args:
            file_records: List of FileRecord objects to process
            
        Returns:
            List of DuplicateGroup objects that were updated
        """
        updated_groups = []
        
        for file_record in file_records:
            if not file_record.checksum:
                logger.warning(f"Skipping file record {file_record.id} - no checksum")
                continue
            
            group = self.process_file_for_duplicates(
                checksum=file_record.checksum,
                hash_algorithm=file_record.hash_algorithm,
                file_size=file_record.file_size
            )
            
            # Track which groups were updated
            if group not in updated_groups:
                updated_groups.append(group)
        
        return updated_groups
    
    def find_duplicates_by_algorithm(self, hash_algorithm: str) -> List[DuplicateGroup]:
        """Find duplicate groups using a specific hash algorithm.
        
        Args:
            hash_algorithm: Hash algorithm to filter by
            
        Returns:
            List of DuplicateGroup objects using the specified algorithm
        """
        if not hash_algorithm or not hash_algorithm.strip():
            return []
        
        hash_algorithm = hash_algorithm.strip().lower()
        duplicates = []
        
        for group in self._duplicate_groups.values():
            if (group.hash_algorithm == hash_algorithm and 
                group.file_count > 1):
                duplicates.append(group)
        
        return duplicates
    
    def mark_group_processed(self, group_id: str) -> bool:
        """Mark a duplicate group as processed.
        
        Args:
            group_id: ID of the group to mark as processed
            
        Returns:
            True if group was found and marked, False otherwise
        """
        if group_id in self._duplicate_groups:
            # Note: DuplicateGroup model doesn't have status field
            # This method is kept for API compatibility but doesn't do anything
            logger.info(f"Marked duplicate group {group_id} as processed")
            return True
        
        logger.warning(f"Duplicate group {group_id} not found")
        return False
    
    def remove_group(self, group_id: str) -> bool:
        """Remove a duplicate group from tracking.
        
        Args:
            group_id: ID of the group to remove
            
        Returns:
            True if group was found and removed, False otherwise
        """
        if group_id not in self._duplicate_groups:
            logger.warning(f"Duplicate group {group_id} not found")
            return False
        
        group = self._duplicate_groups[group_id]
        
        # Remove from checksum mapping
        if group.checksum in self._checksum_to_group:
            del self._checksum_to_group[group.checksum]
        
        # Remove from groups
        del self._duplicate_groups[group_id]
        
        logger.info(f"Removed duplicate group {group_id}")
        return True
    
    def get_group_by_id(self, group_id: str) -> Optional[DuplicateGroup]:
        """Get a duplicate group by ID.
        
        Args:
            group_id: ID of the group to retrieve
            
        Returns:
            DuplicateGroup object or None if not found
        """
        return self._duplicate_groups.get(group_id)
    
    def clear_all_groups(self) -> None:
        """Clear all duplicate groups and reset tracking."""
        self._duplicate_groups.clear()
        self._checksum_to_group.clear()
        logger.info("Cleared all duplicate groups")
    
    def merge_groups(self, target_group_id: str, source_group_id: str) -> bool:
        """Merge two duplicate groups.
        
        Args:
            target_group_id: ID of the group to merge into
            source_group_id: ID of the group to merge from (will be removed)
            
        Returns:
            True if merge was successful, False otherwise
        """
        if (target_group_id not in self._duplicate_groups or 
            source_group_id not in self._duplicate_groups):
            logger.error(f"Cannot merge groups - one or both not found: "
                        f"{target_group_id}, {source_group_id}")
            return False
        
        target_group = self._duplicate_groups[target_group_id]
        source_group = self._duplicate_groups[source_group_id]
        
        # Verify groups can be merged (same checksum)
        if target_group.checksum != source_group.checksum:
            logger.error(f"Cannot merge groups with different checksums: "
                        f"{target_group.checksum} != {source_group.checksum}")
            return False
        
        # Merge counts
        target_group.file_count += source_group.file_count
        target_group.total_size_saved = (target_group.file_count - 1) * \
                                       (target_group.total_size_saved // max(target_group.file_count - source_group.file_count - 1, 1))
        
        # Remove source group
        self.remove_group(source_group_id)
        
        logger.info(f"Merged duplicate group {source_group_id} into {target_group_id}")
        return True
    
    def find_duplicate_candidates(self, 
                                min_file_size: int = 0,
                                max_file_size: Optional[int] = None) -> List[DuplicateGroup]:
        """Find duplicate groups within specified file size range.
        
        Args:
            min_file_size: Minimum file size to consider
            max_file_size: Maximum file size to consider (None for no limit)
            
        Returns:
            List of DuplicateGroup objects matching criteria
        """
        candidates = []
        
        for group in self._duplicate_groups.values():
            if group.file_count <= 1:
                continue
            
            # Estimate file size from total_size_saved
            if group.file_count > 1:
                estimated_file_size = group.total_size_saved // (group.file_count - 1)
                
                if estimated_file_size < min_file_size:
                    continue
                
                if max_file_size is not None and estimated_file_size > max_file_size:
                    continue
                
                candidates.append(group)
        
        return candidates