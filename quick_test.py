#!/usr/bin/env python3
"""
Quick UI Test - Run specific window directly
Usage: python quick_test.py [window_name]
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_processing():
    """Quick test of processing window"""
    from ui.processing_window import ProcessingWindow
    from PIL import Image
    import tempfile

    # Create test image
    test_image = Image.new('RGB', (400, 600), color='lightblue')
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    test_image.save(temp_file.name, 'JPEG')

    app = QApplication(sys.argv)
    window = ProcessingWindow(temp_file.name)
    window.show()
    return app.exec()

def test_print():
    """Quick test of print window"""
    from ui.print_window import PrintWindow
    from PIL import Image

    # Create test processed image
    test_image = Image.new('RGB', (360, 480), color='blue')

    app = QApplication(sys.argv)
    window = PrintWindow(test_image)
    window.show()
    return app.exec()

def test_selection():
    """Quick test of selection window"""
    from ui.selection_window import SelectionWindow
    from PIL import Image
    import tempfile

    # Create test photos
    test_photos = []
    for i in range(4):
        test_image = Image.new('RGB', (400, 600), color=f'hsl({i*90}, 70%, 80%)')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        test_image.save(temp_file.name, 'JPEG')
        test_photos.append(temp_file.name)

    app = QApplication(sys.argv)
    window = SelectionWindow(test_photos)
    window.show()
    return app.exec()

def test_main():
    """Quick test of main window"""
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

def test_admin():
    """Quick test of admin window"""
    from ui.admin_window import AdminWindow

    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_test.py [processing|print|selection|main|admin]")
        sys.exit(1)

    window_type = sys.argv[1].lower()

    if window_type == 'processing':
        test_processing()
    elif window_type == 'print':
        test_print()
    elif window_type == 'selection':
        test_selection()
    elif window_type == 'main':
        test_main()
    elif window_type == 'admin':
        test_admin()
    else:
        print(f"Unknown window: {window_type}")
        print("Available: processing, print, selection, main, admin")
