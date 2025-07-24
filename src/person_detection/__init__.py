"""
Person Detection System using PyQt6 and YOLO.

A modular Python package for real-time person detection with GUI interface,
Telegram bot integration, and camera management capabilities.
"""

__version__ = "1.0.0"
__author__ = "Erfan-ram"

# Don't import main at module level to avoid dependency issues
def get_main():
    """Get the main function when needed."""
    from .main import main
    return main