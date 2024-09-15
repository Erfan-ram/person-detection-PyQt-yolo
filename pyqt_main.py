import cv2
from ultralytics import YOLO
import os
import sys
import urllib.request
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QImage

model_path = 'Model/yolov8n.pt'

if not os.path.exists(model_path):
    print("Downloading YOLO model...")
    url = 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt'
    urllib.request.urlretrieve(url, model_path)
    print("Download complete.")
else:
    print("Model already exists.")

model = YOLO(model_path)

def detect_and_count_persons(frame):
    results = model(frame)
    persons = 0

    for result in results[0].boxes:
        cls = int(result.cls[0])
        conf = float(result.conf[0].cpu().numpy())
        if cls == 0:
            persons += 1
            box = result.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, 'Person', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
            cv2.putText(frame, 'conf: ' + str(round(conf, 2)), (x1 + 20, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
    
    cv2.putText(frame, f'Persons: {persons}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    return frame, persons

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 30)

        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                frame, persons = detect_and_count_persons(frame)

                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                self.change_pixmap_signal.emit(qt_image)

        cap.release()

    def stop(self):
        self._run_flag = False
        # self.wait()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YOLOv8 - Person Detection")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        self.thread = None

    def start_camera(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = VideoThread()
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.thread.start()

    def stop_camera(self):
        if self.thread is not None:
            self.thread.stop()

    def update_image(self, qt_image):
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
