# Person Detection System with PyQt and YOLO

## Overview
A robust desktop application built with PyQt5 that leverages YOLO (You Only Look Once) object detection to identify and track people in video streams. This project combines computer vision capabilities with a user-friendly interface for real-time person detection.

## Features
- Real-time person detection in video streams
- Multiple detection confidence levels (High, Medium, Low)
- Video source selection ( webcams )
- Detection visualization with bounding boxes
- Detection statistics display
- Telegram Bot alart system
- User-friendly PyQt6 interface
- Compatible with Raspberry Pi for edge computing applications

## Technology Stack
- **Frontend**: PyQt5
- **Computer Vision**: OpenCV, YOLO v3
- **Programming Language**: Python
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
The application is structured around a PyQt6 interface that connects to video sources, processes frames through the YOLO detection model, and displays the results with appropriate visual indicators. The system can process live webcam feeds or pre-recorded video files.

## Use Cases
- Security monitoring
- Crowd analysis
- Footfall tracking
- Automated surveillance systems

This project demonstrates the integration of modern deep learning techniques with desktop application development to create practical computer vision solutions.