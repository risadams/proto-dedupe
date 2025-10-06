#!/usr/bin/env python3
"""Integration test for space savings report.

This test validates the space savings report from quickstart scenario 4.
It MUST FAIL initially as no implementation exists.
"""

import pytest
import io
from unittest.mock import patch


class TestSpaceSavings:
    """Test space savings report functionality."""

    def test_space_savings_calculation(self):
        """Test space savings calculation."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        
        # Test stats with JSON output
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = main(['query', '--stats', '--format', 'json'])
        
        assert result == 0
        output = mock_stdout.getvalue()

        # Should contain space savings information
        assert 'duplicate_statistics' in output
        assert 'total_groups' in output
        assert 'duplicate_groups' in output

    def test_space_savings_by_hostname(self):
        """Test space savings breakdown by hostname."""
        # This will fail until implementation exists
        from dedupe.cli.main import main
        
        result = main(['query', '--stats', '--format', 'json'])
        assert result == 0