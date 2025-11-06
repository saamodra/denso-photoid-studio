"""
Image Processor Module
Handles background removal, ID card background application, and image processing
"""
import cv2
import io
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os
from rembg import remove, new_session
from config import PROCESSING_SETTINGS, BACKGROUNDS_DIR, TEMPLATES_DIR, PROCESSED_DIR, BACKGROUND_TEMPLATES, ID_CARD_TEMPLATES


# Global rembg session and shared processor to avoid repeated heavy loads
GLOBAL_REMBG_SESSION = None
_SHARED_PROCESSOR = None


def _assets_dir():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'assets')
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, 'assets')


def preload_rembg_session():
    """Load rembg ONNX model into a global session (CPU provider)."""
    global GLOBAL_REMBG_SESSION
    if GLOBAL_REMBG_SESSION is not None:
        return True
    try:
        assets_dir = _assets_dir()
        model_path = os.path.join(assets_dir, 'models', 'u2net.onnx')
        if os.path.exists(model_path):
            GLOBAL_REMBG_SESSION = new_session(model=model_path, providers=['CPUExecutionProvider'])
        else:
            GLOBAL_REMBG_SESSION = new_session(providers=['CPUExecutionProvider'])
        return True
    except Exception as e:
        print(f"Failed to preload rembg session: {e}")
        GLOBAL_REMBG_SESSION = None
        return False


def get_shared_processor():
    """Return a shared ImageProcessor instance (reuses global rembg session)."""
    global _SHARED_PROCESSOR
    if _SHARED_PROCESSOR is None:
        _SHARED_PROCESSOR = ImageProcessor()
    return _SHARED_PROCESSOR


