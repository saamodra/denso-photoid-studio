#!/usr/bin/env python3
"""
Quick UI Test - Run specific window directly
Usage: python quick_test.py [window_name]
"""
import sys
import os
import argparse
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.session_manager import session_manager


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Quick UI tester untuk jendela tertentu."
    )
    parser.add_argument(
        "window",
        choices=["processing", "print", "selection", "main", "admin"],
        help="Jenis jendela yang ingin diuji.",
    )
    parser.add_argument(
        "--name",
        default="Muhammad Widodo",
        help="Nama pengguna contoh untuk pengujian ProcessingWindow.",
    )
    parser.add_argument(
        "--npk",
        default="2050501",
        help="NPK pengguna contoh untuk pengujian ProcessingWindow.",
    )
    parser.add_argument(
        "--role",
        default="operator",
        help="Peran pengguna contoh untuk pengujian ProcessingWindow.",
    )
    parser.add_argument(
        "--department",
        default="Produksi",
        help="Departemen pengguna contoh untuk pengujian ProcessingWindow.",
    )
    parser.add_argument(
        "--photo",
        help="Path foto lokal untuk pengujian ProcessingWindow.",
    )
    parser.add_argument(
        "--no-auto-process",
        action="store_false",
        dest="auto_process",
        help="Nonaktifkan pemrosesan otomatis saat ProcessingWindow dibuka.",
    )
    parser.set_defaults(auto_process=True)
    return parser.parse_args()


def set_test_session(args):
    """Set user session data for testing."""
    test_user = {
        "name": args.name,
        "npk": args.npk,
        "role": args.role,
        "department_name": args.department,
    }
    session_manager.current_user = test_user
    session_manager.is_logged_in = True
    session_manager.session_id = "quick_test_session"


DEFAULT_TEST_PHOTO = Path(__file__).parent / "assets" / "sample_photos" / "IMG_0014.JPG"


def resolve_test_photo(args):
    """Determine which photo path to use for the ProcessingWindow quick test."""

    if args.photo:
        photo_path = Path(args.photo).expanduser()
        if not photo_path.is_file():
            print(f"Foto tidak ditemukan: {photo_path}")
            sys.exit(1)
        return str(photo_path.resolve())

    if DEFAULT_TEST_PHOTO.is_file():
        return str(DEFAULT_TEST_PHOTO.resolve())

    print(f"Peringatan: foto default tidak ditemukan di {DEFAULT_TEST_PHOTO}")

    return None


def test_processing(args):
    """Quick test of processing window"""
    from ui.processing_window import ProcessingWindow
    photo_path = resolve_test_photo(args)

    if not photo_path:
        from PIL import Image
        import tempfile

        # Create fallback test image when no local photo provided
        test_image = Image.new("RGB", (400, 600), color="lightblue")
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        test_image.save(temp_file.name, "JPEG")
        photo_path = temp_file.name

    app = QApplication(sys.argv)
    set_test_session(args)
    window = ProcessingWindow(photo_path, debug_save=True)
    window.set_session_info(session_manager.get_current_user())

    if args.auto_process:
        # Mulai pemrosesan otomatis setelah event loop berjalan
        QTimer.singleShot(200, window.process_photo)

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
    args = parse_args()

    if args.window == "processing":
        test_processing(args)
    elif args.window == "print":
        test_print()
    elif args.window == "selection":
        test_selection()
    elif args.window == "main":
        test_main()
    elif args.window == "admin":
        test_admin()
