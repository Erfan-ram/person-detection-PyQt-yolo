#!/usr/bin/env python3
"""
DEPRECATED: This file has been replaced by the new modular structure.

This is the original monolithic version of the person detection system.
It has been refactored into a modular structure located in src/person_detection/

Please use one of the following instead:
1. python run.py (compatibility script)
2. pip install -e . && person-detection (recommended)
3. python -m src.person_detection.main

For migration help, see MIGRATION.md
"""

import warnings
import sys
import os

warnings.warn(
    "pyqt_main.py is deprecated. Please use the new modular structure. "
    "See MIGRATION.md for details.",
    DeprecationWarning,
    stacklevel=2
)

# Try to run the new version if possible
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from person_detection.main import main
    print("Running new modular version...")
    sys.exit(main())
except ImportError:
    print("Dependencies not available. Please install with: pip install -r requirements.txt")
    print("Or run the legacy version by commenting out this deprecation warning.")

# Original code would follow here, but we're encouraging migration
print("Please migrate to the new modular structure. See MIGRATION.md")
sys.exit(1)