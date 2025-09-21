#!/usr/bin/env python3
"""
Test script to verify the application structure without running the GUI
"""
import os
import sys
import importlib.util


def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")

    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        'modules/__init__.py',
        'modules/camera_manager.py',
        'modules/image_processor.py',
        'modules/print_manager.py',
        'ui/__init__.py',
        'ui/main_window.py',
        'ui/selection_window.py',
        'ui/processing_window.py',
        'ui/print_window.py'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True


def test_directory_structure():
    """Test that all required directories exist"""
    print("Testing directory structure...")

    required_dirs = [
        'modules',
        'ui',
        'assets',
        'assets/backgrounds',
        'assets/templates',
        'assets/icons',
        'temp',
        'temp/captures',
        'temp/processed'
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)

    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✅ All required directories present")
        return True


def test_import_structure():
    """Test that modules can be imported without dependency issues"""
    print("Testing import structure...")

    # Test config import
    try:
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        print("✅ Config module imports correctly")
    except Exception as e:
        print(f"❌ Config import error: {e}")
        return False

    # Test that we have the basic structure for UI modules
    # (We can't test full imports without PyQt6 installed)
    ui_modules = ['main_window.py', 'selection_window.py', 'processing_window.py', 'print_window.py']

    for module in ui_modules:
        file_path = os.path.join('ui', module)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Check for basic class definitions
                if 'class' in content and 'QMainWindow' in content:
                    print(f"✅ {module} has proper class structure")
                else:
                    print(f"❌ {module} missing proper class structure")
                    return False
        except Exception as e:
            print(f"❌ Error reading {module}: {e}")
            return False

    return True


def test_assets():
    """Test that assets were created"""
    print("Testing assets...")

    # Check background assets
    bg_files = [
        'assets/backgrounds/blue_solid.png',
        'assets/backgrounds/white_solid.png',
        'assets/backgrounds/gradient_blue.png'
    ]

    for bg_file in bg_files:
        if not os.path.exists(bg_file):
            print(f"❌ Missing background: {bg_file}")
            return False

    # Check template assets
    template_files = [
        'assets/templates/id_card_template.png',
        'assets/templates/simple_template.png'
    ]

    for template_file in template_files:
        if not os.path.exists(template_file):
            print(f"❌ Missing template: {template_file}")
            return False

    # Check icon assets
    if not os.path.exists('assets/icons/app_icon.png'):
        print("❌ Missing app icon")
        return False

    print("✅ All assets present")
    return True


def test_configuration():
    """Test configuration settings"""
    print("Testing configuration...")

    try:
        import config

        # Check required settings exist
        required_settings = [
            'APP_NAME',
            'APP_VERSION',
            'CAMERA_SETTINGS',
            'PROCESSING_SETTINGS',
            'PRINT_SETTINGS',
            'UI_SETTINGS'
        ]

        for setting in required_settings:
            if not hasattr(config, setting):
                print(f"❌ Missing configuration: {setting}")
                return False

        print("✅ Configuration complete")
        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def generate_test_report():
    """Generate a test report"""
    print("\n" + "="*50)
    print("ID CARD PHOTO MACHINE - STRUCTURE TEST REPORT")
    print("="*50)

    tests = [
        ("File Structure", test_file_structure),
        ("Directory Structure", test_directory_structure),
        ("Import Structure", test_import_structure),
        ("Assets", test_assets),
        ("Configuration", test_configuration)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")

    print("\n" + "="*50)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Application structure is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run application: python main.py")
        print("3. Or use launcher: python run.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")

    print("="*50)

    return passed == total


def main():
    """Main test function"""
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    success = generate_test_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
