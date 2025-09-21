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
    'capture_format': 'jpg',
    'capture_quality': 95,
    'preview_fps': 30,
    'capture_count': 4,
    'capture_delay': 2.0  # seconds between captures
}

# Processing settings
PROCESSING_SETTINGS = {
    'background_removal_model': 'u2net',
    'output_resolution': (600, 800),  # High resolution for ID cards in portrait orientation (3:4 aspect ratio)
    'portrait_aspect_ratio': 3.0 / 4.0,  # Width/Height ratio for portrait ID card photos
    'supported_formats': ['jpg', 'png'],
    'temp_folder': 'temp/processed/',
    'capture_folder': 'temp/captures/'
}

# Print settings
PRINT_SETTINGS = {
    'default_paper_size': 'CR80',  # ID card standard
    'print_quality': 'high',
    'color_mode': 'color',
    'margins': (5, 5, 5, 5),  # mm
    'dpi': 300,
    'id_card_size': (85.6, 53.98)  # mm - standard CR80 size
}

# UI settings
UI_SETTINGS = {
    'window_size': (1280, 720),
    'camera_preview_size': (960, 720),
    'photo_grid_size': (2, 2),
    'theme': 'modern',
    'font_size': 12
}

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, 'backgrounds')
TEMPLATES_DIR = os.path.join(ASSETS_DIR, 'templates')
ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
CAPTURES_DIR = os.path.join(TEMP_DIR, 'captures')
PROCESSED_DIR = os.path.join(TEMP_DIR, 'processed')

# Ensure directories exist
for directory in [ASSETS_DIR, BACKGROUNDS_DIR, TEMPLATES_DIR, ICONS_DIR,
                  TEMP_DIR, CAPTURES_DIR, PROCESSED_DIR]:
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
            'x_offset_mm': 18.3,  # Center position from left edge
            'y_offset_mm': 16.0,  # Distance from top edge
        },
        'name': 'DENSO ID Card Template'
    }
}
