#!/usr/bin/env python3
"""Integration test for single tarball processing.

This test validates the complete process workflow from quickstart scenario 1.
It MUST FAIL initially as no implementation exists.
"""

import pytest
import os
import tempfile
import tarfile
from datetime import datetime
from unittest.mock import patch, MagicMock


class TestProcessSingleTarball:
    """Test single tarball processing integration."""

    def test_process_single_tarball_workflow(self):
        """Test complete single tarball processing workflow."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        from dedupe.services.database_service import DatabaseService
        
        # Create test tarball
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                # Add test files to tarball
                info1 = tarfile.TarInfo('app.log')
                info1.size = len(b'test log content')
                tar.addfile(info1, fileobj=tempfile.BytesIO(b'test log content'))
                
                info2 = tarfile.TarInfo('error.log') 
                info2.size = len(b'error log content')
                tar.addfile(info2, fileobj=tempfile.BytesIO(b'error log content'))
        
        try:
            # Quickstart scenario 1: Process single tarball from server01
            with patch('sys.stdout') as mock_stdout:
                result = main(['process', '--hostname', 'server01', tar_file.name])
            
            # Should succeed
            assert result == 0
            
            # Should show processing output
            output = mock_stdout.getvalue()
            assert 'Processing' in output
            assert 'server01' in output
            assert 'files' in output.lower()
            
            # Should store records in database
            db_service = DatabaseService()
            tarball_records = db_service.get_tarball_records(hostname='server01')
            assert len(tarball_records) == 1
            
            file_records = db_service.get_file_records(tarball_records[0].id)
            assert len(file_records) == 2
            
        finally:
            os.unlink(tar_file.name)

    def test_process_tarball_file_extraction(self):
        """Test that files are correctly extracted and stored."""
        # This will fail until implementation exists
        from dedupe.services.tarball_service import TarballService
        from dedupe.models.tarball_record import TarballRecord
        from dedupe.models.file_record import FileRecord
        
        # Create test tarball with known content
        test_files = {
            'logs/app.log': b'application log content',
            'logs/error.log': b'error log content',
            'config/app.conf': b'config file content'
        }
        
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                for filename, content in test_files.items():
                    info = tarfile.TarInfo(filename)
                    info.size = len(content)
                    tar.addfile(info, fileobj=tempfile.BytesIO(content))
        
        try:
            # Process tarball
            service = TarballService()
            tarball_record = service.process_tarball(tar_file.name, 'server01')
            
            # Should create tarball record
            assert isinstance(tarball_record, TarballRecord)
            assert tarball_record.hostname == 'server01'
            assert tarball_record.status == 'SUCCESS'
            assert tarball_record.total_files_count == 3
            
            # Should create file records
            file_records = service.get_extracted_files(tarball_record.id)
            assert len(file_records) == 3
            
            # Should calculate checksums
            for record in file_records:
                assert isinstance(record, FileRecord)
                assert record.checksum is not None
                assert len(record.checksum) > 0
                assert record.hash_algorithm == 'sha256'  # Default algorithm
                
        finally:
            os.unlink(tar_file.name)

    def test_process_tarball_checksum_calculation(self):
        """Test that checksums are calculated correctly."""
        # This will fail until implementation exists
        from dedupe.services.hash_service import HashService
        import hashlib
        
        # Test data with known checksum
        test_content = b'test file content for checksum validation'
        expected_sha256 = hashlib.sha256(test_content).hexdigest()
        
        # Create test tarball
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                info = tarfile.TarInfo('test.log')
                info.size = len(test_content)
                tar.addfile(info, fileobj=tempfile.BytesIO(test_content))
        
        try:
            # Process and verify checksum
            hash_service = HashService()
            
            # Extract file and calculate checksum
            with tarfile.open(tar_file.name, 'r:gz') as tar:
                member = tar.getmember('test.log')
                file_obj = tar.extractfile(member)
                calculated_checksum = hash_service.calculate_checksum(file_obj, 'sha256')
            
            assert calculated_checksum == expected_sha256
            
        finally:
            os.unlink(tar_file.name)

    def test_process_tarball_metadata_storage(self):
        """Test that metadata is correctly stored."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        from dedupe.services.database_service import DatabaseService
        
        # Create tarball with specific metadata
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                # Add file with specific timestamp
                info = tarfile.TarInfo('timestamped.log')
                info.size = len(b'content')
                info.mtime = 1696636800  # 2023-10-07 00:00:00 UTC
                tar.addfile(info, fileobj=tempfile.BytesIO(b'content'))
        
        try:
            # Get tarball file size
            tarball_size = os.path.getsize(tar_file.name)
            
            # Process tarball
            result = main(['process', '--hostname', 'server01', tar_file.name])
            assert result == 0
            
            # Verify metadata storage
            db_service = DatabaseService()
            tarball_records = db_service.get_tarball_records(hostname='server01')
            
            tarball_record = tarball_records[0]
            assert tarball_record.filename == os.path.basename(tar_file.name)
            assert tarball_record.hostname == 'server01'
            assert tarball_record.file_size == tarball_size
            assert tarball_record.status == 'SUCCESS'
            assert tarball_record.total_files_count == 1
            
            # Verify file record metadata
            file_records = db_service.get_file_records(tarball_record.id)
            file_record = file_records[0]
            assert file_record.filename == 'timestamped.log'
            assert file_record.file_size == len(b'content')
            assert file_record.file_timestamp is not None
            
        finally:
            os.unlink(tar_file.name)

    def test_process_tarball_error_handling(self):
        """Test error handling for corrupted or invalid tarballs."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        
        # Test nonexistent file
        with pytest.raises(SystemExit) as exc_info:
            main(['process', '--hostname', 'server01', '/nonexistent/file.tar.gz'])
        assert exc_info.value.code == 4  # File processing error
        
        # Test corrupted tarball
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as bad_file:
            bad_file.write(b'not a valid tarball content')
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                main(['process', '--hostname', 'server01', bad_file.name])
            assert exc_info.value.code == 4  # File processing error
            
        finally:
            os.unlink(bad_file.name)

    def test_process_tarball_progress_reporting(self):
        """Test progress reporting during processing."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        
        # Create tarball with multiple files
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                for i in range(10):
                    info = tarfile.TarInfo(f'file_{i}.log')
                    content = f'content for file {i}'.encode()
                    info.size = len(content)
                    tar.addfile(info, fileobj=tempfile.BytesIO(content))
        
        try:
            # Process with progress enabled
            with patch('sys.stdout') as mock_stdout:
                result = main(['process', '--hostname', 'server01', '--progress', tar_file.name])
            
            assert result == 0
            
            # Should show progress information
            output = mock_stdout.getvalue()
            assert 'Processing' in output
            assert any(char in output for char in ['%', '|', 'files'])  # Progress indicators
            
        finally:
            os.unlink(tar_file.name)

    def test_process_tarball_dry_run(self):
        """Test dry run functionality."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        from dedupe.services.database_service import DatabaseService
        
        # Create test tarball
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                info = tarfile.TarInfo('test.log')
                info.size = len(b'test content')
                tar.addfile(info, fileobj=tempfile.BytesIO(b'test content'))
        
        try:
            # Process in dry run mode
            with patch('sys.stdout') as mock_stdout:
                result = main(['process', '--hostname', 'server01', '--dry-run', tar_file.name])
            
            assert result == 0
            
            # Should show dry run output
            output = mock_stdout.getvalue()
            assert 'DRY RUN' in output or 'dry run' in output.lower()
            assert 'would' in output.lower()  # Should use conditional language
            
            # Should NOT create database records
            db_service = DatabaseService()
            tarball_records = db_service.get_tarball_records(hostname='server01')
            assert len(tarball_records) == 0
            
        finally:
            os.unlink(tar_file.name)

    def test_process_tarball_performance_requirements(self):
        """Test that processing meets performance requirements."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        import time
        import psutil
        import os
        
        # Create larger test tarball
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                for i in range(100):  # 100 files
                    info = tarfile.TarInfo(f'file_{i:03d}.log')
                    content = f'log content for file {i}\n' * 100  # ~2KB per file
                    content_bytes = content.encode()
                    info.size = len(content_bytes)
                    tar.addfile(info, fileobj=tempfile.BytesIO(content_bytes))
        
        try:
            # Monitor memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Process tarball and measure time
            start_time = time.time()
            result = main(['process', '--hostname', 'server01', tar_file.name])
            end_time = time.time()
            
            # Check memory after processing
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            assert result == 0
            
            # Performance requirements from spec:
            # - Memory efficient processing (should not load entire tarball into memory)
            # - Reasonable processing time
            processing_time = end_time - start_time
            
            # Memory increase should be reasonable (less than 100MB for this test)
            assert memory_increase < 100 * 1024 * 1024, f"Memory increased by {memory_increase} bytes"
            
            # Should complete within reasonable time (less than 30 seconds for 100 small files)
            assert processing_time < 30, f"Processing took {processing_time} seconds"
            
        finally:
            os.unlink(tar_file.name)