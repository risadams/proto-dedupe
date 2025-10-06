#!/usr/bin/env python3
"""Integration test for duplicate detection across tarballs.

This test validates the complete duplicate detection workflow.
It MUST FAIL initially as no implementation exists.
"""

import pytest
import os
import tempfile
import tarfile
import io
import hashlib
from unittest.mock import patch


class TestDuplicateDetection:
    """Test duplicate detection across multiple tarballs."""

    def setup_method(self):
        """Reset services before each test to avoid state interference."""
        from dedupe.cli.main import reset_services, get_services
        reset_services()
        # Initialize fresh services and clear any existing data
        _, _, db_service, _ = get_services()
        db_service.clear_all_data()

    def test_duplicate_detection_across_tarballs(self):
        """Test duplicate detection between different tarballs."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        from dedupe.services.database_service import DatabaseService
        
        # Create shared content
        shared_content = b'This is a shared log file content that appears in multiple tarballs'
        unique_content_1 = b'Unique content for tarball 1'
        unique_content_2 = b'Unique content for tarball 2'
        
        # Create first tarball
        with tempfile.NamedTemporaryFile(suffix='_day1.tar.gz', delete=False) as tar1_file:
            with tarfile.open(tar1_file.name, 'w:gz') as tar:
                # Shared file
                info1 = tarfile.TarInfo('shared.log')
                info1.size = len(shared_content)
                tar.addfile(info1, fileobj=io.BytesIO(shared_content))
                
                # Unique file
                info2 = tarfile.TarInfo('unique1.log')
                info2.size = len(unique_content_1)
                tar.addfile(info2, fileobj=io.BytesIO(unique_content_1))
        
        # Create second tarball with same shared file
        with tempfile.NamedTemporaryFile(suffix='_day2.tar.gz', delete=False) as tar2_file:
            with tarfile.open(tar2_file.name, 'w:gz') as tar:
                # Same shared file (different name, same content)
                info1 = tarfile.TarInfo('logs/shared.log')  # Different path
                info1.size = len(shared_content)
                tar.addfile(info1, fileobj=io.BytesIO(shared_content))
                
                # Unique file
                info2 = tarfile.TarInfo('unique2.log')
                info2.size = len(unique_content_2)
                tar.addfile(info2, fileobj=io.BytesIO(unique_content_2))
        
        try:
            # Process first tarball
            result1 = main(['process', '--hostname', 'test-server', tar1_file.name])
            assert result1 == 0
            
            # Process second tarball
            result2 = main(['process', '--hostname', 'test-server', tar2_file.name])
            assert result2 == 0
            
            # Query duplicates
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                result3 = main(['query', '--hostname', 'test-server', '--duplicates-only'])
            assert result3 == 0
            
            # Verify duplicate detection
            output = mock_stdout.getvalue()
            
            # Should show duplicate groups table
            assert 'Found duplicate groups:' in output
            assert 'Checksum' in output
            assert 'Files' in output
            
            # Should have at least one duplicate entry
            lines = output.strip().split('\n')
            assert len(lines) >= 3  # Header + separator + at least one data line
            
            # Verify in database
            from dedupe.cli.main import get_services
            _, _, db_service, _ = get_services()
            duplicates = db_service.get_duplicate_files()
            
            # Should find the shared content as duplicate
            shared_checksum = hashlib.sha256(shared_content).hexdigest()
            duplicate_found = any(dup.checksum == shared_checksum for dup in duplicates)
            assert duplicate_found, "Shared content should be detected as duplicate"
            
        finally:
            os.unlink(tar1_file.name)
            os.unlink(tar2_file.name)

    def test_duplicate_group_management(self):
        """Test duplicate group creation and management."""
        # This will fail until implementation exists
        from dedupe.services.duplicate_service import DuplicateService
        from dedupe.models.duplicate_group import DuplicateGroup
        
        service = DuplicateService()
        
        # Test content
        content = b'duplicate test content'
        checksum = hashlib.sha256(content).hexdigest()
        
        # First occurrence - should create new group
        group1 = service.process_file_for_duplicates(
            checksum=checksum,
            hash_algorithm='sha256',
            file_size=len(content)
        )
        
        assert isinstance(group1, DuplicateGroup)
        assert group1.checksum == checksum
        assert group1.file_count == 1
        assert group1.total_size_saved == 0  # No savings for first occurrence
        
        # Second occurrence - should add to existing group
        group2 = service.process_file_for_duplicates(
            checksum=checksum,
            hash_algorithm='sha256',
            file_size=len(content)
        )
        
        # Should be same group
        assert group2.id == group1.id
        assert group2.file_count == 2
        assert group2.total_size_saved == len(content)  # Save space for one duplicate
        
        # Third occurrence
        group3 = service.process_file_for_duplicates(
            checksum=checksum,
            hash_algorithm='sha256',
            file_size=len(content)
        )
        
        assert group3.file_count == 3
        assert group3.total_size_saved == 2 * len(content)  # Save space for two duplicates

    def test_cross_server_duplicate_tracking(self):
        """Test duplicate tracking across different servers."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        from dedupe.services.database_service import DatabaseService
        
        # Shared content between servers
        shared_content = b'Configuration file shared between servers'
        
        # Create tarball for server A
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tarA_file:
            with tarfile.open(tarA_file.name, 'w:gz') as tar:
                info = tarfile.TarInfo('config/app.conf')
                info.size = len(shared_content)
                tar.addfile(info, fileobj=io.BytesIO(shared_content))
        
        # Create tarball for server B with same file
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tarB_file:
            with tarfile.open(tarB_file.name, 'w:gz') as tar:
                info = tarfile.TarInfo('app.conf')  # Different path, same content
                info.size = len(shared_content)
                tar.addfile(info, fileobj=io.BytesIO(shared_content))
        
        try:
            # Process for server A
            result1 = main(['process', '--hostname', 'server-a', tarA_file.name])
            assert result1 == 0
            
            # Process for server B
            result2 = main(['process', '--hostname', 'server-b', tarB_file.name])
            assert result2 == 0
            
            # Query duplicates across all servers
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                result3 = main(['query', '--duplicates-only'])
            assert result3 == 0
            
            output = mock_stdout.getvalue()
            
            # Should show duplicate groups table
            assert 'Found duplicate groups:' in output
            assert 'Checksum' in output
            assert 'Files' in output
            
            # Should show at least 2 files for the shared content duplicate
            lines = output.strip().split('\n')
            assert len(lines) >= 3  # Header + separator + at least one data line
            
            # Verify in database
            from dedupe.cli.main import get_services
            _, _, db_service, _ = get_services()
            
            # Get records for both servers
            records_a = db_service.get_file_records_by_hostname('server-a')
            records_b = db_service.get_file_records_by_hostname('server-b')
            
            assert len(records_a) > 0
            assert len(records_b) > 0
            
            # Both should have same checksum for shared file
            shared_checksum = hashlib.sha256(shared_content).hexdigest()
            checksums_a = {r.checksum for r in records_a}
            checksums_b = {r.checksum for r in records_b}
            
            assert shared_checksum in checksums_a
            assert shared_checksum in checksums_b
            
        finally:
            os.unlink(tarA_file.name)
            os.unlink(tarB_file.name)

    def test_duplicate_detection_performance(self):
        """Test duplicate detection performance requirements."""
        # This will fail until implementation exists
        from dedupe.cli.main import get_services
        import time
        
        _, service, _, _ = get_services()
        
        # Create test data
        test_checksum = hashlib.sha256(b'performance test content').hexdigest()
        
        # Add checksum to database first (first occurrence)
        service.process_file_for_duplicates(test_checksum, 'sha256', 1024)
        
        # Add a second occurrence to make it a duplicate
        service.process_file_for_duplicates(test_checksum, 'sha256', 1024)
        
        # Performance requirement: <2s for duplicate queries
        start_time = time.time()
        
        # Query for duplicates
        duplicates = service.find_duplicates_by_checksum(test_checksum)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should complete within 2 seconds
        assert query_time < 2.0, f"Duplicate query took {query_time}s, should be <2s"
        
        # Should find the duplicate
        assert len(duplicates) > 0

    def test_hash_algorithm_consistency(self):
        """Test that hash algorithm is consistent across operations."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        from dedupe.services.database_service import DatabaseService
        
        content = b'test content for hash consistency'
        
        # Create tarball
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                info = tarfile.TarInfo('test.log')
                info.size = len(content)
                tar.addfile(info, fileobj=io.BytesIO(content))
        
        try:
            # Process with default algorithm (sha256)
            result1 = main(['process', '--hostname', 'test-server', tar_file.name])
            assert result1 == 0
            
            # Process same file with explicit sha256
            result2 = main(['process', '--hostname', 'test-server', '--hash-algorithm', 'sha256', tar_file.name])
            assert result2 == 0
            
            # Verify same checksum is used
            from dedupe.cli.main import get_services
            _, _, db_service, _ = get_services()
            file_records = db_service.get_file_records_by_hostname('test-server')
            
            # All records should use sha256
            for record in file_records:
                assert record.hash_algorithm == 'sha256'
            
            # Should detect as duplicates
            checksums = {record.checksum for record in file_records}
            expected_checksum = hashlib.sha256(content).hexdigest()
            assert expected_checksum in checksums
            
        finally:
            os.unlink(tar_file.name)

    def test_duplicate_detection_with_different_algorithms(self):
        """Test duplicate detection with different hash algorithms."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        from dedupe.services.database_service import DatabaseService
        
        content = b'test content for multi-algorithm testing'
        
        # Create tarballs
        with tempfile.NamedTemporaryFile(suffix='_sha256.tar.gz', delete=False) as tar1_file:
            with tarfile.open(tar1_file.name, 'w:gz') as tar:
                info = tarfile.TarInfo('test.log')
                info.size = len(content)
                tar.addfile(info, fileobj=io.BytesIO(content))
        
        with tempfile.NamedTemporaryFile(suffix='_sha1.tar.gz', delete=False) as tar2_file:
            with tarfile.open(tar2_file.name, 'w:gz') as tar:
                info = tarfile.TarInfo('test.log')
                info.size = len(content)
                tar.addfile(info, fileobj=io.BytesIO(content))
        
        try:
            # Process with SHA256
            result1 = main(['process', '--hostname', 'server1', '--hash-algorithm', 'sha256', tar1_file.name])
            assert result1 == 0
            
            # Process with SHA1
            result2 = main(['process', '--hostname', 'server2', '--hash-algorithm', 'sha1', tar2_file.name])
            assert result2 == 0
            
            # Should NOT detect as duplicates (different algorithms)
            from dedupe.cli.main import get_services
            _, _, db_service, _ = get_services()
            
            records1 = db_service.get_file_records_by_hostname('server1')
            records2 = db_service.get_file_records_by_hostname('server2')
            
            # Different algorithms should produce different checksums
            checksum1 = records1[0].checksum
            checksum2 = records2[0].checksum
            assert checksum1 != checksum2
            
            # Algorithms should be recorded correctly
            assert records1[0].hash_algorithm == 'sha256'
            assert records2[0].hash_algorithm == 'sha1'
            
        finally:
            os.unlink(tar1_file.name)
            os.unlink(tar2_file.name)

    def test_duplicate_detection_edge_cases(self):
        """Test edge cases in duplicate detection."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        from dedupe.services.database_service import DatabaseService
        
        # Test empty files
        empty_content = b''
        normal_content = b'normal file content'
        
        # Create tarball with empty and normal files
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                # Empty file
                info1 = tarfile.TarInfo('empty.log')
                info1.size = 0
                tar.addfile(info1, fileobj=io.BytesIO(empty_content))
                
                # Another empty file
                info2 = tarfile.TarInfo('another_empty.log')
                info2.size = 0
                tar.addfile(info2, fileobj=io.BytesIO(empty_content))
                
                # Normal file
                info3 = tarfile.TarInfo('normal.log')
                info3.size = len(normal_content)
                tar.addfile(info3, fileobj=io.BytesIO(normal_content))
        
        try:
            # Process tarball
            result = main(['process', '--hostname', 'test-server', tar_file.name])
            assert result == 0
            
            # Verify empty files are handled correctly
            from dedupe.cli.main import get_services
            _, _, db_service, _ = get_services()
            file_records = db_service.get_file_records_by_hostname('test-server')
            
            # Should have 3 records
            assert len(file_records) == 3
            
            # Empty files should have same checksum
            empty_records = [r for r in file_records if r.file_size == 0]
            assert len(empty_records) == 2
            assert empty_records[0].checksum == empty_records[1].checksum
            
            # Normal file should have different checksum
            normal_records = [r for r in file_records if r.file_size > 0]
            assert len(normal_records) == 1
            assert normal_records[0].checksum != empty_records[0].checksum
            
        finally:
            os.unlink(tar_file.name)