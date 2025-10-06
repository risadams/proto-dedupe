"""Hash service for dedupe-tarball.

This module provides hash calculation functionality for file checksums
supporting multiple hash algorithms.
"""

import hashlib
from typing import BinaryIO, Optional
import logging

logger = logging.getLogger(__name__)


class HashService:
    """Service for calculating file checksums using various hash algorithms."""
    
    SUPPORTED_ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    DEFAULT_ALGORITHM = 'sha256'
    CHUNK_SIZE = 8192  # 8KB chunks for efficient reading
    
    def __init__(self):
        """Initialize the hash service."""
        self._validate_algorithms()
    
    def _validate_algorithms(self) -> None:
        """Validate that all supported algorithms are available."""
        for algorithm_name in self.SUPPORTED_ALGORITHMS:
            try:
                hasher = self.SUPPORTED_ALGORITHMS[algorithm_name]()
                # Test with dummy data
                hasher.update(b'test')
                hasher.hexdigest()
            except Exception as e:
                logger.warning(f"Hash algorithm {algorithm_name} not available: {e}")
    
    def calculate_checksum(self, 
                          file_obj: BinaryIO, 
                          algorithm: str = DEFAULT_ALGORITHM,
                          chunk_size: Optional[int] = None) -> str:
        """Calculate checksum for a file object.
        
        Args:
            file_obj: File-like object to calculate checksum for
            algorithm: Hash algorithm to use (md5, sha1, sha256, sha512)
            chunk_size: Size of chunks to read (defaults to CHUNK_SIZE)
            
        Returns:
            Hexadecimal string representation of the checksum
            
        Raises:
            ValueError: If algorithm is not supported
            IOError: If file cannot be read
        """
        algorithm = algorithm.lower()
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}. "
                           f"Supported: {', '.join(self.SUPPORTED_ALGORITHMS.keys())}")
        
        if chunk_size is None:
            chunk_size = self.CHUNK_SIZE
        
        try:
            # Create hasher
            hasher = self.SUPPORTED_ALGORITHMS[algorithm]()
            
            # Remember current position
            initial_position = file_obj.tell()
            
            # Read and hash file in chunks
            while True:
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
            
            # Restore file position
            file_obj.seek(initial_position)
            
            checksum = hasher.hexdigest()
            logger.debug(f"Calculated {algorithm} checksum: {checksum}")
            return checksum
            
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            raise IOError(f"Failed to calculate checksum: {e}")
    
    def calculate_file_checksum(self, 
                               file_path: str, 
                               algorithm: str = DEFAULT_ALGORITHM,
                               chunk_size: Optional[int] = None) -> str:
        """Calculate checksum for a file by path.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use
            chunk_size: Size of chunks to read
            
        Returns:
            Hexadecimal string representation of the checksum
            
        Raises:
            ValueError: If algorithm is not supported
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        try:
            with open(file_path, 'rb') as file_obj:
                return self.calculate_checksum(file_obj, algorithm, chunk_size)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise IOError(f"Failed to read file {file_path}: {e}")
    
    def calculate_bytes_checksum(self, 
                                data: bytes, 
                                algorithm: str = DEFAULT_ALGORITHM) -> str:
        """Calculate checksum for bytes data.
        
        Args:
            data: Bytes data to calculate checksum for
            algorithm: Hash algorithm to use
            
        Returns:
            Hexadecimal string representation of the checksum
            
        Raises:
            ValueError: If algorithm is not supported
        """
        algorithm = algorithm.lower()
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}. "
                           f"Supported: {', '.join(self.SUPPORTED_ALGORITHMS.keys())}")
        
        try:
            hasher = self.SUPPORTED_ALGORITHMS[algorithm]()
            hasher.update(data)
            checksum = hasher.hexdigest()
            logger.debug(f"Calculated {algorithm} checksum for {len(data)} bytes: {checksum}")
            return checksum
        except Exception as e:
            logger.error(f"Error calculating checksum for bytes: {e}")
            raise
    
    def verify_checksum(self, 
                       file_obj: BinaryIO, 
                       expected_checksum: str, 
                       algorithm: str = DEFAULT_ALGORITHM) -> bool:
        """Verify that a file matches an expected checksum.
        
        Args:
            file_obj: File-like object to verify
            expected_checksum: Expected checksum value
            algorithm: Hash algorithm to use
            
        Returns:
            True if checksums match, False otherwise
        """
        try:
            calculated_checksum = self.calculate_checksum(file_obj, algorithm)
            match = calculated_checksum.lower() == expected_checksum.lower()
            
            if match:
                logger.debug(f"Checksum verification successful: {calculated_checksum}")
            else:
                logger.warning(f"Checksum mismatch: expected {expected_checksum}, "
                             f"got {calculated_checksum}")
            
            return match
        except Exception as e:
            logger.error(f"Error verifying checksum: {e}")
            return False
    
    def get_supported_algorithms(self) -> list[str]:
        """Get list of supported hash algorithms.
        
        Returns:
            List of supported algorithm names
        """
        return list(self.SUPPORTED_ALGORITHMS.keys())
    
    def is_algorithm_supported(self, algorithm: str) -> bool:
        """Check if a hash algorithm is supported.
        
        Args:
            algorithm: Algorithm name to check
            
        Returns:
            True if algorithm is supported, False otherwise
        """
        return algorithm.lower() in self.SUPPORTED_ALGORITHMS
    
    def get_algorithm_info(self, algorithm: str) -> dict:
        """Get information about a hash algorithm.
        
        Args:
            algorithm: Algorithm name
            
        Returns:
            Dictionary with algorithm information
            
        Raises:
            ValueError: If algorithm is not supported
        """
        algorithm = algorithm.lower()
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        # Calculate expected digest size
        hasher = self.SUPPORTED_ALGORITHMS[algorithm]()
        
        return {
            'name': algorithm,
            'digest_size': hasher.digest_size,
            'hex_length': hasher.digest_size * 2,
            'block_size': hasher.block_size if hasattr(hasher, 'block_size') else None
        }