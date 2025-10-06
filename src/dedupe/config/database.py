"""Database connection and session management for dedupe-tarball.

This module provides database connection pooling, session management,
and schema creation functionality.
"""

import os
import logging
from typing import Optional, Dict, Any
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
import toml

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration management."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize database configuration.
        
        Args:
            config_path: Path to configuration file. If None, uses default locations.
        """
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or environment variables."""
        config = {
            'database': {
                'url': os.getenv('DATABASE_URL', 'postgresql://dedupe_user:password@localhost:5432/dedupe_db'),
                'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
                'timeout': int(os.getenv('DB_TIMEOUT', '30'))
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = toml.load(f)
                    config.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return config
    
    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return self.config['database']['url']
    
    @property
    def pool_size(self) -> int:
        """Get database pool size."""
        return self.config['database']['pool_size']
    
    @property
    def timeout(self) -> int:
        """Get database timeout."""
        return self.config['database']['timeout']


class DatabaseConnectionPool:
    """Database connection pool manager."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize connection pool.
        
        Args:
            config: Database configuration
        """
        self.config = config
        self._pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        
    def initialize(self):
        """Initialize the connection pool."""
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                1,  # minimum connections
                self.config.pool_size,  # maximum connections
                self.config.connection_string,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            logger.info(f"Database pool initialized with {self.config.pool_size} connections")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        if not self._pool:
            self.initialize()
        
        try:
            conn = self._pool.getconn()
            conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
            return conn
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        if self._pool and conn:
            self._pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("Database pool closed")
    
    @property
    def maxconn(self) -> int:
        """Get maximum connections (for contract testing)."""
        return self.config.pool_size
    
    @property
    def timeout(self) -> int:
        """Get connection timeout (for contract testing)."""
        return self.config.timeout


# Global connection pool instance
_connection_pool: Optional[DatabaseConnectionPool] = None


def get_connection_pool() -> DatabaseConnectionPool:
    """Get the global connection pool instance."""
    global _connection_pool
    if not _connection_pool:
        config = DatabaseConfig()
        _connection_pool = DatabaseConnectionPool(config)
        _connection_pool.initialize()
    return _connection_pool


def get_connection():
    """Get a database connection from the pool."""
    pool = get_connection_pool()
    return pool.get_connection()


def create_schema():
    """Create database schema from SQL file."""
    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', 'schema.sql')
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        logger.info("Database schema created successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to create schema: {e}")
        raise
    finally:
        if conn:
            pool = get_connection_pool()
            pool.return_connection(conn)


def test_connection() -> bool:
    """Test database connectivity."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        pool = get_connection_pool()
        pool.return_connection(conn)
        return result is not None
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False