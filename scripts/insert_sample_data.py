#!/usr/bin/env python3
"""
Sample data insertion script for ID Card Photo Machine
This script inserts sample data into the database for testing purposes
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import DatabaseManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_sample_data():
    """Insert sample data into the database"""
    db = DatabaseManager()

    logger.info("Starting sample data insertion...")

    # Sample users data
    sample_users = [
        {
            'npk': 'EMP001',
            'name': 'John Doe',
            'password': 'password123',
            'role': 'admin',
            'section_id': 'SEC001',
            'section_name': 'IT Department',
            'department_id': 'DEPT001',
            'department_name': 'Information Technology',
            'company': 'DENSO Corporation',
            'plant': 'Plant A',
            'last_access': datetime.now() - timedelta(days=1),
            'last_take_photo': datetime.now() - timedelta(days=2),
            'photo_filename': 'john_doe_photo.jpg',
            'card_filename': 'john_doe_card.jpg'
        },
        {
            'npk': 'EMP002',
            'name': 'Jane Smith',
            'password': 'password123',
            'role': 'user',
            'section_id': 'SEC002',
            'section_name': 'HR Department',
            'department_id': 'DEPT002',
            'department_name': 'Human Resources',
            'company': 'DENSO Corporation',
            'plant': 'Plant A',
            'last_access': datetime.now() - timedelta(hours=5),
            'last_take_photo': datetime.now() - timedelta(days=1),
            'photo_filename': 'jane_smith_photo.jpg',
            'card_filename': 'jane_smith_card.jpg'
        },
        {
            'npk': 'EMP003',
            'name': 'Mike Johnson',
            'password': 'password123',
            'role': 'user',
            'section_id': 'SEC003',
            'section_name': 'Production',
            'department_id': 'DEPT003',
            'department_name': 'Manufacturing',
            'company': 'DENSO Corporation',
            'plant': 'Plant B',
            'last_access': datetime.now() - timedelta(hours=2),
            'last_take_photo': None,
            'photo_filename': None,
            'card_filename': None
        },
        {
            'npk': 'EMP004',
            'name': 'Sarah Wilson',
            'password': 'password123',
            'role': 'supervisor',
            'section_id': 'SEC001',
            'section_name': 'IT Department',
            'department_id': 'DEPT001',
            'department_name': 'Information Technology',
            'company': 'DENSO Corporation',
            'plant': 'Plant A',
            'last_access': datetime.now() - timedelta(minutes=30),
            'last_take_photo': datetime.now() - timedelta(hours=3),
            'photo_filename': 'sarah_wilson_photo.jpg',
            'card_filename': 'sarah_wilson_card.jpg'
        },
        {
            'npk': 'EMP005',
            'name': 'David Brown',
            'password': 'password123',
            'role': 'user',
            'section_id': 'SEC004',
            'section_name': 'Quality Control',
            'department_id': 'DEPT004',
            'department_name': 'Quality Assurance',
            'company': 'DENSO Corporation',
            'plant': 'Plant B',
            'last_access': datetime.now() - timedelta(days=3),
            'last_take_photo': datetime.now() - timedelta(days=5),
            'photo_filename': 'david_brown_photo.jpg',
            'card_filename': 'david_brown_card.jpg'
        }
    ]

    # Insert users
    logger.info("Inserting sample users...")
    for user in sample_users:
        if db.create_user(user):
            logger.info(f"Created user: {user['name']} ({user['npk']})")
        else:
            logger.warning(f"Failed to create user: {user['name']} ({user['npk']})")

    # Sample photo histories
    logger.info("Inserting sample photo histories...")
    photo_histories = [
        ('EMP001', datetime.now() - timedelta(days=2)),
        ('EMP001', datetime.now() - timedelta(days=5)),
        ('EMP001', datetime.now() - timedelta(days=10)),
        ('EMP002', datetime.now() - timedelta(days=1)),
        ('EMP002', datetime.now() - timedelta(days=3)),
        ('EMP004', datetime.now() - timedelta(hours=3)),
        ('EMP004', datetime.now() - timedelta(days=1)),
        ('EMP005', datetime.now() - timedelta(days=5)),
        ('EMP005', datetime.now() - timedelta(days=8)),
        ('EMP005', datetime.now() - timedelta(days=15))
    ]

    for npk, photo_time in photo_histories:
        if db.add_photo_history(npk, photo_time):
            logger.info(f"Added photo history for {npk} at {photo_time}")
        else:
            logger.warning(f"Failed to add photo history for {npk}")

    # Sample request histories
    logger.info("Inserting sample request histories...")
    request_histories = [
        ('EMP001', 'Request for new ID card due to damage', 'completed', 'Card replaced successfully', 'Admin User'),
        ('EMP002', 'Request for photo retake', 'completed', 'Photo retaken and updated', 'Admin User'),
        ('EMP003', 'Request for first-time ID card creation', 'requested', None, None),
        ('EMP004', 'Request for card replacement', 'in_progress', 'Processing replacement', 'Admin User'),
        ('EMP005', 'Request for photo update', 'completed', 'Photo updated successfully', 'Admin User'),
        ('EMP001', 'Request for emergency card replacement', 'completed', 'Emergency card issued', 'Supervisor'),
        ('EMP002', 'Request for card reprint', 'requested', None, None),
        ('EMP004', 'Request for card information update', 'completed', 'Information updated', 'Admin User')
    ]

    for npk, request_desc, status, remark, respons_name in request_histories:
        if db.add_request_history(npk, request_desc, status, remark, respons_name):
            logger.info(f"Added request history for {npk}: {request_desc}")
        else:
            logger.warning(f"Failed to add request history for {npk}")

    # Sample app configurations
    logger.info("Inserting sample app configurations...")
    app_configs = [
        ('image_save_path', 'images'),
        ('photo_count', '4'),
        ('capture_delay', '2'),
        ('default_camera', 'Camera 1'),
        ('default_printer', 'Default Printer'),
    ]

    for name, value in app_configs:
        if db.set_app_config(name, value):
            logger.info(f"Set config {name} = {value}")
        else:
            logger.warning(f"Failed to set config {name}")

    logger.info("Sample data insertion completed!")

    # Display summary
    users = db.get_all_users()
    photo_histories = db.get_photo_histories()
    request_histories = db.get_request_histories()

    print("\n" + "="*50)
    print("SAMPLE DATA SUMMARY")
    print("="*50)
    print(f"Users created: {len(users)}")
    print(f"Photo histories: {len(photo_histories)}")
    print(f"Request histories: {len(request_histories)}")
    print("\nUsers:")
    for user in users:
        print(f"  - {user['name']} ({user['npk']}) - {user['role']}")
    print("="*50)

if __name__ == "__main__":
    try:
        insert_sample_data()
    except Exception as e:
        logger.error(f"Sample data insertion failed: {e}")
        sys.exit(1)
