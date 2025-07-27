"""Main window for the Person Detection application."""

import re
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QComboBox, QRadioButton, QCheckBox, QLineEdit, QMessageBox)
from PyQt6.QtGui import QPixmap
from .video_thread import VideoThread
from ..detection.camera import CameraChecker
from ..telegram.bot import TelegramBot
from ..database.handler import DBHelper
from ..core.config import Config
from typing import Optional


class MainWindow(QWidget):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.db = DBHelper()
        self.settings_window = QWidget()
        self.bot_st = ""
        self.camera_running = False
        
        self._setup_ui()
        self._setup_connections()
        self._start_telegram_bot()
        
    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Person Detector")
        self.setFixedSize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)

        # Main image display
        self.image_label = QLabel(self)
        self.image_label.setGeometry(QRect(50, 10, 981, 721))
        self.image_label.setScaledContents(True)

        # Camera selection combo box
        self.combo = QComboBox(self)
        self.combo.setGeometry(QRect(90, 760, 881, 25))

        # Control buttons
        self.start_button = QPushButton("Start Camera", self)
        self.start_button.clicked.connect(self.start_camera)
        self.start_button.setGeometry(QRect(280, 800, 241, 25))
        self.start_button.setStyleSheet("background-color: green")

        self.stop_button = QPushButton("Stop Camera", self)
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setGeometry(QRect(570, 800, 241, 25))
        self.stop_button.setStyleSheet("background-color: red")

        # Accuracy controls
        self._setup_accuracy_controls()
        
        # Bot settings
        self._setup_bot_controls()

        # Initialize camera checker
        self.thread: Optional[VideoThread] = None
        # self.thread: VideoThread | None = None
        # self.thread = None
        self.camera_checker = CameraChecker(self.combo)
        self.camera_checker.start()
        
    def _setup_accuracy_controls(self):
        """Setup accuracy and detection controls."""
        self.radioButton = QRadioButton("0.25", self)
        self.radioButton.setGeometry(QRect(120, 810, 81, 23))
        
        self.radioButton2 = QRadioButton("0.5", self)
        self.radioButton2.setGeometry(QRect(120, 840, 81, 23))
        
        self.radioButton3 = QRadioButton("0.75", self)
        self.radioButton3.setGeometry(QRect(120, 870, 81, 23))
        
        self.label_2 = QLabel("accuracy :", self)
        self.label_2.setGeometry(QRect(40, 810, 81, 31))
        
        self.checkBox = QCheckBox(self)
        self.checkBox.setGeometry(QRect(60, 840, 21, 23))
        
        # Connect radio button and checkbox signals
        self.radioButton.toggled.connect(self._on_setting_changed)
        self.radioButton2.toggled.connect(self._on_setting_changed)
        self.radioButton3.toggled.connect(self._on_setting_changed)
        self.checkBox.toggled.connect(self._on_setting_changed)
        
        # Set defaults
        self.checkBox.setChecked(True)
        self.radioButton2.setChecked(True)
    
    def _setup_bot_controls(self):
        """Setup bot-related UI controls."""
        self.settings_button = QPushButton("Bot Settings", self)
        self.settings_button.setGeometry(QRect(450, 845, 150, 25))
        self.settings_button.setDisabled(True)
        self.settings_button.clicked.connect(self.show_settings_window)
        
        self.bot_status_label = QLabel("Bot Status:", self)
        self.bot_status_label.setGeometry(QRect(350, 880, 150, 25))
        self.bot_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bot_status_label.setStyleSheet("font-weight: bold; color: white;")
        
        self.status_label = QLabel("Checking...", self)
        self.status_label.setGeometry(QRect(450, 880, 150, 25))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; color: yellow;")

        # Status update timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status_label)
        self.status_timer.start(500)
    
    def _setup_connections(self):
        """Setup signal connections."""
        pass  # Will be set up when telegram bot is initialized
    
    def _start_telegram_bot(self):
        """Initialize and start the Telegram bot."""
        self.telegram_bot = TelegramBot(self.db, self._get_camera_status)
        QTimer.singleShot(2000, self.telegram_bot.start)
        
        # Connect bot signals
        self.telegram_bot.bot_status.connect(self.set_bot_status)
        self.telegram_bot.send_start_camera.connect(self.start_camera)
        self.telegram_bot.send_stop_camera.connect(self.stop_camera)
    
    def _get_camera_status(self):
        """Get current camera running status."""
        return self.camera_running
    
    def _update_status_label(self):
        """Update the bot status checking animation."""
        current_text = self.status_label.text()
        if current_text.endswith("..."):
            self.status_label.setText("Checking")
        else:
            self.status_label.setText(current_text + ".")

    def set_bot_status(self, status: str):
        """Set the bot status display."""
        self.status_timer.stop()
        self.status_label.setGeometry(QRect(500, 880, 50, 25))
        self.bot_st = status
        
        if status == "on":
            self.status_label.setText("ON")
            self.status_label.setStyleSheet("background-color:white ;color: green;font-weight: bold;")
        else:
            self.status_label.setText("OFF")
            self.status_label.setStyleSheet("color: red; background-color:white;font-weight: bold;")
        
        self.settings_button.setEnabled(True)
        
    def _on_setting_changed(self):
        """Handle accuracy and detection setting changes."""
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.text() == "0.25":
                print(f"{radioButton.text()} is selected")
                accuracy = 0.25
            elif radioButton.text() == "0.5":
                print(f"{radioButton.text()} is selected")
                accuracy = 0.5
            elif radioButton.text() == "0.75":
                print(f"{radioButton.text()} is selected")
                accuracy = 0.75
            else:
                return
                
            # Update thread settings if running
            if self.thread is not None and isinstance(self.thread, VideoThread):
                if self.thread.isRunning():
                    self.thread.set_accuracy_threshold(accuracy)
        
        # Handle face detection checkbox
        if self.checkBox.isChecked():
            print("Face detection is on")
            show_accuracy = True
        else:
            print("Face detection is off")
            show_accuracy = False
            
        # Update thread settings if running
        if self.thread is not None and isinstance(self.thread, VideoThread):
            if self.thread.isRunning():
                self.thread.set_show_accuracy(show_accuracy)
        
    def start_camera(self):
        """Start the camera and video processing."""
        if self.thread is None or not self.thread.isRunning():
            self.thread = VideoThread(self.combo, self.camera_checker)
            
            # Apply current settings
            if self.radioButton.isChecked():
                self.thread.set_accuracy_threshold(0.25)
            elif self.radioButton2.isChecked():
                self.thread.set_accuracy_threshold(0.5)
            elif self.radioButton3.isChecked():
                self.thread.set_accuracy_threshold(0.75)
                
            self.thread.set_show_accuracy(self.checkBox.isChecked())
            
            # Connect signals
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.telegram_bot.send_persons_signal.connect(self.thread.send_persons)
            self.thread.send_image.connect(self.telegram_bot.send_photo_to_admin)
            
            self.thread.start()
            self.camera_running = True

    def stop_camera(self):
        """Stop the camera and video processing."""
        if self.thread is not None:
            self.thread.stop()
            self.camera_running = False

    def update_image(self, qt_image):
        """Update the image display."""
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))
        
    def show_settings_window(self):
        """Show the bot settings window."""
        self.settings_window.setWindowTitle("Telegram Bot Settings")
        self.settings_window.setFixedSize(550, 300)

        layout = QVBoxLayout()

        self.token_label = QLabel("Bot Token:", self.settings_window)
        layout.addWidget(self.token_label)

        self.token_input = QLineEdit(self.settings_window)
        token = self.db.get_bot_token()
        if token:
            self.token_input.setText(token)
        layout.addWidget(self.token_input)

        self.admin_label = QLabel("Admin IDs (comma separated| max 3):", self.settings_window)
        layout.addWidget(self.admin_label)

        self.admin_input = QLineEdit(self.settings_window)
        cur_admins = self.db.get_admins()
        if cur_admins:
            self.admin_input.setText(",".join(map(str, cur_admins)))
        layout.addWidget(self.admin_input)

        self.save_button = QPushButton("Save", self.settings_window)
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.settings_window.setLayout(layout)
        self.settings_window.show()
        
        # Show status alert
        self._show_settings_alert(token, cur_admins)
        
    def _show_settings_alert(self, token, cur_admins):
        """Show alert about current bot settings status."""
        alert = ""
        msg = QMessageBox(self.settings_window)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Caution")

        if self.bot_st == "on":
            alert += "Connection to Telegram servers succeeded\n"
        else:
            alert += "Connection to Telegram servers failed\n"
        if token is None:
            alert += "You should enter bot token.\n"
            
        if cur_admins is None:
            alert += "You should enter admin ids.\n"

        msg.setText(alert)
        msg.exec()

    def save_settings(self):
        """Save bot settings to database."""
        new_token = self.token_input.text()
        if len(new_token) < 10 or not re.match(r'^\d+:[\w-]+$', new_token):
            QMessageBox.warning(self, "Invalid Token", "The bot token format is invalid.")
            return
        
        if self.admin_input.text() == "":
            QMessageBox.warning(self, "Invalid Admin IDs", "The admin IDs should be positive integers.")
            return
        
        try:
            new_admins = list(map(int, self.admin_input.text().split(',')))
        except ValueError:
            QMessageBox.warning(self, "Invalid Admin IDs", "The admin IDs should be positive integers.")
            return
            
        if not all(x > 0 for x in new_admins):
            QMessageBox.warning(self, "Invalid Admin IDs", "The admin IDs should be positive integers.")
            return
        elif len(new_admins) > 3:
            QMessageBox.warning(self, "Invalid Admin Length", "You must have maximum 3 admins.")
            return
        
        if not self.db.is_sametoken(new_token):
            self.db.replace_token(new_token)
            print("Token changed")
        self.db.add_new_admins(new_admins)

        QMessageBox.information(self, "Settings Saved", "Settings have been updated successfully. Restart the application.")
        self.settings_window.close()