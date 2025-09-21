"""
Setup script for ID Card Photo Machine with Virtual Environment
"""
import subprocess
import sys
import os
import platform


def create_virtual_environment():
    """Create a virtual environment"""
    print("Creating virtual environment...")

    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("Virtual environment created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        return False


def get_venv_python():
    """Get the Python executable from virtual environment"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")


def install_dependencies():
    """Install required dependencies in virtual environment"""
    print("Installing dependencies in virtual environment...")

    # Get virtual environment Python
    venv_python = get_venv_python()

    if not os.path.exists(venv_python):
        print("Virtual environment not found. Creating one...")
        if not create_virtual_environment():
            return False

    try:
        # Upgrade pip in virtual environment
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])

        # Install requirements in virtual environment
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully in virtual environment!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def check_system_requirements():
    """Check system requirements"""
    print("Checking system requirements...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False

    print(f"Python version: {sys.version}")

    # Check if we can import basic modules
    try:
        import tkinter  # Basic GUI support
        print("GUI support: Available")
    except ImportError:
        print("Warning: GUI support may not be available")

    return True


def create_desktop_shortcut():
    """Create desktop shortcut (optional)"""
    try:
        if os.name == 'nt':  # Windows
            create_windows_shortcut()
        elif os.name == 'posix':  # macOS/Linux
            create_unix_shortcut()
    except Exception as e:
        print(f"Could not create desktop shortcut: {e}")


def create_windows_shortcut():
    """Create Windows desktop shortcut"""
    import winshell
    from win32com.client import Dispatch

    desktop = winshell.desktop()
    path = os.path.join(desktop, "ID Card Photo Machine.lnk")
    target = os.path.join(os.getcwd(), "main.py")

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = sys.executable
    shortcut.Arguments = f'"{target}"'
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.IconLocation = os.path.join(os.getcwd(), "assets", "icons", "app_icon.ico")
    shortcut.save()


def create_unix_shortcut():
    """Create macOS/Linux application shortcut"""
    # This would create .desktop file on Linux or .app bundle on macOS
    # Implementation depends on specific platform requirements
    pass


def main():
    """Main setup function"""
    print("ID Card Photo Machine - Setup")
    print("=" * 40)

    # Check system requirements
    if not check_system_requirements():
        print("System requirements not met. Exiting.")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. Please install manually:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    # Create assets using virtual environment
    print("\nCreating application assets...")
    try:
        venv_python = get_venv_python()
        subprocess.check_call([venv_python, "create_assets.py"])
    except Exception as e:
        print(f"Error creating assets: {e}")
        print(f"You can create assets manually by running: {get_venv_python()} create_assets.py")

    # Optional: Create desktop shortcut
    response = input("\nWould you like to create a desktop shortcut? (y/n): ")
    if response.lower() in ['y', 'yes']:
        create_desktop_shortcut()

    print("\nSetup complete!")
    print("You can now run the application with:")
    print("  python run.py                    # Recommended launcher")
    print("  ./venv/bin/python main.py        # Direct execution")
    print("  source venv/bin/activate && python main.py  # Manual activation")


if __name__ == "__main__":
    main()
