#!/usr/bin/env python3
"""Unit tests for ProcessingLog model.

This test validates that the ProcessingLog model meets all requirements.
It MUST FAIL initially as no implementation exists.
"""

import pytest
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any


class TestProcessingLogModel:
    """Test ProcessingLog model implementation."""

    def test_processing_log_model_exists(self):
        """Test that ProcessingLog model can be imported."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        assert ProcessingLog is not None

    def test_processing_log_creation_required_fields(self):
        """Test ProcessingLog creation with required fields."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        # Data model: Required fields
        log = ProcessingLog(
            operation_type="PROCESS_TARBALL",
            log_level="INFO",
            message="Processing tarball completed successfully"
        )
        
        assert log.operation_type == "PROCESS_TARBALL"
        assert log.log_level == "INFO"
        assert log.message == "Processing tarball completed successfully"
        assert log.tarball_id is None  # Optional field

    def test_processing_log_all_fields(self):
        """Test ProcessingLog with all fields."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        # Data model: All attributes
        tarball_id = str(uuid.uuid4())
        details = {"files_processed": 100, "errors": 0, "duration_seconds": 45.3}
        timestamp = datetime(2025, 10, 6, 14, 30, 0)
        
        log = ProcessingLog(
            operation_type="DETECT_DUPLICATES",
            tarball_id=tarball_id,
            log_level="INFO",
            message="Duplicate detection completed",
            details=details,
            timestamp=timestamp
        )
        
        assert log.operation_type == "DETECT_DUPLICATES"
        assert log.tarball_id == tarball_id
        assert log.log_level == "INFO"
        assert log.message == "Duplicate detection completed"
        assert log.details == details
        assert log.timestamp == timestamp

    def test_processing_log_id_generation(self):
        """Test that UUID id is generated."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        log = ProcessingLog(
            operation_type="TEST",
            log_level="DEBUG",
            message="Test message"
        )
        
        # Data model: id (UUID, Primary Key)
        assert hasattr(log, 'id'), "ProcessingLog must have id field"
        assert isinstance(log.id, (str, uuid.UUID)), "ID must be UUID type"

    def test_processing_log_operation_type_validation(self):
        """Test operation_type field validation."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        # Data model: operation_type (VARCHAR(50), NOT NULL)
        valid_operations = [
            "PROCESS_TARBALL",
            "DETECT_DUPLICATES", 
            "QUERY_FILES",
            "CLEANUP_OLD_RECORDS",
            "DATABASE_MAINTENANCE"
        ]
        
        # Valid operations should work
        for operation in valid_operations:
            log = ProcessingLog(
                operation_type=operation,
                log_level="INFO",
                message="Test message"
            )
            assert log.operation_type == operation
        
        # Empty operation type should raise error
        with pytest.raises(ValueError):
            ProcessingLog(
                operation_type="",
                log_level="INFO",
                message="Test message"
            )
        
        # None operation type should raise error
        with pytest.raises(ValueError):
            ProcessingLog(
                operation_type=None,
                log_level="INFO",
                message="Test message"
            )
        
        # Operation type too long should raise error (>50 chars)
        long_operation = "a" * 51
        with pytest.raises(ValueError):
            ProcessingLog(
                operation_type=long_operation,
                log_level="INFO",
                message="Test message"
            )

    def test_processing_log_level_validation(self):
        """Test log_level field validation."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        # Data model: log_level (VARCHAR(10), NOT NULL) - Must be valid log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        # Valid levels should work
        for level in valid_levels:
            log = ProcessingLog(
                operation_type="TEST",
                log_level=level,
                message="Test message"
            )
            assert log.log_level == level
        
        # Invalid level should raise error
        with pytest.raises(ValueError):
            ProcessingLog(
                operation_type="TEST",
                log_level="INVALID_LEVEL",
                message="Test message"
            )
        
        # Empty level should raise error
        with pytest.raises(ValueError):
            ProcessingLog(
                operation_type="TEST",
                log_level="",
                message="Test message"
            )

    def test_processing_log_message_validation(self):
        """Test message field validation."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        # Data model: message (TEXT, NOT NULL)
        
        # Valid message
        log = ProcessingLog(
            operation_type="TEST",
            log_level="INFO",
            message="This is a test log message"
        )
        assert log.message == "This is a test log message"
        
        # Long message should be valid (TEXT field)
        long_message = "a" * 1000
        log = ProcessingLog(
            operation_type="TEST",
            log_level="INFO",
            message=long_message
        )
        assert log.message == long_message
        
        # Empty message should raise error
        with pytest.raises(ValueError):
            ProcessingLog(
                operation_type="TEST",
                log_level="INFO",
                message=""
            )
        
        # None message should raise error
        with pytest.raises(ValueError):
            ProcessingLog(
                operation_type="TEST",
                log_level="INFO",
                message=None
            )

    def test_processing_log_tarball_id_validation(self):
        """Test tarball_id foreign key validation."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        # Data model: tarball_id (UUID, Foreign Key → TarballRecord.id, NULLABLE)
        
        # None tarball_id should be valid (nullable)
        log = ProcessingLog(
            operation_type="CLEANUP",
            log_level="INFO",
            message="Cleanup operation",
            tarball_id=None
        )
        assert log.tarball_id is None
        
        # Valid UUID should work
        valid_uuid = str(uuid.uuid4())
        log = ProcessingLog(
            operation_type="PROCESS_TARBALL",
            log_level="INFO",
            message="Processing tarball",
            tarball_id=valid_uuid
        )
        assert log.tarball_id == valid_uuid
        
        # Invalid UUID format should raise error
        with pytest.raises(ValueError):
            ProcessingLog(
                operation_type="TEST",
                log_level="INFO",
                message="Test message",
                tarball_id="not-a-uuid"
            )

    def test_processing_log_details_json_field(self):
        """Test details JSONB field."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        # Data model: details (JSONB) - Additional structured data
        
        # None details should be valid
        log = ProcessingLog(
            operation_type="TEST",
            log_level="INFO",
            message="Test message",
            details=None
        )
        assert log.details is None
        
        # Dictionary details should work
        details = {
            "files_processed": 150,
            "errors": 2,
            "warnings": 5,
            "duration_ms": 45000,
            "memory_usage_mb": 128
        }
        log = ProcessingLog(
            operation_type="PROCESS_TARBALL",
            log_level="INFO",
            message="Processing completed with warnings",
            details=details
        )
        assert log.details == details
        
        # Nested details should work
        nested_details = {
            "summary": {
                "total_files": 100,
                "duplicates_found": 25
            },
            "errors": [
                {"file": "corrupted.log", "error": "Cannot read file"},
                {"file": "large.log", "error": "File too large"}
            ]
        }
        log = ProcessingLog(
            operation_type="DETECT_DUPLICATES",
            log_level="WARNING",
            message="Duplicate detection completed with errors",
            details=nested_details
        )
        assert log.details == nested_details

    def test_processing_log_timestamp_default(self):
        """Test timestamp field default value."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        # Data model: timestamp (TIMESTAMP, DEFAULT NOW())
        log = ProcessingLog(
            operation_type="TEST",
            log_level="INFO",
            message="Test message"
        )
        
        # Should have timestamp field with default value
        assert hasattr(log, 'timestamp'), "Must have timestamp field"
        assert isinstance(log.timestamp, datetime)
        
        # Should be close to current time (within 1 minute)
        now = datetime.now()
        time_diff = abs((log.timestamp - now).total_seconds())
        assert time_diff < 60, "Timestamp should be close to current time"

    def test_processing_log_custom_timestamp(self):
        """Test setting custom timestamp."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        custom_time = datetime(2025, 10, 6, 12, 0, 0)
        log = ProcessingLog(
            operation_type="TEST",
            log_level="INFO",
            message="Test message",
            timestamp=custom_time
        )
        
        assert log.timestamp == custom_time

    def test_processing_log_relationships(self):
        """Test model relationships."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        tarball_id = str(uuid.uuid4())
        log = ProcessingLog(
            operation_type="PROCESS_TARBALL",
            log_level="INFO",
            message="Processing tarball",
            tarball_id=tarball_id
        )
        
        # Data model: Many-to-One with TarballRecord
        assert hasattr(log, 'tarball'), "Must have tarball relationship"

    def test_processing_log_string_representation(self):
        """Test string representation."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        log = ProcessingLog(
            operation_type="PROCESS_TARBALL",
            log_level="ERROR",
            message="Failed to process tarball"
        )
        
        # Should have meaningful string representation
        str_repr = str(log)
        assert "ERROR" in str_repr
        assert "PROCESS_TARBALL" in str_repr or "Failed to process" in str_repr

    def test_processing_log_equality(self):
        """Test record equality comparison."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        timestamp = datetime(2025, 10, 6, 12, 0, 0)
        
        log1 = ProcessingLog(
            operation_type="TEST",
            log_level="INFO",
            message="Test message",
            timestamp=timestamp
        )
        
        log2 = ProcessingLog(
            operation_type="TEST",
            log_level="INFO",
            message="Test message",
            timestamp=timestamp
        )
        
        # Logs with same data should be equal
        assert log1 == log2
        
        # Logs with different message should not be equal
        log3 = ProcessingLog(
            operation_type="TEST",
            log_level="INFO",
            message="Different message",
            timestamp=timestamp
        )
        assert log1 != log3

    def test_processing_log_to_dict(self):
        """Test conversion to dictionary."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        details = {"files": 100, "errors": 0}
        log = ProcessingLog(
            operation_type="PROCESS_TARBALL",
            log_level="INFO",
            message="Processing completed",
            details=details
        )
        
        # Should be able to convert to dict
        data = log.to_dict()
        assert isinstance(data, dict)
        assert data['operation_type'] == "PROCESS_TARBALL"
        assert data['log_level'] == "INFO"
        assert data['message'] == "Processing completed"
        assert data['details'] == details

    def test_processing_log_from_dict(self):
        """Test creation from dictionary."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        data = {
            'operation_type': 'QUERY_FILES',
            'log_level': 'DEBUG',
            'message': 'Query executed successfully',
            'details': {'query_time_ms': 150, 'results_count': 25}
        }
        
        # Should be able to create from dict
        log = ProcessingLog.from_dict(data)
        assert log.operation_type == data['operation_type']
        assert log.log_level == data['log_level']
        assert log.message == data['message']
        assert log.details == data['details']

    def test_processing_log_severity_ordering(self):
        """Test log level severity ordering."""
        # This will fail until model is implemented
        from dedupe.models.processing_log import ProcessingLog
        
        debug_log = ProcessingLog(
            operation_type="TEST",
            log_level="DEBUG",
            message="Debug message"
        )
        
        error_log = ProcessingLog(
            operation_type="TEST",
            log_level="ERROR",
            message="Error message"
        )
        
        # Should be able to compare severity
        assert debug_log.get_severity_level() < error_log.get_severity_level()
        assert error_log.is_more_severe_than(debug_log)