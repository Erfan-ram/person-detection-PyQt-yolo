import cv2
import os
import sys
import urllib.request
from ultralytics import YOLO
from PyQt6.QtCore import QThread, pyqtSignal, Qt , QTimer , QObject , QRect
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel , QComboBox ,QRadioButton ,QCheckBox
from PyQt6.QtGui import QPixmap, QImage
import subprocess
from PyQt6.QtWidgets import QMessageBox
import numpy
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from Db_handler import DBHelper


model_path = 'Model/yolov8n.pt'
cam_flag = False
accuracy_flag = False
accuracy_c = 0.5

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

# class TelegramBot(QObject):
class TelegramBot(QThread):
    send_persons_signal = pyqtSignal()
    send_start_camera = pyqtSignal()
    send_stop_camera = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = DBHelper()
        self.admin_id = [250377535, 0000]
        
        self.BOT_TOKEN = '7579055761:AAF5SSfCqPNXA3T4f02jZbquWefnTlMuXiM'
        self.bot = AsyncTeleBot(self.BOT_TOKEN)
        self.loop = None
        
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['help', 'start'])
        async def send_welcome(message):
            text = 'Hello !'
            await self.bot.reply_to(message, text)

        @self.bot.message_handler(func=lambda message: int(message.chat.id) not in self.admin_id)
        async def echo_message(message):
            user_name = message.from_user.first_name
            user_id = message.from_user.id
            if self.db.user_exists(user_id):
                print(f"User {user_name} already exists in the database.")
            else:
                self.db.add_user(user_name, user_id)
                print(f"User {user_name} added to the database.")
                await self.bot.reply_to(message, message.text)

        @self.bot.message_handler(func=lambda message: message.text == 'sendtext' and int(message.chat.id) in self.admin_id)
        async def send_text(message):
            print("Sending message to all users...")
            await self.send_message_to_all_users()

        @self.bot.message_handler(func=lambda message: int(message.from_user.id) in self.admin_id)
        async def handle_admin_command(message):
            if message.text == '/panel':
                await handle_admin(message)

        async def handle_admin(message):
            keyboard = InlineKeyboardMarkup()
            keyboard.row_width = 2
            keyboard.add(
                InlineKeyboardButton("Get photo", callback_data="photo"),
                InlineKeyboardButton("shutdown", callback_data="shutdown"),
                InlineKeyboardButton("start camera", callback_data="start_camera"),
                InlineKeyboardButton("stop camera", callback_data="stop_camera")
            )
            await self.bot.reply_to(message, 'You are my admin. Choose an action:', reply_markup=keyboard)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        async def callback_query(call):
            if call.data == "photo":
                if cam_flag:
                    self.send_persons_signal.emit()
                else :
                    await self.bot.send_message(call.message.chat.id, "Please start the camera first.")
            elif call.data == "shutdown":
                # await self.bot.send_message(call.message.chat.id, "I'm shutting down...")
                await self.bot.send_message(call.message.chat.id, "Shutting down the application...")
                os._exit(0)
                self.loop.stop()
                QApplication.quit()
                # self.loop.stop()
                # subprocess.run(['sudo', 'shutdown', 'now'])
            elif call.data == "start_camera":
                if not cam_flag:
                    self.send_start_camera.emit()
                else:
                    await self.bot.send_message(call.message.chat.id, "Camera is already running.")
            elif call.data == "stop_camera":
                if cam_flag:
                    self.send_stop_camera.emit()
                else:
                    await self.bot.send_message(call.message.chat.id, "Camera is not running.")

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.loop.run_until_complete(self.bot.polling(none_stop=True))
    
    def send_photo_to_admin(self, data):
        # print("\n\n\n\nGOT AN IMAGE\n\n\n\n")
        
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_photoo(data), self.loop)
    
    async def send_photoo(self, data):
        print("Sending photo to admin...")
        

        _, buffer = cv2.imencode('.jpg', data[0])
        
        photo = buffer.tobytes()
        await self.bot.send_photo(self.admin_id[0], photo , caption="Person detected!")
        
        if len(data) == 2:
            _, buffer = cv2.imencode('.jpg', data[1])
            face = buffer.tobytes()
            await self.bot.send_photo(self.admin_id[0], face, caption="Face detected!")
        # await self.bot.send_message(self.admin_id[0], "Photo sent to admin.")

    async def send_message_to_all_users(self):
        users = self.db.get_all_users()
        print(f"Users: {users}")
        for user in users:
            user_id = user[0]
            chat = await self.bot.get_chat(user_id)
            await self.bot.send_message(user_id, f"Hello {chat.first_name} @{chat.username}!")
        
        await self.bot.send_message(self.admin_id[0], "Message sent to all users.")


# class BotThread(QThread):
#     def __init__(self, bot_instance):
#         super().__init__()
#         self.bot_instance = bot_instance

