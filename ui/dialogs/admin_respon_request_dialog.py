import sys
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QTextEdit, QMessageBox,
                             QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal

# Asumsikan Anda memiliki modul database yang bisa diimpor
# Jika tidak, ganti `db_manager` dengan implementasi Anda
from modules.database import db_manager
# try:
# except ImportError:
#     # Mock object untuk testing jika db_manager tidak tersedia
#     class MockDBManager:
#         def update_request_status(self, *args, **kwargs): return True
#         def get_user_by_npk(self, npk): return {"name": "Nama Karyawan Dummy"}
#     db_manager = MockDBManager()


class AdminResponseDialog(QDialog):
    """
    Dialog untuk admin guna menyetujui atau menolak permintaan
    pengambilan foto dari karyawan.
    """
    # Sinyal yang akan dikirim saat aksi berhasil, untuk me-refresh data di halaman sebelumnya
    request_updated = pyqtSignal()

    def __init__(self, request_data, admin_user, parent=None):
        super().__init__(parent)
        self.request_data = request_data
        self.admin_user = admin_user
        
        self.setWindowTitle("Tanggapi Permintaan Karyawan")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        self.init_ui()
        self.apply_styles()
        self.load_request_info()

    def init_ui(self):
        """Inisialisasi semua komponen UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Tanggapi Permintaan")
        title_label.setObjectName("TitleLabel")
        main_layout.addWidget(title_label)

        # --- Bagian Detail Permintaan (Read-only) ---
        details_group = QGroupBox("Detail Permintaan")
        details_layout = QFormLayout(details_group)
        details_layout.setSpacing(10)
        
        self.requester_name_label = QLabel("...")
        self.request_time_label = QLabel("...")
        self.request_desc_label = QLabel("...")
        self.request_desc_label.setWordWrap(True)
        self.request_desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        details_layout.addRow("<b>Pemohon:</b>", self.requester_name_label)
        details_layout.addRow("<b>Waktu Permintaan:</b>", self.request_time_label)
        details_layout.addRow("<b>Alasan Pemohon:</b>", self.request_desc_label)

        # --- Bagian Form Respon Admin ---
        response_group = QGroupBox("Formulir Respon")
        response_layout = QVBoxLayout(response_group)
        
        response_layout.addWidget(QLabel("Catatan / Remark (Opsional):"))
        self.remark_input = QTextEdit()
        self.remark_input.setPlaceholderText("Berikan alasan atau catatan untuk respon Anda...")
        self.remark_input.setMinimumHeight(100)
        response_layout.addWidget(self.remark_input)

        # --- Bagian Tombol Aksi ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Batal")
        self.cancel_button.setObjectName("CancelButton")
        self.cancel_button.clicked.connect(self.reject) # QDialog.reject()

        self.reject_button = QPushButton("Tolak Permintaan")
        self.reject_button.setObjectName("RejectButton")
        self.reject_button.clicked.connect(self._handle_reject)

        self.approve_button = QPushButton("Setujui Permintaan")
        self.approve_button.setObjectName("ApproveButton")
        self.approve_button.clicked.connect(self._handle_approve)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.reject_button)
        button_layout.addWidget(self.approve_button)

        main_layout.addWidget(details_group)
        main_layout.addWidget(response_group)
        main_layout.addLayout(button_layout)
        
    def apply_styles(self):
        """Menerapkan styling ke seluruh widget dialog."""
        primary_color = "#E60012"
        primary_hover_color = "#C30010"
        dark_font_color = "#212121"
        light_font_color = "#757575"
        border_color = "#E0E0E0"
        reject_color = "#424242"
        reject_hover_color = "#313131"
        cancel_color = "#BDBDBD"
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: #FFFFFF; }}
            #TitleLabel {{
                font-size: 22px;
                font-weight: bold;
                color: {dark_font_color};
                padding-bottom: 10px;
            }}
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
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
            QTextEdit {{
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 8px;
                background-color: #F9F9F9;
            }}
            QTextEdit:focus {{ border: 1px solid {primary_color}; }}
            QPushButton {{
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 12px 20px;
                min-width: 120px;
            }}
            #ApproveButton {{
                background-color: {primary_color};
                color: white;
            }}
            #ApproveButton:hover {{ background-color: {primary_hover_color}; }}
            #RejectButton {{
                background-color: {reject_color};
                color: white;
            }}
            #RejectButton:hover {{ background-color: {reject_hover_color}; }}
            #CancelButton {{
                background-color: {cancel_color};
                color: {dark_font_color};
            }}
            #CancelButton:hover {{ background-color: #A1A1A1; }}
        """)
        
    def load_request_info(self):
        """Memuat data dari `request_data` ke dalam UI."""
        npk = self.request_data.get("npk", "N/A")
        
        # Ambil nama user dari database
        user_info = db_manager.get_user_by_npk(npk)
        user_name = user_info.get("name", "Tidak Ditemukan")
        self.requester_name_label.setText(f"{user_name} (NPK: {npk})")

        # Format waktu
        try:
            req_time_str = self.request_data.get("request_time", "")
            req_time_dt = datetime.fromisoformat(req_time_str.replace('Z', '+00:00'))
            self.request_time_label.setText(req_time_dt.strftime('%d %B %Y, %H:%M:%S'))
        except (ValueError, TypeError):
            self.request_time_label.setText("Waktu tidak valid")

        self.request_desc_label.setText(self.request_data.get("request_desc", "Tidak ada alasan diberikan."))

    def _handle_approve(self):
        """Menangani logika saat tombol 'Setujui' diklik."""
        self._submit_response("approved")

        # Update user last_take_photo supaya bisa foto lagi
        update_data = {
            'last_take_photo': '',
        }
        user_npk = self.request_data.get("npk")
        db_manager.update_user(user_npk, update_data)

    def _handle_reject(self):
        """Menangani logika saat tombol 'Tolak' diklik."""
        self._submit_response("rejected")

    def _submit_response(self, new_status):
        """Fungsi inti untuk mengirimkan respon ke database."""
        request_id = self.request_data.get("request_id")
        remark = self.remark_input.toPlainText().strip()
        admin_name = self.admin_user.get("name", "System")
        
        if not request_id:
            QMessageBox.critical(self, "Error", "ID Permintaan tidak valid.")
            return

        # Panggil fungsi database untuk update
        success = db_manager.update_request_history(
            request_id=request_id,
            status=new_status,
            remark=remark,
            respons_name=admin_name
        )
        
        if success:
            QMessageBox.information(self, "Sukses", f"Permintaan telah berhasil di-{new_status}.")
            self.request_updated.emit() # Kirim sinyal
            self.accept() # Tutup dialog dengan status sukses
        else:
            QMessageBox.critical(self, "Gagal", "Gagal memperbarui status permintaan di database.")


# --- Untuk Menjalankan Jendela Ini Secara Mandiri (Testing) ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Buat data dummy untuk testing
    dummy_request = {
        "id": 101,
        "npk": "00123",
        "request_time": "2025-10-12T08:30:00Z",
        "request_desc": "Kartu identitas lama saya hilang saat perjalanan dinas. Saya memerlukan kartu baru secepatnya untuk akses ke area produksi.",
        "status": "requested"
    }
    dummy_admin = {
        "npk": "99999",
        "name": "Admin HR"
    }

    dialog = AdminResponseDialog(request_data=dummy_request, admin_user=dummy_admin)
    dialog.exec()
    
    sys.exit()
