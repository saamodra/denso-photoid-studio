#!/usr/bin/env python3
"""
Minimal UI test to verify PyQt6 is working correctly
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Test Window")
        self.setGeometry(200, 200, 400, 300)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)

        # Test label
        label = QLabel("PyQt6 UI Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; color: #2c3e50; margin: 20px;")
        layout.addWidget(label)

        # Test button
        button = QPushButton("Test Button - Click Me!")
        button.clicked.connect(self.button_clicked)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(button)

        # Status label
        self.status_label = QLabel("UI is working correctly!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #27ae60; margin: 10px;")
        layout.addWidget(self.status_label)

    def button_clicked(self):
        self.status_label.setText("Button clicked! PyQt6 is functioning properly.")
        print("✅ Button clicked - UI is responsive")

def main():
    print("Testing PyQt6 UI...")

    try:
        # Create application
        app = QApplication(sys.argv)
        print("✅ QApplication created successfully")

        # Create and show window
        window = TestWindow()
        print("✅ Test window created")

        window.show()
        print("✅ Window shown")
        print("If you can see the test window, PyQt6 UI is working correctly.")
        print("Close the window to continue...")

        # Run application
        exit_code = app.exec()
        print(f"✅ Application exited with code: {exit_code}")

        return exit_code

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
