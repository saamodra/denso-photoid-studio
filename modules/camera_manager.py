"""
Camera Manager Module
Handles camera detection, preview, and photo capture functionality
"""
import cv2
import time
import os
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QImage, QPixmap
import numpy as np
from config import CAMERA_SETTINGS, CAPTURES_DIR


class CameraThread(QThread):
    """Thread for handling camera operations"""
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_index=0, backend=cv2.CAP_ANY):
        super().__init__()
        self.camera_index = camera_index
        self.backend = backend
        self.camera = None
        self.running = False

    def run(self):
        """Main camera thread loop"""
        try:
            print(f"Camera thread starting for camera {self.camera_index} with backend {self.backend}")
            self.camera = cv2.VideoCapture(self.camera_index, self.backend)

            if not self.camera.isOpened():
                print(f"Failed to open camera {self.camera_index}")
                return

            print(f"Camera {self.camera_index} opened successfully")

            # Set camera properties with error handling
            try:
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_SETTINGS['default_resolution'][0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_SETTINGS['default_resolution'][1])
                self.camera.set(cv2.CAP_PROP_FPS, CAMERA_SETTINGS['preview_fps'])
            except Exception as e:
                print(f"Warning: Could not set camera properties: {e}")

            # Test if we can read a frame before starting the loop
            ret, test_frame = self.camera.read()
            if not ret or test_frame is None:
                print(f"Camera {self.camera_index} cannot read frames")
                return

            print(f"Camera {self.camera_index} frame test successful, starting preview loop")
            self.running = True
            frame_count = 0

            while self.running:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    # Flip frame horizontally for mirror effect
                    frame = cv2.flip(frame, 1)
                    self.frame_ready.emit(frame)
                    frame_count += 1

                    # Log every 30 frames (roughly once per second)
                    if frame_count % 30 == 0:
                        print(f"Camera {self.camera_index}: {frame_count} frames processed")
                else:
                    print(f"Camera {self.camera_index}: Failed to read frame")
                    break

                self.msleep(33)  # ~30 FPS

        except Exception as e:
            print(f"Camera thread error: {e}")
        finally:
            print(f"Camera thread for camera {self.camera_index} ending")

    def stop(self):
        """Stop camera thread"""
        self.running = False
        if self.camera:
            self.camera.release()
        self.quit()
        self.wait()


