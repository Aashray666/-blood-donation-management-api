import aiosqlite
import logging

logger = logging.getLogger(__name__)

# SQL statements for creating tables
CREATE_DONORS_TABLE = """
CREATE TABLE IF NOT EXISTS donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    blood_group VARCHAR(3) NOT NULL CHECK (blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    city VARCHAR(100) NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_BLOOD_REQUESTS_TABLE = """
CREATE TABLE IF NOT EXISTS blood_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name VARCHAR(100) NOT NULL,
    blood_group VARCHAR(3) NOT NULL CHECK (blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    city VARCHAR(100) NOT NULL,
    urgency VARCHAR(10) NOT NULL CHECK (urgency IN ('Low', 'Medium', 'High', 'Critical')),
    hospital_name VARCHAR(100),
    contact_number VARCHAR(15) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Fulfilled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# SQL statements for creating indexes
CREATE_DONORS_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_donors_blood_group ON donors(blood_group);",
    "CREATE INDEX IF NOT EXISTS idx_donors_city ON donors(city);",
    "CREATE INDEX IF NOT EXISTS idx_donors_blood_group_city ON donors(blood_group, city);"
]

CREATE_BLOOD_REQUESTS_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_blood_requests_blood_group ON blood_requests(blood_group);",
    "CREATE INDEX IF NOT EXISTS idx_blood_requests_city ON blood_requests(city);",
    "CREATE INDEX IF NOT EXISTS idx_blood_requests_status ON blood_requests(status);",
    "CREATE INDEX IF NOT EXISTS idx_blood_requests_urgency ON blood_requests(urgency);",
    "CREATE INDEX IF NOT EXISTS idx_blood_requests_blood_group_city ON blood_requests(blood_group, city);"
]

# SQL statements for dropping tables
DROP_TABLES = [
    "DROP TABLE IF EXISTS blood_requests;",
    "DROP TABLE IF EXISTS donors;"
]


async def create_tables(connection: aiosqlite.Connection):
    """
    Create all database tables and indexes.
    
    Args:
        connection: Database connection object
    """
    try:
        # Create donors table
        await connection.execute(CREATE_DONORS_TABLE)
        logger.info("Created donors table")
        
        # Create blood_requests table
        await connection.execute(CREATE_BLOOD_REQUESTS_TABLE)
        logger.info("Created blood_requests table")
        
        # Create indexes for donors table
        for index_sql in CREATE_DONORS_INDEXES:
            await connection.execute(index_sql)
        logger.info("Created indexes for donors table")
        
        # Create indexes for blood_requests table
        for index_sql in CREATE_BLOOD_REQUESTS_INDEXES:
            await connection.execute(index_sql)
        logger.info("Created indexes for blood_requests table")
        
        await connection.commit()
        logger.info("All database tables and indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        await connection.rollback()
        raise


async def drop_tables(connection: aiosqlite.Connection):
    """
    Drop all database tables.
    
    Args:
        connection: Database connection object
    """
    try:
        for drop_sql in DROP_TABLES:
            await connection.execute(drop_sql)
        
        await connection.commit()
        logger.info("All database tables dropped successfully")
        
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        await connection.rollback()
        raise


async def get_table_info(connection: aiosqlite.Connection, table_name: str) -> list:
    """
    Get information about a table structure.
    
    Args:
        connection: Database connection object
        table_name: Name of the table
        
    Returns:
        List of column information
    """
    cursor = await connection.execute(f"PRAGMA table_info({table_name})")
    return await cursor.fetchall()


async def check_table_exists(connection: aiosqlite.Connection, table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        connection: Database connection object
        table_name: Name of the table to check
        
    Returns:
        True if table exists, False otherwise
    """
    cursor = await connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    result = await cursor.fetchone()
    return result is not None


async def get_database_version(connection: aiosqlite.Connection) -> str:
    """
    Get SQLite version information.
    
    Args:
        connection: Database connection object
        
    Returns:
        SQLite version string
    """
    cursor = await connection.execute("SELECT sqlite_version()")
    result = await cursor.fetchone()
    return result[0] if result else "Unknown"