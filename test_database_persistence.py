#!/usr/bin/env python3
"""Test database persistence across CLI calls."""

import tempfile
import tarfile
import io
import os
import sys

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.dedupe.cli.main import main

def test_database_persistence():
    """Test that database persists data across CLI calls."""
    print("🧪 Testing database persistence...")
    
    # Create test tarball
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
        try:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                info = tarfile.TarInfo('test.log')
                content = b'test content'
                info.size = len(content)
                tar.addfile(info, fileobj=io.BytesIO(content))
            
            print(f"📁 Created test tarball: {tar_file.name}")
            
            # First CLI call - process tarball
            print("🔄 Processing tarball...")
            result1 = main(['process', '--hostname', 'test-server', tar_file.name])
            print(f"Process result: {result1}")
            
            # Second CLI call - query stats
            print("📊 Querying stats...")
            result2 = main(['query', '--stats'])
            print(f"Query result: {result2}")
            
            return result1 == 0 and result2 == 0
            
        finally:
            try:
                os.unlink(tar_file.name)
            except (OSError, PermissionError):
                pass

if __name__ == '__main__':
    success = test_database_persistence()
    print(f"\n{'✅' if success else '❌'} Database persistence test {'passed' if success else 'failed'}")