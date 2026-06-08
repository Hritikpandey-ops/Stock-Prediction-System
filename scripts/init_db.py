#!/usr/bin/env python3
"""
Initialize database tables.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import init_db, test_connection
from loguru import logger

def main():
    logger.info("Initializing database...")
    
    # Test connection
    if not test_connection():
        logger.error("Failed to connect to database")
        return False
    
    # Create tables
    try:
        init_db()
        logger.info("Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)