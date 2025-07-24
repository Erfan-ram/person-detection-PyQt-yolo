#!/usr/bin/env python3
"""
Compatibility script for running the person detection system.

This script provides backward compatibility while using the new modular structure.
You can run this directly like the old pyqt_main.py file.
"""

import sys
import os

# Add src directory to path so we can import the new modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from person_detection.main import main

if __name__ == "__main__":
    sys.exit(main())