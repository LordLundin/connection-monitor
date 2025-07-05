#!/usr/bin/env python3
"""
Build script for creating executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil


def check_pyinstaller():
    """Check if PyInstaller is available"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller using pip"""
    print("PyInstaller not found. Installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install PyInstaller")
        return False


def build_executable():
    """Build the executable using PyInstaller"""
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("Cannot proceed without PyInstaller")
            return False
    
    print("\nBuilding Connection Monitor executable...")
    
    # Use the spec file if it exists, otherwise create it
    spec_file = "ConnectionMonitor.spec"
    
    if os.path.exists(spec_file):
        print(f"Using existing spec file: {spec_file}")
        cmd = [sys.executable, "-m", "PyInstaller", spec_file]
    else:
        print("Creating new build configuration...")
        # Create a comprehensive PyInstaller command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name", "ConnectionMonitor",
            "--onefile",
            "--console",
            "--add-data", "connection_monitor:connection_monitor",
            # Hidden imports for all dependencies
            "--hidden-import", "psutil",
            "--hidden-import", "psutil._pswindows",
            "--hidden-import", "psutil._pslinux", 
            "--hidden-import", "psutil._psposix",
            "--hidden-import", "psutil._common",
            "--hidden-import", "flask",
            "--hidden-import", "flask_socketio",
            "--hidden-import", "socketio",
            "--hidden-import", "engineio",
            "--hidden-import", "engineio.async_drivers.threading",
            "--hidden-import", "wx",
            "--hidden-import", "wx._core",
            "--hidden-import", "wx._grid",
            "main.py"
        ]
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild completed successfully!")
        
        # Check if dist directory exists
        if os.path.exists("dist"):
            exe_name = "ConnectionMonitor.exe" if sys.platform == "win32" else "ConnectionMonitor"
            exe_path = os.path.join("dist", exe_name)
            if os.path.exists(exe_path):
                print(f"\nExecutable created at: {os.path.abspath(exe_path)}")
                print(f"File size: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
                return True
        
        print("Executable not found in expected location")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed:")
        print("   pip install psutil flask flask-socketio wxpython")
        print("2. If wxPython fails to install, you can skip it")
        print("3. Try running PyInstaller directly:")
        print("   pyinstaller ConnectionMonitor.spec")
        return False


def main():
    print("Connection Monitor Build Script")
    print("=" * 50)
    
    # Change to project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Build executable
    if build_executable():
        print("\nBuild process completed!")
        print("\nTo run the executable:")
        print("  dist\\ConnectionMonitor.exe              (for interface selection)")
        print("  dist\\ConnectionMonitor.exe --console    (for console interface only)")
    else:
        print("\nBuild process failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()