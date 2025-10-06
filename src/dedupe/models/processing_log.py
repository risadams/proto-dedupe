"""ProcessingLog model for dedupe-tarball.

This module provides the ProcessingLog model which represents a log entry
for operations performed by the system.
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json


class ProcessingLog:
    """Model representing a processing log entry.
    
    Attributes:
        id (str): UUID primary key
        operation_type (str): Type of operation being logged
        tarball_id (Optional[str]): Foreign key to TarballRecord (optional)
        log_level (str): Log level (DEBUG, INFO, WARNING, ERROR)
        message (str): Log message
        details (Optional[Dict[str, Any]]): Additional details as JSON
        timestamp (datetime): When the log entry was created
    """
    
    def __init__(self, 
                 operation_type: str,
                 log_level: str,
                 message: str,
                 id: Optional[str] = None,
                 tarball_id: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None,
                 timestamp: Optional[datetime] = None):
        """Initialize a ProcessingLog.
        
        Args:
            operation_type: Type of operation being logged
            log_level: Log level (DEBUG, INFO, WARNING, ERROR)
            message: Log message
            id: UUID string (auto-generated if not provided)
            tarball_id: Foreign key to TarballRecord (optional)
            details: Additional details as JSON
            timestamp: When the log entry was created (auto-generated if not provided)
            
        Raises:
            ValueError: If required fields are invalid
        """
        # Validate required fields
        if not operation_type or not operation_type.strip():
            raise ValueError("operation_type cannot be empty")
        
        if not log_level or not log_level.strip():
            raise ValueError("log_level cannot be empty")
        
        if not message or not message.strip():
            raise ValueError("message cannot be empty")
        
        # Validate field lengths
        if len(operation_type.strip()) > 50:
            raise ValueError("operation_type too long (max 50 characters)")
        
        if len(log_level.strip()) > 20:
            raise ValueError("log_level too long (max 20 characters)")
        
        if len(message.strip()) > 2000:
            raise ValueError("message too long (max 2000 characters)")
        
        # Validate log level
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR'}
        if log_level.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of: {', '.join(valid_levels)}")
        
        # Validate operation type (basic validation)
        valid_operations = {
            'PROCESS_TARBALL', 'DETECT_DUPLICATES', 'CLEANUP', 'QUERY',
            'SCHEMA_MIGRATION', 'BACKUP', 'RESTORE', 'TEST'
        }
        if operation_type.upper() not in valid_operations:
            # Allow any operation type for flexibility, just warn
            pass
        
        # Set attributes
        self.id = id or str(uuid.uuid4())
        self.operation_type = operation_type.strip().upper()
        self.tarball_id = tarball_id.strip() if tarball_id else None
        self.log_level = log_level.strip().upper()
        self.message = message.strip()
        self.details = details.copy() if details else None
        self.timestamp = timestamp or datetime.now(timezone.utc)
    
    def __str__(self) -> str:
        """String representation of the record."""
        return f"ProcessingLog(id={self.id[:8]}..., level={self.log_level}, operation={self.operation_type})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the record."""
        return (f"ProcessingLog(id='{self.id}', operation_type='{self.operation_type}', "
                f"log_level='{self.log_level}', message='{self.message[:50]}...')")
    
    def __eq__(self, other) -> bool:
        """Test equality based on ID."""
        if not isinstance(other, ProcessingLog):
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
            'operation_type': self.operation_type,
            'tarball_id': self.tarball_id,
            'log_level': self.log_level,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingLog':
        """Create record from dictionary.
        
        Args:
            data: Dictionary containing record data
            
        Returns:
            ProcessingLog instance
        """
        # Parse timestamp
        timestamp = None
        if data.get('timestamp'):
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            else:
                timestamp = data['timestamp']
        
        return cls(
            id=data.get('id'),
            operation_type=data['operation_type'],
            tarball_id=data.get('tarball_id'),
            log_level=data['log_level'],
            message=data['message'],
            details=data.get('details'),
            timestamp=timestamp
        )
    
    def add_detail(self, key: str, value: Any) -> None:
        """Add a detail to the log entry.
        
        Args:
            key: Detail key
            value: Detail value
        """
        if self.details is None:
            self.details = {}
        self.details[key] = value
    
    def get_detail(self, key: str, default: Any = None) -> Any:
        """Get a detail from the log entry.
        
        Args:
            key: Detail key
            default: Default value if key not found
            
        Returns:
            Detail value or default
        """
        if self.details is None:
            return default
        return self.details.get(key, default)
    
    def is_error(self) -> bool:
        """Check if this is an error log.
        
        Returns:
            True if log_level is ERROR
        """
        return self.log_level == 'ERROR'
    
    def is_warning(self) -> bool:
        """Check if this is a warning log.
        
        Returns:
            True if log_level is WARNING
        """
        return self.log_level == 'WARNING'
    
    def get_severity_level(self) -> int:
        """Get numeric severity level for ordering.
        
        Returns:
            Numeric severity (higher = more severe)
        """
        levels = {
            'DEBUG': 1,
            'INFO': 2,
            'WARNING': 3,
            'ERROR': 4
        }
        return levels.get(self.log_level, 0)
    
    def format_message(self) -> str:
        """Format the log message with timestamp and level.
        
        Returns:
            Formatted log message
        """
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') if self.timestamp else 'Unknown'
        return f"[{timestamp_str}] {self.log_level}: {self.message}"