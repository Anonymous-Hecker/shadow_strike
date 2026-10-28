"""
Paths - one place that knows where things live.

* Running from source (python main.py): assets and save file live in the
  project folder, exactly as before.
* Running as a packaged build (PyInstaller): read-only assets live inside the
  bundle, but the save file / crash log must go to a per-user writable folder
  (the install folder may be read-only, and a one-file build unpacks to a temp
  dir that is deleted on exit, which would wipe the player's progress).
"""
import os
import sys

APP_NAME = "ShadowStrike"


def is_frozen():
    return bool(getattr(sys, "frozen", False))


def base_dir():
    """Folder that contains the `assets` directory."""
    if is_frozen():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(*parts):
    """Path to a bundled, read-only resource (e.g. resource_path('assets'))."""
    return os.path.join(base_dir(), *parts)


def user_data_dir():
    """Writable folder for save data and logs (created on demand)."""
    if not is_frozen():
        return base_dir()                      # dev: keep saves in the project

    if sys.platform.startswith("win"):
        root = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        root = os.path.expanduser("~/Library/Application Support")
    else:
        root = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")

    path = os.path.join(root, APP_NAME)
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        path = os.path.expanduser("~")         # last resort
    return path
