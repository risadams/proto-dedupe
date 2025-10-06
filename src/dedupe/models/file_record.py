"""FileRecord model for dedupe-tarball.

This module provides the FileRecord model which represents a file
within a processed tarball.
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class FileRecord:
    """Model representing a file record within a tarball.
    
    Attributes:
        id (str): UUID primary key
        tarball_id (str): Foreign key to TarballRecord
        filename (str): Path to the file within the tarball
        file_size (int): Size of the file in bytes
        checksum (str): Checksum/hash of the file
        hash_algorithm (str): Algorithm used for checksum
        file_timestamp (Optional[datetime]): Original timestamp of the file
        is_duplicate (bool): Whether this file is a duplicate
        created_at (datetime): When the record was created
        updated_at (datetime): When the record was last updated
    """
    
    def __init__(self, 
                 tarball_id: str,
                 filename: str, 
                 file_size: int,
                 checksum: str,
                 hash_algorithm: str,
                 id: Optional[str] = None,
                 file_timestamp: Optional[datetime] = None,
                 is_duplicate: bool = False,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        """Initialize a FileRecord.
        
        Args:
            tarball_id: Foreign key to TarballRecord
            filename: Path to the file within the tarball
            file_size: Size of the file in bytes
            checksum: Checksum/hash of the file
            hash_algorithm: Algorithm used for checksum
            id: UUID string (auto-generated if not provided)
            file_timestamp: Original timestamp of the file
            is_duplicate: Whether this file is a duplicate
            created_at: Creation timestamp (auto-generated if not provided)
            updated_at: Update timestamp (auto-generated if not provided)
            
        Raises:
            ValueError: If required fields are invalid
        """
        # Validate required fields
        if not tarball_id or not tarball_id.strip():
            raise ValueError("tarball_id cannot be empty")
        
        # Validate tarball_id as UUID
        try:
            uuid.UUID(tarball_id.strip())
        except ValueError:
            raise ValueError("tarball_id must be a valid UUID")
        
        if not filename or not filename.strip():
            raise ValueError("filename cannot be empty")
        
        if file_size < 0:
            raise ValueError("file_size cannot be negative")
        
        if not checksum or not checksum.strip():
            raise ValueError("checksum cannot be empty")
        
        if not hash_algorithm or not hash_algorithm.strip():
            raise ValueError("hash_algorithm cannot be empty")
        
        # Validate field lengths (500 chars max for filename as per test)
        if len(filename.strip()) > 500:
            raise ValueError("filename too long (max 500 characters)")
        
        if len(checksum.strip()) > 128:
            raise ValueError("checksum too long (max 128 characters)")
        
        if len(hash_algorithm.strip()) > 50:
            raise ValueError("hash_algorithm too long (max 50 characters)")
        
        # Validate hash algorithm
        valid_algorithms = {'md5', 'sha1', 'sha256', 'sha512'}
        if hash_algorithm.lower() not in valid_algorithms:
            raise ValueError(f"hash_algorithm must be one of: {', '.join(valid_algorithms)}")
        
        # Set attributes
        self.id = id or str(uuid.uuid4())
        self.tarball_id = tarball_id.strip()
        self.filename = filename.strip()
        self.file_size = file_size
        self.checksum = checksum.strip()
        self.hash_algorithm = hash_algorithm.strip()
        self.file_timestamp = file_timestamp
        self.is_duplicate = is_duplicate
        
        now = datetime.now(timezone.utc)
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        
        # Initialize relationship (placeholder for ORM)
        self.tarball = None
        self.duplicate_group = None
    
    def __str__(self) -> str:
        """String representation of the record."""
        return f"FileRecord(id={self.id[:8]}..., filename={self.filename}, size={self.file_size}, checksum={self.checksum[:8]}...)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the record."""
        return (f"FileRecord(id='{self.id}', tarball_id='{self.tarball_id}', "
                f"filename='{self.filename}', file_size={self.file_size}, "
                f"checksum='{self.checksum}', hash_algorithm='{self.hash_algorithm}')")
    
    def __eq__(self, other) -> bool:
        """Test equality based on content, not ID."""
        if not isinstance(other, FileRecord):
            return False
        return (self.tarball_id == other.tarball_id and
                self.filename == other.filename and
                self.file_size == other.file_size and
                self.checksum == other.checksum and
                self.hash_algorithm == other.hash_algorithm)
    
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
            'tarball_id': self.tarball_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'checksum': self.checksum,
            'hash_algorithm': self.hash_algorithm,
            'file_timestamp': self.file_timestamp.isoformat() if self.file_timestamp else None,
            'is_duplicate': self.is_duplicate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileRecord':
        """Create record from dictionary.
        
        Args:
            data: Dictionary containing record data
            
        Returns:
            FileRecord instance
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
        
        file_timestamp = None
        if data.get('file_timestamp'):
            if isinstance(data['file_timestamp'], str):
                file_timestamp = datetime.fromisoformat(data['file_timestamp'].replace('Z', '+00:00'))
            else:
                file_timestamp = data['file_timestamp']
        
        return cls(
            id=data.get('id'),
            tarball_id=data['tarball_id'],
            filename=data['filename'],
            file_size=data['file_size'],
            checksum=data['checksum'],
            hash_algorithm=data['hash_algorithm'],
            file_timestamp=file_timestamp,
            is_duplicate=data.get('is_duplicate', False),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def mark_as_duplicate(self) -> None:
        """Mark this file as a duplicate."""
        self.is_duplicate = True
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_as_unique(self) -> None:
        """Mark this file as unique (not a duplicate)."""
        self.is_duplicate = False
        self.updated_at = datetime.now(timezone.utc)
    
    def update_checksum(self, checksum: str, hash_algorithm: str) -> None:
        """Update the file checksum and algorithm.
        
        Args:
            checksum: New checksum value
            hash_algorithm: New hash algorithm
            
        Raises:
            ValueError: If checksum or hash_algorithm is invalid
        """
        if not checksum or not checksum.strip():
            raise ValueError("checksum cannot be empty")
        
        if not hash_algorithm or not hash_algorithm.strip():
            raise ValueError("hash_algorithm cannot be empty")
        
        # Validate hash algorithm
        valid_algorithms = {'md5', 'sha1', 'sha256', 'sha512'}
        if hash_algorithm.lower() not in valid_algorithms:
            raise ValueError(f"hash_algorithm must be one of: {', '.join(valid_algorithms)}")
        
        self.checksum = checksum.strip()
        self.hash_algorithm = hash_algorithm.strip()
        self.updated_at = datetime.now(timezone.utc)