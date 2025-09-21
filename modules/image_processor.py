"""
Image Processor Module
Handles background removal, ID card background application, and image processing
"""
import cv2
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import os
from rembg import remove, new_session
from config import PROCESSING_SETTINGS, BACKGROUNDS_DIR, TEMPLATES_DIR, PROCESSED_DIR, BACKGROUND_TEMPLATES


class ImageProcessor:
    """Main image processing class"""

    def __init__(self):
        self.background_templates = self.load_backgrounds()
        self.rembg_session = new_session(PROCESSING_SETTINGS['background_removal_model'])

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
        """Remove background from image using rembg"""
        try:
            # Load image
            with open(image_path, 'rb') as f:
                input_data = f.read()

            # Remove background
            output_data = remove(input_data, session=self.rembg_session)

            # Convert to PIL Image
            no_bg_image = Image.open(io.BytesIO(output_data))

            # Ensure portrait aspect ratio for ID cards
            no_bg_image = self._ensure_portrait_aspect_ratio(no_bg_image)

            return no_bg_image

        except Exception as e:
            print(f"Error removing background: {e}")
            # Fallback: return original image
            original_image = Image.open(image_path)
            return self._ensure_portrait_aspect_ratio(original_image)

    def apply_id_background(self, image, background_type='blue_solid'):
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

        # Resize subject to fit ID card proportions
        subject_resized = self._resize_for_id_card(subject_image)

        # Composite images
        final_image = self._composite_images(background, subject_resized)

        return final_image

    def get_background(self, background_type):
        """Get background image by type"""
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

    def _resize_for_id_card(self, image):
        """Resize image to fit ID card proportions"""
        # Standard ID card has person's head/shoulders
        # Typically 70-80% of card height for the person
        # Using portrait background (600x800)
        target_height = int(800 * 0.75)  # 75% of background height

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

        # Create ID card canvas in portrait
        id_card = Image.new('RGB', (width_px, height_px), 'white')

        # Ensure processed image is portrait
        if processed_image.size[0] > processed_image.size[1]:
            # Rotate landscape image to portrait
            processed_image = processed_image.rotate(90, expand=True)

        # Resize processed image to fit card while maintaining aspect ratio
        processed_image.thumbnail((width_px, height_px), Image.Resampling.LANCZOS)

        # Center the image on the card
        paste_x = (width_px - processed_image.size[0]) // 2
        paste_y = (height_px - processed_image.size[1]) // 2
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
        """Get list of available backgrounds"""
        return list(self.background_templates.keys())

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
