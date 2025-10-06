#!/usr/bin/env python3
"""Unit tests for FileRecord model.

This test validates that the FileRecord model meets all requirements.
It MUST FAIL initially as no implementation exists.
"""

import pytest
import uuid
from datetime import datetime
from typing import Optional


class TestFileRecordModel:
    """Test FileRecord model implementation."""

    def test_file_record_model_exists(self):
        """Test that FileRecord model can be imported."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        assert FileRecord is not None

    def test_file_record_creation_required_fields(self):
        """Test FileRecord creation with required fields."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        # Data model: Required fields
        tarball_id = str(uuid.uuid4())
        record = FileRecord(
            tarball_id=tarball_id,
            filename="app.log",
            file_size=1024,
            checksum="abc123def456789",
            hash_algorithm="sha256"
        )
        
        assert record.tarball_id == tarball_id
        assert record.filename == "app.log"
        assert record.file_size == 1024
        assert record.checksum == "abc123def456789"
        assert record.hash_algorithm == "sha256"
        assert record.is_duplicate is False  # Default value

    def test_file_record_all_fields(self):
        """Test FileRecord with all fields."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        # Data model: All attributes
        tarball_id = str(uuid.uuid4())
        file_timestamp = datetime(2025, 10, 6, 12, 0, 0)
        
        record = FileRecord(
            tarball_id=tarball_id,
            filename="logs/app.log",
            file_size=2048,
            checksum="def456abc123789",
            hash_algorithm="sha1",
            file_timestamp=file_timestamp,
            is_duplicate=True
        )
        
        assert record.tarball_id == tarball_id
        assert record.filename == "logs/app.log"
        assert record.file_size == 2048
        assert record.checksum == "def456abc123789"
        assert record.hash_algorithm == "sha1"
        assert record.file_timestamp == file_timestamp
        assert record.is_duplicate is True

    def test_file_record_id_generation(self):
        """Test that UUID id is generated."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        record = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=512,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Data model: id (UUID, Primary Key)
        assert hasattr(record, 'id'), "FileRecord must have id field"
        assert isinstance(record.id, (str, uuid.UUID)), "ID must be UUID type"

    def test_file_record_filename_validation(self):
        """Test filename field validation."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        
        # Data model: filename (VARCHAR(500), NOT NULL)
        
        # Valid filename
        record = FileRecord(
            tarball_id=tarball_id,
            filename="logs/application.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        assert record.filename == "logs/application.log"
        
        # Empty filename should raise error
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id=tarball_id,
                filename="",
                file_size=1024,
                checksum="abc123",
                hash_algorithm="sha256"
            )
        
        # None filename should raise error
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id=tarball_id,
                filename=None,
                file_size=1024,
                checksum="abc123",
                hash_algorithm="sha256"
            )
        
        # Filename too long should raise error (>500 chars)
        long_filename = "a" * 501
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id=tarball_id,
                filename=long_filename,
                file_size=1024,
                checksum="abc123",
                hash_algorithm="sha256"
            )

    def test_file_record_file_size_validation(self):
        """Test file_size field validation."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        
        # Data model: file_size (BIGINT, NOT NULL) - Must be non-negative
        
        # Valid file size
        record = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        assert record.file_size == 1024
        
        # Zero file size should be valid
        record = FileRecord(
            tarball_id=tarball_id,
            filename="empty.log",
            file_size=0,
            checksum="da39a3ee5e6b4b0d3255bfef95601890afd80709",
            hash_algorithm="sha1"
        )
        assert record.file_size == 0
        
        # Negative file size should raise error
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id=tarball_id,
                filename="test.log",
                file_size=-1,
                checksum="abc123",
                hash_algorithm="sha256"
            )

    def test_file_record_checksum_validation(self):
        """Test checksum field validation."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        
        # Data model: checksum (VARCHAR(64), NOT NULL)
        
        # Valid SHA256 checksum
        sha256_checksum = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        record = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=0,
            checksum=sha256_checksum,
            hash_algorithm="sha256"
        )
        assert record.checksum == sha256_checksum
        
        # Valid SHA1 checksum
        sha1_checksum = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        record = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=0,
            checksum=sha1_checksum,
            hash_algorithm="sha1"
        )
        assert record.checksum == sha1_checksum
        
        # Empty checksum should raise error
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id=tarball_id,
                filename="test.log",
                file_size=1024,
                checksum="",
                hash_algorithm="sha256"
            )
        
        # None checksum should raise error
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id=tarball_id,
                filename="test.log",
                file_size=1024,
                checksum=None,
                hash_algorithm="sha256"
            )

    def test_file_record_hash_algorithm_validation(self):
        """Test hash_algorithm field validation."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        
        # Data model: hash_algorithm (VARCHAR(10), NOT NULL) - Must be approved algorithm
        valid_algorithms = ["sha256", "sha1", "md5"]
        
        # Valid algorithms should work
        for algorithm in valid_algorithms:
            record = FileRecord(
                tarball_id=tarball_id,
                filename="test.log",
                file_size=1024,
                checksum="abc123",
                hash_algorithm=algorithm
            )
            assert record.hash_algorithm == algorithm
        
        # Invalid algorithm should raise error
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id=tarball_id,
                filename="test.log",
                file_size=1024,
                checksum="abc123",
                hash_algorithm="invalid_algo"
            )

    def test_file_record_tarball_id_validation(self):
        """Test tarball_id foreign key validation."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        # Data model: tarball_id (UUID, Foreign Key → TarballRecord.id)
        
        # Valid UUID
        valid_uuid = str(uuid.uuid4())
        record = FileRecord(
            tarball_id=valid_uuid,
            filename="test.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        assert record.tarball_id == valid_uuid
        
        # None tarball_id should raise error
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id=None,
                filename="test.log",
                file_size=1024,
                checksum="abc123",
                hash_algorithm="sha256"
            )
        
        # Invalid UUID format should raise error
        with pytest.raises(ValueError):
            FileRecord(
                tarball_id="not-a-uuid",
                filename="test.log",
                file_size=1024,
                checksum="abc123",
                hash_algorithm="sha256"
            )

    def test_file_record_timestamps(self):
        """Test timestamp fields."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        record = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Data model: created_at (TIMESTAMP, DEFAULT NOW())
        assert hasattr(record, 'created_at'), "Must have created_at field"
        assert isinstance(record.created_at, datetime)
        
        # file_timestamp is optional
        assert hasattr(record, 'file_timestamp'), "Must have file_timestamp field"

    def test_file_record_is_duplicate_flag(self):
        """Test is_duplicate flag."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        
        # Data model: is_duplicate (BOOLEAN, DEFAULT FALSE)
        record = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Default should be False
        assert record.is_duplicate is False
        
        # Should be able to set to True
        record.is_duplicate = True
        assert record.is_duplicate is True

    def test_file_record_relationships(self):
        """Test model relationships."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        record = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Data model: Many-to-One with TarballRecord
        assert hasattr(record, 'tarball'), "Must have tarball relationship"
        
        # Data model: Many-to-Many with DuplicateGroup through membership
        assert hasattr(record, 'duplicate_group'), "Must have duplicate_group relationship"

    def test_file_record_string_representation(self):
        """Test string representation."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        record = FileRecord(
            tarball_id=tarball_id,
            filename="logs/app.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Should have meaningful string representation
        str_repr = str(record)
        assert "logs/app.log" in str_repr
        assert "1024" in str_repr or "abc123" in str_repr

    def test_file_record_equality(self):
        """Test record equality comparison."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        
        record1 = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        record2 = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Records with same data should be equal
        assert record1 == record2
        
        # Records with different checksum should not be equal
        record3 = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=1024,
            checksum="def456",
            hash_algorithm="sha256"
        )
        assert record1 != record3

    def test_file_record_to_dict(self):
        """Test conversion to dictionary."""
        # This will fail until model is implemented
        from dedupe.models.file_record import FileRecord
        
        tarball_id = str(uuid.uuid4())
        record = FileRecord(
            tarball_id=tarball_id,
            filename="test.log",
            file_size=1024,
            checksum="abc123",
            hash_algorithm="sha256",
            is_duplicate=True
        )
        
        # Should be able to convert to dict
        data = record.to_dict()
        assert isinstance(data, dict)
        assert data['tarball_id'] == tarball_id
        assert data['filename'] == "test.log"
        assert data['file_size'] == 1024
        assert data['checksum'] == "abc123"
        assert data['hash_algorithm'] == "sha256"
        assert data['is_duplicate'] is True