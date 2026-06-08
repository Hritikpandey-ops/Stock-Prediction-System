#!/usr/bin/env python3
"""
Simple database connection test with retry logic.
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config.settings import get_settings

def main():
    # Get settings
    settings = get_settings()
    
    print(f"Database URL: {settings.database_url}")
    print(f"Port: {settings.db_port}")
    print(f"Host: {settings.db_host}")
    
    # Create database engine
    engine = create_engine(
        settings.database_url,
        connect_args={"connect_timeout": 10},
        pool_pre_ping=True
    )
    
    # Try connecting with retries
    for attempt in range(5):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"❌ Attempt {attempt+1} failed: {e}")
            if attempt < 4:
                print("Waiting 5 seconds before retry...")
                time.sleep(5)
            else:
                print("Max retries reached.")
                return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)