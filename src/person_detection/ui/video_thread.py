"""Video thread for camera processing."""

import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from ..detection.detector import PersonDetector
from ..detection.camera import CameraChecker
from ..core.config import Config


class VideoThread(QThread):
    """Thread for handling video capture and person detection."""
    
    change_pixmap_signal = pyqtSignal(QImage)
    send_image = pyqtSignal(object, str)

    def __init__(self, combo_obj, camera_obj: CameraChecker):
        super().__init__()
        self._run_flag = True
        self.detected_img = None
        self.combo_obj = combo_obj
        self.camera_obj = camera_obj
        self.detector = PersonDetector()
    
    def set_accuracy_threshold(self, threshold):
        """Set the accuracy threshold for detection."""
        self.detector.set_accuracy_threshold(threshold)
    
    def set_show_accuracy(self, show):
        """Set whether to show accuracy labels."""
        self.detector.set_show_accuracy(show)

    def send_persons(self):
        """Send detected persons to admin via Telegram."""
        print("Sending persons to all users...")
        
        detections = self.detector.get_detections_with_faces()
        
        if not detections:
            self.send_image.emit((self.detected_img,), "Noperson")
            return
        
        for detection, face in detections:
            if face is not None:
                self.send_image.emit((detection, face), "pandf")
            else:
                self.send_image.emit((detection,), "Noface")
        
        print("Persons sent to all users.")

    def run(self):
        """Main video processing loop."""
        try:
            option_selected = self.combo_obj.currentText()
            address = self.camera_obj.get_cameras().get(option_selected)
            if address is None:
                raise ValueError(f"No address found for the selected camera: {option_selected}")

            cap = cv2.VideoCapture(address)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.DEFAULT_FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.DEFAULT_FRAME_HEIGHT)
            cap.set(cv2.CAP_PROP_FPS, Config.DEFAULT_FPS)

            while self._run_flag:
                ret, frame = cap.read()
                if ret:
                    frame, persons = self.detector.detect_and_count_persons(frame)
                    
                    self.detected_img = frame.copy()
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(
                        rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
                    )

                    self.change_pixmap_signal.emit(qt_image)
                else:
                    print("Failed to read frame from camera.")
                    break

            cap.release()
        except Exception as e:
            print(f"An error occurred: {e}")
            if 'cap' in locals():
                cap.release()

    def stop(self):
        """Stop the video thread."""
        self._run_flag = False