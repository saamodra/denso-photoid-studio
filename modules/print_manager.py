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
try:
    import win32ui
    import win32print
    import win32con
    from PIL import ImageWin
    WIN32_PRINT_AVAILABLE = True
except ImportError:
    win32ui = None
    win32print = None
    win32con = None
    ImageWin = None
    WIN32_PRINT_AVAILABLE = False


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
                    # printers.append({
                    #     'name': printer[2],
                    #     'status': 'available'
                    # })
                    name = printer[2]
                    status = 'available'
                    # Detect HID Fargo printer specifically
                    if 'DTC1250' in name.upper():
                        status = 'HID Fargo detected'
                    printers.append({
                        'name': name,
                        'status': status
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

    # In class PrintManager

    def prepare_image_for_printing(self, image, copies=1):
        """Prepare image for printing, resizing to exact ID card pixel dimensions."""
        if isinstance(image, str):
            image = Image.open(image)

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Target DPI for the card printer (Confirm this for your specific model if needed)
        dpi = self.print_settings.get('card_printer_dpi', 300)

        # Standard CR80 ID card size in mm (approx 85.6mm x 53.98mm)
        # Adjust if your card size or required print area differs slightly
        width_mm = self.print_settings['id_card_size'][0] # e.g., 85.6
        height_mm = self.print_settings['id_card_size'][1] # e.g., 53.98

        # Calculate exact target pixel dimensions
        # IMPORTANT: Ensure width_mm corresponds to width_px, height_mm to height_px
        # Check printer driver settings for expected orientation (Portrait vs Landscape input)
        # Assuming the input image *should be* landscape to print correctly on a portrait card feed
        # If the printer expects portrait input, swap width_px and height_px calculations.
        width_px = int(width_mm * dpi / 25.4)
        height_px = int(height_mm * dpi / 25.4)
        
        # Let's assume CR80: 85.6mm x 53.98mm at 300 DPI
        # width_px = int(85.6 * 300 / 25.4)  # ~1011 pixels
        # height_px = int(53.98 * 300 / 25.4) # ~638 pixels
        # If your card is printed portrait first, maybe dimensions are swapped?
        # width_px = int(53.98 * 300 / 25.4) # ~638
        # height_px = int(85.6 * 300 / 25.4) # ~1011

        print(f"Resizing image for printer: Target {width_px}x{height_px} px at {dpi} DPI")

        # Resize image to the *exact* target dimensions.
        # If the input image aspect ratio doesn't match, it will be stretched.
        # Consider adding cropping here if you need to maintain aspect ratio from original.
        print_image = image.resize((width_px, height_px), Image.Resampling.LANCZOS)

        # --- REMOVE multi-copy layout for single card printing ---
        # Card printers typically print one card at a time.
        # if copies > 1:
        #     print_image = self._create_multi_copy_layout(print_image, copies)

        return print_image
    # def prepare_image_for_printing(self, image, copies=1):
    #     """Prepare image for printing with proper scaling"""
    #     if isinstance(image, str):
    #         image = Image.open(image)

    #     # Convert to RGB if necessary
    #     if image.mode != 'RGB':
    #         image = image.convert('RGB')

    #     # Scale to proper DPI for printing
    #     dpi = self.print_settings['dpi']

    #     # Calculate ID card size in pixels
    #     width_mm, height_mm = self.print_settings['id_card_size']
    #     width_px = int(width_mm * dpi / 25.4)
    #     height_px = int(height_mm * dpi / 25.4)

    #     # Resize image to exact ID card dimensions
    #     print_image = image.resize((width_px, height_px), Image.Resampling.LANCZOS)

    #     # Create print layout for multiple copies
    #     if copies > 1:
    #         print_image = self._create_multi_copy_layout(print_image, copies)

    #     return print_image

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

    # def print_image_system(self, image, printer_name=None, copies=1):
    #     """Print image using system print command"""
    #     try:
    #         # Save image to temporary file
    #         temp_path = self._save_temp_image(image)

    #         # Check if this is a Fargo printer
    #         if printer_name and ('DTC1250' in printer_name.upper()):
    #             print_image = self.prepare_image_for_printing(temp_path, copies)
    #             path = self._save_temp_image(print_image, suffix='_fargo')
    #             result = self.print_to_hid_fargo(path, printer_name)
    #             return result

    #         # Prepare image for printing
    #         print_image = self.prepare_image_for_printing(temp_path, copies)
    #         print_path = self._save_temp_image(print_image, suffix='_print')

    #         # Print using system command
    #         success = self._system_print_command(print_path, printer_name)

    #         # Cleanup temp files
    #         try:
    #             os.remove(temp_path)
    #             os.remove(print_path)
    #         except:
    #             pass

    #         return success

    #     except Exception as e:
    #         print(f"Error printing with system command: {e}")
    #         return False

    # In class PrintManager

    def print_image_system(self, image, printer_name=None, copies=1):
        """Print image using system print command or specific Fargo handler."""
        temp_original_path = None
        temp_prepared_path = None
        try:
            # Save original PIL image/path to a temporary file IF it's not already a path
            if not isinstance(image, str):
                temp_original_path = self._save_temp_image(image, suffix='_orig')
                image_to_prepare = temp_original_path
            else:
                image_to_prepare = image # Use the path directly

            is_fargo = printer_name and ('DTC1250' in printer_name.upper())

            # Prepare image specifically for the target (Fargo or general)
            # For Fargo, ensure prepare_image_for_printing resizes to exact pixels
            print_image_pil = self.prepare_image_for_printing(image_to_prepare, copies if not is_fargo else 1)
            temp_prepared_path = self._save_temp_image(print_image_pil, suffix='_prepared')

            if is_fargo:
                print(f"Detected Fargo printer '{printer_name}'. Using dedicated print function.")
                result = self.print_to_hid_fargo(temp_prepared_path, printer_name)
                return result
            else:
                # Print using generic system command (might still need adjustments)
                print(f"Using generic system print command for '{printer_name}'.")
                success = self._system_print_command(temp_prepared_path, printer_name)
                return success

        except Exception as e:
            print(f"❌ Error in print_image_system: {e}")
            return False
        finally:
            # Cleanup temporary files
            for p in [temp_original_path, temp_prepared_path]:
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception as e_rem:
                        print(f"Warning: Could not remove temp file {p}: {e_rem}")
                        
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
 
    def print_to_hid_fargo(self, image_path, printer_name=None):
        """Send pre-sized image directly to HID Fargo printer using pixel coordinates."""
        if not WIN32_PRINT_AVAILABLE:
            print("HID Fargo printing is only available on Windows with pywin32 installed.")
            return False

        print(f"Attempting to print {os.path.basename(image_path)} to HID Fargo: {printer_name}")

        hprinter = None
        hdc = None
        try:
            if not printer_name:
                printer_name = self.default_printer
            if not printer_name:
                raise ValueError("No printer specified or default printer set.")

            # Load the image (it should already be correctly sized by prepare_image...)
            img = Image.open(image_path)
            img = img.convert("RGB") # Ensure RGB
            img_width, img_height = img.size
            print(f"Image dimensions being sent to printer: {img_width}x{img_height} pixels")

            # --- Printer Setup ---
            hprinter = win32print.OpenPrinter(printer_name)
            # Optional: Get DEVMODE to potentially set specific options like orientation later
            # devmode = win32print.GetPrinter(hprinter, 2)['pDevMode']

            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_name)

            # --- Use MM_TEXT (Pixel Mode) ---
            hdc.SetMapMode(win32con.MM_TEXT)

            # --- Start Print Job ---
            hdc.StartDoc(f"PhotoID Print - {os.path.basename(image_path)}")
            hdc.StartPage()

            # --- Prepare Bitmap ---
            # Convert PIL image to device-independent bitmap (DIB)
            dib = ImageWin.Dib(img)

            # --- Draw Image at (0,0) with exact dimensions ---
            # Since map mode is MM_TEXT, coordinates are pixels.
            # Draw from source (0,0) to (img_width, img_height)
            # onto destination (0,0) to (img_width, img_height) on the printer DC.
            dib.draw(hdc.GetHandleOutput(), (0, 0, img_width, img_height))
            print(f"Drawing image at (0, 0) with size {img_width}x{img_height} using MM_TEXT.")

            # --- Finish Print Job ---
            hdc.EndPage()
            hdc.EndDoc()
            print("✅ Print job successfully sent to spooler for HID Fargo.")
            return True

        except Exception as e:
            print(f"❌ Error printing to HID Fargo: {e}")
            import traceback
            traceback.print_exc() # Print full traceback for detailed debugging
            return False
        finally:
            # --- Cleanup ---
            if hdc:
                try:
                    hdc.DeleteDC()
                except Exception as e_del:
                    print(f"Error deleting DC: {e_del}")
            if hprinter:
                try:
                    win32print.ClosePrinter(hprinter)
                except Exception as e_close:
                    print(f"Error closing printer handle: {e_close}")

    def create_print_preview(self, image, copies=1):
        """Create print preview image"""
        preview_image = self.prepare_image_for_printing(image, copies)

        # Add print margins and page border for preview
        margin = 0
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
