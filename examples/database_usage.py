#!/usr/bin/env python3
"""
Database Usage Examples for ID Card Photo Machine
This script demonstrates how to use the database module
"""
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_user_management():
    """Example: User management operations"""
    print("\n" + "="*50)
    print("USER MANAGEMENT EXAMPLES")
    print("="*50)

    # Get all users
    users = db_manager.get_all_users()
    print(f"Total users in database: {len(users)}")

    # Display users
    for user in users:
        print(f"  - {user['name']} ({user['npk']}) - {user['role']} - {user['section_name']}")

    # Get specific user
    if users:
        first_user = users[0]
        user_detail = db_manager.get_user_by_npk(first_user['npk'])
        print(f"\nUser details for {first_user['name']}:")
        print(f"  Department: {user_detail['department_name']}")
        print(f"  Company: {user_detail['company']}")
        print(f"  Last Access: {user_detail['last_access']}")

def example_photo_histories():
    """Example: Photo history operations"""
    print("\n" + "="*50)
    print("PHOTO HISTORY EXAMPLES")
    print("="*50)

    # Get all photo histories
    photo_histories = db_manager.get_photo_histories()
    print(f"Total photo histories: {len(photo_histories)}")

    # Get recent photo histories (last 5)
    recent_photos = photo_histories[:5]
    print("\nRecent photo captures:")
    for photo in recent_photos:
        print(f"  - {photo['npk']} at {photo['photo_time']}")

    # Get photo histories for specific user
    if photo_histories:
        user_npk = photo_histories[0]['npk']
        user_photos = db_manager.get_photo_histories(user_npk)
        print(f"\nPhoto histories for user {user_npk}: {len(user_photos)}")

def example_request_histories():
    """Example: Request history operations"""
    print("\n" + "="*50)
    print("REQUEST HISTORY EXAMPLES")
    print("="*50)

    # Get all request histories
    request_histories = db_manager.get_request_histories()
    print(f"Total request histories: {len(request_histories)}")

    # Group by status
    status_counts = {}
    for req in request_histories:
        status = req['status'] or 'unknown'
        status_counts[status] = status_counts.get(status, 0) + 1

    print("\nRequest status summary:")
    for status, count in status_counts.items():
        print(f"  - {status}: {count}")

    # Show requested requests
    requested_requests = [req for req in request_histories if req['status'] == 'requested']
    print(f"\nRequested requests: {len(requested_requests)}")
    for req in requested_requests:
        print(f"  - {req['npk']}: {req['request_desc']}")

def example_app_config():
    """Example: Application configuration operations"""
    print("\n" + "="*50)
    print("APPLICATION CONFIGURATION EXAMPLES")
    print("="*50)

    # Get some configuration values
    configs_to_check = [
        'app_name',
        'app_version',
        'maintenance_mode',
        'max_photo_size_mb',
        'system_language',
        'timezone'
    ]

    print("Current configuration values:")
    for config_name in configs_to_check:
        value = db_manager.get_app_config(config_name)
        print(f"  - {config_name}: {value}")

    # Update a configuration
    print("\nUpdating configuration...")
    db_manager.set_app_config('last_updated', datetime.now().isoformat())
    updated_value = db_manager.get_app_config('last_updated')
    print(f"  - last_updated: {updated_value}")

def example_adding_new_data():
    """Example: Adding new data to the database"""
    print("\n" + "="*50)
    print("ADDING NEW DATA EXAMPLES")
    print("="*50)

    # Add a new photo history for existing user
    users = db_manager.get_all_users()
    if users:
        user_npk = users[0]['npk']
        print(f"Adding photo history for user {user_npk}...")

        if db_manager.add_photo_history(user_npk):
            print("✓ Photo history added successfully")
        else:
            print("✗ Failed to add photo history")

    # Add a new request
    if users:
        user_npk = users[0]['npk']
        print(f"Adding request for user {user_npk}...")

        if db_manager.add_request_history(
            user_npk,
            "Example request from script",
            "requested",
            "This is an example request"
        ):
            print("✓ Request added successfully")
        else:
            print("✗ Failed to add request")

def example_database_queries():
    """Example: Custom database queries"""
    print("\n" + "="*50)
    print("CUSTOM DATABASE QUERIES EXAMPLES")
    print("="*50)

    # Query: Users by role
    admin_users = db_manager.execute_query(
        "SELECT name, npk, section_name FROM users WHERE role = ?",
        ('admin',)
    )
    print(f"Admin users: {len(admin_users)}")
    for user in admin_users:
        print(f"  - {user['name']} ({user['npk']}) - {user['section_name']}")

    # Query: Recent photo activities
    recent_photos = db_manager.execute_query("""
        SELECT u.name, ph.photo_time
        FROM photo_histories ph
        JOIN users u ON ph.npk = u.npk
        ORDER BY ph.photo_time DESC
        LIMIT 5
    """)
    print(f"\nRecent photo activities:")
    for photo in recent_photos:
        print(f"  - {photo['name']} at {photo['photo_time']}")

    # Query: Request statistics
    request_stats = db_manager.execute_query("""
        SELECT status, COUNT(*) as count
        FROM request_histories
        GROUP BY status
        ORDER BY count DESC
    """)
    print(f"\nRequest statistics:")
    for stat in request_stats:
        print(f"  - {stat['status']}: {stat['count']}")

def main():
    """Run all examples"""
    print("Database Usage Examples for ID Card Photo Machine")
    print("=" * 60)

    try:
        example_user_management()
        example_photo_histories()
        example_request_histories()
        example_app_config()
        example_adding_new_data()
        example_database_queries()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        logger.error(f"Example execution failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
