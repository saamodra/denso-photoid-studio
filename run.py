#!/usr/bin/env python3
"""
Simple launcher script for ID Card Photo Machine with Virtual Environment Support
"""
import os
import sys
import subprocess
import platform


def get_venv_python():
    """Get the Python executable from virtual environment"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, "venv")

    if platform.system() == "Windows":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    return venv_python if os.path.exists(venv_python) else None


def create_venv():
    """Create virtual environment"""
    print("Creating virtual environment...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to create virtual environment: {e}")
        return False


def install_dependencies_venv(venv_python):
    """Install dependencies in virtual environment"""
    print("Installing dependencies in virtual environment...")
    try:
        # Upgrade pip first
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
        # Install requirements
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


def check_dependencies_venv(venv_python):
    """Check if dependencies are installed in virtual environment"""
    required_modules = ['PyQt6', 'cv2', 'PIL', 'rembg', 'numpy']
    missing = []

    for module in required_modules:
        try:
            result = subprocess.run([venv_python, "-c", f"import {module}"],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                missing.append(module)
        except Exception:
            missing.append(module)

    return missing


def main():
    """Main launcher function"""
    print("ID Card Photo Machine Launcher (Virtual Environment)")
    print("=" * 55)

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Check for virtual environment
    venv_python = get_venv_python()

    if not venv_python:
        print("Virtual environment not found. Creating one...")
        if not create_venv():
            print("Failed to create virtual environment. Exiting.")
            sys.exit(1)
        venv_python = get_venv_python()

        if not venv_python:
            print("Could not locate virtual environment Python. Exiting.")
            sys.exit(1)

    print(f"Using virtual environment: {os.path.dirname(venv_python)}")

    # Check dependencies in virtual environment
    missing = check_dependencies_venv(venv_python)

    if missing:
        print(f"Missing dependencies in venv: {', '.join(missing)}")
        print("Installing dependencies...")
        if not install_dependencies_venv(venv_python):
            print("Failed to install dependencies.")
            print("Please try manually:")
            print(f"  {venv_python} -m pip install -r requirements.txt")
            sys.exit(1)

    # Launch application
    print("Launching ID Card Photo Machine...")
    try:
        # Run the main application in the virtual environment
        result = subprocess.run([venv_python, "main.py"], cwd=script_dir)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
