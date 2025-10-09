import sys
import os
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame, QGroupBox, QFormLayout,
                             QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from modules.database import db_manager

from config import PROCESSED_DIR 

class EmployeeDetailPage(QDialog):
    """
    Jendela dialog untuk menampilkan rincian data seorang karyawan,
    termasuk pratinjau foto dan kartu ID.
    """
    def __init__(self, employee_data, parent=None):
        super().__init__(parent)
        self.employee_data = employee_data
        
        # Get image save path from database configuration
        self.PHOTOS_DIR = db_manager.get_app_config('image_save_path')
        
        self.setWindowTitle(f"Detail Karyawan - {self.employee_data.get('name', 'N/A')}")
        self.setMinimumSize(1000, 600)
        
        self.init_ui()
        self.apply_styles()
        self.load_data()

    def init_ui(self):
        """Inisialisasi semua komponen UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        content_layout = QHBoxLayout()
        
        # --- Kolom Kiri: Detail Data Karyawan ---
        details_groupbox = QGroupBox("Data Karyawan")
        details_form_layout = QFormLayout()
        details_form_layout.setSpacing(15)
        details_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Siapkan label untuk setiap field data
        self.labels = {
            "npk": QLabel("..."), "name": QLabel("..."), "password": QLabel("..."),
            "role": QLabel("..."), "section_id": QLabel("..."), "section_name": QLabel("..."),
            "department_id": QLabel("..."), "department_name": QLabel("..."),
            "company": QLabel("..."), "plant": QLabel("..."), "last_access": QLabel("..."),
            "last_take_photo": QLabel("..."), "photo_filename": QLabel("..."),
            "card_filename": QLabel("...")
        }
        
        # Tambahkan baris ke form layout
        details_form_layout.addRow("<b>NPK:</b>", self.labels["npk"])
        details_form_layout.addRow("<b>Nama:</b>", self.labels["name"])
        details_form_layout.addRow("<b>Role:</b>", self.labels["role"])
        details_form_layout.addRow("<b>Password:</b>", self.labels["password"])
        details_form_layout.addRow(QLabel()) # Separator
        details_form_layout.addRow("<b>Seksi:</b>", self.labels["section_name"])
        details_form_layout.addRow("<b>Departemen:</b>", self.labels["department_name"])
        details_form_layout.addRow("<b>Perusahaan:</b>", self.labels["company"])
        details_form_layout.addRow("<b>Plant:</b>", self.labels["plant"])
        details_form_layout.addRow(QLabel()) # Separator
        details_form_layout.addRow("<b>Akses Terakhir:</b>", self.labels["last_access"])
        details_form_layout.addRow("<b>Pengambilan Foto Terakhir:</b>", self.labels["last_take_photo"])
        details_form_layout.addRow("<b>File Foto:</b>", self.labels["photo_filename"])
        details_form_layout.addRow("<b>File Kartu:</b>", self.labels["card_filename"])

        details_groupbox.setLayout(details_form_layout)

        # --- Kolom Kanan: Pratinjau Foto ---
        photos_layout = QVBoxLayout()
        
        original_photo_groupbox = QGroupBox("Preview Foto Original")
        original_photo_layout = QVBoxLayout()
        self.original_photo_label = QLabel("Foto tidak ditemukan")
        self.original_photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_photo_label.setMinimumSize(300, 300)
        original_photo_layout.addWidget(self.original_photo_label)
        original_photo_groupbox.setLayout(original_photo_layout)

        card_photo_groupbox = QGroupBox("Preview Kartu ID")
        card_photo_layout = QVBoxLayout()
        self.card_photo_label = QLabel("Kartu ID tidak ditemukan")
        self.card_photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_photo_label.setMinimumSize(300, 300)
        card_photo_layout.addWidget(self.card_photo_label)
        card_photo_groupbox.setLayout(card_photo_layout)
        
        photos_layout.addWidget(original_photo_groupbox)
        photos_layout.addWidget(card_photo_groupbox)

        content_layout.addWidget(details_groupbox, 60) # 60% width
        content_layout.addLayout(photos_layout, 40)    # 40% width

        # --- Footer: Tombol Aksi ---
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        self.back_button = QPushButton("Kembali")
        self.back_button.setObjectName("BackButton")
        self.back_button.clicked.connect(self.accept) # Menutup dialog

        self.print_button = QPushButton("🖨️ Print ID Card")
        self.print_button.clicked.connect(self.print_card_action)
        
        footer_layout.addWidget(self.back_button)
        footer_layout.addWidget(self.print_button)
        
        main_layout.addLayout(content_layout)
        main_layout.addLayout(footer_layout)

    def apply_styles(self):
        """Menerapkan styling ke seluruh widget dialog."""
        primary_color = "#E60012"
        dark_font_color = "#212121"
        border_color = "#E0E0E0"
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #FFFFFF;
            }}
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: {dark_font_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                background-color: #FFFFFF;
            }}
            QLabel {{
                font-size: 14px;
                color: {dark_font_color};
            }}
            QPushButton {{
                background-color: {primary_color};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background-color: #C30010;
            }}
            #BackButton {{
                background-color: {border_color};
                color: {dark_font_color};
            }}
            #BackButton:hover {{
                background-color: #BDBDBD;
            }}
            #OriginalPhotoLabel, #CardPhotoLabel {{
                border: 2px dashed {border_color};
                border-radius: 5px;
            }}
        """)

    def load_data(self):
        """Memuat data karyawan ke dalam widget UI."""
        for key, label_widget in self.labels.items():
            value = self.employee_data.get(key, "-")
            label_widget.setText(str(value))
        
        # Atur password agar tidak ditampilkan secara penuh
        self.labels["password"].setText("••••••••")
        
        # Muat gambar original
        photo_filename = self.employee_data.get("photo_filename")
        if photo_filename:
            # Ganti PHOTOS_DIR dengan path folder foto asli Anda
            photo_path = os.path.join(self.PHOTOS_DIR, photo_filename)
            self.set_image_preview(self.original_photo_label, photo_path)

        # Muat gambar kartu ID
        card_filename = self.employee_data.get("card_filename")
        if card_filename:
            # Ganti PROCESSED_DIR dengan path folder kartu ID Anda
            card_path = os.path.join(PROCESSED_DIR, card_filename)
            self.set_image_preview(self.card_photo_label, card_path)

    def set_image_preview(self, label_widget, image_path):
        """Menampilkan gambar di QLabel dengan ukuran yang pas."""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(label_widget.size(), 
                                          Qt.AspectRatioMode.KeepAspectRatio, 
                                          Qt.TransformationMode.SmoothTransformation)
            label_widget.setPixmap(scaled_pixmap)
        else:
            label_widget.setText(f"File tidak ditemukan:\n{os.path.basename(image_path)}")

    def print_card_action(self):
        """Fungsi placeholder untuk aksi print kartu ID."""
        # TODO: Implementasikan logika untuk print kartu ID di sini
        # Contoh: menggunakan QPrinter atau memanggil library lain.
        QMessageBox.information(self, "Informasi", "Fungsi 'Print ID Card' belum diimplementasikan.")

# --- Untuk Menjalankan Jendela Ini Secara Mandiri (Testing) ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Buat data dummy untuk testing
    dummy_employee = {
        "npk": "00123", "name": "Budi Santoso", "password": "pass",
        "role": "Operator", "section_id": "SEC01", "section_name": "Produksi A",
        "department_id": "DEP01", "department_name": "Manufaktur",
        "company": "PT. Denso Indonesia", "plant": "Cikarang",
        "last_access": "2025-10-10 05:00:00", "last_take_photo": "2025-09-15 10:30:00",
        "photo_filename": "photo_123.jpg", "card_filename": "card_123.png"
    }
    # Pastikan Anda memiliki folder dan file gambar dummy untuk testing
    # os.makedirs(PHOTOS_DIR, exist_ok=True)
    # os.makedirs(PROCESSED_DIR, exist_ok=True)
    # Image.new('RGB', (100, 100), color = 'red').save(os.path.join(PHOTOS_DIR, 'photo_123.jpg'))
    # Image.new('RGB', (100, 100), color = 'blue').save(os.path.join(PROCESSED_DIR, 'card_123.png'))

    dialog = EmployeeDetailPage(dummy_employee)
    dialog.exec()
    
    sys.exit()