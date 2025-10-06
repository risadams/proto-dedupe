"""TarballRecord model for dedupe-tarball.

This module provides the TarballRecord model which represents a tarball file
that has been processed by the system.
"""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum


class TarballStatus(Enum):
    """Enumeration of tarball processing statuses."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TarballRecord:
    """Model representing a tarball file record.
    
    Attributes:
        id (str): UUID primary key
        filename (str): Full path to the tarball file
        hostname (str): Hostname where the tarball was processed
        status (TarballStatus): Processing status
        file_size (int): Size of the tarball file in bytes
        created_at (datetime): When the record was created
        updated_at (datetime): When the record was last updated
        processing_duration (Optional[int]): Processing time in seconds
        total_files_count (Optional[int]): Number of files in the tarball
        error_message (Optional[str]): Error message if processing failed
    """
    
    def __init__(self, 
                 filename: str, 
                 hostname: str, 
                 file_size: int = 0,
                 status: TarballStatus = TarballStatus.PROCESSING,
                 id: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 processing_duration: Optional[int] = None,
                 total_files_count: Optional[int] = None,
                 error_message: Optional[str] = None):
        """Initialize a TarballRecord.
        
        Args:
            filename: Full path to the tarball file
            hostname: Hostname where tarball was processed
            file_size: Size of the tarball file in bytes
            status: Processing status (defaults to PENDING)
            id: UUID string (auto-generated if not provided)
            created_at: Creation timestamp (auto-generated if not provided)
            updated_at: Update timestamp (auto-generated if not provided)
            processing_duration: Processing time in seconds
            total_files_count: Number of files in the tarball
            error_message: Error message if processing failed
            
        Raises:
            ValueError: If required fields are invalid
        """
        # Validate required fields
        if not filename or not filename.strip():
            raise ValueError("filename cannot be empty")
        
        if not hostname or not hostname.strip():
            raise ValueError("hostname cannot be empty")
        
        if file_size < 0:
            raise ValueError("file_size cannot be negative")
        
        # Validate filename format (basic check for reasonable paths)
        if len(filename.strip()) > 1000:
            raise ValueError("filename too long (max 1000 characters)")
        
        # Validate hostname format (basic check)
        if len(hostname.strip()) > 255:
            raise ValueError("hostname too long (max 255 characters)")
        
        # Set attributes
        self.id = id or str(uuid.uuid4())
        self.filename = filename.strip()
        self.hostname = hostname.strip()
        self._status = status if isinstance(status, TarballStatus) else TarballStatus(status)
        self.file_size = file_size
        
        now = datetime.now(timezone.utc)
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self.processing_duration = processing_duration
        
        # Validate processing_duration
        if self.processing_duration is not None and self.processing_duration < 0:
            raise ValueError("processing_duration cannot be negative")
        
        # Validate total_files_count
        if total_files_count is not None and total_files_count < 0:
            raise ValueError("total_files_count cannot be negative")
        
        # Set additional fields
        self.total_files_count = total_files_count
        self.error_message = error_message
    
    @property
    def status(self) -> str:
        """Get the status as a string."""
        return self._status.value
    
    @status.setter
    def status(self, value) -> None:
        """Set the status from string or enum."""
        if isinstance(value, str):
            self._status = TarballStatus(value)
        elif isinstance(value, TarballStatus):
            self._status = value
        else:
            raise ValueError(f"Invalid status type: {type(value)}")
    
    def __str__(self) -> str:
        """String representation of the record."""
        return f"TarballRecord(id={self.id[:8]}..., filename={self.filename}, status={self.status})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the record."""
        return (f"TarballRecord(id='{self.id}', filename='{self.filename}', "
                f"hostname='{self.hostname}', status='{self.status}', "
                f"file_size={self.file_size})")
    
    def __eq__(self, other) -> bool:
        """Test equality based on ID."""
        if not isinstance(other, TarballRecord):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary.
        
        Returns:
            Dictionary representation of the record
        """
        return {
            'id': self.id,
            'filename': self.filename,
            'hostname': self.hostname,
            'status': self.status,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processing_duration': self.processing_duration,
            'total_files_count': self.total_files_count,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TarballRecord':
        """Create record from dictionary.
        
        Args:
            data: Dictionary containing record data
            
        Returns:
            TarballRecord instance
        """
        # Parse timestamps
        created_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        updated_at = None
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            else:
                updated_at = data['updated_at']
        
        # Parse status
        status = data.get('status', 'PROCESSING')
        
        return cls(
            id=data.get('id'),
            filename=data['filename'],
            hostname=data['hostname'],
            file_size=data['file_size'],
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            processing_duration=data.get('processing_duration'),
            total_files_count=data.get('total_files_count'),
            error_message=data.get('error_message')
        )
    
    def update_status(self, status: str) -> None:
        """Update the record status and timestamp.
        
        Args:
            status: New status value
        """
        self.status = status
        self.updated_at = datetime.now(timezone.utc)
    
    def set_processing_duration(self, duration: int) -> None:
        """Set the processing duration.
        
        Args:
            duration: Processing time in seconds
            
        Raises:
            ValueError: If duration is negative
        """
        if duration < 0:
            raise ValueError("processing_duration cannot be negative")
        self.processing_duration = duration
        self.updated_at = datetime.now(timezone.utc)
    
    def is_completed(self) -> bool:
        """Check if processing is completed.
        
        Returns:
            True if status is COMPLETED
        """
        return self._status == TarballStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if processing failed.
        
        Returns:
            True if status is FAILED
        """
        return self._status == TarballStatus.FAILED
    
    def is_processing(self) -> bool:
        """Check if currently processing.
        
        Returns:
            True if status is PROCESSING
        """
        return self._status == TarballStatus.PROCESSING