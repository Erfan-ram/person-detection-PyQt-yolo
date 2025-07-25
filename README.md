# Person Detection System with PyQt and YOLO

## Overview
A robust desktop application built with PyQt6 that leverages YOLO object detection to identify and track people in video streams. This project combines computer vision capabilities with a user-friendly interface for real-time person detection and works both offline and online.

> Currently works on Unix-based systems, with Windows compatibility planned for future releases.


## Screenshots

<div align="center">
    <img src="images/1.png" alt="Application Interface" width="600"/>
    <p><em>Person Detection in Action</em></p>
</div>

<div align="center">
    <img src="images/2.png" alt="Person Detection in Action" width="400" style="display: inline-block; margin-right: 10px;"/>
    <img src="images/3.png" alt="Detection Results" width="400" style="display: inline-block;"/>
    <br>
    <p><em>Application Interface &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Detection Results on Telegram</em></p>
</div>


## Project Structure

The project follows a modular Python package structure for better maintainability and extensibility:

```
person-detection-PyQt-yolo/
├── src/
│   └── person_detection/          # Main package
│       ├── __init__.py
│       ├── main.py               # Application entry point
│       ├── core/                 # Core functionality
│       │   ├── config.py         # Configuration settings
│       │   └── models.py         # YOLO model management
│       ├── detection/            # Detection logic
│       │   ├── detector.py       # Person detection algorithms
│       │   └── camera.py         # Camera management
│       ├── ui/                   # User interface
│       │   ├── main_window.py    # Main application window
│       │   └── video_thread.py   # Video processing thread
│       ├── telegram/             # Telegram bot integration
│       │   └── bot.py            # Bot functionality
│       └── database/             # Database operations
│           └── handler.py        # Database management
├── run.py                        # Compatibility script
├── setup.py                      # Package installation
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Installation

### Method 1: Direct Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/Erfan-ram/person-detection-PyQt-yolo.git
cd person-detection-PyQt-yolo

# Install system dependencies
sudo apt install v4l-utils

# Install Python dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Run the application
person-detection
```

### Method 2: Run Directly (without package installation)
```bash
# After cloning and installing dependencies
python run.py
```

### Method 3: Development Mode
```bash
# From the project root
python -m src.person_detection.main
```


## Features
- [x] **Real-time person detection** using YOLOv8
- [x] **Modular architecture** for easy maintenance and extension
- [x] **Multiple camera support** with automatic detection
- [x] **Telegram bot integration** for remote monitoring
- [x] **Configurable accuracy levels** (0.25, 0.5, 0.75)
- [x] **Face detection** within person bounding boxes
- [x] **Database management** for users and settings
- [x] **Professional package structure** following Python best practices
- [x] **Backward compatibility** with previous versions

## Technology Stack
- **GUI**: PyQt6
- **Computer Vision**: OpenCV, YOLO v8
- **Camera Utilities**: v4l-utils

## Prerequisites
Before using this application, you need to install v4l-utils:
```bash
sudo apt install v4l-utils
```
This utility is used to identify and configure camera devices in the system.

## Dependencies
All Python dependencies are listed in `requirements.txt` and will be installed automatically with the installation methods above.

## Usage Examples

### Basic Detection
```python
from person_detection.detection.detector import PersonDetector
import cv2

detector = PersonDetector()
detector.set_accuracy_threshold(0.5)

# Process a frame
frame = cv2.imread('your_image.jpg')
annotated_frame, person_count = detector.detect_and_count_persons(frame)
print(f"Detected {person_count} persons")
```

### Using as Library
```python
from person_detection.core.config import Config
from person_detection.database.handler import DBHelper

# Access configuration
print(f"Model path: {Config.MODEL_PATH}")

# Database operations
db = DBHelper()
users = db.get_all_users()
```

## Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Run the application and go to "Bot Settings"
4. Enter your bot token and admin user IDs
5. Restart the application to apply changes
6. Send `/panel` to your bot to access controls

## 📜 Legacy Version Available

**Looking for the original single-file version?** The legacy monolithic implementation (663-line `pyqt_main.py`) is preserved on the `old-code` branch for reference and backward compatibility.

```bash
git checkout old-code  # Access original pyqt_main.py
python pyqt_main.py   # Run legacy version
```

For detailed migration instructions, see [MIGRATION.md](MIGRATION.md).

The current main branch features a modern, modular architecture that's easier to maintain and extend.


## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development guidelines and architecture documentation.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Roadmap
### Planned Features
- [ ] Add facial recognition capability to identify unique individuals and track their presence over time
- [ ] Generate detailed statistics and reports for each identified person
- [ ] Full support for Windows operating systems
- [ ] Upgrade to newer YOLO versions for improved accuracy and performance
- [ ] Simultaneous monitoring from multiple camera sources
- [ ] Backup detection logs and statistics to cloud services
- [ ] Customizable notification rules based on person count, time of day, or specific individuals
- [ ] Docker containerization support
- [ ] REST API for integration with other systems ( not knowing how to do this yet )