class CameraManager:
    """Main camera management class"""

    def __init__(self):
        self.available_cameras = self.detect_cameras()
        self.current_camera_index = 0
        self.camera_thread = None
        self.current_frame = None
        self.captured_photos = []
        self.capture_count = CAMERA_SETTINGS['capture_count']

    def detect_cameras(self):
        """Detect all available cameras"""
        cameras = []

        # Try different camera backends and indices
        backends = [cv2.CAP_ANY]
        if hasattr(cv2, 'CAP_AVFOUNDATION'):  # macOS
            backends.append(cv2.CAP_AVFOUNDATION)
        if hasattr(cv2, 'CAP_DSHOW'):  # Windows
            backends.append(cv2.CAP_DSHOW)
        if hasattr(cv2, 'CAP_V4L2'):  # Linux
            backends.append(cv2.CAP_V4L2)

        found_cameras = set()  # To avoid duplicates

        for backend in backends:
            for i in range(5):  # Check first 5 camera indices for each backend
                try:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        # Test if camera actually works
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            camera_id = f"{backend}_{i}"
                            if camera_id not in found_cameras:
                                found_cameras.add(camera_id)
                                cameras.append({
                                    'index': i,
                                    'backend': backend,
                                    'name': self._get_camera_name(i, backend),
                                    'resolution': self._get_camera_resolution(cap)
                                })
                        cap.release()
                except Exception as e:
                    print(f"Error testing camera {i} with backend {backend}: {e}")
                    continue

        # If no cameras found with backends, try simple approach
        if not cameras:
            print("No cameras found with backends, trying simple detection...")
            for i in range(3):  # Try first 3 indices
                try:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            cameras.append({
                                'index': i,
                                'backend': cv2.CAP_ANY,
                                'name': f'Camera {i}',
                                'resolution': self._get_camera_resolution(cap)
                            })
                        cap.release()
                except Exception as e:
                    print(f"Error testing camera {i}: {e}")
                    continue

        print(f"Found {len(cameras)} camera(s)")
        return cameras

    def _get_camera_name(self, index, backend):
        """Get a descriptive camera name"""
        backend_names = {
            cv2.CAP_ANY: "Camera",
            cv2.CAP_AVFOUNDATION: "AVFoundation Camera",
            cv2.CAP_DSHOW: "DirectShow Camera",
            cv2.CAP_V4L2: "V4L2 Camera"
        }

        if hasattr(cv2, 'CAP_AVFOUNDATION') and backend == cv2.CAP_AVFOUNDATION:
            backend_name = "AVFoundation Camera"
        elif hasattr(cv2, 'CAP_DSHOW') and backend == cv2.CAP_DSHOW:
            backend_name = "DirectShow Camera"
        elif hasattr(cv2, 'CAP_V4L2') and backend == cv2.CAP_V4L2:
            backend_name = "V4L2 Camera"
        else:
            backend_name = "Camera"

        return f"{backend_name} {index}"

    def _get_camera_resolution(self, cap):
        """Get camera resolution"""
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def get_available_cameras(self):
        """Return list of available cameras"""
        return self.available_cameras

    def debug_camera_detection(self):
        """Debug camera detection for troubleshooting"""
        print("=== Camera Detection Debug ===")
        print(f"OpenCV version: {cv2.__version__}")

        # List available backends
        backends_to_test = []
        if hasattr(cv2, 'CAP_AVFOUNDATION'):
            backends_to_test.append(('AVFoundation', cv2.CAP_AVFOUNDATION))
        if hasattr(cv2, 'CAP_DSHOW'):
            backends_to_test.append(('DirectShow', cv2.CAP_DSHOW))
        if hasattr(cv2, 'CAP_V4L2'):
            backends_to_test.append(('V4L2', cv2.CAP_V4L2))
        backends_to_test.append(('ANY', cv2.CAP_ANY))

        print(f"Available backends: {[name for name, _ in backends_to_test]}")

        for backend_name, backend in backends_to_test:
            print(f"\nTesting {backend_name} backend:")
            for i in range(3):
                try:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            print(f"  Camera {i}: WORKING ({frame.shape})")
                        else:
                            print(f"  Camera {i}: OPENED but no frame")
                        cap.release()
                    else:
                        print(f"  Camera {i}: Cannot open")
                except Exception as e:
                    print(f"  Camera {i}: Error - {e}")

        print(f"\nTotal detected cameras: {len(self.available_cameras)}")
        for cam in self.available_cameras:
            print(f"  {cam['name']}: {cam['resolution']}")
        print("=============================")

    def switch_camera(self, camera_index):
        """Switch to a different camera"""
        if camera_index < len(self.available_cameras):
            self.stop_preview()
            self.current_camera_index = camera_index
            return True
        return False

    def start_preview(self, frame_callback=None):
        """Start camera preview"""
        if self.camera_thread and self.camera_thread.isRunning():
            self.stop_preview()

        # Get backend for current camera
        backend = cv2.CAP_ANY
        if self.current_camera_index < len(self.available_cameras):
            backend = self.available_cameras[self.current_camera_index].get('backend', cv2.CAP_ANY)

        self.camera_thread = CameraThread(self.current_camera_index, backend)
        if frame_callback:
            self.camera_thread.frame_ready.connect(frame_callback)
        self.camera_thread.frame_ready.connect(self._update_current_frame)
        self.camera_thread.start()

    def stop_preview(self):
        """Stop camera preview"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None

    def _update_current_frame(self, frame):
        """Update current frame for capture"""
        self.current_frame = frame.copy()

    def capture_photo(self, save_path=None):
        """Capture a single photo with fresh frame"""
        # Get a fresh frame directly from camera for better real-time capture
        fresh_frame = self._capture_fresh_frame()
        if fresh_frame is None:
            # Fallback to current frame if fresh capture fails
            if self.current_frame is None:
                return None
            fresh_frame = self.current_frame

        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            save_path = os.path.join(CAPTURES_DIR, f"capture_{timestamp}.jpg")

        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the fresh image
        success = cv2.imwrite(save_path, fresh_frame,
                             [cv2.IMWRITE_JPEG_QUALITY, CAMERA_SETTINGS['capture_quality']])

        if success:
            print(f"Captured fresh photo: {os.path.basename(save_path)}")
            return save_path
        return None

    def _capture_fresh_frame(self):
        """Capture a fresh frame directly from camera"""
        if not self.camera_thread or not self.camera_thread.camera:
            return None

        try:
            # Read multiple frames to get the latest one
            for _ in range(3):  # Read a few frames to get the most recent
                ret, frame = self.camera_thread.camera.read()
                if not ret or frame is None:
                    return None

            # Apply same processing as in camera thread
            frame = cv2.flip(frame, 1)  # Mirror effect
            print("Captured fresh frame from camera")
            return frame.copy()

        except Exception as e:
            print(f"Error capturing fresh frame: {e}")
            return None

    def capture_multiple_photos(self, count=None, delay=None, progress_callback=None):
        """Capture multiple photos with delay"""
        if count is None:
            count = self.capture_count
        if delay is None:
            delay = CAMERA_SETTINGS['capture_delay']

        captured_paths = []

        for i in range(count):
            if progress_callback:
                progress_callback(i + 1, count)

            # Wait for delay (except first photo)
            if i > 0:
                time.sleep(delay)

            photo_path = self.capture_photo()
            if photo_path:
                captured_paths.append(photo_path)
            else:
                break

        self.captured_photos = captured_paths
        return captured_paths

    def get_captured_photos(self):
        """Get list of captured photo paths"""
        return self.captured_photos

    def clear_captured_photos(self):
        """Clear captured photos list"""
        self.captured_photos = []

    def frame_to_qimage(self, frame):
        """Convert OpenCV frame to QImage"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return qt_image

    def frame_to_qpixmap(self, frame, size=None, maintain_aspect_ratio=False):
        """Convert OpenCV frame to QPixmap"""
        qt_image = self.frame_to_qimage(frame)
        pixmap = QPixmap.fromImage(qt_image)

        if size:
            if maintain_aspect_ratio:
                # Scale while maintaining aspect ratio
                from PyQt6.QtCore import Qt
                pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            else:
                pixmap = pixmap.scaled(size[0], size[1])

        return pixmap


    def get_camera_info(self):
        """Get current camera information"""
        if self.current_camera_index < len(self.available_cameras):
            return self.available_cameras[self.current_camera_index]
        return None

    def cleanup(self):
        """Cleanup camera resources"""
        self.stop_preview()
        # Optional: Clean up old capture files
        self._cleanup_old_captures()

    def _cleanup_old_captures(self, max_age_hours=24):
        """Clean up old capture files"""
        try:
            current_time = time.time()
            for filename in os.listdir(CAPTURES_DIR):
                file_path = os.path.join(CAPTURES_DIR, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > max_age_hours * 3600:  # Convert hours to seconds
                        os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up captures: {e}")


class CaptureTimer(QThread):
    """Timer for countdown during photo capture"""
    countdown_update = pyqtSignal(int)
    capture_ready = pyqtSignal()

    def __init__(self, countdown_seconds=3):
        super().__init__()
        self.countdown_seconds = countdown_seconds

    def run(self):
        """Run countdown timer"""
        for i in range(self.countdown_seconds, 0, -1):
            self.countdown_update.emit(i)
            self.sleep(1)
        self.capture_ready.emit()
