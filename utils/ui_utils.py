"""
UI utility functions and common styling
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


def create_standard_button_styles():
    """Return standard button styles for the application"""
    return """
        QPushButton {
            background-color: #E60012;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 14px;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #CC0010;
        }
        QPushButton:pressed {
            background-color: #99000C;
        }
        QPushButton#cancelButton {
            background-color: #6c757d;
        }
        QPushButton#cancelButton:hover {
            background-color: #5a6268;
        }
        QPushButton#cancelButton:pressed {
            background-color: #495057;
        }
    """


def create_dialog_styles():
    """Return standard dialog styles"""
    return """
        QDialog {
            background-color: #FFFFFF;
            color: #333333;
        }
        QLabel {
            color: #333333;
            font-size: 14px;
            margin: 0px;
            padding: 0px;
        }
        QLabel#TitleLabel {
            font-size: 20px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 10px;
        }
        QLabel#SectionTitle {
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 5px;
        }
    """


def create_frame_styles():
    """Return standard frame styles"""
    return """
        QFrame#DetailsFrame {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 10px;
        }
        QFrame#ExplanationFrame {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
        }
    """


def create_text_edit_styles():
    """Return standard text edit styles"""
    return """
        QTextEdit {
            border: 1px solid #CCCCCC;
            border-radius: 8px;
            padding: 8px;
            font-size: 13px;
            background-color: #FFFFFF;
            color: #333333;
        }
    """
