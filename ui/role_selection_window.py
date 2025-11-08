from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSignal
import sys
from config import APP_NAME, APP_VERSION, UI_SETTINGS
from ui.admin_window import AdminWindow

from modules.session_manager import session_manager

class RoleSelectionWindow(QWidget):
    logout_successful = pyqtSignal()
    user_role_selected = pyqtSignal()
    admin_role_selected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.admin_window = None
        self.current_user = session_manager.get_current_user()  # ambil user aktif
        self._fullscreen_initialized = False
        self._base_font = QFont("Helvetica", 22)
        self.setFont(self._base_font)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Role Selection - " + APP_NAME)
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(self.get_stylesheet())

        # Layout utama serupa login (tanpa card)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 100, 80, 80)
        main_layout.setSpacing(40)

        # Judul
        title = QLabel("Pilih Peran Anda")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)
        main_layout.addSpacing(20)
        main_layout.addStretch()

        # Tombol User
        self.user_btn = QPushButton(" Masuk sebagai User")
        self.user_btn.setIcon(QIcon.fromTheme("user"))  # Bisa ganti ke path ikon custom
        self.user_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.user_btn.setMinimumHeight(160)
        self.user_btn.setMinimumWidth(420)
        self.user_btn.setMaximumWidth(600)
        self.user_btn.clicked.connect(self.handle_user_btn_click)

        # Tombol Admin
        self.admin_btn = QPushButton(" Masuk sebagai Admin")
        self.admin_btn.setIcon(QIcon.fromTheme("administrator"))  # Bisa ganti ke path ikon custom
        self.admin_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.admin_btn.setMinimumHeight(160)
        self.admin_btn.setMinimumWidth(420)
        self.admin_btn.setMaximumWidth(600)
        self.admin_btn.clicked.connect(self.handle_admin_btn_click)

        # Layout tengah untuk tombol User & Admin
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(60)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addStretch()
        btn_layout.addWidget(self.user_btn)

        if not self.current_user or self.current_user.get("role") == "admin":
            btn_layout.addWidget(self.admin_btn)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

        # Tombol Logout di kanan bawah
        self.logout_btn = QPushButton("Keluar")
        self.logout_btn.setObjectName("LogoutButton")
        self.logout_btn.setMinimumHeight(80)
        self.logout_btn.clicked.connect(self.handle_logout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.logout_btn)

        main_layout.addLayout(bottom_layout)

    def handle_logout(self):
        self.close()
        self.logout_successful.emit()

    def handle_user_btn_click(self):
        self.user_role_selected.emit()

    def handle_admin_btn_click(self):
        self.admin_role_selected.emit()

    def show_admin_window(self):
        if self.admin_window is None:
            self.admin_window = AdminWindow()
            self.admin_window.logout_requested.connect(self.handle_admin_logout)
        self.admin_window.showFullScreen()

    def handle_admin_logout(self):
        if self.admin_window:
            self.admin_window.hide()
        self.showFullScreen()  # Show the role selection window again

    def showEvent(self, event):
        super().showEvent(event)
        if not self._fullscreen_initialized:
            self.showFullScreen()
            self._fullscreen_initialized = True

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #F5F5F5;
        }

        #TitleLabel {
            color: #E60012;
            font-size: 40px;
            font-weight: bold;
        }

        QPushButton {
            background-color: #E60012;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 24px;
            border: none;
            border-radius: 30px;
            padding: 24px 48px;
        }
        QPushButton:hover {
            background-color: #CC0010;
        }
        QPushButton:pressed {
            background-color: #99000C;
        }

        #LogoutButton {
            background-color: #555555;
            border-radius: 18px;
            padding: 18px 28px;
            font-size: 18px;
        }
        #LogoutButton:hover {
            background-color: #333333;
        }
        """
