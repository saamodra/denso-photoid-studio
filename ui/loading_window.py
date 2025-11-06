# (Tambahkan import ini di bagian atas main.py jika menaruh kelas di sini)
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QSizePolicy
from PyQt6.QtCore import Qt

class LoadingWindow(QWidget):
    """Widget sederhana untuk menampilkan status loading."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Tampil sebagai splash sederhana; gunakan latar putih dan teks gelap
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #E0E0E0; border-radius: 10px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        self.loading_label = QLabel("Menyiapkan aplikasi...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #1a1a1a; font-size: 14px; font-weight: normal; margin-bottom: 8px;")
        self.loading_label.setWordWrap(True)
        self.loading_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.loading_label)

        # Opsional: Tambahkan progress bar indeterminate
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Mode indeterminate (bolak-balik)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #D0D0D0;
                border-radius: 5px;
                background-color: #f2f2f2;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #E60012; /* Warna primer */
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.setFixedSize(360, 130) # Sedikit lebih lebar agar teks tidak terpotong

    def center_on_screen(self, app):
        """Pusatkan jendela di layar utama."""
        screen = app.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
