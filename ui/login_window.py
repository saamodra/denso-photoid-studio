import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QDialog, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class CustomDialog(QDialog):
    """Custom dialog with consistent styling"""
    def __init__(self, parent=None, title="", message="", buttons=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if buttons is None:
            buttons = [("OK", QDialog.DialogCode.Accepted)]

        self.buttons = []
        for text, role in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, r=role: self.done(r))
            button_layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addLayout(button_layout)

        # Apply styling
        self.setStyleSheet("""
            CustomDialog {
                background-color: #FFFFFF;
                color: #333333;
            }
            QLabel {
                background-color: #FFFFFF;
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #E60012;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #CC0010;
            }
            QPushButton:pressed {
                background-color: #99000C;
            }
        """)

class LoginPage(QWidget):
    """
    Halaman login yang dibuat menggunakan PyQt6.
    Mengirimkan sinyal 'login_successful' ketika otentikasi berhasil.
    """
    login_successful = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Inisialisasi user interface untuk halaman login."""
        # Layout utama untuk memusatkan kotak login di tengah jendela
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
        self.id_entry.setMinimumHeight(40)
        container_layout.addWidget(id_label)
        container_layout.addWidget(self.id_entry)

        # Input Password
        password_label = QLabel("Password:")
        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Masukkan Password")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password) # Sembunyikan karakter password
        self.password_entry.setMinimumHeight(40)
        container_layout.addWidget(password_label)
        container_layout.addWidget(self.password_entry)

        container_layout.addSpacing(20)

        # Tombol Login
        login_button = QPushButton("Login")
        login_button.setMinimumHeight(50)
        login_button.clicked.connect(self.check_login)
        container_layout.addWidget(login_button)

        # Tempatkan kontainer login di tengah grid layout utama
        main_layout.addWidget(login_container, 0, 0, Qt.AlignmentFlag.AlignCenter)

        # Atur fokus awal ke input ID
        self.id_entry.setFocus()

        # Terapkan styling
        self.apply_style()

    def check_login(self):
        """Memeriksa kredensial yang dimasukkan pengguna."""
        user_id = self.id_entry.text()
        password = self.password_entry.text()

        # ####################################################################
        # ###                                                              ###
        # ###    GANTI BAGIAN INI DENGAN LOGIKA ID & PASSWORD ANDA         ###
        # ###                                                              ###
        # ####################################################################

        # Contoh validasi:
        if user_id == "admin" and password == "12345":
            print("Login berhasil!")
            self.login_successful.emit()  # Kirim sinyal bahwa login berhasil
        else:
            # Tampilkan pesan error menggunakan custom dialog
            error_dialog = CustomDialog(
                self,
                "Login Gagal",
                "ID Pengguna atau Password yang Anda masukkan salah."
            )
            error_dialog.exec()

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
        confirm_dialog = CustomDialog(
            self,
            "Konfirmasi",
            "Apakah anda yakin anda ingin keluar?",
            [("Tidak", QDialog.DialogCode.Rejected), ("Ya", QDialog.DialogCode.Accepted)]
        )

        result = confirm_dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            event.accept()
        else:
            event.ignore()
