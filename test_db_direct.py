#!/usr/bin/env python3
"""
Direct database connection test without Docker.
"""
import os
import sys
from sqlalchemy import create_engine
from config.settings import get_settings

def main():
    # Get settings
    settings = get_settings()
    
    print(f"Database URL: {settings.database_url}")
    print(f"Port: {settings.db_port}")
    print(f"Host: {settings.db_host}")
    
    # Create database engine
    engine = create_engine(settings.database_url, connect_args={"connect_timeout": 10})
    
    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)