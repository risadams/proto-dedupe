#!/usr/bin/env python3
"""Unit tests for DuplicateGroup model.

This test validates that the DuplicateGroup model meets all requirements.
It MUST FAIL initially as no implementation exists.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from typing import Optional


class TestDuplicateGroupModel:
    """Test DuplicateGroup model implementation."""

    def test_duplicate_group_model_exists(self):
        """Test that DuplicateGroup model can be imported."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        assert DuplicateGroup is not None

    def test_duplicate_group_creation_required_fields(self):
        """Test DuplicateGroup creation with required fields."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        # Data model: Required fields
        group = DuplicateGroup(
            checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            hash_algorithm="sha256"
        )
        
        assert group.checksum == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert group.hash_algorithm == "sha256"
        assert group.file_count == 0  # Default value
        assert group.total_size_saved == 0  # Default value

    def test_duplicate_group_all_fields(self):
        """Test DuplicateGroup with all fields."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        # Data model: All attributes
        first_seen = datetime(2025, 10, 6, 10, 0, 0)
        last_seen = datetime(2025, 10, 6, 15, 30, 0)
        
        group = DuplicateGroup(
            checksum="abc123def456789",
            hash_algorithm="sha1",
            file_count=5,
            first_seen_at=first_seen,
            last_seen_at=last_seen,
            total_size_saved=10240
        )
        
        assert group.checksum == "abc123def456789"
        assert group.hash_algorithm == "sha1"
        assert group.file_count == 5
        assert group.first_seen_at == first_seen
        assert group.last_seen_at == last_seen
        assert group.total_size_saved == 10240

    def test_duplicate_group_id_generation(self):
        """Test that UUID id is generated."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Data model: id (UUID, Primary Key)
        assert hasattr(group, 'id'), "DuplicateGroup must have id field"
        assert isinstance(group.id, (str, uuid.UUID)), "ID must be UUID type"

    def test_duplicate_group_checksum_validation(self):
        """Test checksum field validation."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        # Data model: checksum (VARCHAR(64), NOT NULL, UNIQUE)
        
        # Valid SHA256 checksum
        sha256_checksum = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        group = DuplicateGroup(
            checksum=sha256_checksum,
            hash_algorithm="sha256"
        )
        assert group.checksum == sha256_checksum
        
        # Valid SHA1 checksum
        sha1_checksum = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        group = DuplicateGroup(
            checksum=sha1_checksum,
            hash_algorithm="sha1"
        )
        assert group.checksum == sha1_checksum
        
        # Empty checksum should raise error
        with pytest.raises(ValueError):
            DuplicateGroup(
                checksum="",
                hash_algorithm="sha256"
            )
        
        # None checksum should raise error
        with pytest.raises(ValueError):
            DuplicateGroup(
                checksum=None,
                hash_algorithm="sha256"
            )
        
        # Checksum too long should raise error (>64 chars)
        long_checksum = "a" * 65
        with pytest.raises(ValueError):
            DuplicateGroup(
                checksum=long_checksum,
                hash_algorithm="sha256"
            )

    def test_duplicate_group_hash_algorithm_validation(self):
        """Test hash_algorithm field validation."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        # Data model: hash_algorithm (VARCHAR(10), NOT NULL) - Must be approved algorithm
        valid_algorithms = ["sha256", "sha1", "md5"]
        
        # Valid algorithms should work
        for algorithm in valid_algorithms:
            group = DuplicateGroup(
                checksum="abc123",
                hash_algorithm=algorithm
            )
            assert group.hash_algorithm == algorithm
        
        # Invalid algorithm should raise error
        with pytest.raises(ValueError):
            DuplicateGroup(
                checksum="abc123",
                hash_algorithm="invalid_algo"
            )
        
        # Empty algorithm should raise error
        with pytest.raises(ValueError):
            DuplicateGroup(
                checksum="abc123",
                hash_algorithm=""
            )

    def test_duplicate_group_file_count_validation(self):
        """Test file_count field validation."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        # Data model: file_count (INTEGER, DEFAULT 0) - Must be non-negative
        
        # Valid file count
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256",
            file_count=5
        )
        assert group.file_count == 5
        
        # Zero file count should be valid (default)
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256",
            file_count=0
        )
        assert group.file_count == 0
        
        # Negative file count should raise error
        with pytest.raises(ValueError):
            DuplicateGroup(
                checksum="abc123",
                hash_algorithm="sha256",
                file_count=-1
            )

    def test_duplicate_group_total_size_saved_validation(self):
        """Test total_size_saved field validation."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        # Data model: total_size_saved (BIGINT, DEFAULT 0) - Must be non-negative
        
        # Valid size saved
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256",
            total_size_saved=10240
        )
        assert group.total_size_saved == 10240
        
        # Zero size saved should be valid (default)
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256",
            total_size_saved=0
        )
        assert group.total_size_saved == 0
        
        # Negative size saved should raise error
        with pytest.raises(ValueError):
            DuplicateGroup(
                checksum="abc123",
                hash_algorithm="sha256",
                total_size_saved=-1
            )

    def test_duplicate_group_timestamps(self):
        """Test timestamp fields."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Data model: first_seen_at (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
        assert hasattr(group, 'first_seen_at'), "Must have first_seen_at field"
        assert isinstance(group.first_seen_at, datetime)
        
        # Data model: last_seen_at (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
        assert hasattr(group, 'last_seen_at'), "Must have last_seen_at field"
        assert isinstance(group.last_seen_at, datetime)
        
        # first_seen_at should be <= last_seen_at
        assert group.first_seen_at <= group.last_seen_at

    def test_duplicate_group_update_last_seen(self):
        """Test updating last_seen_at timestamp."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        original_last_seen = group.last_seen_at
        
        # Should be able to update last_seen_at
        new_timestamp = datetime.now() + timedelta(hours=1)
        group.update_last_seen(new_timestamp)
        
        assert group.last_seen_at == new_timestamp
        assert group.last_seen_at > original_last_seen

    def test_duplicate_group_add_file(self):
        """Test adding a file to the group."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256",
            file_count=2,
            total_size_saved=1024
        )
        
        # Should be able to add a file with size
        file_size = 512
        group.add_file(file_size)
        
        # Should increment file count and update size saved
        assert group.file_count == 3
        assert group.total_size_saved == 1024 + file_size

    def test_duplicate_group_remove_file(self):
        """Test removing a file from the group."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256",
            file_count=3,
            total_size_saved=1536
        )
        
        # Should be able to remove a file with size
        file_size = 512
        group.remove_file(file_size)
        
        # Should decrement file count and update size saved
        assert group.file_count == 2
        assert group.total_size_saved == 1536 - file_size

    def test_duplicate_group_checksum_uniqueness(self):
        """Test checksum uniqueness constraint."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        # Data model: checksum (VARCHAR(64), NOT NULL, UNIQUE)
        # Should have method to check uniqueness
        assert hasattr(DuplicateGroup, 'is_checksum_unique'), "Must have uniqueness validation"
        
        # Same checksum should not be allowed to exist twice
        checksum = "abc123def456"
        assert DuplicateGroup.is_checksum_unique(checksum)

    def test_duplicate_group_relationships(self):
        """Test model relationships."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Data model: One-to-Many with FileRecord
        assert hasattr(group, 'file_records'), "Must have file_records relationship"
        
        # Should be able to access related file records
        file_records = group.file_records
        assert hasattr(file_records, '__iter__'), "file_records must be iterable"

    def test_duplicate_group_string_representation(self):
        """Test string representation."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123def456",
            hash_algorithm="sha256",
            file_count=3
        )
        
        # Should have meaningful string representation
        str_repr = str(group)
        assert "abc123def456" in str_repr
        assert "3" in str_repr or "files" in str_repr.lower()

    def test_duplicate_group_equality(self):
        """Test record equality comparison."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group1 = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        group2 = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256"
        )
        
        # Groups with same checksum should be equal
        assert group1 == group2
        
        # Groups with different checksum should not be equal
        group3 = DuplicateGroup(
            checksum="def456",
            hash_algorithm="sha256"
        )
        assert group1 != group3

    def test_duplicate_group_to_dict(self):
        """Test conversion to dictionary."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256",
            file_count=3,
            total_size_saved=1536
        )
        
        # Should be able to convert to dict
        data = group.to_dict()
        assert isinstance(data, dict)
        assert data['checksum'] == "abc123"
        assert data['hash_algorithm'] == "sha256"
        assert data['file_count'] == 3
        assert data['total_size_saved'] == 1536

    def test_duplicate_group_space_savings_calculation(self):
        """Test space savings calculation."""
        # This will fail until model is implemented
        from dedupe.models.duplicate_group import DuplicateGroup
        
        group = DuplicateGroup(
            checksum="abc123",
            hash_algorithm="sha256",
            file_count=4,
            total_size_saved=3072  # 3 * 1024 (keep 1, save space for 3 duplicates)
        )
        
        # Should calculate space savings correctly
        original_file_size = 1024
        expected_savings = original_file_size * (group.file_count - 1)  # Keep one, save others
        
        assert group.calculate_space_savings(original_file_size) == expected_savings