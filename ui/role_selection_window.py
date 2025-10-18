from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QSizePolicy
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
import sys
from config import APP_NAME, APP_VERSION, UI_SETTINGS
from ui.admin_window import AdminWindow

class RoleSelectionWindow(QWidget):
    logout_successful = pyqtSignal()
    user_role_selected = pyqtSignal()
    admin_role_selected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.admin_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Role Selection - " + APP_NAME)
        self.setMinimumSize(800, 600)
        self.setStyleSheet(self.get_stylesheet())

        # Label Judul
        title = QLabel("Pilih Peran Anda")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("TitleLabel")

        # Tombol User
        self.user_btn = QPushButton(" Masuk sebagai User")
        self.user_btn.setIcon(QIcon.fromTheme("user"))  # Bisa ganti ke path ikon custom
        self.user_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.user_btn.setMinimumHeight(120)
        self.user_btn.setMaximumWidth(320)
        self.user_btn.clicked.connect(self.handle_user_btn_click)


        # Tombol Admin
        self.admin_btn = QPushButton(" Masuk sebagai Admin")
        self.admin_btn.setIcon(QIcon.fromTheme("administrator"))  # Bisa ganti ke path ikon custom
        self.admin_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.admin_btn.setMinimumHeight(120)
        self.admin_btn.setMaximumWidth(320)
        self.admin_btn.clicked.connect(self.handle_admin_btn_click)


        # Layout tengah untuk tombol User & Admin
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(self.user_btn)
        btn_layout.addWidget(self.admin_btn)

        # Tombol Logout di kanan bawah
        self.logout_btn = QPushButton("Keluar")
        self.logout_btn.setObjectName("LogoutButton")
        self.logout_btn.clicked.connect(self.handle_logout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.logout_btn)

        # Layout utama
        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addStretch()
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

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

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #F5F5F5;
        }

        #TitleLabel {
            color: #E60012;
            font-size: 18px;
            font-weight: bold;
        }

        QPushButton {
            background-color: #E60012;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 16px;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
        }
        QPushButton:hover {
            background-color: #CC0010;
        }
        QPushButton:pressed {
            background-color: #99000C;
        }

        #LogoutButton {
            background-color: #555555;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 12px;
        }
        #LogoutButton:hover {
            background-color: #333333;
        }
        """