class ImageProcessor:
    """Main image processing class"""

    def __init__(self):
        """Initialize the processor, loading resources."""
        self.background_templates = self.load_backgrounds()
        self.id_card_templates = self.load_id_card_templates()
        self._font_cache = {}
        # Inisialisasi sesi rembg; gunakan global jika sudah tersedia (tanpa memblokir)
        try:
            global GLOBAL_REMBG_SESSION
            self._rembg_session = GLOBAL_REMBG_SESSION
        except Exception:
            self._rembg_session = None

    def load_backgrounds(self):
        """Load available background templates"""
        backgrounds = {}

        # Load solid color backgrounds from config
        for name, value in BACKGROUND_TEMPLATES.items():
            if value.startswith('#') or value.startswith('gradient'):
                backgrounds[name] = value
            else:
                # Try to load image file
                bg_path = os.path.join(BACKGROUNDS_DIR, value)
                if os.path.exists(bg_path):
                    backgrounds[name] = bg_path

        # Create default backgrounds if none exist
        if not backgrounds:
            backgrounds = self._create_default_backgrounds()

        return backgrounds

    def load_id_card_templates(self):
        """Load available ID card templates"""
        templates = {}

        for template_id, template_config in ID_CARD_TEMPLATES.items():
            template_path = os.path.join(TEMPLATES_DIR, template_config['file'])
            if os.path.exists(template_path):
                templates[template_id] = {
                    'path': template_path,
                    'config': template_config
                }

        return templates

    def _create_default_backgrounds(self):
        """Create default background templates"""
        backgrounds = {}
        # Use portrait orientation for ID card backgrounds (3:4 aspect ratio)
        default_size = (600, 800)

        # Create solid color backgrounds
        colors = {
            'blue_solid': (74, 144, 226),
            'white_solid': (255, 255, 255),
            'light_blue': (227, 242, 253),
            'professional_gray': (245, 245, 245)
        }

        for name, color in colors.items():
            bg_image = Image.new('RGB', default_size, color)
            bg_path = os.path.join(BACKGROUNDS_DIR, f"{name}.png")
            bg_image.save(bg_path)
            backgrounds[name] = bg_path

        # Create gradient background
        gradient_bg = self._create_gradient_background(default_size)
        gradient_path = os.path.join(BACKGROUNDS_DIR, "gradient_blue.png")
        gradient_bg.save(gradient_path)
        backgrounds['gradient_blue'] = gradient_path

        return backgrounds

    def _create_gradient_background(self, size):
        """Create gradient background"""
        width, height = size
        gradient = Image.new('RGB', size)
        draw = ImageDraw.Draw(gradient)

        for y in range(height):
            # Create blue gradient from light to dark
            ratio = y / height
            r = int(227 * (1 - ratio) + 74 * ratio)
            g = int(242 * (1 - ratio) + 144 * ratio)
            b = int(253 * (1 - ratio) + 226 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        return gradient

    def remove_background(self, image_path):
        """Remove background from image using rembg (ONNX-based)."""
        try:
            # Load image and ensure RGBA for alpha handling
            image = Image.open(image_path).convert('RGBA')

            # Pastikan sesi rembg tersedia; jika belum, preload sekarang (sekali)
            if self._rembg_session is None:
                preload_rembg_session()
                self._rembg_session = GLOBAL_REMBG_SESSION

            # Run rembg background removal. It may return bytes or PIL Image.
            result = remove(image, session=self._rembg_session) if self._rembg_session else remove(image)

            if isinstance(result, Image.Image):
                final_image = result.convert('RGBA')
            else:
                # Assume bytes-like
                final_image = Image.open(io.BytesIO(result)).convert('RGBA')

            # Ensure portrait aspect ratio for ID cards
            final_image = self._ensure_portrait_aspect_ratio(final_image)

            return final_image

        except Exception as e:
            print(f"Error removing background with rembg: {e}")
            # Fallback: return original image
            original_image = Image.open(image_path)
            return self._ensure_portrait_aspect_ratio(original_image)

    def apply_id_background(self, image, background_type='blue_solid', user_info=None):
        """Apply ID card background to image"""
        if isinstance(image, str):
            # If image is a path, load it
            if image.endswith('.jpg') or image.endswith('.png'):
                subject_image = Image.open(image)
                # Ensure portrait aspect ratio for ID cards
                subject_image = self._ensure_portrait_aspect_ratio(subject_image)
            else:
                subject_image = self.remove_background(image)
        else:
            subject_image = image

        # Get background
        background = self.get_background(background_type)
        if background is None:
            return subject_image

        # Check if this is a template with specific positioning
        if background_type in self.id_card_templates:
            return self._apply_template_with_positioning(
                subject_image,
                background_type,
                background,
                user_info=user_info
            )
        else:
            # Use regular background processing
            # Resize subject to fit ID card proportions
            subject_resized = self._resize_for_id_card(subject_image)
            # Composite images
            final_image = self._composite_images(background, subject_resized)
            return final_image

    def get_background(self, background_type):
        """Get background image by type (includes templates)"""
        # Check if it's a template first
        if background_type in self.id_card_templates:
            template_info = self.id_card_templates[background_type]
            template_path = template_info['path']
            if os.path.exists(template_path):
                # Load image in a way that doesn't keep file handles open (important in PyInstaller)
                try:
                    with open(template_path, 'rb') as f:
                        data = f.read()
                    background = Image.open(io.BytesIO(data))
                    background.load()  # fully load into memory, release file
                except Exception:
                    # Fallback to direct open
                    background = Image.open(template_path)

                # Convert RGBA to RGB if needed (avoid writing to disk)
                if background.mode == 'RGBA':
                    rgb_background = Image.new('RGB', background.size, (255, 255, 255))
                    rgb_background.paste(background, mask=background.split()[-1])
                    return rgb_background
                return background

        # Handle regular backgrounds
        if background_type not in self.background_templates:
            background_type = 'blue_solid'

        bg_value = self.background_templates[background_type]

        if bg_value.startswith('#'):
            # Solid color - use portrait orientation for ID cards
            color = self._hex_to_rgb(bg_value)
            background = Image.new('RGB', (600, 800), color)
        elif os.path.exists(bg_value):
            # Image file - ensure it's in portrait orientation
            background = Image.open(bg_value)
            # If background is not portrait, resize to portrait
            if background.size[0] >= background.size[1]:
                background = background.resize((600, 800), Image.Resampling.LANCZOS)
        else:
            # Default blue background in portrait
            background = Image.new('RGB', (600, 800), (74, 144, 226))

        return background

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _ensure_portrait_aspect_ratio(self, image):
        """Ensure image has portrait aspect ratio suitable for ID cards"""
        width, height = image.size

        # If image is already portrait (height > width), return as-is
        if height >= width:
            return image

        # Image is landscape, we need to crop it to portrait
        # Calculate the ideal portrait crop area
        # For ID cards, we want roughly 3:4 aspect ratio (width:height)
        ideal_aspect_ratio = PROCESSING_SETTINGS.get('portrait_aspect_ratio', 3.0 / 4.0)  # width/height for portrait

        # Calculate new dimensions
        if width > height:
            # Landscape image - crop width to make it portrait
            new_width = int(height * ideal_aspect_ratio)
            if new_width <= width:
                # Crop from center horizontally
                left = (width - new_width) // 2
                right = left + new_width
                top = 0
                bottom = height

                cropped_image = image.crop((left, top, right, bottom))
                return cropped_image
            else:
                # If calculated width is too large, crop height instead
                new_height = int(width / ideal_aspect_ratio)
                top = (height - new_height) // 2
                bottom = top + new_height
                left = 0
                right = width

                cropped_image = image.crop((left, top, right, bottom))
                return cropped_image

        # Fallback: return original image
        return image

    def _apply_template_with_positioning(self, subject_image, template_id, template_background, user_info=None):
        """Apply ID card template with precise photo positioning"""
        template_config = self.id_card_templates[template_id]['config']
        photo_area = template_config['photo_area']

        # Get template dimensions
        template_width, template_height = template_background.size

        # Convert mm to pixels (assuming 300 DPI)
        dpi = 300
        mm_to_px = dpi / 25.4

        # Calculate photo area in pixels
        photo_width_px = int(photo_area['width_mm'] * mm_to_px)
        photo_height_px = int(photo_area['height_mm'] * mm_to_px)

        # Calculate position in pixels (from top-left of template)
        x_offset_px = int(photo_area['x_offset_mm'] * mm_to_px)
        y_offset_px = int(photo_area['y_offset_mm'] * mm_to_px)

        # The x_offset_mm is center position, so we need to adjust for left edge
        photo_left_px = x_offset_px - (photo_width_px // 2)
        photo_top_px = y_offset_px

        # Resize subject image to fit the exact photo area
        # Ensure the subject is portrait and fits the photo area
        subject_resized = self._resize_to_exact_area(subject_image, photo_width_px, photo_height_px)

        # Create final image by pasting subject onto template
        final_image = template_background.copy()

        # Paste the subject image at the precise position
        if subject_resized.mode == 'RGBA':
            final_image.paste(subject_resized, (photo_left_px, photo_top_px), subject_resized)
        else:
            final_image.paste(subject_resized, (photo_left_px, photo_top_px))

        if user_info:
            self._draw_user_identity(
                final_image,
                template_config,
                user_info,
                photo_left_px,
                photo_top_px,
                photo_width_px,
                photo_height_px,
                mm_to_px
            )

        return final_image

    def _resize_to_exact_area(self, image, target_width, target_height):
        """Resize image to fit exact area, cropping if necessary to maintain aspect ratio"""
        original_width, original_height = image.size
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height

        if original_ratio > target_ratio:
            # Image is wider than target - crop width
            new_width = int(original_height * target_ratio)
            left = (original_width - new_width) // 2
            image = image.crop((left, 0, left + new_width, original_height))
        elif original_ratio < target_ratio:
            # Image is taller than target - crop height
            new_height = int(original_width / target_ratio)
            top = (original_height - new_height) // 2
            image = image.crop((0, top, original_width, top + new_height))

        # Now resize to exact target dimensions
        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

    def _draw_user_identity(self, final_image, template_config, user_info,
                             photo_left_px, photo_top_px, photo_width_px, photo_height_px, mm_to_px):
        """Draw user name and NPK text onto the template below the photo area."""
        name = (user_info.get('name') or "").strip()
        npk = (user_info.get('npk') or "").strip()
        if not name and not npk:
            return

        draw = ImageDraw.Draw(final_image)
        template_width, template_height = final_image.size

        # Base positioning: centered below the photo area with configurable margins
        center_x = photo_left_px + (photo_width_px // 2)
        margin_mm = template_config.get('identity_margin_mm', 2.7)
        line_gap_mm = template_config.get('identity_line_gap_mm', 1.3)
        margin_px = int(margin_mm * mm_to_px)
        line_gap_px = max(int(line_gap_mm * mm_to_px), 4)

        dpi = max(int(round(mm_to_px * 25.4)), 72)
        font_size_px = max(int(round(6.5 * dpi / 72.0)), 10)

        current_y = photo_top_px + photo_height_px + margin_px
        max_bottom = template_height - int(4 * mm_to_px)
        current_y = min(current_y, max_bottom)

        if name:
            name = self._format_identity_name(name, max_length=15)
            name = name.upper()
            name_font = self._get_font(font_size_px, bold=True, family="Verdana")
            name_height = self._draw_centered_text(
                draw, name, center_x, current_y, name_font, fill=(0, 0, 0)
            )
            current_y = min(current_y + name_height + line_gap_px, max_bottom)

        if npk:
            npk = npk.upper()
            npk_font = self._get_font(font_size_px, bold=True, family="Verdana")
            self._draw_centered_text(
                draw, npk, center_x, current_y, npk_font, fill=(0, 0, 0)
            )

    def _get_font(self, size, bold=False, family=None):
        """Load and cache fonts with fallback options."""
        cache_key = (family or 'default', size, bold)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        font_candidates = []

        if family:
            family_lower = family.lower()
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            font_dir = os.path.join(project_root, "assets", "fonts")

            if family_lower == "verdana":
                if bold:
                    font_candidates.extend([
                        os.path.join(font_dir, "Verdana-Bold.ttf"),
                        os.path.join(font_dir, "Verdana Bold.ttf"),
                        os.path.join(font_dir, "verdanab.ttf"),
                        "Verdana Bold.ttf",
                        "verdana bold.ttf",
                        "Verdana-Bold.ttf",
                        "VERDANAB.TTF",
                        "verdanab.ttf",
                        "/Library/Fonts/Verdana Bold.ttf",
                        "/System/Library/Fonts/Verdana Bold.ttf",
                        "C:\\Windows\\Fonts\\verdanab.ttf",
                    ])
                else:
                    font_candidates.extend([
                        os.path.join(font_dir, "Verdana.ttf"),
                        os.path.join(font_dir, "verdana.ttf"),
                        "Verdana.ttf",
                        "verdana.ttf",
                        "/Library/Fonts/Verdana.ttf",
                        "/System/Library/Fonts/Verdana.ttf",
                        "C:\\Windows\\Fonts\\verdana.ttf",
                    ])
            elif family_lower == "calibri":
                if bold:
                    font_candidates.extend([
                        os.path.join(font_dir, "Calibri-Bold.ttf"),
                        os.path.join(font_dir, "Calibri Bold.ttf"),
                        os.path.join(font_dir, "calibrib.ttf"),
                        "Calibri Bold.ttf",
                        "calibri bold.ttf",
                        "Calibri-Bold.ttf",
                        "calibrib.ttf",
                        "/Library/Fonts/Calibri Bold.ttf",
                        "/System/Library/Fonts/Calibri Bold.ttf",
                        "C:\\Windows\\Fonts\\calibrib.ttf",
                    ])
                else:
                    font_candidates.extend([
                        os.path.join(font_dir, "Calibri.ttf"),
                        os.path.join(font_dir, "calibri.ttf"),
                        "Calibri.ttf",
                        "calibri.ttf",
                        "/Library/Fonts/Calibri.ttf",
                        "/System/Library/Fonts/Calibri.ttf",
                        "C:\\Windows\\Fonts\\calibri.ttf",
                    ])

        fallback_fonts = [
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
            "Arial Bold.ttf" if bold else "Arial.ttf",
            "Arialbd.ttf" if bold else "Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
            "Helvetica Bold.ttf" if bold else "Helvetica.ttf",
        ]
        font_candidates.extend(fallback_fonts)

        font = None
        for path in font_candidates:
            if not path:
                continue
            try:
                font = ImageFont.truetype(path, size)
                break
            except (OSError, IOError):
                continue

        if font is None:
            font = ImageFont.load_default()

        print(f"Using font: {font.path if hasattr(font, 'path') else 'default font'} for size {size}, bold={bold}")
        self._font_cache[cache_key] = font
        return font

    def _format_identity_name(self, name, max_length=15):
        parts = name.strip().split()

        if len(name) <= max_length:
            return name

        if len(parts) == 1:
            return parts[0][:max_length]

        # Normalize and check for Muhammad variants
        muhammad_variants = {"muhammad", "muhamad", "mohamad", "mohammad", "mochammad", "mochamad"}
        first_name = parts[0].lower()

        formatted_parts = []

        if first_name in muhammad_variants:
            formatted_parts.append("M.")
            if len(parts) > 1:
                formatted_parts.append(parts[1])
                remaining = parts[2:]
            else:
                remaining = []
        else:
            formatted_parts.append(parts[0])
            remaining = parts[1:]

        # Add initials for the remaining parts
        for part in remaining:
            if part:
                formatted_parts.append(part[0] + ".")

        result = " ".join(formatted_parts)

        if len(result) > max_length:
            result = result[:max_length].rstrip()

        return result

    def _draw_centered_text(self, draw, text, center_x, top_y, font, fill):
        """Draw text centered horizontally around center_x and return its height."""
        if not text:
            return 0

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = int(center_x - (text_width / 2))
        y = int(top_y)
        draw.text((x, y), text, fill=fill, font=font)
        return text_height

    def _resize_for_id_card(self, image):
        """Resize image to fit ID card proportions"""
        # Standard ID card has person's head/shoulders
        # Typically 70-80% of card height for the person
        # Using portrait background (600x800)
        target_height = int(800 * 0.8)  # Slightly taller subject framing

        # Calculate new width maintaining aspect ratio
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height
        target_width = int(target_height * aspect_ratio)

        # Ensure subject doesn't exceed background width
        if target_width > 600:
            target_width = 600
            target_height = int(target_width / aspect_ratio)

        # Resize image
        resized_image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

        return resized_image

    def _composite_images(self, background, subject):
        """Composite subject onto background"""
        bg_width, bg_height = background.size
        subj_width, subj_height = subject.size

        # Center the subject on the background
        x_offset = (bg_width - subj_width) // 2
        y_offset = (bg_height - subj_height) // 4  # Position slightly higher

        # Create a copy of background
        result = background.copy()
        print(f"Compositing subject of size {subject.size} onto background of size {background.size} at offset ({x_offset}, {y_offset})")

        # Paste subject onto background
        if subject.mode == 'RGBA':
            result.paste(subject, (x_offset, y_offset), subject)
        else:
            result.paste(subject, (x_offset, y_offset))

        return result

    def create_id_card_layout(self, processed_image, template_type='standard'):
        """Create final ID card layout in portrait orientation"""
        # Standard ID card dimensions in portrait (53.98 x 85.6 mm at 300 DPI)
        dpi = 300
        width_mm, height_mm = 53.98, 85.6  # Portrait orientation
        width_px = int(width_mm * dpi / 25.4)
        height_px = int(height_mm * dpi / 25.4)

        print(f"ID card dimensions: {width_px}x{height_px} pixels")
        print(f"Input image size: {processed_image.size}")

        # Create ID card canvas in portrait
        id_card = Image.new('RGB', (width_px, height_px), 'white')

        # Ensure processed image is portrait
        if processed_image.size[0] > processed_image.size[1]:
            # Rotate landscape image to portrait
            print("Rotating landscape image to portrait")
            processed_image = processed_image.rotate(90, expand=True)
            print(f"After rotation: {processed_image.size}")

        # Resize processed image to fit card while maintaining aspect ratio
        processed_image.thumbnail((width_px, height_px), Image.Resampling.LANCZOS)
        print(f"After thumbnail resize: {processed_image.size}")

        # Center the image on the card
        paste_x = (width_px - processed_image.size[0]) // 2
        paste_y = (height_px - processed_image.size[1]) // 2
        print(f"Pasting at position: ({paste_x}, {paste_y})")

        id_card.paste(processed_image, (paste_x, paste_y))

        return id_card

    def enhance_image(self, image, brightness=1.0, contrast=1.0, sharpness=1.0):
        """Enhance image with brightness, contrast, and sharpness"""
        from PIL import ImageEnhance

        if isinstance(image, str):
            image = Image.open(image)

        # Apply brightness
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)

        # Apply contrast
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)

        # Apply sharpness
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(sharpness)

        return image

    def save_processed_image(self, image, filename=None):
        """Save processed image to processed directory"""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processed_{timestamp}.png"

        save_path = os.path.join(PROCESSED_DIR, filename)
        os.makedirs(PROCESSED_DIR, exist_ok=True)

        if isinstance(image, str):
            # Copy file
            import shutil
            shutil.copy2(image, save_path)
        else:
            # Save PIL Image
            image.save(save_path, format='PNG', quality=95)

        return save_path

    def get_background_list(self):
        """Get list of available backgrounds and templates"""
        # Combine backgrounds and templates
        backgrounds = list(self.background_templates.keys())
        templates = list(self.id_card_templates.keys())
        return backgrounds + templates

    def create_before_after_comparison(self, original_path, processed_image):
        """Create before/after comparison image"""
        original = Image.open(original_path)

        # Resize both to same height
        height = 400
        orig_width = int(original.size[0] * height / original.size[1])
        proc_width = int(processed_image.size[0] * height / processed_image.size[1])

        original_resized = original.resize((orig_width, height))
        processed_resized = processed_image.resize((proc_width, height))

        # Create comparison canvas
        total_width = orig_width + proc_width + 20  # 20px gap
        comparison = Image.new('RGB', (total_width, height), 'white')

        # Paste images
        comparison.paste(original_resized, (0, 0))
        comparison.paste(processed_resized, (orig_width + 20, 0))

        return comparison

    def cleanup_temp_files(self, max_age_hours=24):
        """Clean up temporary processed files"""
        import time
        try:
            current_time = time.time()
            for filename in os.listdir(PROCESSED_DIR):
                file_path = os.path.join(PROCESSED_DIR, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > max_age_hours * 3600:
                        os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up processed files: {e}")


# Import io for BytesIO
import io
