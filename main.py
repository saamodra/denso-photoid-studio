"""
ID Card Photo Machine - Main Application
Desktop application for automated ID card photo processing
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, UI_SETTINGS
from modules.session_manager import session_manager


class IDCardPhotoApp:
    """Main application class coordinating the workflow"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)

        # Application state
        self.current_window = None
        self.current_user = None
        self.captured_photos = []
        self.selected_photo = None
        self.processed_image = None
        self.camera_manager = None

        # Windows
        self.login_window = None
        self.role_selection_window = None
        self.dashboard_window = None
        self.admin_window = None
        self.employee_list_window = None
        self.camera_window = None
        self.selection_window = None
        self.processing_window = None
        self.print_window = None

        self.setup_application()
        self.app.aboutToQuit.connect(self.cleanup_resources)
        self._camera_warmup_thread = None

    def get_camera_manager(self):
        """Dapatkan instance CameraManager yang dibagikan"""
        if not self.camera_manager:
            from modules.camera_manager import CameraManager
            self.camera_manager = CameraManager()
        return self.camera_manager

    def preload_camera(self):
        """(Deprecated) Kept for compatibility; now starts background warmup."""
        self.start_camera_warmup()
        return

    def start_camera_warmup(self):
        """Mulai pemanasan kamera di background tanpa blok UI"""
        if getattr(self, '_camera_warmup_thread', None) is not None:
            return

        class _Warmup(QThread):
            def __init__(self, outer):
                super().__init__()
                self.outer = outer
            def run(self):
                try:
                    print("Memanaskan kamera di background...")
                    mgr = self.outer.get_camera_manager()
                    mgr.warm_up_camera()
                    print("Pemanasan kamera selesai (background)")
                except Exception as e:
                    print(f"Gagal pemanasan kamera (background): {e}")

        self._camera_warmup_thread = _Warmup(self)
        self._camera_warmup_thread.start()

    def start_rembg_warmup(self):
        """Preload rembg ONNX model in background"""
        if getattr(self, '_rembg_warmup_thread', None) is not None:
            return
        class _RembgWarm(QThread):
            def run(self_inner):
                try:
                    print("Memuat model penghapus background (rembg) di background...")
                    from modules.image_processor import preload_rembg_session, get_shared_processor
                    preload_rembg_session()
                    # Inisialisasi instance bersama agar siap dipakai di ProcessingWindow
                    get_shared_processor()
                    print("Model rembg siap (background)")
                except Exception as e:
                    print(f"Gagal memuat model rembg: {e}")
        self._rembg_warmup_thread = _RembgWarm()
        self._rembg_warmup_thread.start()

    def show_loading_and_preload(self):
        """Tampilkan layar loading, preload rembg + kamera, lalu lanjut ke login."""
        from ui.loading_window import LoadingWindow
        loader = LoadingWindow()
        loader.center_on_screen(self.app)
        loader.show()

        class _Preload(QThread):
            progress = pyqtSignal(str)
            done = pyqtSignal()
            def __init__(self, outer):
                super().__init__()
                self.outer = outer
            def run(self):
                try:
                    # 1) Muat model rembg
                    self.progress.emit("Memuat model penghapus latar...")
                    from modules.image_processor import preload_rembg_session, get_shared_processor
                    preload_rembg_session()
                    get_shared_processor()
                    # 2) Pemanasan kamera
                    self.progress.emit("Memanaskan kamera...")
                    mgr = self.outer.get_camera_manager()
                    mgr.warm_up_camera()
                except Exception as e:
                    print(f"Preload error: {e}")
                finally:
                    self.done.emit()

        # Simpan thread & loader sebagai atribut agar tidak di-GC saat berjalan
        self._preload_thread = _Preload(self)
        self._loading_window = loader
        self._preload_thread.progress.connect(lambda text: self._loading_window.loading_label.setText(text))
        def _finish():
            if self._loading_window:
                self._loading_window.close()
                self._loading_window = None
            self.show_login_window()
        self._preload_thread.done.connect(_finish)
        self._preload_thread.start()
    def setup_application(self):
        """Setup application-wide settings"""
        # Set application font
        font = QFont()
        font.setPointSize(UI_SETTINGS['font_size'])
        self.app.setFont(font)

        # Set application style
        self.app.setStyle('Fusion')  # Modern look across platforms

        # macOS specific settings for window visibility
        import platform
        if platform.system() == 'Darwin':  # macOS
            self.app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, True)
            # Ensure app appears in dock
            try:
                import objc
                from Foundation import NSBundle
                bundle = NSBundle.mainBundle()
                if bundle:
                    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                    if info:
                        info['CFBundleName'] = APP_NAME
            except ImportError:
                pass  # objc not available, continue without

        # Set application icon (if available)
        try:
            icon_path = os.path.join('assets', 'icons', 'app_icon.png')
            if os.path.exists(icon_path):
                self.app.setWindowIcon(QIcon(icon_path))
        except:
            pass

    def cleanup_resources(self):
        """Pastikan resource kamera ditutup ketika aplikasi keluar"""
        if self.camera_manager:
            try:
                self.camera_manager.cleanup()
            except Exception as e:
                print(f"⚠️ Tidak dapat membersihkan kamera saat keluar: {e}")

    def run(self):
        """Start the application"""
        try:
            print("🚀 Starting ID Card Photo Machine...")
            print(f"📱 Available screens: {len(self.app.screens())}")

            primary_screen = self.app.primaryScreen()
            if primary_screen:
                geometry = primary_screen.availableGeometry()
                print(f"🖥️  Primary screen: {geometry.width()}x{geometry.height()}")

            # self.show_main_window()
            # Tampilkan layar loading dan lakukan preload sumber daya berat
            self.show_loading_and_preload()

            print("✅ Application UI should now be visible")
            print("   If you don't see the window, check:")
            print("   - Dock for the application icon")
            print("   - Mission Control for hidden windows")
            print("   - Alt+Tab to cycle through windows")

            return self.app.exec()
        except Exception as e:
            print(f"❌ Application error: {e}")
            self.show_error_dialog("Application Error", str(e))
            return 1

    def show_login_window(self):
        """Show login window"""
        try:
            if self.login_window:
                self.current_window.hide()

                # If main window exists, just show it
                self.login_window.showFullScreen()
                self.login_window.raise_()  # Bring to front
                self.login_window.activateWindow()  # Activate window

            else:

                # Create new main window (lazy import)
                from ui.login_window import LoginPage
                self.login_window = LoginPage()
                # Hubungkan sinyal dari halaman login ke fungsi di atas
                self.login_window.login_successful.connect(self.login_success)

                # Ensure window appears on screen
                self.login_window.showFullScreen()
                self.login_window.raise_()  # Bring to front
                self.login_window.activateWindow()  # Activate window

                # Force window to center and be visible
                if not self.login_window.isFullScreen():
                    screen = self.app.primaryScreen()
                    if screen:
                        screen_geometry = screen.availableGeometry()
                        window_geometry = self.login_window.geometry()
                        x = (screen_geometry.width() - window_geometry.width()) // 2
                        y = (screen_geometry.height() - window_geometry.height()) // 2
                        self.login_window.move(x, y)

            self.current_window = self.login_window
            print(f"✅ Login window shown at position: {self.login_window.x()}, {self.login_window.y()}")
            print(f"✅ Window size: {self.login_window.width()}x{self.login_window.height()}")
            print(f"✅ Window visible: {self.login_window.isVisible()}")


        except Exception as e:
            print(f"❌ Error showing main window: {e}")
            self.show_error_dialog("Camera Error",
                                 f"Failed to initialize camera:\n{str(e)}\n\n"
                                 "Please ensure your camera is connected and not in use by another application.")

    def login_success(self, user_data):
        """Handle successful login with user data"""
        # Start session using session manager
        if session_manager.login(user_data):
            self.current_user = user_data  # Keep for backward compatibility
            self.current_window.hide()

            self.show_role_selection_window()
        else:
            self.show_error_dialog("Session Error", "Failed to start user session")

    def show_dashboard_window(self):
        """Show dashboard window"""
        try:
            if self.dashboard_window:
                # If dashboard window exists, just show it
                self.dashboard_window.show()
                self.dashboard_window.raise_()  # Bring to front
                self.dashboard_window.activateWindow()  # Activate window
                # Update user info in existing window with current session data
                self.dashboard_window.set_session_info(session_manager.get_current_user())
            else:
                # Create new dashboard window (lazy import)
                from ui.dashboard_window import DashboardWindow
                self.dashboard_window = DashboardWindow()
                self.dashboard_window.start_photo_capture.connect(self.show_camera_window)
                self.dashboard_window.logout_requested.connect(self.logout)
                # Pass session information to dashboard window
                self.dashboard_window.set_session_info(session_manager.get_current_user())

                # Ensure window appears on screen
                self.dashboard_window.show()
                self.dashboard_window.raise_()  # Bring to front
                self.dashboard_window.activateWindow()  # Activate window

                # Force window to center and be visible
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.dashboard_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.dashboard_window.move(x, y)

            # Close current window
            if self.current_window:
                self.current_window.hide()

            self.current_window = self.dashboard_window
            print(f"✅ Dashboard window shown at position: {self.dashboard_window.x()}, {self.dashboard_window.y()}")
            print(f"✅ Window size: {self.dashboard_window.width()}x{self.dashboard_window.height()}")
            print(f"✅ Window visible: {self.dashboard_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing dashboard window: {e}")
            self.show_error_dialog("Dashboard Error", f"Failed to show dashboard:\n{str(e)}")

    def show_role_selection_window(self):
        """Show role selection window"""
        try:
            # Create new role selection window (lazy import)
            from ui.role_selection_window import RoleSelectionWindow
            self.role_selection_window = RoleSelectionWindow()
            # Connect signals from role selection to appropriate functions
            self.role_selection_window.user_role_selected.connect(self.show_dashboard_window)
            self.role_selection_window.admin_role_selected.connect(self.show_admin_window)
            self.role_selection_window.logout_successful.connect(self.show_login_window)

            # Ensure window appears on screen
            self.role_selection_window.showFullScreen()
            self.role_selection_window.raise_()  # Bring to front
            self.role_selection_window.activateWindow()  # Activate window

            # Force positioning only when not fullscreen (fallback for platforms that block full screen)
            if not self.role_selection_window.isFullScreen():
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.role_selection_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.role_selection_window.move(x, y)

            self.current_window = self.role_selection_window
            print(f"✅ Role selection window shown at position: {self.role_selection_window.x()}, {self.role_selection_window.y()}")
            print(f"✅ Window size: {self.role_selection_window.width()}x{self.role_selection_window.height()}")
            print(f"✅ Window visible: {self.role_selection_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing role selection window: {e}")
            self.show_error_dialog("Role Selection Error", f"Failed to show role selection:\n{str(e)}")

    def show_admin_window(self):
        """Show admin window"""
        try:
            from ui.admin_window import AdminWindow

            if self.admin_window:
                # If admin window exists, bring it back in fullscreen mode
                self.admin_window.showFullScreen()
            else:
                # Create new admin window
                self.admin_window = AdminWindow()
                self.admin_window.logout_requested.connect(self.show_role_selection_window)  # keluar dari admin, masuk ke pilih role lagi
                self.admin_window.show_employee_list.connect(self.show_employee_list_window)

            # Ensure window is front-most and active
            self.admin_window.showFullScreen()
            self.admin_window.raise_()  # Bring to front
            self.admin_window.activateWindow()  # Activate window

            #  Force window to center only if not fullscreen
            if not self.admin_window.isFullScreen():
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.admin_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.admin_window.move(x, y)

            # Close current window
            if self.current_window:
                self.current_window.hide()

            self.current_window = self.admin_window
            print(f"✅ Admin window shown at position: {self.admin_window.x()}, {self.admin_window.y()}")
            print(f"✅ Window size: {self.admin_window.width()}x{self.admin_window.height()}")
            print(f"✅ Window visible: {self.admin_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing admin window: {e}")
            self.show_error_dialog("Admin Error", f"Failed to show admin window:\n{str(e)}")

    # def show_employee_list_window(self):
    #     """Show admin Employee List"""
    #     try:
    #         from ui.employee_list_window import EmployeeListPage

    #         if self.employee_list_window:
    #             # If admin Employee List exists, just show it
    #             self.employee_list_window.show()
    #             self.employee_list_window.raise_()  # Bring to front
    #             self.employee_list_window.activateWindow()  # Activate window
    #         else:
    #             # Create new admin Employee List
    #             self.employee_list_window = EmployeeListPage()
    #             self.employee_list_window.back_button_click.connect(self.show_admin_window) # keluar dari employee list masuk ke admin
    #             # self.employee_list_window.show_employee_list.connect(self.show_employee_list_window)

    #             # Ensure window appears on screen
    #             self.employee_list_window.show()
    #             self.employee_list_window.raise_()  # Bring to front
    #             self.employee_list_window.activateWindow()  # Activate window

    #         # Di keluarin dari else, supaya full screen pasti
    #         #
    #         #  Force window to center and be visible
    #         screen = self.app.primaryScreen()
    #         if screen:
    #             screen_geometry = screen.availableGeometry()
    #             window_geometry = self.employee_list_window.geometry()
    #             x = (screen_geometry.width() - window_geometry.width()) // 2
    #             y = (screen_geometry.height() - window_geometry.height()) // 2
    #             self.employee_list_window.move(x, y)

    #         # Close current window
    #         if self.current_window:
    #             self.current_window.hide()

    #         self.current_window = self.employee_list_window
    #         print(f"✅ Admin Employee List shown at position: {self.employee_list_window.x()}, {self.employee_list_window.y()}")
    #         print(f"✅ Window size: {self.employee_list_window.width()}x{self.employee_list_window.height()}")
    #         print(f"✅ Window visible: {self.employee_list_window.isVisible()}")

    #     except Exception as e:
    #         print(f"❌ Error showing admin Employee List: {e}")
    #         self.show_error_dialog("Admin Error", f"Failed to show admin Employee List:\n{str(e)}")

    def show_employee_list_window(self):
        """Menampilkan jendela daftar karyawan dalam mode maximized."""
        try:
            from ui.employee_list_window import EmployeeListPage

            # 1. Buat instance jendela HANYA jika belum ada
            if not hasattr(self, 'employee_list_window') or not self.employee_list_window:
                self.employee_list_window = EmployeeListPage()
                # Hubungkan sinyal "kembali" ke tampilan admin
                self.employee_list_window.back_button_click.connect(self.show_admin_window)

            # 2. Sembunyikan jendela yang aktif saat ini (jika ada)
            if hasattr(self, 'current_window') and self.current_window and self.current_window is not self.employee_list_window:
                self.current_window.hide()

            # 3. Tetapkan jendela daftar karyawan sebagai jendela saat ini
            self.current_window = self.employee_list_window

            # 4. Tampilkan jendela dalam mode maximized (INI KUNCINYA)
            # Gunakan showMaximized() untuk pengalaman desktop terbaik.
            self.current_window.showMaximized()

            # Opsi alternatif jika Anda benar-benar ingin menutupi taskbar:
            # self.current_window.showFullScreen()

            # 5. Bawa jendela ke depan (opsional, tapi praktik yang baik)
            self.current_window.raise_()
            self.current_window.activateWindow()

            print("✅ Jendela daftar karyawan berhasil ditampilkan dalam mode maximized.")

        except Exception as e:
            print(f"❌ Error saat menampilkan daftar karyawan: {e}")
            # Asumsikan Anda memiliki fungsi untuk menampilkan dialog error
            # self.show_error_dialog("Error", f"Gagal menampilkan daftar karyawan:\n{str(e)}")

    def show_camera_window(self):
        """Show camera window"""
        try:
            manager = self.get_camera_manager()
            if self.camera_window:
                # If camera window exists, just show it and restart camera
                self.camera_window.set_camera_manager(manager)
                self.camera_window.show()
                self.camera_window.raise_()  # Bring to front
                self.camera_window.activateWindow()  # Activate window
                self.camera_window.setup_camera()  # Restart camera
                # Update user info in existing window with current session data
                self.camera_window.set_session_info(session_manager.get_current_user())
            else:
                # Create new camera window (lazy import)
                from ui.camera_window import MainWindow as CameraWindow
                self.camera_window = CameraWindow(camera_manager=manager)
                self.camera_window.photos_captured.connect(self.on_photos_captured)
                self.camera_window.logout_requested.connect(self.logout)
                self.camera_window.back_to_dashboard_requested.connect(self.show_dashboard_window)
                # Pass session information to camera window
                self.camera_window.set_session_info(session_manager.get_current_user())

                # Ensure window appears on screen
                self.camera_window.show()
                self.camera_window.raise_()  # Bring to front
                self.camera_window.activateWindow()  # Activate window

                # Force window to center and be visible
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.camera_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.camera_window.move(x, y)

            # close current window open, such as dashboard window
            if self.current_window:
                self.current_window.hide()

            self.current_window = self.camera_window
            print(f"✅ Camera window shown at position: {self.camera_window.x()}, {self.camera_window.y()}")
            print(f"✅ Window size: {self.camera_window.width()}x{self.camera_window.height()}")
            print(f"✅ Window visible: {self.camera_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing camera window: {e}")
            self.show_error_dialog("Camera Error",
                                 f"Failed to initialize camera:\n{str(e)}\n\n"
                                 "Please ensure your camera is connected and not in use by another application.")

    def on_photos_captured(self, photo_paths):
        """Handle photos captured from main window"""
        if not photo_paths:
            self.show_info_dialog("No Photos", "No photos were captured. Please try again.")
            return

        self.captured_photos = photo_paths
        self.show_selection_window()

    def show_selection_window(self):
        """Show photo selection window"""
        try:
            if not self.captured_photos:
                self.show_error_dialog("No Photos", "No photos available for selection.")
                return

            if self.selection_window:
                self.selection_window.close()

            from ui.selection_window import SelectionWindow
            self.selection_window = SelectionWindow(self.captured_photos)
            self.selection_window.photo_selected.connect(self.on_photo_selected)
            self.selection_window.back_requested.connect(self.show_camera_window)
            self.selection_window.show()
            self.current_window = self.selection_window

            # Stop camera and close camera window to save resources
            if self.camera_window:
                self.camera_window.stop_camera()  # Stop camera before hiding
                self.camera_window.hide()

        except Exception as e:
            self.show_error_dialog("Selection Error", f"Failed to show selection window:\n{str(e)}")

    def on_photo_selected(self, photo_path):
        """Handle photo selection"""
        if not photo_path or not os.path.exists(photo_path):
            self.show_error_dialog("Invalid Photo", "Selected photo is not available.")
            return

        self.selected_photo = photo_path
        self.show_processing_window()

    def show_processing_window(self):
        """Show processing window"""
        try:
            if not self.selected_photo:
                self.show_error_dialog("No Photo Selected", "Please select a photo first.")
                return

            if self.processing_window:
                self.processing_window.close()

            from ui.processing_window import ProcessingWindow
            self.processing_window = ProcessingWindow(self.selected_photo)
            self.processing_window.set_session_info(session_manager.get_current_user())
            self.processing_window.processing_complete.connect(self.on_processing_complete)
            self.processing_window.back_requested.connect(self.show_selection_window)
            self.processing_window.show()
            self.current_window = self.processing_window

            # Close selection window
            if self.selection_window:
                self.selection_window.hide()

        except Exception as e:
            self.show_error_dialog("Processing Error", f"Failed to show processing window:\n{str(e)}")

    def on_processing_complete(self, processed_image):
        """Handle processing completion"""
        if processed_image is None:
            self.show_error_dialog("Processing Failed", "Image processing failed. Please try again.")
            return

        self.processed_image = processed_image
        self.show_print_window()

    def show_print_window(self):
        """Show print window"""
        try:
            if not self.processed_image:
                self.show_error_dialog("No Processed Image", "Please process a photo first.")
                return

            if self.print_window:
                self.print_window.close()

            from ui.print_window import PrintWindow
            self.print_window = PrintWindow(self.processed_image, self.selected_photo)
            self.print_window.print_complete.connect(self.on_print_complete)
            self.print_window.back_requested.connect(self.show_processing_window)
            self.print_window.logout_requested.connect(self.logout)
            self.print_window.show()
            self.current_window = self.print_window

            # Close processing window
            if self.processing_window:
                self.processing_window.hide()

        except Exception as e:
            self.show_error_dialog("Print Error", f"Failed to show print window:\n{str(e)}")

    def on_print_complete(self, success):
        """Handle print completion"""
        from ui.dialogs.custom_dialog import CustomStyledDialog

        if success:
            dialog = CustomStyledDialog(
                self.current_window,
                "Proses Cetak Berhasil!",
                "Kartu berhasil dicetak dan fotonya sudah tersimpan otomatis.\n\nSilakan ambil ID card Anda.",
                [("Selesai", QDialog.DialogCode.Accepted)]
            )
        else:
            dialog = CustomStyledDialog(
                self.current_window,
                "Ups! Proses Cetak Gagal",
                "File Foto/ID Anda tersimpan otomatis, hanya saja mesin tidak bisa mencetak saat ini.\n\nMohon hubungi admin untuk membantu proses cetak.",
                [("Selesai", QDialog.DialogCode.Accepted)]
            )

        dialog.exec()
        self.logout()

    def restart_workflow(self):
        """Restart the entire workflow"""
        try:
            # Stop camera and close all windows except dashboard
            if self.camera_window:
                self.camera_window.stop_camera()
            if self.print_window:
                self.print_window.close()
            if self.processing_window:
                self.processing_window.close()
            if self.selection_window:
                self.selection_window.close()

            # Reset state
            self.captured_photos = []
            self.selected_photo = None
            self.processed_image = None

            # Show role selection window
            QTimer.singleShot(100, self.show_login_window)  # Small delay for cleanup

        except Exception as e:
            self.show_error_dialog("Restart Error", f"Failed to restart workflow:\n{str(e)}")

    def logout(self):
        """Logout current user and return to login"""
        try:
            # End current session
            session_manager.logout()
            self.current_user = None

            # Close all windows
            if self.role_selection_window:
                self.role_selection_window.hide()
            if self.dashboard_window:
                self.dashboard_window.hide()
            if self.admin_window:
                self.admin_window.hide()
            if self.camera_window:
                self.camera_window.hide()
            if self.selection_window:
                self.selection_window.hide()
            if self.processing_window:
                self.processing_window.hide()
            if self.print_window:
                self.print_window.hide()

            # Show login window
            self.show_login_window()

        except Exception as e:
            print(f"❌ Error during logout: {e}")
            self.show_error_dialog("Logout Error", f"Failed to logout:\n{str(e)}")

    def show_error_dialog(self, title, message):
        """Show error dialog"""
        from ui.dialogs.custom_dialog import CustomStyledDialog
        dialog = CustomStyledDialog(self.current_window, title, message)
        dialog.exec()

    def show_info_dialog(self, title, message):
        """Show info dialog"""
        from ui.dialogs.custom_dialog import CustomStyledDialog
        dialog = CustomStyledDialog(self.current_window, title, message)
        dialog.exec()

    def show_warning_dialog(self, title, message):
        """Show warning dialog"""
        from ui.dialogs.custom_dialog import CustomStyledDialog
        dialog = CustomStyledDialog(self.current_window, title, message)
        dialog.exec()

    def cleanup(self):
        """Cleanup application resources"""
        try:
            # Close all windows
            if self.role_selection_window:
                self.role_selection_window.close()
            if self.dashboard_window:
                self.dashboard_window.close()
            if self.admin_window:
                self.admin_window.close()
            if self.camera_window:
                self.camera_window.close()
            if self.selection_window:
                self.selection_window.close()
            if self.processing_window:
                self.processing_window.close()
            if self.print_window:
                self.print_window.close()

            # Cleanup temp files (optional)
            self.cleanup_temp_files()

        except Exception as e:
            print(f"Cleanup error: {e}")

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        from modules.camera_manager import CameraManager
        from modules.image_processor import ImageProcessor

        try:
            # Cleanup camera temp files
            camera_manager = CameraManager()
            camera_manager.cleanup()

            # Cleanup image processor temp files
            image_processor = ImageProcessor()
            image_processor.cleanup_temp_files()

        except Exception as e:
            print(f"Temp file cleanup error: {e}")


def check_dependencies():
    """Check if all required dependencies are available"""
    # Skip dependency checks in frozen (PyInstaller) builds to speed up startup
    if getattr(sys, 'frozen', False):
        return True
    required_modules = [
        'cv2',
        'PIL',
        'rembg',
        'onnxruntime',
        'numpy',
        'PyQt6'
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install dependencies using:")
        print("pip install -r requirements.txt")
        return False

    return True


def main():
    """Main entry point"""
    print(f"Starting {APP_NAME} v{APP_VERSION}")

    # Check dependencies
    if not check_dependencies():
        print("Dependency check failed. Exiting.")
        sys.exit(1)

    # Create and run application
    app = IDCardPhotoApp()

    try:
        exit_code = app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        exit_code = 0
    except Exception as e:
        print(f"Application error: {e}")
        exit_code = 1
    finally:
        app.cleanup()

    print(f"{APP_NAME} exited with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
