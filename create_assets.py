"""
Script to create default assets for the ID Card Photo Machine
"""
import os
from PIL import Image, ImageDraw, ImageFont
from config import BACKGROUNDS_DIR, TEMPLATES_DIR, ICONS_DIR


def create_background_assets():
    """Create default background images"""
    print("Creating background assets...")

    # Ensure directory exists
    os.makedirs(BACKGROUNDS_DIR, exist_ok=True)

    # Standard size for backgrounds
    size = (600, 600)

    # Create solid color backgrounds
    backgrounds = {
        'blue_solid.png': (74, 144, 226),
        'white_solid.png': (255, 255, 255),
        'light_blue.png': (227, 242, 253),
        'professional_gray.png': (245, 245, 245),
        'navy_blue.png': (52, 73, 94),
        'light_gray.png': (236, 240, 241)
    }

    for filename, color in backgrounds.items():
        bg = Image.new('RGB', size, color)
        bg.save(os.path.join(BACKGROUNDS_DIR, filename))
        print(f"Created {filename}")

    # Create gradient background
    gradient_bg = create_gradient_background(size)
    gradient_bg.save(os.path.join(BACKGROUNDS_DIR, 'gradient_blue.png'))
    print("Created gradient_blue.png")

    # Create professional gradient
    prof_gradient = create_professional_gradient(size)
    prof_gradient.save(os.path.join(BACKGROUNDS_DIR, 'professional_gradient.png'))
    print("Created professional_gradient.png")


def create_gradient_background(size):
    """Create blue gradient background"""
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