#     def run(self):
#         """Run the bot in the separate thread."""
#         self.bot_instance.start_bot()

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
    send_image = pyqtSignal(object)
    # send_image = pyqtSignal(numpy.ndarray,numpy.ndarray)

    def __init__(self, combo_obj: QComboBox, camera_obj: CameraChecker):
        super().__init__()
        self._run_flag = True
        self.combo_obj = combo_obj
        self.camera_obj = camera_obj
        self.detection_list = []
    
    def detect_and_count_persons(self,frame):
        # results = model(frame)
        results = model.predict(frame, classes=[0],conf=accuracy_c)
        persons = 0
        self.detection_list = []

        for result in results[0].boxes:
            cls = int(result.cls[0])
            conf = float(result.conf[0].cpu().numpy())
            if cls == 0:
                persons += 1
                box = result.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = box
                
                color = (0, 150, 0)
                thickness = 1
                cut_frame = frame[y1:y2, x1:x2].copy()
                self.detection_list.append(cut_frame)
                draw_rounded_rectangle(frame, (x1, y1), (x2, y2), color, thickness, radius=8)

                label = f'Person: {round(conf, 2)}'
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_w, label_h = label_size
                
                label_bg_top_left = (x1, y1 - label_h - 10)
                label_bg_bottom_right = (x1 + label_w, y1)
                if accuracy_flag:
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
    
    def send_persons(self):
        print("Sending persons to all users...")
        for detection in self.detection_list:
            face = None
            face_results = fmodel.predict(detection, conf=0.6)
            for fresult in face_results[0].boxes:
                fbox = fresult.xyxy[0].cpu().numpy().astype(int)
                fx1, fy1, fx2, fy2 = fbox
                face = detection[fy1:fy2, fx1:fx2]
            if face is not None:
                self.send_image.emit((detection,face))
            else:
                self.send_image.emit((detection, ))
        print("Persons sent to all users.")

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
                    frame, persons = self.detect_and_count_persons(frame)

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
        # self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(1074,908)

        # layout = QVBoxLayout()

        self.image_label = QLabel(self)
        # self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setGeometry(QRect(50, 10, 981, 721))
        self.image_label.setScaledContents(True)
        # layout.addWidget(self.image_label)

        self.combo = QComboBox(self)
        self.combo.setGeometry(QRect(90, 760, 881, 25))
        # layout.addWidget(self.combo)

        self.start_button = QPushButton("Start Camera",self)
        self.start_button.clicked.connect(self.start_camera)
        self.start_button.setGeometry(QRect(280, 800, 241, 25))
        self.start_button.setStyleSheet("background-color: green")
        # layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera",self)
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setGeometry(QRect(570, 800, 241, 25))
        self.stop_button.setStyleSheet("background-color: red")
        # layout.addWidget(self.stop_button)

        # self.setLayout(layout)
        self.radioButton = QRadioButton("0.25",self)
        self.radioButton.setGeometry(QRect(120, 810, 81, 23))
        self.radioButton2 = QRadioButton("0.5",self)
        self.radioButton2.setGeometry(QRect(120, 840, 81, 23))
        self.radioButton3 = QRadioButton("0.75",self)
        self.radioButton3.setGeometry(QRect(120, 870, 81, 23))
        self.label_2 = QLabel("accuracy :",self)
        self.label_2.setGeometry(QRect(40, 810, 81, 31))
        self.checkBox = QCheckBox(self)
        self.checkBox.setGeometry(QRect(60, 840, 21, 23))
        
        self.radioButton.toggled.connect(self.onClicked)
        self.radioButton2.toggled.connect(self.onClicked)
        self.radioButton3.toggled.connect(self.onClicked)
        self.checkBox.toggled.connect(self.onClicked)
        
        self.checkBox.setChecked(True)
        self.radioButton2.setChecked(True)
        self.thread = None
        self.camera_checker = CameraChecker(self.combo)
        self.camera_checker.start_()
        

        self.telegram_bot = TelegramBot()
        self.telegram_bot.start()
        
        self.telegram_bot.send_start_camera.connect(self.start_camera)
        self.telegram_bot.send_stop_camera.connect(self.stop_camera)

        # self.bot_thread = BotThread(self.telegram_bot)
        # self.bot_thread.start()
        
    def onClicked(self):
        global accuracy_flag
        global accuracy_c
        
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.text() == "0.25":
                print(f"{radioButton.text()} is selected")
                accuracy_c = 0.25
            elif radioButton.text() == "0.5":
                print(f"{radioButton.text()} is selected")
                accuracy_c = 0.5
            elif radioButton.text() == "0.75":
                print(f"{radioButton.text()} is selected")
                accuracy_c = 0.75
        if self.checkBox.isChecked():
            print("Face detection is on")
            accuracy_flag = True
        else:
            print("Face detection is off")
            accuracy_flag = False
        
    def start_camera(self):
        global cam_flag
        if self.thread is None or not self.thread.isRunning():
            self.thread = VideoThread(self.combo , self.camera_checker)
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.telegram_bot.send_persons_signal.connect(self.thread.send_persons)
            self.thread.send_image.connect(self.telegram_bot.send_photo_to_admin)
            self.thread.start()
            cam_flag = True

    def stop_camera(self):
        global cam_flag
        if self.thread is not None:
            self.thread.stop()
            cam_flag = False

    def update_image(self, qt_image):
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
