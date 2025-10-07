#!/usr/bin/env python3
"""
Database initialization script
"""

import asyncio
import sys
from database.connection import init_database

async def main():
    """Initialize the database"""
    try:
        print("Initializing database...")
        await init_database(force_recreate=True)
        print("[SUCCESS] Database initialized successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)