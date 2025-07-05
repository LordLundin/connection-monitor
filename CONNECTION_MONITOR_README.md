# Connection Monitor

A simple network connection monitoring tool that shows what programs on your computer are connecting to the internet.

## Features

- Monitor active network connections in real-time
- Display process name, PID, local and remote addresses, and connection status
- **Web Interface**: Fully accessible with screen readers, works in any browser
- Console-based interface (works everywhere, including WSL)
- Optional native GUI interfaces (wxPython, PyQt5, Tkinter)
- No root required (though some connections may not be visible without elevated privileges)

## Installation

### Prerequisites

The tool requires Python 3.8+ and psutil:

```bash
pip install psutil
```

### Recommended: Web Interface (Accessible & WSL-friendly)

```bash
pip install flask flask-socketio
```

### Optional GUI Libraries

For native GUI interfaces (may require additional setup on WSL):

#### wxPython (Accessible with screen readers)
```bash
# First install system dependencies:
sudo apt-get update
sudo apt-get install -y libgtk-3-dev libwebkitgtk-4.0-dev \
    libgstreamer-gl1.0-0 libgstreamer-plugins-base1.0-dev \
    libnotify-dev libsdl2-dev

# Then install wxPython:
pip install wxPython
```

#### PyQt5
```bash
pip install PyQt5
```

#### Tkinter
Usually comes with Python. If not:
```bash
sudo apt-get install python3-tk
```

## Usage

### Running from Source

```bash
# Console interface (recommended for WSL)
python main.py --console

# Auto-detect available interfaces
python main.py

# Force GUI mode
python main.py --gui
```

### Console Interface Commands

- **Enter**: Start monitoring
- **R**: Refresh display
- **S**: Stop monitoring
- **Q**: Quit application
- **Ctrl+C**: Force quit

### Running with Elevated Privileges

For full visibility of all connections:
```bash
sudo python main.py --console
```

## Building Executable (Optional)

To create a standalone executable using PyInstaller:

### Install PyInstaller
```bash
pip install pyinstaller
# or
pipx install pyinstaller
```

### Build Executable
```bash
# Using the build script
python build_executable.py

# Or manually with PyInstaller
pyinstaller ConnectionMonitor.spec

# Or simple one-liner
pyinstaller --onefile --console --name ConnectionMonitor main.py
```

The executable will be created in the `dist/` directory.

## Project Structure

```
connection-monitor/
├── connection_monitor/
│   ├── __init__.py
│   ├── console_monitor.py    # Console interface
│   ├── network_monitor.py    # Tkinter GUI (if available)
│   └── qt_monitor.py         # PyQt5 GUI (if available)
├── main.py                   # Entry point
├── build_executable.py       # Build script for PyInstaller
└── ConnectionMonitor.spec    # PyInstaller specification
```

## Limitations on WSL

- GUI applications require X11 server setup (like VcXsrv or WSLg)
- Some system connections may not be visible without root
- PyInstaller executables may have limited functionality

## Security Note

This tool only reads connection information and does not modify any network settings. It's designed for monitoring and diagnostic purposes only.