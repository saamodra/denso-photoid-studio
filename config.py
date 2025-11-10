"""
Configuration settings for ID Card Photo Machine
"""
import os

# Application settings
APP_NAME = "ID Card Photo Machine"
APP_VERSION = "1.0.0"

# Camera settings
CAMERA_SETTINGS = {
    'default_resolution': (1920, 1080),
    'capture_quality': 95,
    'preview_fps': 30,
    'capture_count': 4,
    'capture_delay': 2.0  # seconds between captures
}

# Processing settings
PROCESSING_SETTINGS = {
    'background_removal_model': 'u2net',
    'portrait_aspect_ratio': 3.0 / 4.0,  # Width/Height ratio for portrait ID card photos
}

# Print settings
PRINT_SETTINGS = {
    'id_card_size': (53.98, 85.6),  # mm - standard CR80 size
    'dpi': 300  # Dots per inch for printing
}

# UI settings
UI_SETTINGS = {
    'camera_preview_size': (960, 720),
    'font_size': 12
}

# Database settings
DATABASE_SETTINGS = {
    'db_path': 'data/photoid_studio.db',
    'backup_path': 'data/backups',
    'max_connections': 10,
    'timeout': 30.0
}

import sys

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# When running under PyInstaller, assets are unpacked under sys._MEIPASS.
# Point ASSETS_DIR there so resource loading works in packaged builds.
if hasattr(sys, '_MEIPASS'):
    ASSETS_DIR = os.path.join(sys._MEIPASS, 'assets')
else:
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, 'backgrounds')
TEMPLATES_DIR = os.path.join(ASSETS_DIR, 'templates')
ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
CAPTURES_DIR = os.path.join(TEMP_DIR, 'captures')
PROCESSED_DIR = os.path.join(TEMP_DIR, 'processed')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Pastikan hanya direktori yang dapat ditulis yang dibuat.
# Direktori assets/templates/icons dibundel saat packaging dan tidak perlu dibuat.
for directory in [TEMP_DIR, CAPTURES_DIR, PROCESSED_DIR, DATA_DIR]:
    os.makedirs(directory, exist_ok=True)

# Background templates
BACKGROUND_TEMPLATES = {
    'blue_solid': '#4A90E2',
    'white_solid': '#FFFFFF',
    'light_blue': '#E3F2FD',
    'gradient_blue': 'gradient_blue.png',
    'professional_gray': '#F5F5F5'
}

# ID Card templates with positioning specifications
ID_CARD_TEMPLATES = {
    'denso_id_card': {
        'file': 'id_card.png',
        'photo_area': {
            'width_mm': 30.0,
            'height_mm': 37.0,
            'x_offset_mm': 18.1,  # Center position from left edge
            'y_offset_mm': 25.0,  # Distance from top edge
        },
        'name': 'DENSO ID Card Template'
    }
}
