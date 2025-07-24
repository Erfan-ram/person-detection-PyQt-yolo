# Person Detection System with PyQt and YOLO

## Overview
A robust desktop application built with PyQt6 that leverages YOLO (You Only Look Once) object detection to identify and track people in video streams. This project combines computer vision capabilities with a user-friendly interface for real-time person detection.
> Currently works on Unix-based systems, with Windows compatibility planned for future releases.

## Features
- [x] Real-time person detection in video streams
- [x] Multiple detection confidence levels (High, Medium, Low)
- [x] Video source selection ( webcams )
- [x] Detection visualization with bounding boxes
- [x] Security monitoring
- [x] Telegram Bot alert system
- [x] User-friendly PyQt6 interface
- [x] Compatible with Raspberry Pi for edge computing applications

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

## Required Python Packages
Install the following Python packages using pip:
```bash
pip install ultralytics PyQt6 telebot opencv-python
```

## Implementation
The application is structured around a PyQt6 interface that connects to video sources, processes frames through the YOLO detection model, and displays the results with appropriate visual indicators. The system can process live webcam .
This project demonstrates the integration of modern deep learning techniques with desktop application development to create practical computer vision solutions.

## Future Roadmap

### Planned Features
- [ ] Add facial recognition capability to identify unique individuals and track their presence over time
- [ ] Generate detailed statistics and reports for each identified person
- [ ] Full support for Windows operating systems with native camera drivers
- [ ] Upgrade to newer YOLO versions for improved accuracy and performance
- [ ] Simultaneous monitoring from multiple camera sources
- [ ] Backup detection logs and statistics to cloud services
- [ ] Remote monitoring and alert management through mobile application
- [ ] Customizable notification rules based on person count, time of day, or specific individuals
- [ ] Generate PDF reports and export data in various formats (CSV, JSON)
- [ ] Configurable face blurring and data retention policies
- [ ] Database integration for persistent storage