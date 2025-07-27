"""Person detection functionality."""

import cv2
from ..core.config import Config


def draw_rounded_rectangle(img, top_left, bottom_right, color, thickness, radius=50):
    """Draw a rounded rectangle on the image."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    overlay = img.copy()
    edge_color = (0, 0, 255)
    
    cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
    cv2.circle(overlay, (x1 + radius, y1 + radius), radius, edge_color, -1)
    cv2.circle(overlay, (x2 - radius, y1 + radius), radius, edge_color, -1)
    cv2.circle(overlay, (x1 + radius, y2 - radius), radius, edge_color, -1)
    cv2.circle(overlay, (x2 - radius, y2 - radius), radius, edge_color, -1)

    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)


class PersonDetector:
    """Handles person detection using YOLO models."""
    
    def __init__(self):
        self.accuracy_threshold = Config.DEFAULT_ACCURACY
        self.show_accuracy = False
        self.detection_list = []
        self._model_manager = None
    
    def _get_model_manager(self):
        """Lazy load model manager."""
        if self._model_manager is None:
            from ..core.models import model_manager
            self._model_manager = model_manager
        return self._model_manager
    
    def set_accuracy_threshold(self, threshold):
        """Set the accuracy threshold for detection."""
        self.accuracy_threshold = threshold
    
    def set_show_accuracy(self, show):
        """Set whether to show accuracy labels."""
        self.show_accuracy = show
    
    def detect_and_count_persons(self, frame):
        """Detect persons in frame and return annotated frame and count."""
        model_manager = self._get_model_manager()
        model = model_manager.get_person_model()
        # results = model.predict(frame, classes=[Config.PERSON_CLASS_ID], conf=self.accuracy_threshold)
        results = model.predict(frame, classes=[Config.PERSON_CLASS_ID], conf=self.accuracy_threshold, verbose=False)
        persons = 0
        self.detection_list = []

        for result in results[0].boxes:
            cls = int(result.cls[0])
            conf = float(result.conf[0].cpu().numpy())
            if cls == Config.PERSON_CLASS_ID:
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
                if self.show_accuracy:
                    cv2.rectangle(frame, label_bg_top_left, label_bg_bottom_right, (0, 255, 0), cv2.FILLED)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
        cv2.putText(frame, f'Persons: {persons}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        return frame, persons
    
    def get_detections_with_faces(self):
        """Get detected persons with face analysis."""
        if not self.detection_list:
            return []
        
        model_manager = self._get_model_manager()
        face_model = model_manager.get_face_model()
        if not face_model:
            return [(detection, None) for detection in self.detection_list]
        
        results = []
        for detection in self.detection_list:
            face = None
            face_results = face_model.predict(detection, conf=0.6)
            for fresult in face_results[0].boxes:
                fbox = fresult.xyxy[0].cpu().numpy().astype(int)
                fx1, fy1, fx2, fy2 = fbox
                face = detection[fy1:fy2, fx1:fx2]
                break  # Take first face found
            results.append((detection, face))
        
        return results