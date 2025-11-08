#!/usr/bin/env python3
"""
Quick UI Test - Run specific window directly
Usage: python quick_test.py [window_name]
"""
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CAMERA_SETTINGS, CAPTURES_DIR, UI_SETTINGS
from modules.camera_manager import CameraManager
from modules.database import db_manager
from modules.session_manager import session_manager


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Quick UI tester untuk jendela tertentu."
    )
    parser.add_argument(
        "window",
        choices=["processing", "print", "selection", "main", "admin", "camera"],
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
        "--real-camera",
        action="store_true",
        help="Gunakan kamera fisik saat menguji jendela kamera.",
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


class MockCameraManager(CameraManager):
    """Kamera tiruan agar CameraWindow dapat diuji tanpa perangkat keras."""

    def __init__(self, fps: int = 15):
        self._mock_cameras = [{
            "index": 0,
            "backend": None,
            "name": "Mock Camera",
            "resolution": UI_SETTINGS["camera_preview_size"],
        }]
        self._fps = max(1, fps)
        self._preview_timer: QTimer | None = None
        self._frame_callback = None
        self._tick = 0
        super().__init__()
        self.available_cameras = list(self._mock_cameras)
        self.current_camera_index = 0
        self.camera_thread = None

    def detect_cameras(self):
        """Lewati deteksi hardware dan gunakan konfigurasi mock."""
        return list(self._mock_cameras)

    def start_preview(self, frame_callback=None):
        """Mulai timer yang memancarkan frame simulasi."""
        self.stop_preview()
        self._frame_callback = frame_callback
        if self._preview_timer is None:
            self._preview_timer = QTimer()
            self._preview_timer.timeout.connect(self._emit_frame)

        interval = max(1, int(1000 / self._fps))
        self._preview_timer.start(interval)

    def stop_preview(self):
        """Hentikan timer simulasi."""
        if self._preview_timer and self._preview_timer.isActive():
            self._preview_timer.stop()
        self._frame_callback = None
        self.camera_thread = None

    def capture_photo(self, save_path=None):
        """Simpan frame terakhir agar alur capture tetap berjalan."""
        frame = self.current_frame.copy() if self.current_frame is not None else self._generate_frame()

        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            os.makedirs(CAPTURES_DIR, exist_ok=True)
            save_path = os.path.join(CAPTURES_DIR, f"mock_capture_{timestamp}.jpg")

        cv2.imwrite(save_path, frame, [cv2.IMWRITE_JPEG_QUALITY, CAMERA_SETTINGS["capture_quality"]])
        return save_path

    def _emit_frame(self):
        """Buat frame baru lalu kirim ke callback UI."""
        frame = self._generate_frame()
        self.current_frame = frame

        if self._frame_callback:
            self._frame_callback(frame.copy())

        self._tick += 1

    def _generate_frame(self):
        """Hasilkan frame BGR dengan animasi sederhana."""
        width, height = UI_SETTINGS["camera_preview_size"]
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        gradient = np.linspace(50, 180, width, dtype=np.uint8)
        frame[:, :, 0] = gradient
        frame[:, :, 1] = gradient[::-1]
        frame[:, :, 2] = 120

        center_x = int((np.sin(self._tick / 10.0) * 0.4 + 0.5) * width)
        center_y = int((np.cos(self._tick / 12.0) * 0.4 + 0.5) * height)
        cv2.circle(frame, (center_x, center_y), 90, (40, 40, 200), thickness=-1)

        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, "Kamera Simulasi", (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                    (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, f"Waktu: {timestamp}", (40, height - 60), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (230, 230, 230), 2, cv2.LINE_AA)
        return frame


def ensure_default_camera_config(camera_name: str):
    """Pastikan konfigurasi default_camera sesuai dengan kamera yang dipakai."""
    current = db_manager.get_app_config("default_camera")
    if current != camera_name:
        db_manager.set_app_config("default_camera", camera_name)


def build_camera_manager(use_mock: bool):
    if use_mock:
        manager = MockCameraManager()
        ensure_default_camera_config(manager.get_available_cameras()[0]["name"])
        print("Menggunakan kamera simulasi.")
        return manager

    manager = CameraManager()
    cameras = manager.get_available_cameras()
    if not cameras:
        print("Tidak ada kamera fisik yang terdeteksi. Menggunakan simulasi.")
        return build_camera_manager(use_mock=True)

    ensure_default_camera_config(cameras[0]["name"])
    print(f"Menggunakan kamera fisik: {cameras[0]['name']}")
    return manager


def test_camera(args):
    """Quick test of camera window."""
    from ui.camera_window import MainWindow

    app = QApplication(sys.argv)
    set_test_session(args)
    camera_manager = build_camera_manager(use_mock=not args.real_camera)
    window = MainWindow(camera_manager=camera_manager)
    window.set_session_info(session_manager.get_current_user())
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
    elif args.window == "camera":
        test_camera(args)
