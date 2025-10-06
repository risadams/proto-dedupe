"""Tarball service for dedupe-tarball.

This module provides tarball processing functionality including extraction,
file analysis, and metadata collection.
"""

import tarfile
import os
import tempfile
from typing import List, Optional, Dict, Any, BinaryIO
from pathlib import Path
import logging
from datetime import datetime, timezone

from ..models.tarball_record import TarballRecord, TarballStatus
from ..models.file_record import FileRecord
from .hash_service import HashService

logger = logging.getLogger(__name__)


class TarballService:
    """Service for processing tarball files and extracting metadata."""
    
    def __init__(self, hash_service: Optional[HashService] = None):
        """Initialize the tarball service.
        
        Args:
            hash_service: Hash service instance (creates new one if not provided)
        """
        self.hash_service = hash_service or HashService()
        self._extracted_files: Dict[str, List[FileRecord]] = {}
    
    def validate_tarball(self, file_path: str) -> bool:
        """Validate that a file is a valid tarball.
        
        Args:
            file_path: Path to the tarball file
            
        Returns:
            True if valid tarball, False otherwise
        """
        try:
            with tarfile.open(file_path, 'r:*') as tar:
                # Try to list members to validate structure
                tar.getnames()
                return True
        except (tarfile.TarError, OSError) as e:
            logger.warning(f"Invalid tarball {file_path}: {e}")
            return False
    
    def get_tarball_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic information about a tarball.
        
        Args:
            file_path: Path to the tarball file
            
        Returns:
            Dictionary with tarball information
            
        Raises:
            tarfile.TarError: If tarball is invalid
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tarball file not found: {file_path}")
        
        try:
            file_size = os.path.getsize(file_path)
            
            with tarfile.open(file_path, 'r:*') as tar:
                members = tar.getmembers()
                
                # Count files vs directories
                files = [m for m in members if m.isfile()]
                directories = [m for m in members if m.isdir()]
                
                # Calculate total uncompressed size
                total_size = sum(m.size for m in files)
                
                return {
                    'file_path': file_path,
                    'file_size': file_size,
                    'total_files': len(files),
                    'total_directories': len(directories),
                    'total_uncompressed_size': total_size,
                    'compression_ratio': (file_size / total_size) if total_size > 0 else 0,
                    'members': len(members)
                }
                
        except tarfile.TarError as e:
            logger.error(f"Error reading tarball {file_path}: {e}")
            raise
    
    def process_tarball(self, 
                       file_path: str, 
                       hostname: str,
                       hash_algorithm: str = 'sha256') -> TarballRecord:
        """Process a tarball file and extract metadata.
        
        Args:
            file_path: Path to the tarball file
            hostname: Hostname where processing is occurring
            hash_algorithm: Hash algorithm to use for checksums
            
        Returns:
            TarballRecord with processing results
            
        Raises:
            FileNotFoundError: If tarball file doesn't exist
            tarfile.TarError: If tarball is invalid
        """
        start_time = datetime.now(timezone.utc)
        
        # Validate inputs
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tarball file not found: {file_path}")
        
        if not hostname or not hostname.strip():
            raise ValueError("hostname cannot be empty")
        
        logger.info(f"Starting tarball processing: {file_path}")
        
        try:
            # Get basic file info
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            
            # Create tarball record
            tarball_record = TarballRecord(
                filename=filename,
                hostname=hostname.strip(),
                file_size=file_size,
                status=TarballStatus.PROCESSING
            )
            
            # Extract and process files
            file_records = self._extract_and_analyze_files(
                file_path, tarball_record.id, hash_algorithm
            )
            
            # Update tarball record with results
            tarball_record.total_files_count = len(file_records)
            tarball_record.status = TarballStatus.SUCCESS
            
            # Calculate processing duration
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            tarball_record.set_processing_duration(int(duration))
            
            # Store extracted files for retrieval
            self._extracted_files[tarball_record.id] = file_records
            
            logger.info(f"Successfully processed tarball: {file_path}, "
                       f"files: {len(file_records)}, duration: {duration:.2f}s")
            
            return tarball_record
            
        except Exception as e:
            logger.error(f"Error processing tarball {file_path}: {e}")
            
            # Create failed record
            tarball_record = TarballRecord(
                filename=os.path.basename(file_path),
                hostname=hostname.strip(),
                file_size=file_size if 'file_size' in locals() else 0,
                status=TarballStatus.FAILED,
                error_message=str(e)
            )
            
            # Calculate processing duration even for failures
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            tarball_record.set_processing_duration(int(duration))
            
            raise
    
    def _extract_and_analyze_files(self, 
                                 tarball_path: str, 
                                 tarball_id: str,
                                 hash_algorithm: str) -> List[FileRecord]:
        """Extract files from tarball and analyze them.
        
        Args:
            tarball_path: Path to the tarball
            tarball_id: ID of the tarball record
            hash_algorithm: Hash algorithm to use
            
        Returns:
            List of FileRecord objects
        """
        file_records = []
        
        with tarfile.open(tarball_path, 'r:*') as tar:
            for member in tar.getmembers():
                # Skip directories, links, and other non-regular files
                if not member.isfile():
                    continue
                
                try:
                    # Extract file content
                    file_obj = tar.extractfile(member)
                    if file_obj is None:
                        logger.warning(f"Could not extract file: {member.name}")
                        continue
                    
                    # Calculate checksum
                    checksum = self.hash_service.calculate_checksum(
                        file_obj, hash_algorithm
                    )
                    
                    # Get file timestamp (use member modification time if available)
                    file_timestamp = None
                    if hasattr(member, 'mtime') and member.mtime:
                        file_timestamp = datetime.fromtimestamp(
                            member.mtime, tz=timezone.utc
                        )
                    
                    # Create file record
                    file_record = FileRecord(
                        tarball_id=tarball_id,
                        filename=member.name,
                        file_size=member.size,
                        checksum=checksum,
                        hash_algorithm=hash_algorithm,
                        file_timestamp=file_timestamp
                    )
                    
                    file_records.append(file_record)
                    
                    logger.debug(f"Processed file: {member.name}, "
                               f"size: {member.size}, checksum: {checksum[:16]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing file {member.name}: {e}")
                    # Continue processing other files
                    continue
        
        return file_records
    
    def get_extracted_files(self, tarball_id: str) -> List[FileRecord]:
        """Get the list of extracted files for a tarball.
        
        Args:
            tarball_id: ID of the tarball record
            
        Returns:
            List of FileRecord objects
        """
        return self._extracted_files.get(tarball_id, [])
    
    def clear_extracted_files(self, tarball_id: str) -> None:
        """Clear extracted files data for a tarball to free memory.
        
        Args:
            tarball_id: ID of the tarball record
        """
        if tarball_id in self._extracted_files:
            del self._extracted_files[tarball_id]
    
    def extract_file_to_temp(self, 
                            tarball_path: str, 
                            file_path: str) -> str:
        """Extract a specific file from tarball to temporary location.
        
        Args:
            tarball_path: Path to the tarball
            file_path: Path of file within tarball
            
        Returns:
            Path to extracted temporary file
            
        Raises:
            FileNotFoundError: If tarball or file not found
            tarfile.TarError: If extraction fails
        """
        with tarfile.open(tarball_path, 'r:*') as tar:
            try:
                member = tar.getmember(file_path)
                if not member.isfile():
                    raise ValueError(f"Not a regular file: {file_path}")
                
                # Extract to temporary file
                file_obj = tar.extractfile(member)
                if file_obj is None:
                    raise ValueError(f"Could not extract file: {file_path}")
                
                # Create temporary file
                temp_fd, temp_path = tempfile.mkstemp()
                try:
                    with os.fdopen(temp_fd, 'wb') as temp_file:
                        temp_file.write(file_obj.read())
                    return temp_path
                except:
                    # Clean up on error
                    os.unlink(temp_path)
                    raise
                    
            except KeyError:
                raise FileNotFoundError(f"File not found in tarball: {file_path}")
    
    def list_files(self, tarball_path: str) -> List[Dict[str, Any]]:
        """List all files in a tarball with their metadata.
        
        Args:
            tarball_path: Path to the tarball
            
        Returns:
            List of file information dictionaries
        """
        files = []
        
        with tarfile.open(tarball_path, 'r:*') as tar:
            for member in tar.getmembers():
                if member.isfile():
                    files.append({
                        'name': member.name,
                        'size': member.size,
                        'mtime': member.mtime,
                        'mode': member.mode,
                        'uid': member.uid,
                        'gid': member.gid,
                        'type': 'file'
                    })
                elif member.isdir():
                    files.append({
                        'name': member.name,
                        'size': 0,
                        'mtime': member.mtime,
                        'mode': member.mode,
                        'uid': member.uid,
                        'gid': member.gid,
                        'type': 'directory'
                    })
        
        return files