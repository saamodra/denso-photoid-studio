import sys
import os
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame, QGroupBox, QFormLayout,
                             QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from modules.database import db_manager
from modules.print_manager import PrintManager
from ui.dialogs.custom_dialog import CustomStyledDialog

class EmployeeDetailPage(QDialog):
    """
    Jendela dialog untuk menampilkan rincian data seorang karyawan,
    termasuk pratinjau foto dan kartu ID.
    """
    def __init__(self, employee_data, parent=None):
        super().__init__(parent)
        self.employee_data = employee_data
        
        # --- Tambahkan instance PrintManager ---
        self.print_manager = PrintManager()

        # Get image save path from database configuration
        self.PHOTOS_DIR = db_manager.get_app_config('image_save_path')

        if not self.PHOTOS_DIR:
             # Tentukan path default, misal subfolder 'data_karyawan' di direktori aplikasi
             base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Asumsi struktur project
             self.PHOTOS_DIR = os.path.join(base_path, 'data_karyawan', 'photos')
             print(f"⚠️ Peringatan: 'image_save_path' tidak ditemukan di config. Menggunakan default: {self.PHOTOS_DIR}")
             os.makedirs(self.PHOTOS_DIR, exist_ok=True) # Pastikan folder ada
        
        self.setWindowTitle(f"Detail Karyawan - {self.employee_data.get('name', 'N/A')}")
        self.setMinimumSize(1000, 600)
        
        self.init_ui()
        self.apply_styles()
        self.load_data()

    # def init_ui(self):
    #     """Inisialisasi semua komponen UI."""
    #     main_layout = QVBoxLayout(self)
    #     main_layout.setContentsMargins(20, 20, 20, 20)
        
    #     content_layout = QHBoxLayout()
        
    #     # --- Kolom Kiri: Detail Data Karyawan ---
    #     details_groupbox = QGroupBox("Data Karyawan")
    #     details_form_layout = QFormLayout()
    #     details_form_layout.setSpacing(15)
    #     details_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

    #     # Siapkan label untuk setiap field data
    #     self.labels = {
    #         "npk": QLabel("..."), "name": QLabel("..."), "password": QLabel("..."),
    #         "role": QLabel("..."), "section_id": QLabel("..."), "section_name": QLabel("..."),
    #         "department_id": QLabel("..."), "department_name": QLabel("..."),
    #         "company": QLabel("..."), "plant": QLabel("..."), "last_access": QLabel("..."),
    #         "last_take_photo": QLabel("..."), "photo_filename": QLabel("..."),
    #         "card_filename": QLabel("...")
    #     }
        
    #     # Tambahkan baris ke form layout
    #     details_form_layout.addRow("<b>NPK:</b>", self.labels["npk"])
    #     details_form_layout.addRow("<b>Nama:</b>", self.labels["name"])
    #     details_form_layout.addRow("<b>Role:</b>", self.labels["role"])
    #     details_form_layout.addRow("<b>Password:</b>", self.labels["password"])
    #     details_form_layout.addRow(QLabel()) # Separator
    #     details_form_layout.addRow("<b>Seksi:</b>", self.labels["section_name"])
    #     details_form_layout.addRow("<b>Departemen:</b>", self.labels["department_name"])
    #     details_form_layout.addRow("<b>Perusahaan:</b>", self.labels["company"])
    #     details_form_layout.addRow("<b>Plant:</b>", self.labels["plant"])
    #     details_form_layout.addRow(QLabel()) # Separator
    #     details_form_layout.addRow("<b>Akses Terakhir:</b>", self.labels["last_access"])
    #     details_form_layout.addRow("<b>Pengambilan Foto Terakhir:</b>", self.labels["last_take_photo"])
    #     details_form_layout.addRow("<b>File Foto:</b>", self.labels["photo_filename"])
    #     details_form_layout.addRow("<b>File Kartu:</b>", self.labels["card_filename"])

    #     details_groupbox.setLayout(details_form_layout)

    #     # --- Kolom Kanan: Pratinjau Foto ---
    #     photos_layout = QVBoxLayout()
        
    #     original_photo_groupbox = QGroupBox("Preview Foto Original")
    #     original_photo_layout = QVBoxLayout()
    #     self.original_photo_label = QLabel("Foto tidak ditemukan")
    #     self.original_photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     self.original_photo_label.setMinimumSize(300, 300)
    #     original_photo_layout.addWidget(self.original_photo_label)
    #     original_photo_groupbox.setLayout(original_photo_layout)

    #     card_photo_groupbox = QGroupBox("Preview Kartu ID")
    #     card_photo_layout = QVBoxLayout()
    #     self.card_photo_label = QLabel("Kartu ID tidak ditemukan")
    #     self.card_photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     self.card_photo_label.setMinimumSize(300, 300)
    #     card_photo_layout.addWidget(self.card_photo_label)
    #     card_photo_groupbox.setLayout(card_photo_layout)
        
    #     photos_layout.addWidget(original_photo_groupbox)
    #     photos_layout.addWidget(card_photo_groupbox)

    #     content_layout.addWidget(details_groupbox, 60) # 60% width
    #     content_layout.addLayout(photos_layout, 40)    # 40% width

    #     # --- Footer: Tombol Aksi ---
    #     footer_layout = QHBoxLayout()
    #     footer_layout.addStretch()
    #     self.back_button = QPushButton("Kembali")
    #     self.back_button.setObjectName("BackButton")
    #     self.back_button.clicked.connect(self.accept) # Menutup dialog

    #     self.print_button = QPushButton("🖨️ Print ID Card")
    #     self.print_button.clicked.connect(self.print_card_action)
        
    #     footer_layout.addWidget(self.back_button)
    #     footer_layout.addWidget(self.print_button)
        
    #     main_layout.addLayout(content_layout)
    #     main_layout.addLayout(footer_layout)
    def init_ui(self):
        """Inisialisasi semua komponen UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        content_layout = QHBoxLayout()
        
        # --- Kolom Kiri: Detail Data Karyawan (Tidak Berubah) ---
        details_groupbox = QGroupBox("Data Karyawan")
        details_form_layout = QFormLayout()
        details_form_layout.setSpacing(15)
        details_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.labels = {
            "npk": QLabel("..."), "name": QLabel("..."), "password": QLabel("..."),
            "role": QLabel("..."), "section_id": QLabel("..."), "section_name": QLabel("..."),
            "department_id": QLabel("..."), "department_name": QLabel("..."),
            "company": QLabel("..."), "plant": QLabel("..."), "last_access": QLabel("..."),
            "last_take_photo": QLabel("..."), "photo_filename": QLabel("..."),
            "card_filename": QLabel("...")
        }
        
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

        # --- Kolom Kanan: Pratinjau Foto dan Tombol ---
        # Tata letak vertikal baru untuk kolom kanan
        right_column_layout = QVBoxLayout()

        # Layout horizontal BARU untuk menampung DUA pratinjau berdampingan
        previews_layout = QHBoxLayout()
        
        # Pratinjau Foto Original
        original_photo_groupbox = QGroupBox("Preview Foto Original")
        original_photo_layout = QVBoxLayout()
        self.original_photo_label = QLabel("Foto tidak ditemukan")
        self.original_photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Mengubah ukuran agar lebih sesuai dengan rasio potret seperti di gambar
        self.original_photo_label.setMinimumSize(360, 480) 
        self.original_photo_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        original_photo_layout.addWidget(self.original_photo_label)
        original_photo_groupbox.setLayout(original_photo_layout)
        original_photo_groupbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Pratinjau Kartu ID
        card_photo_groupbox = QGroupBox("Preview Kartu ID")
        card_photo_layout = QVBoxLayout()
        self.card_photo_label = QLabel("Kartu ID tidak ditemukan")
        self.card_photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Mengubah ukuran agar lebih sesuai dengan rasio potret
        self.card_photo_label.setMinimumSize(360, 480)
        self.card_photo_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_photo_layout.addWidget(self.card_photo_label)
        card_photo_groupbox.setLayout(card_photo_layout)
        card_photo_groupbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Tambahkan kedua groupbox pratinjau ke layout horizontal
        previews_layout.addWidget(original_photo_groupbox)
        previews_layout.addWidget(card_photo_groupbox)
        
        # --- Tombol Aksi (Dipindahkan) ---
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        self.back_button = QPushButton("Kembali")
        self.back_button.setObjectName("BackButton")
        self.back_button.clicked.connect(self.accept) # Menutup dialog

        self.print_button = QPushButton("🖨️ Print ID Card")
        self.print_button.clicked.connect(self.print_card_action)
        
        footer_layout.addWidget(self.back_button)
        footer_layout.addWidget(self.print_button)
        
        # Tambahkan layout pratinjau (horizontal) dan layout tombol (horizontal)
        # ke dalam tata letak kolom kanan (vertikal)
        right_column_layout.addLayout(previews_layout)
        right_column_layout.addLayout(footer_layout)

        # --- Selesaikan Layout Utama ---
        content_layout.addWidget(details_groupbox, 50) # Beri 50% untuk data
        content_layout.addLayout(right_column_layout, 50) # Beri 50% untuk pratinjau & tombol
        
        # Hapus penambahan footer_layout di sini karena sudah dipindah
        main_layout.addLayout(content_layout)

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
            # Pastikan path folder foto asli Anda benar
            photo_path = os.path.join(self.PHOTOS_DIR, f"original/{photo_filename}") # Konsisten dengan struktur Anda
            self.set_image_preview(self.original_photo_label, photo_path)
        else:
             self.original_photo_label.setText("Foto original\ntidak ditemukan") # Pesan lebih jelas

        # Muat gambar kartu ID
        card_filename = self.employee_data.get("card_filename")
        if card_filename:
            # Pastikan path folder kartu ID Anda benar
            card_path = os.path.join(self.PHOTOS_DIR, f"card/{card_filename}") # Konsisten dengan struktur Anda
            self.set_image_preview(self.card_photo_label, card_path)
        else:
            self.card_photo_label.setText("File Kartu ID\ntidak ditemukan") # Pesan lebih jelas

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
        """Mencetak kartu ID karyawan yang sedang ditampilkan."""
        card_filename = self.employee_data.get("card_filename")

        if not card_filename:
            CustomStyledDialog(self, "Error Cetak", "Nama file kartu ID tidak ditemukan untuk karyawan ini.").exec()
            return

        # Pastikan path folder kartu ID Anda benar
        card_path = os.path.join(self.PHOTOS_DIR, f"card/{card_filename}")

        if not os.path.exists(card_path):
            CustomStyledDialog(self, "Error Cetak", f"File kartu ID tidak ditemukan di:\n{card_path}").exec()
            return

        # --- Dapatkan nama printer target ---
        # Opsi 1: Dari konfigurasi database (direkomendasikan)
        target_printer_name = db_manager.get_app_config('default_printer')

        # Opsi 2: Jika tidak ada di config, coba gunakan default dari PrintManager
        if not target_printer_name:
             target_printer_name = self.print_manager.default_printer
             print(f"Menggunakan printer default yang terdeteksi: {target_printer_name}")

        # Opsi 3: Jika masih tidak ada, minta pengguna memilih (lebih kompleks)
        # Atau tampilkan error jika tidak ada printer sama sekali
        if not target_printer_name:
             printers = self.print_manager.get_available_printers()
             if not printers:
                  CustomStyledDialog(self, "Error Cetak", "Tidak ada printer yang terdeteksi atau dikonfigurasi.").exec()
                  return
             else:
                  # Jika ada printer tapi tidak ada default, ambil yang pertama sebagai fallback
                  target_printer_name = printers[0]['name']
                  print(f"Peringatan: Tidak ada printer kartu default. Menggunakan printer pertama: {target_printer_name}")
                  # Anda mungkin ingin menampilkan dialog pemilihan printer di sini

        # --- Konfirmasi sebelum mencetak ---
        confirm_dialog = CustomStyledDialog(
            self,
            title="Konfirmasi Cetak",
            message=f"Anda akan mencetak kartu ID untuk:\n"
                    f"Nama: {self.employee_data.get('name', 'N/A')}\n"
                    f"NPK: {self.employee_data.get('npk', 'N/A')}\n\n"
                    f"Ke Printer: {target_printer_name}\n\nLanjutkan?",
            buttons=[("Batal", QDialog.DialogCode.Rejected), ("Cetak", QDialog.DialogCode.Accepted)]
        )
        confirm_dialog.set_cancel_button(0)

        if confirm_dialog.exec() == QDialog.DialogCode.Accepted:
            # --- Panggil fungsi print dari PrintManager ---
            print(f"Mencoba mencetak {card_path} ke {target_printer_name}...")
            # Gunakan print_image_system karena memiliki logika Fargo
            success = self.print_manager.print_image_system(
                image=card_path,
                printer_name=target_printer_name,
                copies=1 # Biasanya hanya 1 kartu per cetak
            )

            if success:
                CustomStyledDialog(self, "Cetak Berhasil", f"Kartu ID untuk {self.employee_data.get('name')} telah dikirim ke printer.").exec()
            else:
                CustomStyledDialog(self, "Cetak Gagal", f"Gagal mengirim kartu ID ke printer.\nPeriksa log aplikasi atau status printer.").exec()

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