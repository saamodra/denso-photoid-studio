#!/usr/bin/env python3
"""
Database initialization script for ID Card Photo Machine
This script initializes the database and runs migrations
"""
import sys
import os
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import DatabaseManager
from migrations.migration_manager import MigrationManager
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with migrations"""
    try:
        logger.info("Starting database initialization...")

        # Initialize database manager
        db_path = config.DATABASE_SETTINGS['db_path']
        logger.info(f"Database path: {db_path}")

        # Create database manager (this will create tables if they don't exist)
        db_manager = DatabaseManager(db_path)
        logger.info("Database manager initialized")

        # Run migrations
        migration_manager = MigrationManager(db_path)
        logger.info("Running migrations...")

        if migration_manager.run_migrations():
            logger.info("Migrations completed successfully")
        else:
            logger.error("Migration failed")
            return False

        # Check migration status
        status = migration_manager.get_migration_status()
        logger.info(f"Migration status: {status['applied_count']} applied, {status['pending_count']} pending")

        # Test database connection
        logger.info("Testing database connection...")
        users = db_manager.get_all_users()
        logger.info(f"Database connection successful. Found {len(users)} users")

        # Display database info
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETED")
        print("="*60)
        print(f"Database Path: {os.path.abspath(db_path)}")
        print(f"Applied Migrations: {status['applied_count']}")
        print(f"Pending Migrations: {status['pending_count']}")

        if status['applied_migrations']:
            print("\nApplied Migrations:")
            for migration in status['applied_migrations']:
                print(f"  ✓ {migration}")

        if status['pending_migrations']:
            print("\nPending Migrations:")
            for migration in status['pending_migrations']:
                print(f"  ⏳ {migration}")

        print("\nDatabase is ready for use!")
        print("="*60)

        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def show_database_info():
    """Show current database information"""
    try:
        db_path = config.DATABASE_SETTINGS['db_path']

        if not os.path.exists(db_path):
            print("Database does not exist yet. Run init_database() first.")
            return

        db_manager = DatabaseManager(db_path)
        migration_manager = MigrationManager(db_path)

        # Get database info
        users = db_manager.get_all_users()
        photo_histories = db_manager.get_photo_histories()
        request_histories = db_manager.get_request_histories()
        status = migration_manager.get_migration_status()

        print("\n" + "="*60)
        print("DATABASE INFORMATION")
        print("="*60)
        print(f"Database Path: {os.path.abspath(db_path)}")
        print(f"Database Size: {os.path.getsize(db_path) / 1024:.2f} KB")
        print(f"Created: {datetime.fromtimestamp(os.path.getctime(db_path))}")
        print(f"Modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
        print(f"\nApplied Migrations: {status['applied_count']}")
        print(f"Pending Migrations: {status['pending_count']}")
        print(f"\nRecords:")
        print(f"  Users: {len(users)}")
        print(f"  Photo Histories: {len(photo_histories)}")
        print(f"  Request Histories: {len(request_histories)}")
        print("="*60)

    except Exception as e:
        logger.error(f"Failed to get database info: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "info":
        show_database_info()
    else:
        success = init_database()
        if not success:
            sys.exit(1)
