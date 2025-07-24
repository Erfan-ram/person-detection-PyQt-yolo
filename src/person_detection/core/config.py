"""Configuration settings for the person detection system."""

import os


class Config:
    """Configuration class for person detection system."""
    
    # Model settings
    MODEL_PATH = 'Model/yolov8n.pt'
    FACE_MODEL_PATH = "Model/face_yolov8n.pt"
    MODEL_URL = 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt'
    
    # Detection settings
    DEFAULT_ACCURACY = 0.5
    PERSON_CLASS_ID = 0
    
    # Camera settings
    DEFAULT_FRAME_WIDTH = 640
    DEFAULT_FRAME_HEIGHT = 480
    DEFAULT_FPS = 30
    
    # UI settings
    WINDOW_WIDTH = 1074
    WINDOW_HEIGHT = 908
    
    # Database settings
    DATABASE_NAME = "person_dt.db"
    
    @classmethod
    def get_model_dir(cls):
        """Get the directory where models are stored."""
        return os.path.dirname(cls.MODEL_PATH)
    
    @classmethod
    def ensure_model_dir_exists(cls):
        """Ensure the model directory exists."""
        model_dir = cls.get_model_dir()
        if not os.path.exists(model_dir):
            print(f"Creating directory {model_dir}...")
            os.makedirs(model_dir, exist_ok=True)