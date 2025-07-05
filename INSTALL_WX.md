# Installing wxPython on WSL/Linux

## Option 1: Install System Dependencies for Building wxPython

```bash
# Install GTK+ and other required development libraries
sudo apt-get update
sudo apt-get install -y \
    libgtk-3-dev \
    libwebkitgtk-4.0-dev \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer1.0-dev \
    libnotify-dev \
    libsdl2-dev \
    libxtst-dev \
    libgtk-3-0 \
    libsm6 \
    libxxf86vm1 \
    libxkbfile1 \
    libgl1 \
    libglu1-mesa \
    freeglut3-dev

# Then install wxPython with pip
pip install wxPython
```

## Option 2: Use Pre-built System Package

```bash
# Install pre-built wxPython
sudo apt-get install -y python3-wxgtk4.0

# Then in your Python environment, you might need to:
# 1. Create a virtual environment with system packages
python -m venv --system-site-packages venv
source venv/bin/activate

# Or 2. Install via pip with specific version
pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04 wxPython
```

## Option 3: HTML Frontend Alternative

If wxPython continues to be problematic, we could create a web-based frontend that's:
- Fully accessible with screen readers
- Runs in any browser
- Uses Flask/FastAPI backend with WebSocket for real-time updates
- Can be packaged as a desktop app with Electron or similar

Let me know which approach you'd prefer!