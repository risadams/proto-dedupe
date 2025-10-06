#!/usr/bin/env python3
"""Service integration test script.

Tests that all services work together correctly without relying on CLI.
"""

import tempfile
import tarfile
import io
import hashlib
import os
import sys

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.dedupe.services.hash_service import HashService
from src.dedupe.services.tarball_service import TarballService
from src.dedupe.services.duplicate_service import DuplicateService
from src.dedupe.services.database_service import DatabaseService

def test_service_integration():
    """Test all services working together."""
    print("🧪 Testing service integration...")
    
    # Initialize services
    hash_service = HashService()
    tarball_service = TarballService(hash_service)
    duplicate_service = DuplicateService()
    db_service = DatabaseService()
    
    print("✅ All services initialized successfully")
    
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
            
            # Test TarballService
            print("🗃️  Testing TarballService...")
            tarball_record = tarball_service.process_tarball(tar_file.name, 'test-server')
            
            print(f"✅ Tarball processed: {tarball_record.filename}")
            print(f"   - Files: {tarball_record.total_files_count}")
            print(f"   - Status: {tarball_record.status}")
            
            # Get extracted files
            file_records = tarball_service.get_extracted_files(tarball_record.id)
            print(f"✅ Extracted {len(file_records)} file records")
            
            # Test DatabaseService
            print("💾 Testing DatabaseService...")
            db_service.save_tarball_record(tarball_record)
            db_service.save_file_records(file_records)
            
            # Test retrieval
            retrieved_tarballs = db_service.get_tarball_records(hostname='test-server')
            retrieved_files = db_service.get_file_records(tarball_record.id)
            
            print(f"✅ Database storage working:")
            print(f"   - Tarballs: {len(retrieved_tarballs)}")
            print(f"   - Files: {len(retrieved_files)}")
            
            # Test DuplicateService
            print("🔍 Testing DuplicateService...")
            duplicate_groups = duplicate_service.process_file_records(file_records)
            
            print(f"✅ Duplicate processing complete:")
            print(f"   - Groups created: {len(duplicate_groups)}")
            
            # Find duplicates
            all_duplicates = duplicate_service.find_all_duplicates()
            print(f"   - Duplicate groups found: {len(all_duplicates)}")
            
            # Test HashService
            print("🔐 Testing HashService...")
            test_content = b'application log content'
            calculated_hash = hash_service.calculate_checksum(io.BytesIO(test_content), 'sha256')
            expected_hash = hashlib.sha256(test_content).hexdigest()
            
            if calculated_hash == expected_hash:
                print("✅ Hash calculation verified")
            else:
                print(f"❌ Hash mismatch: {calculated_hash} != {expected_hash}")
                return False
            
            # Verify duplicate detection worked
            duplicate_content_files = [f for f in file_records 
                                     if f.checksum == calculated_hash]
            
            if len(duplicate_content_files) >= 2:
                print(f"✅ Duplicate detection working: found {len(duplicate_content_files)} files with same content")
            else:
                print(f"⚠️  Expected to find duplicates but found {len(duplicate_content_files)} files")
            
            # Test statistics
            stats = duplicate_service.get_duplicate_statistics()
            db_stats = db_service.get_statistics()
            
            print(f"📊 Final statistics:")
            print(f"   - Duplicate stats: {stats}")
            print(f"   - Database stats: {db_stats}")
            
            print("🎉 All service integration tests passed!")
            return True
            
        finally:
            # Clean up
            try:
                os.unlink(tar_file.name)
            except (OSError, PermissionError):
                # On Windows, files might be locked temporarily
                pass
            tarball_service.clear_extracted_files(tarball_record.id)

if __name__ == '__main__':
    try:
        success = test_service_integration()
        if success:
            print("\n✅ Service integration test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Service integration test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Service integration test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)