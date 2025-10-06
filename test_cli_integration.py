#!/usr/bin/env python3
"""Simple CLI integration test.

Tests the CLI interface with actual tarball processing.
"""

import tempfile
import tarfile
import io
import os
import sys

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.dedupe.cli.main import main

def test_cli_integration():
    """Test CLI integration with process and query commands."""
    print("🧪 Testing CLI integration...")
    
    # Create test tarball with duplicate content
    test_files = {
        'logs/app.log': b'application log content',
        'logs/error.log': b'error log content',
        'config/app.conf': b'application log content',  # Duplicate content
        'config/server.conf': b'server configuration'
    }
    
    print(f"📁 Creating test tarball with {len(test_files)} files...")
    
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tar_file:
        try:
            with tarfile.open(tar_file.name, 'w:gz') as tar:
                for filename, content in test_files.items():
                    info = tarfile.TarInfo(filename)
                    info.size = len(content)
                    tar.addfile(info, fileobj=io.BytesIO(content))
            
            print(f"✅ Test tarball created: {tar_file.name}")
            
            # Test CLI process command
            print("🖥️  Testing CLI process command...")
            result = main(['process', '--hostname', 'test-server', tar_file.name])
            
            if result == 0:
                print("✅ Process command succeeded")
            else:
                print(f"❌ Process command failed with exit code {result}")
                return False
            
            # Test CLI query command - stats
            print("📊 Testing CLI query stats...")
            result = main(['query', '--stats'])
            
            if result == 0:
                print("✅ Query stats succeeded")
            else:
                print(f"❌ Query stats failed with exit code {result}")
                return False
            
            # Test CLI query command - duplicates only
            print("🔍 Testing CLI query duplicates...")
            result = main(['query', '--duplicates-only'])
            
            if result == 0:
                print("✅ Query duplicates succeeded")
            else:
                print(f"❌ Query duplicates failed with exit code {result}")
                return False
            
            # Test CLI query command - JSON format
            print("📋 Testing CLI query JSON format...")
            result = main(['query', '--duplicates-only', '--format', 'json'])
            
            if result == 0:
                print("✅ Query JSON format succeeded")
            else:
                print(f"❌ Query JSON format failed with exit code {result}")
                return False
            
            # Test dry-run mode
            print("🔬 Testing CLI dry-run mode...")
            result = main(['process', '--hostname', 'test-server-2', '--dry-run', tar_file.name])
            
            if result == 0:
                print("✅ Dry-run mode succeeded")
            else:
                print(f"❌ Dry-run mode failed with exit code {result}")
                return False
            
            print("🎉 All CLI integration tests passed!")
            return True
            
        finally:
            # Clean up
            try:
                os.unlink(tar_file.name)
            except (OSError, PermissionError):
                # On Windows, files might be locked temporarily
                pass

if __name__ == '__main__':
    try:
        success = test_cli_integration()
        if success:
            print("\n✅ CLI integration test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ CLI integration test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 CLI integration test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)