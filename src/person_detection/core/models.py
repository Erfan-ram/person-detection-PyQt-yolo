"""Model management for YOLO models."""

import os
import urllib.request
from ultralytics import YOLO
from .config import Config


class ModelManager:
    """Manages YOLO model downloading and initialization."""
    
    def __init__(self):
        self.person_model = None
        self.face_model = None
        self._initialized = False
    
    def initialize(self):
        """Initialize models by downloading if needed and loading them."""
        if self._initialized:
            return
            
        Config.ensure_model_dir_exists()
        self._download_models()
        self._load_models()
        self._initialized = True
    
    def _download_models(self):
        """Download models if they don't exist."""
        # Download person detection model
        if not os.path.exists(Config.MODEL_PATH):
            print("Downloading YOLO model...")
            urllib.request.urlretrieve(Config.MODEL_URL, Config.MODEL_PATH)
            print("Download complete.")
        else:
            print("Model already exists.")
        
        # Check face detection model
        if not os.path.exists(Config.FACE_MODEL_PATH):
            print("Face detection model not found.")
            print("Please contact developer to get face model.")
        else:
            print("Face model already exists.")
    
    def _load_models(self):
        """Load the models into memory."""
        self.person_model = YOLO(Config.MODEL_PATH)
        
        if os.path.exists(Config.FACE_MODEL_PATH):
            self.face_model = YOLO(Config.FACE_MODEL_PATH)
        else:
            self.face_model = None
            print("Face model not available.")
    
    def get_person_model(self):
        """Get the person detection model."""
        if not self._initialized:
            self.initialize()
        return self.person_model
    
    def get_face_model(self):
        """Get the face detection model."""
        if not self._initialized:
            self.initialize()
        return self.face_model
    
    def has_face_model(self):
        """Check if face model is available."""
        return self.face_model is not None


# Global model manager instance
model_manager = ModelManager()