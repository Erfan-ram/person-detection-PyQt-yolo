import cv2
from ultralytics import YOLO
import os

#TODO: use GUI PYQT
#TODO: use openvino super fast implementation of yolo

import urllib.request

model_path = 'Model/yolov8n.pt'

if not os.path.exists(model_path):
    print("Downloading YOLO model...")
    url = 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt'
    urllib.request.urlretrieve(url, model_path)
    print("Download complete.")
else :
    print("Model already exists. ok")

model = YOLO(model_path)

def detect_and_count_persons(frame):
    results = model(frame)
    # results = model.predict(frame, classes=[0], conf=0.5)
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
            cv2.putText(frame, 'conf: ' + str(round(conf,2)), (x1 + 20, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
    
    cv2.putText(frame, f'Persons: {persons}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    return frame, persons

cap = cv2.VideoCapture(0)
# input_shape = (640, 640)
# output_shape = (1280, 720)

cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("Error: Could not open video source.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    frame, persons = detect_and_count_persons(frame)

    cv2.imshow('YOLOv8', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
