"""
Print Manager Module
Handles printing functionality and printer management
"""
import os
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtWidgets import QApplication
from config import PRINT_SETTINGS


class PrintManager:
    """Main print management class"""

    def __init__(self):
        self.available_printers = self.get_system_printers()
        self.default_printer = None
        self.print_settings = PRINT_SETTINGS.copy()

    def get_system_printers(self):
        """Get list of system printers"""
        printers = []

        try:
            # For macOS
            if os.name == 'posix' and os.uname().sysname == 'Darwin':
                result = subprocess.run(['lpstat', '-p'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line.startswith('printer '):
                            printer_name = line.split()[1]
                            printers.append({
                                'name': printer_name,
                                'status': 'available'
                            })

            # For Windows
            elif os.name == 'nt':
                import win32print
                printer_list = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
                for printer in printer_list:
                    printers.append({
                        'name': printer[2],
                        'status': 'available'
                    })

            # For Linux
            else:
                result = subprocess.run(['lpstat', '-p'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if 'printer' in line:
                            parts = line.split()
                            if len(parts) > 1:
                                printers.append({
                                    'name': parts[1],
                                    'status': 'available'
                                })

        except Exception as e:
            print(f"Error getting system printers: {e}")
            # Add a default printer entry
            printers.append({
                'name': 'Default Printer',
                'status': 'available'
            })

        return printers

    def get_available_printers(self):
        """Return list of available printers"""
        return self.available_printers

    def set_default_printer(self, printer_name):
        """Set default printer"""
        for printer in self.available_printers:
            if printer['name'] == printer_name:
                self.default_printer = printer_name
                return True
        return False

    def prepare_image_for_printing(self, image, copies=1):
        """Prepare image for printing with proper scaling"""
        if isinstance(image, str):
            image = Image.open(image)

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Scale to proper DPI for printing
        dpi = self.print_settings['dpi']

        # Calculate ID card size in pixels
        width_mm, height_mm = self.print_settings['id_card_size']
        width_px = int(width_mm * dpi / 25.4)
        height_px = int(height_mm * dpi / 25.4)

        # Resize image to exact ID card dimensions
        print_image = image.resize((width_px, height_px), Image.Resampling.LANCZOS)

        # Create print layout for multiple copies
        if copies > 1:
            print_image = self._create_multi_copy_layout(print_image, copies)

        return print_image

    def _create_multi_copy_layout(self, image, copies):
        """Create layout for multiple copies"""
        # Calculate layout (e.g., 2x2 for 4 copies)
        if copies <= 1:
            return image
        elif copies <= 4:
            cols, rows = 2, 2
        elif copies <= 6:
            cols, rows = 3, 2
        elif copies <= 9:
            cols, rows = 3, 3
        else:
            cols, rows = 4, 3

        img_width, img_height = image.size
        layout_width = cols * img_width + (cols - 1) * 20  # 20px gap
        layout_height = rows * img_height + (rows - 1) * 20

        layout = Image.new('RGB', (layout_width, layout_height), 'white')

        for i in range(min(copies, cols * rows)):
            row = i // cols
            col = i % cols
            x = col * (img_width + 20)
            y = row * (img_height + 20)
            layout.paste(image, (x, y))

        return layout

    def print_image_qt(self, image, printer_name=None):
        """Print image using Qt print system"""
        try:
            # Create printer
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)

            if printer_name:
                printer.setPrinterName(printer_name)

            # Set print quality
            printer.setResolution(self.print_settings['dpi'])
            printer.setColorMode(QPrinter.ColorMode.Color)

            # Show print dialog
            app = QApplication.instance()
            if app is None:
                app = QApplication([])

            print_dialog = QPrintDialog(printer)
            if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
                return self._do_qt_print(image, printer)

        except Exception as e:
            print(f"Error printing with Qt: {e}")
            return False

        return False

    def _do_qt_print(self, image, printer):
        """Perform actual Qt printing"""
        try:
            # Convert PIL image to QPixmap
            if isinstance(image, str):
                pixmap = QPixmap(image)
            else:
                # Convert PIL to QPixmap
                image_path = self._save_temp_image(image)
                pixmap = QPixmap(image_path)

            # Create painter
            painter = QPainter()
            painter.begin(printer)

            # Get print area
            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)

            # Scale image to fit page while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                int(page_rect.width()),
                int(page_rect.height()),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # Center image on page
            x = (page_rect.width() - scaled_pixmap.width()) / 2
            y = (page_rect.height() - scaled_pixmap.height()) / 2

            # Draw image
            painter.drawPixmap(int(x), int(y), scaled_pixmap)
            painter.end()

            return True

        except Exception as e:
            print(f"Error in Qt printing: {e}")
            return False

    def print_image_system(self, image, printer_name=None, copies=1):
        """Print image using system print command"""
        try:
            # Save image to temporary file
            temp_path = self._save_temp_image(image)

            # Prepare image for printing
            print_image = self.prepare_image_for_printing(temp_path, copies)
            print_path = self._save_temp_image(print_image, suffix='_print')

            # Print using system command
            success = self._system_print_command(print_path, printer_name)

            # Cleanup temp files
            try:
                os.remove(temp_path)
                os.remove(print_path)
            except:
                pass

            return success

        except Exception as e:
            print(f"Error printing with system command: {e}")
            return False

    def _save_temp_image(self, image, suffix=''):
        """Save image to temporary file"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'{suffix}.png') as temp_file:
            if isinstance(image, str):
                # Copy existing file
                import shutil
                shutil.copy2(image, temp_file.name)
            else:
                # Save PIL image
                image.save(temp_file.name, format='PNG', dpi=(300, 300))
            return temp_file.name

    def _system_print_command(self, image_path, printer_name=None):
        """Execute system print command"""
        try:
            if os.name == 'posix' and os.uname().sysname == 'Darwin':
                # macOS
                cmd = ['lpr']
                if printer_name:
                    cmd.extend(['-P', printer_name])
                cmd.append(image_path)

            elif os.name == 'nt':
                # Windows
                if printer_name:
                    cmd = ['print', f'/D:{printer_name}', image_path]
                else:
                    cmd = ['print', image_path]

            else:
                # Linux
                cmd = ['lpr']
                if printer_name:
                    cmd.extend(['-P', printer_name])
                cmd.append(image_path)

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception as e:
            print(f"Error executing print command: {e}")
            return False

    def create_print_preview(self, image, copies=1):
        """Create print preview image"""
        preview_image = self.prepare_image_for_printing(image, copies)

        # Add print margins and page border for preview
        margin = 50
        width, height = preview_image.size
        preview_width = width + 2 * margin
        preview_height = height + 2 * margin

        preview = Image.new('RGB', (preview_width, preview_height), 'white')

        # Draw page border
        draw = ImageDraw.Draw(preview)
        draw.rectangle([0, 0, preview_width-1, preview_height-1], outline='gray', width=2)

        # Paste image with margin
        preview.paste(preview_image, (margin, margin))

        return preview

    def get_print_settings(self):
        """Get current print settings"""
        return self.print_settings.copy()

    def update_print_settings(self, **settings):
        """Update print settings"""
        for key, value in settings.items():
            if key in self.print_settings:
                self.print_settings[key] = value

    def validate_printer(self, printer_name):
        """Validate if printer is available"""
        for printer in self.available_printers:
            if printer['name'] == printer_name:
                return True
        return False

    def get_printer_status(self, printer_name):
        """Get printer status"""
        try:
            if os.name == 'posix':
                result = subprocess.run(['lpstat', '-p', printer_name],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    if 'idle' in result.stdout.lower():
                        return 'ready'
                    elif 'printing' in result.stdout.lower():
                        return 'printing'
                    else:
                        return 'unknown'
                else:
                    return 'offline'
            else:
                return 'unknown'  # Status check not implemented for Windows

        except Exception as e:
            print(f"Error checking printer status: {e}")
            return 'unknown'

    def refresh_printers(self):
        """Refresh printer list"""
        self.available_printers = self.get_system_printers()
        return self.available_printers
