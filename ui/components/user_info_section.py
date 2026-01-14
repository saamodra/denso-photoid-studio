"""
User information section component for dashboard
"""
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont


class UserInfoSection:
    """User information section"""

    def __init__(self):
        self.user_name_label = None
        self.user_npk_label = None
        self.user_role_label = None
        self.user_department_label = None

    def create(self, parent):
        """Create user information section"""
        group = QGroupBox()
        group.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # User info labels
        self.user_name_label = QLabel("Memuat...")
        self.user_npk_label = QLabel("")
        self.user_role_label = QLabel("")
        self.user_department_label = QLabel("")

        # Style the labels
        user_style = """
            QLabel {
                font-size: 24px;
                color: #2c3e50;
                margin: 5px 0px;
                padding: 5px;
                border-radius: 5px;
            }
        """

        self.user_name_label.setStyleSheet(user_style + """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #E60012;
                background-color: #fff5f5;
            }
        """)

        self.user_npk_label.setStyleSheet(user_style)
        self.user_role_label.setStyleSheet(user_style)
        self.user_department_label.setStyleSheet(user_style)

        layout.addWidget(self.user_name_label)
        layout.addWidget(self.user_npk_label)
        layout.addWidget(self.user_role_label)
        layout.addWidget(self.user_department_label)

        # Add some spacing
        layout.addStretch()

        return group

    def update_user_info(self, current_user):
        """Update user information display"""
        if current_user:
            self.user_name_label.setText(f"👤 {current_user.get('name', 'Unknown')}")
            self.user_npk_label.setText(f"NPK: {current_user.get('npk', 'N/A')}")
            self.user_role_label.setText(f"Role: {current_user.get('role', 'N/A').title()}")
            self.user_department_label.setText(f"Dept: {current_user.get('department_name', 'N/A')}")
        else:
            self.user_name_label.setText("Tidak ada data pengguna")
            self.user_npk_label.setText("")
            self.user_role_label.setText("")
            self.user_department_label.setText("")
