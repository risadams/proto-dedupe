#!/usr/bin/env python3
"""Contract test for CLI query command.

This test validates that the query command meets all contract requirements.
It MUST FAIL initially as no implementation exists.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
from io import StringIO


class TestQueryCommandContract:
    """Test query command contract compliance."""

    def test_query_command_exists(self):
        """Test that query command can be imported and called."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        assert hasattr(cmd, 'execute'), "QueryCommand must have execute method"

    def test_query_command_basic_execution(self):
        """Test query command executes without required args per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.main import main
        
        # Contract: Query can run without arguments (shows all)
        with patch('dedupe.services.database_service.DatabaseService'):
            result = main(['query'])
            assert result == 0  # Success exit code

    def test_query_command_hostname_filter(self):
        """Test --hostname filter option per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        
        # Contract: Hostname filtering support
        assert hasattr(cmd, 'filter_by_hostname'), "Must support hostname filtering"
        
        cmd.set_hostname_filter('server01')
        assert cmd.hostname_filter == 'server01'

    def test_query_command_since_filter(self):
        """Test --since date filter option per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        
        # Contract: Date filtering support (YYYY-MM-DD format)
        assert hasattr(cmd, 'filter_by_date'), "Must support date filtering"
        
        cmd.set_since_filter('2025-10-01')
        assert cmd.since_filter == '2025-10-01'

    def test_query_command_duplicates_only_filter(self):
        """Test --duplicates-only filter option per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        
        # Contract: Duplicates-only filtering
        assert hasattr(cmd, 'set_duplicates_only'), "Must support duplicates-only filter"
        
        cmd.set_duplicates_only(True)
        assert cmd.duplicates_only is True

    def test_query_command_output_formats(self):
        """Test output format options per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        
        # Contract: Support table, json, csv formats, default table
        valid_formats = ['table', 'json', 'csv']
        assert cmd.get_default_format() == 'table'
        
        for fmt in valid_formats:
            cmd.set_output_format(fmt)
            assert cmd.output_format == fmt

    def test_query_command_table_format_output(self):
        """Test table format output per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        cmd.set_output_format('table')
        
        # Contract: Table format with specific columns
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sample_data = [
                {'hostname': 'server01', 'tarball': 'logs.tar.gz', 'duplicates': 15, 'space_saved': '1.2 GB'},
                {'hostname': 'server02', 'tarball': 'logs.tar.gz', 'duplicates': 8, 'space_saved': '0.8 GB'}
            ]
            cmd.output_table(sample_data)
        
        output = mock_stdout.getvalue()
        assert 'Hostname' in output
        assert 'Tarball File' in output
        assert 'Duplicates' in output
        assert 'Space Saved' in output

    def test_query_command_json_format_output(self):
        """Test JSON format output per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        cmd.set_output_format('json')
        
        # Contract: JSON format with summary and duplicates sections
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sample_data = {
                'summary': {
                    'total_files': 1234,
                    'duplicate_files': 567,
                    'space_saved_bytes': 1073741824
                },
                'duplicates': [
                    {
                        'checksum': 'abc123',
                        'file_count': 3,
                        'files': [
                            {
                                'hostname': 'server01',
                                'tarball': 'logs.tar.gz',
                                'filename': 'app.log',
                                'size': 1024
                            }
                        ]
                    }
                ]
            }
            cmd.output_json(sample_data)
        
        output = mock_stdout.getvalue()
        parsed = json.loads(output)
        assert 'summary' in parsed
        assert 'duplicates' in parsed
        assert 'total_files' in parsed['summary']

    def test_query_command_csv_format_output(self):
        """Test CSV format output per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        cmd.set_output_format('csv')
        
        # Contract: CSV format with specific headers
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sample_data = [
                {
                    'hostname': 'server01',
                    'tarball': 'logs.tar.gz',
                    'filename': 'app.log',
                    'checksum': 'abc123',
                    'size': 1024,
                    'is_duplicate': True
                }
            ]
            cmd.output_csv(sample_data)
        
        output = mock_stdout.getvalue()
        headers = output.split('\n')[0]
        assert 'hostname,tarball,filename,checksum,size,is_duplicate' == headers

    def test_query_command_output_file_option(self):
        """Test --output file option per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        
        # Contract: Support writing output to file
        assert hasattr(cmd, 'set_output_file'), "Must support output file option"
        
        cmd.set_output_file('/tmp/report.json')
        assert cmd.output_file == '/tmp/report.json'

    def test_query_command_stats_option(self):
        """Test --stats option per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        
        # Contract: Show summary statistics
        assert hasattr(cmd, 'enable_stats'), "Must support stats option"
        
        cmd.enable_stats(True)
        assert cmd.show_stats is True

    def test_query_command_help_option(self):
        """Test --help option per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.main import main
        
        # Contract: Show help and exit
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main(['query', '--help'])
        
        assert exc_info.value.code == 0  # Success exit for help
        help_output = mock_stdout.getvalue()
        assert 'query' in help_output.lower()
        assert 'duplicate' in help_output.lower()

    def test_query_command_examples_work(self):
        """Test that contract examples execute correctly."""
        # This will fail until CLI implementation exists
        from dedupe.cli.main import main
        
        # Contract example 1: Show duplicates only
        with patch('dedupe.services.database_service.DatabaseService'):
            result = main(['query', '--duplicates-only'])
            assert result == 0

        # Contract example 2: Filter by hostname and date
        with patch('dedupe.services.database_service.DatabaseService'):
            result = main(['query', '--hostname', 'server01', '--since', '2025-10-01'])
            assert result == 0

        # Contract example 3: Stats with JSON output
        with patch('dedupe.services.database_service.DatabaseService'):
            result = main(['query', '--stats', '--format', 'json', '--output', 'report.json'])
            assert result == 0

    def test_query_command_date_validation(self):
        """Test date format validation per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        
        # Contract: YYYY-MM-DD format validation
        assert hasattr(cmd, 'validate_date_format'), "Must validate date format"
        
        # Valid date should not raise error
        cmd.validate_date_format('2025-10-01')
        
        # Invalid format should raise error
        with pytest.raises(ValueError):
            cmd.validate_date_format('10/01/2025')

    def test_query_command_database_integration(self):
        """Test database service integration per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.query_command import QueryCommand
        
        cmd = QueryCommand()
        
        # Contract: Must integrate with database service
        assert hasattr(cmd, 'database_service'), "Must have database service"
        
        # Should execute queries through service
        with patch('dedupe.services.database_service.DatabaseService') as mock_service:
            cmd.execute()
            mock_service.return_value.query_files.assert_called()

    def test_query_command_error_handling(self):
        """Test error handling per contract."""
        # This will fail until CLI implementation exists
        from dedupe.cli.main import main
        
        # Contract: Database errors should exit with code 3
        with patch('dedupe.services.database_service.DatabaseService') as mock_service:
            mock_service.side_effect = Exception("Database connection failed")
            
            with pytest.raises(SystemExit) as exc_info:
                main(['query'])
            assert exc_info.value.code == 3  # Database connection error