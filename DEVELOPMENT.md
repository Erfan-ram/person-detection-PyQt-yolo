# Development Guide

## Project Architecture

This project follows a modular Python package structure that separates concerns for maintainability and extensibility.

### Module Overview

#### Core (`src/person_detection/core/`)
- **`config.py`**: Centralized configuration settings for models, UI, camera, and database
- **`models.py`**: YOLO model management including downloading and initialization

#### Detection (`src/person_detection/detection/`)
- **`detector.py`**: Person detection algorithms and face detection integration
- **`camera.py`**: Camera management and device detection using v4l2-ctl

#### UI (`src/person_detection/ui/`)
- **`main_window.py`**: Main application window with controls and settings
- **`video_thread.py`**: Video processing thread for real-time detection

#### Telegram (`src/person_detection/telegram/`)
- **`bot.py`**: Telegram bot for remote monitoring and control

#### Database (`src/person_detection/database/`)
- **`handler.py`**: Database operations for user management and bot settings

## Key Design Decisions

### 1. Lazy Loading
Models and heavy dependencies are loaded only when needed to avoid import errors and improve startup time.

### 2. Configuration Centralization
All configuration constants are centralized in `Config` class for easy maintenance.

### 3. Thread Safety
Database operations use `check_same_thread=False` for multi-threaded access.

### 4. Signal-Slot Pattern
PyQt signals are used for communication between threads and components.

## Migration from Original Code

The original `pyqt_main.py` (664 lines) has been refactored into:

1. **Configuration extraction**: Global variables moved to `Config` class
2. **Model management**: YOLO model handling separated into `ModelManager`
3. **Detection logic**: Person detection algorithms extracted to `PersonDetector`
4. **UI separation**: Main window and video thread separated
5. **Bot isolation**: Telegram functionality moved to dedicated module
6. **Database abstraction**: Database operations cleaned up and isolated

## Adding New Features

### Adding a New Detection Algorithm
1. Create new class in `detection/` module
2. Implement standard interface (`detect_and_count_persons`)
3. Update `PersonDetector` to use new algorithm

### Adding New UI Components
1. Create new module in `ui/` package
2. Follow PyQt signal-slot pattern for communication
3. Import and integrate in `main_window.py`

### Extending Telegram Bot
1. Add new handlers in `telegram/bot.py`
2. Use existing signal system for UI communication
3. Update admin panel with new buttons if needed

## Testing

### Unit Testing
```bash
# Test individual modules
python -c "from person_detection.core.config import Config; print('Config OK')"
python -c "from person_detection.database.handler import DBHelper; print('Database OK')"
```

### Integration Testing
```bash
# Test full application (requires dependencies)
python run.py
```

## Building and Distribution

### Development Installation
```bash
pip install -e .
```

### Production Build
```bash
python setup.py sdist bdist_wheel
```

### Docker Support (Future)
The modular structure makes it easy to containerize:
```dockerfile
FROM python:3.9
COPY src/ /app/src/
COPY requirements.txt setup.py /app/
RUN pip install /app
CMD ["person-detection"]
```