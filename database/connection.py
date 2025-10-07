import sqlite3
import aiosqlite
from typing import Optional
import os
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_PATH = "blood_donation.db"
TEST_DATABASE_PATH = "test_blood_donation.db"


class DatabaseConnection:
    """Singleton class to manage database connections."""
    
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[aiosqlite.Connection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    async def connect(self, database_path: str = DATABASE_PATH) -> aiosqlite.Connection:
        """Establish database connection."""
        if self._connection is None:
            try:
                self._connection = await aiosqlite.connect(database_path)
                # Enable foreign key constraints
                await self._connection.execute("PRAGMA foreign_keys = ON")
                await self._connection.commit()
                logger.info(f"Connected to database: {database_path}")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise
        return self._connection
    
    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    async def get_connection(self) -> aiosqlite.Connection:
        """Get current database connection."""
        if self._connection is None:
            await self.connect()
        return self._connection


# Global database connection instance
db_connection = DatabaseConnection()


async def get_database_connection(database_path: str = DATABASE_PATH) -> aiosqlite.Connection:
    """
    Get database connection.
    
    Args:
        database_path: Path to the SQLite database file
        
    Returns:
        aiosqlite.Connection: Database connection object
    """
    return await db_connection.connect(database_path)


async def close_database_connection():
    """Close the database connection."""
    await db_connection.close()


@asynccontextmanager
async def get_db_session(database_path: str = DATABASE_PATH):
    """
    Context manager for database sessions.
    
    Args:
        database_path: Path to the SQLite database file
        
    Yields:
        aiosqlite.Connection: Database connection object
    """
    connection = None
    try:
        connection = await aiosqlite.connect(database_path)
        # Enable foreign key constraints
        await connection.execute("PRAGMA foreign_keys = ON")
        yield connection
    except Exception as e:
        if connection:
            await connection.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        if connection:
            await connection.close()


async def init_database(database_path: str = DATABASE_PATH, force_recreate: bool = False):
    """
    Initialize the database by creating tables.
    
    Args:
        database_path: Path to the SQLite database file
        force_recreate: If True, drop existing tables and recreate them
    """
    from .schema import create_tables, drop_tables
    
    try:
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(database_path), exist_ok=True) if os.path.dirname(database_path) else None
        
        async with get_db_session(database_path) as connection:
            if force_recreate:
                logger.info("Dropping existing tables...")
                await drop_tables(connection)
            
            logger.info("Creating database tables...")
            await create_tables(connection)
            await connection.commit()
            logger.info(f"Database initialized successfully: {database_path}")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_test_database_path() -> str:
    """Get path for test database."""
    return TEST_DATABASE_PATH


def cleanup_test_database():
    """Remove test database file if it exists."""
    if os.path.exists(TEST_DATABASE_PATH):
        os.remove(TEST_DATABASE_PATH)
        logger.info("Test database cleaned up")


async def execute_query(query: str, params: tuple = (), database_path: str = DATABASE_PATH) -> list:
    """
    Execute a SELECT query and return results.
    
    Args:
        query: SQL query string
        params: Query parameters
        database_path: Path to database file
        
    Returns:
        List of query results
    """
    async with get_db_session(database_path) as connection:
        cursor = await connection.execute(query, params)
        results = await cursor.fetchall()
        return results


async def execute_insert(query: str, params: tuple = (), database_path: str = DATABASE_PATH) -> int:
    """
    Execute an INSERT query and return the last row ID.
    
    Args:
        query: SQL INSERT query string
        params: Query parameters
        database_path: Path to database file
        
    Returns:
        Last inserted row ID
    """
    async with get_db_session(database_path) as connection:
        cursor = await connection.execute(query, params)
        await connection.commit()
        return cursor.lastrowid


async def execute_update(query: str, params: tuple = (), database_path: str = DATABASE_PATH) -> int:
    """
    Execute an UPDATE or DELETE query and return affected rows count.
    
    Args:
        query: SQL UPDATE/DELETE query string
        params: Query parameters
        database_path: Path to database file
        
    Returns:
        Number of affected rows
    """
    async with get_db_session(database_path) as connection:
        cursor = await connection.execute(query, params)
        await connection.commit()
        return cursor.rowcount