# (Tambahkan import ini di bagian atas main.py jika menaruh kelas di sini)
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

class LoadingWindow(QWidget):
    """Widget sederhana untuk menampilkan status loading."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Membuatnya tampil seperti splash screen tanpa frame
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # Opsional: background transparan
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 10px;") # Latar semi-transparan

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        self.loading_label = QLabel("Memuat Kamera...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(self.loading_label)

        # Opsional: Tambahkan progress bar indeterminate
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Mode indeterminate (bolak-balik)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #555;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #E60012; /* Warna primer Denso */
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.setFixedSize(300, 120) # Sesuaikan ukuran

    def center_on_screen(self, app):
        """Pusatkan jendela di layar utama."""
        screen = app.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)