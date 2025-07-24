# Migration Guide

## From Old Structure to New Modular Structure

If you were using the previous version with `pyqt_main.py`, here's how to migrate to the new modular structure.

## What Changed

### Before (Old Structure)
```
person-detection-PyQt-yolo/
├── pyqt_main.py          # 664 lines - everything in one file
├── Db_handler.py         # Database operations
├── requirements.txt
├── Model/                # YOLO models
└── README.md
```

### After (New Structure)
```
person-detection-PyQt-yolo/
├── src/
│   └── person_detection/          # Main package
│       ├── __init__.py
│       ├── main.py               # Entry point
│       ├── core/                 # Configuration & models
│       ├── detection/            # Detection logic
│       ├── ui/                   # User interface
│       ├── telegram/             # Bot functionality
│       └── database/             # Database operations
├── run.py                        # Compatibility script
├── setup.py                      # Package installation
└── requirements.txt
```

## Migration Steps

### 1. Update Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### 2. Running the Application

#### Method 1: Use Compatibility Script (Easiest)
```bash
# Replace your old command:
# python pyqt_main.py

# With:
python run.py
```

#### Method 2: Install as Package (Recommended)
```bash
pip install -e .
person-detection
```

#### Method 3: Direct Module Execution
```bash
python -m src.person_detection.main
```

### 3. Custom Modifications

If you made modifications to the original `pyqt_main.py`, here's where to find equivalent code:

| Original Code Section | New Location |
|----------------------|--------------|
| Global variables (model_path, cam_flag, etc.) | `src/person_detection/core/config.py` |
| Model downloading and initialization | `src/person_detection/core/models.py` |
| `draw_rounded_rectangle` function | `src/person_detection/detection/detector.py` |
| `TelegramBot` class | `src/person_detection/telegram/bot.py` |
| `CameraChecker` class | `src/person_detection/detection/camera.py` |
| `VideoThread` class | `src/person_detection/ui/video_thread.py` |
| `MainWindow` class | `src/person_detection/ui/main_window.py` |
| Database operations | `src/person_detection/database/handler.py` |

### 4. Configuration Changes

Configuration is now centralized in `Config` class:

#### Before:
```python
model_path = 'Model/yolov8n.pt'
cam_flag = False
accuracy_c = 0.5
```

#### After:
```python
from person_detection.core.config import Config

Config.MODEL_PATH  # 'Model/yolov8n.pt'
Config.DEFAULT_ACCURACY  # 0.5
```

### 5. Importing Components

#### Before:
```python
# Everything was in one file
from pyqt_main import MainWindow, TelegramBot
```

#### After:
```python
# Import from specific modules
from person_detection.ui.main_window import MainWindow
from person_detection.telegram.bot import TelegramBot
from person_detection.detection.detector import PersonDetector
```

## Benefits of New Structure

1. **Maintainability**: Code is organized into logical modules
2. **Testability**: Individual components can be tested separately
3. **Extensibility**: Easy to add new features without touching existing code
4. **Reusability**: Components can be imported and used independently
5. **Professional**: Follows Python package best practices
6. **Documentation**: Each module is self-contained and documented

## Troubleshooting

### Import Errors
If you get import errors, ensure you're using one of the recommended run methods above.

### Dependencies Missing
```bash
pip install -r requirements.txt
```

### Database Issues
The database handling is backward compatible. Your existing `person_dt.db` will work with the new structure.

### Model Files
Model files in the `Model/` directory will be automatically detected and used by the new structure.

## Rollback (if needed)

If you need to temporarily use the old structure:
1. Keep the original `pyqt_main.py` and `Db_handler.py` files
2. Run with: `python pyqt_main.py`

However, we recommend migrating to the new structure for better long-term maintainability.