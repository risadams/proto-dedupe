#!/usr/bin/env python3
"""Integration test for querying duplicate files.

This test validates the query functionality from quickstart scenario 3.
It MUST FAIL initially as no implementation exists.
"""

import pytest
import tempfile
import tarfile
from unittest.mock import patch


class TestQueryDuplicates:
    """Test query duplicate files functionality."""

    def test_query_duplicates_basic(self):
        """Test basic duplicate query functionality."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        
        # Setup test data first
        content1 = b'duplicate content'
        content2 = b'unique content'
        
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                # Add duplicate files
                for i in range(3):
                    info = tarfile.TarInfo(f'duplicate_{i}.log')
                    info.size = len(content1)
                    tar.addfile(info, fileobj=tempfile.BytesIO(content1))
                
                # Add unique file
                info = tarfile.TarInfo('unique.log')
                info.size = len(content2)
                tar.addfile(info, fileobj=tempfile.BytesIO(content2))
        
        try:
            # Process tarball
            main(['process', '--hostname', 'server01', tar_file.name])
            
            # Query duplicates only
            with patch('sys.stdout') as mock_stdout:
                result = main(['query', '--duplicates-only'])
            
            assert result == 0
            output = mock_stdout.getvalue()
            
            # Should show duplicate files
            assert 'duplicate_' in output
            assert 'server01' in output
            
        finally:
            import os
            os.unlink(tar_file.name)

    def test_query_output_formats(self):
        """Test different output formats."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        
        # Test table format (default)
        with patch('sys.stdout') as mock_stdout:
            result = main(['query', '--format', 'table'])
        assert result == 0
        
        # Test JSON format
        with patch('sys.stdout') as mock_stdout:
            result = main(['query', '--format', 'json'])
        assert result == 0
        
        # Test CSV format
        with patch('sys.stdout') as mock_stdout:
            result = main(['query', '--format', 'csv'])
        assert result == 0

    def test_query_filtering(self):
        """Test query filtering options."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        
        # Test hostname filter
        result = main(['query', '--hostname', 'server01'])
        assert result == 0
        
        # Test date filter
        result = main(['query', '--since', '2025-10-01'])
        assert result == 0
        
        # Test stats option
        result = main(['query', '--stats'])
        assert result == 0