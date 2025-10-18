import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QDialog, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from modules.database import db_manager
from ui.dialogs.custom_dialog import CustomStyledDialog


class LoginPage(QWidget):
    """
    Halaman login yang dibuat menggunakan PyQt6.
    Mengirimkan sinyal 'login_successful' ketika otentikasi berhasil.
    """
    login_successful = pyqtSignal(dict)  # Emit user data on successful login

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        """Inisialisasi user interface untuk halaman login."""
        # Layout utama untuk memusatkan kotak login di tengah jendela
        self.setWindowTitle("Login Window")
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        # Kontainer untuk elemen-elemen login dengan frame dan style
        login_container = QFrame(self)
        login_container.setFrameShape(QFrame.Shape.StyledPanel)
        login_container.setObjectName("LoginContainer")
        login_container.setFixedWidth(400) # Atur lebar kotak login

        # Layout vertikal untuk isi dari kotak login
        container_layout = QVBoxLayout(login_container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(15)

        # --- Tambahkan Widget ke Kontainer ---

        # Judul
        title = QLabel("Selamat Datang")
        title.setFont(QFont("Helvetica", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("TitleLabel")
        container_layout.addWidget(title)

        # Sub-judul
        subtitle = QLabel("Silakan login untuk melanjutkan")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("SubtitleLabel")
        container_layout.addWidget(subtitle)
        container_layout.addSpacing(20) # Beri jarak

        # Input ID Pengguna
        id_label = QLabel("ID Pengguna:")
        self.id_entry = QLineEdit(self)
        self.id_entry.setPlaceholderText("Masukkan ID Anda")
        self.id_entry.setText("ADMIN001")
        self.id_entry.setMinimumHeight(40)
        container_layout.addWidget(id_label)
        container_layout.addWidget(self.id_entry)

        # Input Password
        password_label = QLabel("Password:")
        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Masukkan Password")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password) # Sembunyikan karakter password
        self.password_entry.setMinimumHeight(40)
        self.password_entry.setText("admin123")
        container_layout.addWidget(password_label)
        container_layout.addWidget(self.password_entry)
        self.password_entry.returnPressed.connect(self.check_login)

        container_layout.addSpacing(20)

        # Tombol Login
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(50)
        self.login_button.clicked.connect(self.check_login)
        container_layout.addWidget(self.login_button)

        # Tempatkan kontainer login di tengah grid layout utama
        main_layout.addWidget(login_container, 0, 0, Qt.AlignmentFlag.AlignCenter)

        # Atur fokus awal ke input ID
        self.id_entry.setFocus()

        # Terapkan styling
        self.apply_style()

    def check_login(self):
        """Memeriksa kredensial yang dimasukkan pengguna menggunakan database."""
        user_id = self.id_entry.text().strip()
        password = self.password_entry.text()

        # Validasi input
        if not user_id or not password:
            error_dialog = CustomStyledDialog(
                self,
                title="Input Tidak Valid",
                message="ID Pengguna dan Password harus diisi."
            )
            error_dialog.exec()
            return

        try:
            # Authenticate user using database
            user = db_manager.authenticate_user(user_id, password)

            if user:
                # Store current user data
                self.current_user = user

                # Clear password field for security
                self.password_entry.clear()

                # Emit signal with user data
                self.login_successful.emit(user)
            else:
                # Show error message
                error_dialog = CustomStyledDialog(
                    self,
                    title="Login Gagal",
                    message="ID Pengguna atau Password yang Anda masukkan salah.\nPastikan Anda telah terdaftar dalam sistem."
                )
                error_dialog.exec()

        except Exception as e:
            # Show error message for database/system errors
            error_dialog = CustomStyledDialog(
                self,
                title="Error Sistem",
                message=f"Terjadi kesalahan saat melakukan login:\n{str(e)}"
            )
            error_dialog.exec()

    def get_current_user(self):
        """Get current logged in user data"""
        return self.current_user

    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.id_entry.clear()
        self.password_entry.clear()
        self.id_entry.setFocus()

    def apply_style(self):
        """Menerapkan styling modern menggunakan Qt StyleSheet (mirip CSS)."""
        self.setStyleSheet("""
            /* Style untuk widget utama (latar belakang) */
            LoginPage {
                background-color: #F5F5F5; /* abu terang */
            }

            /* Style untuk kontainer/kotak login */
            #LoginContainer {
                background-color: #FFFFFF; /* putih */
                border-radius: 15px;
                border: 1px solid #E0E0E0; /* sedikit border abu */
            }

            /* Style untuk label judul dan sub-judul */
            #TitleLabel {
                color: #E60012; /* merah Denso */
                font-weight: bold;
                font-size: 18px;
            }
            #SubtitleLabel {
                color: #555555; /* abu gelap */
                font-size: 12px;
            }

            /* Style untuk semua QLabel */
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #333333; /* teks utama */
            }

            /* Style untuk input field QLineEdit */
            QLineEdit {
                border: 2px solid #CCCCCC;
                border-radius: 8px;
                padding: 0 10px;
                font-size: 14px;
                background-color: #FFFFFF;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #E60012; /* merah saat fokus */
            }

            /* Style untuk tombol */
            QPushButton {
                background-color: #E60012; /* merah Denso */
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 25px;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background-color: #CC0010; /* merah lebih gelap */
            }
            QPushButton:pressed {
                background-color: #99000C; /* merah tua */
            }

        """)

    def closeEvent(self, event):
        """Handle window close event"""
        confirm_dialog = CustomStyledDialog(
            self,
            title="Konfirmasi",
            message="Apakah anda yakin anda ingin keluar?",
            buttons=[("Tidak", QDialog.DialogCode.Rejected), ("Ya", QDialog.DialogCode.Accepted)]
        )

        # Set cancel button styling
        confirm_dialog.set_cancel_button(0)  # "Tidak" button as cancel

        result = confirm_dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            event.accept()
        else:
            event.ignore()