def create_professional_gradient(size):
    """Create professional gray-blue gradient"""
    width, height = size
    gradient = Image.new('RGB', size)
    draw = ImageDraw.Draw(gradient)

    for y in range(height):
        # Create gradient from light gray to blue
        ratio = y / height
        r = int(245 * (1 - ratio) + 52 * ratio)
        g = int(245 * (1 - ratio) + 73 * ratio)
        b = int(245 * (1 - ratio) + 94 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return gradient


def create_id_card_templates():
    """Create ID card templates"""
    print("Creating ID card templates...")

    # Ensure directory exists
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

    # Standard ID card size at 300 DPI (85.6 x 53.98 mm)
    dpi = 300
    width_mm, height_mm = 85.6, 53.98
    width_px = int(width_mm * dpi / 25.4)
    height_px = int(height_mm * dpi / 25.4)

    # Create basic template
    template = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(template)

    # Add border
    border_width = 5
    draw.rectangle([0, 0, width_px-1, height_px-1], outline='#34495e', width=border_width)

    # Add corner decorations
    corner_size = 20
    for corner in [(0, 0), (width_px-corner_size, 0), (0, height_px-corner_size), (width_px-corner_size, height_px-corner_size)]:
        draw.rectangle([corner[0], corner[1], corner[0]+corner_size, corner[1]+corner_size], fill='#3498db')

    template.save(os.path.join(TEMPLATES_DIR, 'id_card_template.png'))
    print("Created id_card_template.png")

    # Create simple template (no decorations)
    simple_template = Image.new('RGB', (width_px, height_px), 'white')
    simple_template.save(os.path.join(TEMPLATES_DIR, 'simple_template.png'))
    print("Created simple_template.png")


def create_app_icons():
    """Create application icons"""
    print("Creating application icons...")

    # Ensure directory exists
    os.makedirs(ICONS_DIR, exist_ok=True)

    # Create simple app icon
    icon_size = 256
    icon = Image.new('RGB', (icon_size, icon_size), '#3498db')
    draw = ImageDraw.Draw(icon)

    # Draw camera-like shape
    camera_size = icon_size // 2
    camera_x = (icon_size - camera_size) // 2
    camera_y = (icon_size - camera_size) // 2

    # Camera body
    draw.rounded_rectangle([camera_x, camera_y, camera_x + camera_size, camera_y + camera_size],
                          radius=20, fill='white')

    # Camera lens
    lens_size = camera_size // 3
    lens_x = camera_x + (camera_size - lens_size) // 2
    lens_y = camera_y + (camera_size - lens_size) // 2
    draw.ellipse([lens_x, lens_y, lens_x + lens_size, lens_y + lens_size], fill='#2c3e50')

    # Inner lens
    inner_lens = lens_size // 2
    inner_x = lens_x + (lens_size - inner_lens) // 2
    inner_y = lens_y + (lens_size - inner_lens) // 2
    draw.ellipse([inner_x, inner_y, inner_x + inner_lens, inner_y + inner_lens], fill='#34495e')

    icon.save(os.path.join(ICONS_DIR, 'app_icon.png'))
    print("Created app_icon.png")

    # Create smaller sizes
    for size in [128, 64, 32, 16]:
        small_icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        small_icon.save(os.path.join(ICONS_DIR, f'app_icon_{size}.png'))
        print(f"Created app_icon_{size}.png")


def create_readme():
    """Create README file"""
    readme_content = """# ID Card Photo Machine

A desktop application for automated ID card photo processing using PyQt6.

## Features

- **Camera Management**: Multiple camera support with live preview
- **Photo Capture**: Take multiple photos with countdown timer
- **Photo Selection**: Choose the best photo from captured images
- **Background Processing**: AI-powered background removal and replacement
- **Print System**: Professional ID card printing with preview

## Requirements

- Python 3.8+
- PyQt6
- OpenCV
- PIL (Pillow)
- rembg
- numpy

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create default assets:
```bash
python create_assets.py
```

3. Run the application:
```bash
python main.py
```

## Usage

1. **Take Photos**: Use the main window to capture 4 photos with your camera
2. **Select Photo**: Choose your best photo from the captured images
3. **Process Image**: Remove background and apply professional ID card background
4. **Print**: Preview and print your ID card

## Configuration

Edit `config.py` to customize:
- Camera settings (resolution, quality)
- Processing settings (background removal model)
- Print settings (paper size, DPI)
- UI settings (window size, theme)

## Supported Cameras

- USB webcams
- Built-in laptop cameras
- External USB cameras

## Supported Printers

- System printers (Windows, macOS, Linux)
- Network printers
- Photo printers

## Troubleshooting

### Camera Issues
- Ensure camera is connected and not in use by another app
- Try switching to a different camera in the dropdown

### Background Removal Issues
- Ensure good lighting for better results
- Position subject clearly against contrasting background

### Print Issues
- Check printer connectivity
- Verify printer drivers are installed
- Try different print quality settings

## File Structure

```
photocard-studio/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── modules/               # Core functionality
│   ├── camera_manager.py  # Camera operations
│   ├── image_processor.py # Image processing
│   └── print_manager.py   # Printing functionality
├── ui/                    # User interface
│   ├── main_window.py     # Main camera window
│   ├── selection_window.py# Photo selection
│   ├── processing_window.py# Background processing
│   └── print_window.py    # Print preview
├── assets/                # Assets and templates
│   ├── backgrounds/       # Background images
│   ├── templates/         # ID card templates
│   └── icons/            # Application icons
└── temp/                  # Temporary files
    ├── captures/          # Captured photos
    └── processed/         # Processed images
```

## License

This project is for educational and personal use.
"""

    with open('/Users/samodra/Projects/photocard-studio/README.md', 'w') as f:
        f.write(readme_content)
    print("Created README.md")


def main():
    """Main function to create all assets"""
    print("Creating assets for ID Card Photo Machine...")

    try:
        create_background_assets()
        create_id_card_templates()
        create_app_icons()
        create_readme()

        print("\nAll assets created successfully!")
        print("You can now run the application with: python main.py")

    except Exception as e:
        print(f"Error creating assets: {e}")


if __name__ == "__main__":
    main()
