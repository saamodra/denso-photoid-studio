#!/usr/bin/env python3
"""
Script to create sample users with encrypted passwords for testing
"""
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import db_manager

def create_sample_users():
    """Create sample users for testing the authentication system"""

    # Sample users data
    sample_users = [
        {
            'npk': 'ADMIN001',
            'name': 'Administrator',
            'role': 'admin',
            'section_id': 'IT',
            'section_name': 'Information Technology',
            'department_id': 'ITD',
            'department_name': 'IT Department',
            'company': 'Denso',
            'plant': 'Plant 1',
            'password': 'admin123'  # This will be encrypted
        },
        {
            'npk': 'USER001',
            'name': 'John Doe',
            'role': 'user',
            'section_id': 'PROD',
            'section_name': 'Production',
            'department_id': 'MFG',
            'department_name': 'Manufacturing',
            'company': 'Denso',
            'plant': 'Plant 1',
            'password': 'user123'  # This will be encrypted
        },
        {
            'npk': 'USER002',
            'name': 'Jane Smith',
            'role': 'user',
            'section_id': 'QA',
            'section_name': 'Quality Assurance',
            'department_id': 'QAD',
            'department_name': 'Quality Department',
            'company': 'Denso',
            'plant': 'Plant 1',
            'password': 'password123'  # This will be encrypted
        },
        {
            'npk': 'MANAGER001',
            'name': 'Manager User',
            'role': 'manager',
            'section_id': 'MGT',
            'section_name': 'Management',
            'department_id': 'MGT',
            'department_name': 'Management',
            'company': 'Denso',
            'plant': 'Plant 1',
            'password': 'manager123'  # This will be encrypted
        }
    ]

    print("Creating sample users with encrypted passwords...")

    created_count = 0
    failed_count = 0

    for user_data in sample_users:
        try:
            # Extract password before creating user
            password = user_data.pop('password')

            # Create user with encrypted password
            success = db_manager.create_user_with_password(user_data, password)

            if success:
                print(f"✓ Created user: {user_data['name']} (NPK: {user_data['npk']})")
                created_count += 1
            else:
                print(f"✗ Failed to create user: {user_data['name']} (NPK: {user_data['npk']})")
                failed_count += 1

        except Exception as e:
            print(f"✗ Error creating user {user_data.get('name', 'Unknown')}: {e}")
            failed_count += 1

    print(f"\nSummary:")
    print(f"Successfully created: {created_count} users")
    print(f"Failed to create: {failed_count} users")

    if created_count > 0:
        print(f"\nSample login credentials:")
        print(f"Admin: NPK=ADMIN001, Password=admin123")
        print(f"User: NPK=USER001, Password=user123")
        print(f"User: NPK=USER002, Password=password123")
        print(f"Manager: NPK=MANAGER001, Password=manager123")

def list_existing_users():
    """List all existing users in the database"""
    print("\nExisting users in database:")
    users = db_manager.get_all_users()

    if not users:
        print("No users found in database.")
        return

    for user in users:
        print(f"NPK: {user['npk']}, Name: {user['name']}, Role: {user['role']}")

if __name__ == "__main__":
    print("Sample User Creation Script")
    print("=" * 40)

    # List existing users first
    list_existing_users()

    # Create sample users
    create_sample_users()

    print("\nScript completed.")
