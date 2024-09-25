import cv2
import os
import sys
import urllib.request
from ultralytics import YOLO
from PyQt6.QtCore import QThread, pyqtSignal, Qt , QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel , QComboBox
from PyQt6.QtGui import QPixmap, QImage
import subprocess
from PyQt6.QtWidgets import QMessageBox

import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from Db_handler import DBHelper


model_path = 'Model/yolov8n.pt'

if not os.path.exists(model_path):
    print("Downloading YOLO model...")
    url = 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt'
    urllib.request.urlretrieve(url, model_path)
    print("Download complete.")
else:
    print("Model already exists.")

model = YOLO(model_path)
fmodel = YOLO("Model/face_yolov8n.pt")


def draw_rounded_rectangle(img, top_left, bottom_right, color, thickness, radius=50):
    x1, y1 = top_left
    x2, y2 = bottom_right
    overlay = img.copy()
    edje_color = (0, 0, 255)
    
    cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
    cv2.circle(overlay, (x1 + radius, y1 + radius), radius, edje_color, -1)
    cv2.circle(overlay, (x2 - radius, y1 + radius), radius, edje_color, -1)
    cv2.circle(overlay, (x1 + radius, y2 - radius), radius, edje_color, -1)
    cv2.circle(overlay, (x2 - radius, y2 - radius), radius, edje_color, -1)

    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)

def detect_and_count_persons(frame):
    # results = model(frame)
    results = model.predict(frame, classes=[0],conf=0.2)
    persons = 0

    for result in results[0].boxes:
        cls = int(result.cls[0])
        conf = float(result.conf[0].cpu().numpy())
        if cls == 0:
            persons += 1
            box = result.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = box
            
            color = (0, 200, 0)
            thickness = 1
            
            draw_rounded_rectangle(frame, (x1, y1), (x2, y2), color, thickness, radius=10)

            label = f'Person: {round(conf, 2)}'
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            label_w, label_h = label_size
            
            label_bg_top_left = (x1, y1 - label_h - 10)
            label_bg_bottom_right = (x1 + label_w, y1)
            cv2.rectangle(frame, label_bg_top_left, label_bg_bottom_right, (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # face_results = fmodel(frame[y1:y2, x1:x2])
            #     cv2.rectangle(frame, (x1 + fx1, y1 + fy1), (x1 + fx2, y1 + fy2), (0, 0, 255), 2)
            # face_results = fmodel(frame)
            
            # face_results = fmodel.predict(frame, conf=0.6)
            # # face_results = fmodel.predict(frame)
            # for fresult in face_results[0].boxes:
            #     fbox = fresult.xyxy[0].cpu().numpy().astype(int)
            #     fx1, fy1, fx2, fy2 = fbox
            #     cv2.rectangle(frame, (fx1, fy1), (fx2, fy2), (0, 0, 255), 2)
            
    
    cv2.putText(frame, f'Persons: {persons}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    return frame, persons

# def detect_and_count_persons(frame):
#     results = model(frame)
#     persons = 0

#     for result in results[0].boxes:
#         cls = int(result.cls[0])
#         conf = float(result.conf[0].cpu().numpy())
#         if cls == 0:
#             persons += 1
#             box = result.xyxy[0].cpu().numpy().astype(int)
#             x1, y1, x2, y2 = box
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             cv2.putText(frame, 'Person', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
#             cv2.putText(frame, 'conf: ' + str(round(conf, 2)), (x1 + 20, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
    
#     cv2.putText(frame, f'Persons: {persons}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
#     return frame, persons

class telegrambot:
    def __init__(self):
        self.db = DBHelper()
        self.admin_id = ['250377535']

        self.BOT_TOKEN = '7579055761:AAF5SSfCqPNXA3T4f02jZbquWefnTlMuXiM'
        # CHANNEL_NAME = '@khabaryub'

        self.bot = AsyncTeleBot(self.BOT_TOKEN)
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['help', 'start'])
        async def send_welcome(message):
            text = 'hello babe!'
            await self.bot.reply_to(message, text)

        @self.bot.message_handler(func=lambda message: True)
        async def echo_message(message):
            user_name = message.from_user.first_name
            user_id = message.from_user.id
            if self.db.user_exists(user_id):
                print(f"User {user_name} already exists in the database.")
            else:
                self.db.add_user(user_name, user_id)
                print(f"User {user_name} added to the database.")
                await self.bot.reply_to(message, message.text)
                
        @self.bot.message_handler(func=lambda message: True and message.text == 'sendtext' and message.chat.id in self.admin_id)
        async def send_text(message):
            print("Sending message to all users...")
            await self.send_message_to_all_users()
                
        async def send_message_to_all_users():
            users = self.db.get_all_users()
            for user in users:
                user_id = user[0]
                user_name = user[1]
                await self.bot.send_message(user_id, f"Hello {user_name}!")
            
    def start_(self):
        asyncio.run(self.bot.polling())

class CameraChecker:
    def __init__(self, combo_obj: QComboBox):
        self.cameras = {}
        self.combo_obj = combo_obj

    def cam_available(self):     
        try:
            result = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                lines = output.split('\n')
                new_cameras = {}
                camera_name = None

                for i, line in enumerate(lines):
                    # print(i, line)
                    if "usb-" in line:
                        camera_name = lines[i].strip()
                        # camera_name = camera_name[:(line.index('usb-') - 1)]
                        address = lines[i+1].strip()
                        new_cameras[camera_name] = address

                # print(f"Cameras: {new_cameras}")

                for camera in new_cameras.keys():
                    if camera not in self.cameras:
                        # print(f"New camera detected: {camera}")
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Icon.Information)
                        msg.setText(f"New camera detected: {camera}")
                        msg.setWindowTitle("Camera Detection")
                        msg.exec()
                        self.combo_obj.addItem(camera)

                for camera in self.cameras.keys():
                    if camera not in new_cameras:
                        # print(f"Camera removed: {camera}")
                        self.combo_obj.removeItem(self.combo_obj.findText(camera))

                self.cameras = new_cameras.copy()

            else:
                print("Error running v4l2-ctl")
                self.cameras = {}
        except Exception as e:
            print(f"Exception occurred: {e}")
            self.cameras = {}

    def start_(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.cam_available)
        self.timer.start(1000)

    def get_cameras(self):
        return self.cameras


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, combo_obj: QComboBox, camera_obj: CameraChecker):
        super().__init__()
        self._run_flag = True
        self.combo_obj = combo_obj
        self.camera_obj = camera_obj

    def run(self):
        try:
            # cam_availabe = self.camera_checker.get_cameras()
            # print(f"Available cameras: {cam_availabe}")
            option_selected = self.combo_obj.currentText()
            address = self.camera_obj.get_cameras().get(option_selected)
            if address is None:
                raise ValueError(f"No address found for the selected camera: {option_selected}")

            cap = cv2.VideoCapture(address)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)

            while self._run_flag:
                ret, frame = cap.read()
                if ret:
                    frame, persons = detect_and_count_persons(frame)

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

        self.combo = QComboBox(self)
        layout.addWidget(self.combo)

        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        self.thread = None
        self.camera_checker = CameraChecker(self.combo)
        self.camera_checker.start_()
        
        self.telegram_bot = telegrambot()
        self.telegram_bot.start_()
        
    def start_camera(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = VideoThread(self.combo , self.camera_checker)
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
